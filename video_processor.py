# video_processor.py
import cv2
import os
import subprocess
import numpy as np
import pandas as pd
import mediapipe as mp
from scipy.signal import find_peaks, savgol_filter


# Inicialización compatible con MediaPipe 0.10.14
mp_pose = mp.solutions.pose  # type: ignore
mp_drawing = mp.solutions.drawing_utils  # type: ignore
mp_drawing_styles = mp.solutions.drawing_styles # type: ignore

def preprocess_frame(frame):
    """
    Aplica filtros de mejora (CLAHE, Sobel, Sharpen) al frame de entrada.
    """
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = cv2.bilateralFilter(rgb, 7, 60, 60)

    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
    edges = cv2.magnitude(sobelx, sobely)
    edges = cv2.normalize(edges, None, 0, 255, cv2.NORM_MINMAX).astype("uint8") # type: ignore
    edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    
    rgb = cv2.addWeighted(rgb, 1.0, edges_color, 0.15, 0)

    kernel_sharpen = np.array([
        [-1, -1, -1],
        [-1,  9, -1],
        [-1, -1, -1]
    ])
    rgb = cv2.filter2D(rgb, -1, kernel_sharpen)

    return rgb


def process_video_and_extract_csv(video_path, output_csv_path=None, generate_skeleton_video=False, generate_overlay_video=False, vista="lateral"):
    video_name = os.path.basename(video_path)
    
    # ⚡ 1. LEER DIMENSIONES Y CONFIGURAR ORIENTACIÓN
    cap_check = cv2.VideoCapture(video_path)
    w_orig = int(cap_check.get(cv2.CAP_PROP_FRAME_WIDTH))
    h_orig = int(cap_check.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_original = cap_check.get(cv2.CAP_PROP_FPS)
    if fps_original == 0: fps_original = 30
    
    es_horizontal = w_orig > h_orig
    mirando_a_izquierda = False
    
    # Si es horizontal, sus dimensiones "reales" finales estarán invertidas
    if es_horizontal:
        w_orig, h_orig = h_orig, w_orig

    # ⚡ 2. PASO 0: DETECCIÓN AUTOMÁTICA DE ORIENTACIÓN (VISTA LATERAL)
    if vista == "lateral":
        with mp_pose.Pose(static_image_mode=False, model_complexity=1) as pose_check:
            for _ in range(15):
                ret, frame_chk = cap_check.read()
                if not ret: break
                
                # Aplicamos la rotación en memoria temporalmente para que MediaPipe vea bien la pose
                if es_horizontal:
                    frame_chk = cv2.rotate(frame_chk, cv2.ROTATE_90_CLOCKWISE)
                    
                res_chk = pose_check.process(cv2.cvtColor(frame_chk, cv2.COLOR_BGR2RGB))
                if res_chk.pose_landmarks:
                    nariz_x = res_chk.pose_landmarks.landmark[0].x
                    hombro_izq_x = res_chk.pose_landmarks.landmark[11].x
                    hombro_der_x = res_chk.pose_landmarks.landmark[12].x
                    centro_hombros_x = (hombro_izq_x + hombro_der_x) / 2
                    
                    mirando_a_izquierda = nariz_x < centro_hombros_x
                    if mirando_a_izquierda:
                        print("🔄 [Orientación] Persona mirando a la izquierda. Se reflejará el video.")
                    break
                    
    cap_check.release()

    # ⚡ 3. PROCESAMIENTO PRINCIPAL
    cap = cv2.VideoCapture(video_path)
    
    saltar_frames = (fps_original > 45)
    fps_salida = fps_original / 2 if saltar_frames else fps_original
    
    max_height = 720
    if h_orig > max_height:
        escala = max_height / h_orig
        w_reducido = int(w_orig * escala)
        h_reducido = max_height
    else:
        w_reducido, h_reducido = w_orig, h_orig

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_overlay = None
    tmp_overlay_path = None
    final_overlay_path = None
    
    out_skeleton = None
    tmp_skeleton_path = None
    final_skeleton_path = None

    if generate_overlay_video:
        tmp_overlay_path = video_path.replace(".mp4", "_raw_overlay.mp4")
        final_overlay_path = video_path.replace(".mp4", "_Postura_Overlay.mp4")
        out_overlay = cv2.VideoWriter(tmp_overlay_path, fourcc, fps_salida, (w_reducido, h_reducido))

    if generate_skeleton_video:
        tmp_skeleton_path = video_path.replace(".mp4", "_raw_black.mp4")
        final_skeleton_path = video_path.replace(".mp4", "_Postura_Black.mp4")
        out_skeleton = cv2.VideoWriter(tmp_skeleton_path, fourcc, fps_salida, (w_reducido, h_reducido))

    landmarks_data = []
    frame_idx = 0
    real_frame_idx = 0 

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        while True:
            ret, frame_original = cap.read()
            if not ret: break
            real_frame_idx += 1
            
            if saltar_frames and real_frame_idx % 2 == 0:
                continue
                
            # ⚡ 4. APLICAR CORRECCIONES EN MEMORIA (MUCHO MÁS RÁPIDO)
            if es_horizontal:
                frame_original = cv2.rotate(frame_original, cv2.ROTATE_90_CLOCKWISE)
            if mirando_a_izquierda:
                frame_original = cv2.flip(frame_original, 1) # Reflejo de espejo

            if h_orig > max_height:
                frame_ia = cv2.resize(frame_original, (w_reducido, h_reducido))
            else:
                frame_ia = frame_original

            frame_rgb = cv2.cvtColor(frame_ia, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)
                
            if generate_overlay_video:
                overlay_frame = frame_original.copy()
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        overlay_frame, 
                        results.pose_landmarks, 
                        mp_pose.POSE_CONNECTIONS
                    )
                if h_orig > max_height:
                    overlay_frame = cv2.resize(overlay_frame, (w_reducido, h_reducido))
                out_overlay.write(overlay_frame)

            if generate_skeleton_video:
                black_frame = np.zeros((h_orig, w_orig, 3), dtype=np.uint8)
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        black_frame, 
                        results.pose_landmarks, 
                        mp_pose.POSE_CONNECTIONS
                    )
                if h_orig > max_height:
                    black_frame = cv2.resize(black_frame, (w_reducido, h_reducido))
                out_skeleton.write(black_frame)
            
            if results.pose_landmarks:
                for landmark_id, landmark in enumerate(results.pose_landmarks.landmark):
                    landmarks_data.append({
                        "video": video_name,
                        "frame": frame_idx,
                        "landmark_id": landmark_id,
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z
                    })
            frame_idx += 1

    cap.release()
    if out_overlay: out_overlay.release()
    if out_skeleton: out_skeleton.release()

    # ⚡ 5. COMPRESIÓN FFMPEG FINAL
    if generate_overlay_video and tmp_overlay_path:
        cmd_overlay = [
            "ffmpeg", "-y", "-i", tmp_overlay_path,
            "-an", "-r", str(int(fps_salida)),
            "-b:v", "900k", 
            "-c:v", "libx264", "-preset", "ultrafast", final_overlay_path
        ]
        try:
            subprocess.run(cmd_overlay, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            os.remove(tmp_overlay_path)
        except FileNotFoundError:
            if os.path.exists(final_overlay_path): os.remove(final_overlay_path)
            os.rename(tmp_overlay_path, final_overlay_path)

    if generate_skeleton_video and tmp_skeleton_path:
        cmd_skeleton = [
            "ffmpeg", "-y", "-i", tmp_skeleton_path,
            "-an", "-r", str(int(fps_salida)),
            "-b:v", "900k", 
            "-c:v", "libx264", "-preset", "ultrafast", final_skeleton_path
        ]
        try:
            subprocess.run(cmd_skeleton, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            os.remove(tmp_skeleton_path)
        except FileNotFoundError:
            if os.path.exists(final_skeleton_path): os.remove(final_skeleton_path)
            os.rename(tmp_skeleton_path, final_skeleton_path)

    df = pd.DataFrame(landmarks_data)
    if output_csv_path and not df.empty:
        df.to_csv(output_csv_path, index=False)
        
    return df, final_skeleton_path, final_overlay_path

def detectar_repeticiones(df_raw, ejercicio):
    """
    Analiza las coordenadas Y para detectar repeticiones.
    Incluye aislamiento de la fase activa (detectando quietud) 
    y corrección de bordes para repeticiones reales.
    """
    landmark_ref = 24 if ejercicio in ["sentadilla", "peso muerto"] else 16
    
    datos = df_raw[df_raw['landmark_id'] == landmark_ref].sort_values('frame')
    y_vals = datos['y'].values
    frames = datos['frame'].values
    
    if len(y_vals) < 15:
        return []
    
    window_length = min(15, len(y_vals) - 1 if len(y_vals) % 2 == 0 else len(y_vals))
    if window_length < 3:
        y_smooth = y_vals
    else:
        y_smooth = savgol_filter(y_vals, window_length=window_length, polyorder=3)
        
    # --- 1. DETECCIÓN DE QUIETUD (Filtro de preparación) ---
    # Calculamos qué tanto se mueve el punto Y en cada frame
    velocidad = np.abs(np.diff(y_smooth, prepend=y_smooth[0]))
    
    # Suavizamos la velocidad para encontrar las "zonas" (ventana de ~15 frames)
    volatilidad = pd.Series(velocidad).rolling(window=15, center=True).mean().bfill().ffill().values
    
    # Si se mueve menos del 0.4% del frame de alto, consideramos que está "quieto"
    umbral_quietud = 0.004
    es_quieto = volatilidad < umbral_quietud
    
    inicio_idx = 0
    fin_idx = len(y_smooth) - 1
    
    # Buscar cuándo termina de acomodarse y empieza el primer movimiento real
    en_preparacion = False
    for i in range(len(es_quieto)):
        if es_quieto[i]:
            en_preparacion = True # Ya llegó a su posición inicial y se estabilizó
        elif en_preparacion and not es_quieto[i]:
            inicio_idx = i # Rompió la quietud, arranca la repetición
            break
            
    # Buscar de atrás hacia adelante cuándo terminó su última repetición
    en_finalizacion = False
    for i in range(len(es_quieto)-1, -1, -1):
        if es_quieto[i]:
            en_finalizacion = True # Ya terminó y está quieto antes de irse
        elif en_finalizacion and not es_quieto[i]:
            fin_idx = i # Retrocediendo, aquí fue el final del último esfuerzo
            break
            
    # Validamos por seguridad (si el video es corto o nunca se quedó quieto, usamos todo)
    if inicio_idx >= fin_idx or (fin_idx - inicio_idx) < 30:
        inicio_idx = 0
        fin_idx = len(y_smooth) - 1
        
    # --- 2. RECORTAR SEÑAL A LA FASE ACTIVA ---
    señal_analisis = y_smooth[inicio_idx:fin_idx+1]
    frames_activos = frames[inicio_idx:fin_idx+1]
    
    if ejercicio in ["sentadilla", "peso muerto"]:
        señal_analisis = -señal_analisis # Invertir señal porque se baja
        prominencia = 0.015 
    else:
        prominencia = 0.03
        
    # --- 3. CORRECCIÓN DE BORDES Y DETECCIÓN DE PICOS ---
    min_val = np.min(señal_analisis) - 1
    señal_modificada = np.insert(señal_analisis, 0, min_val)
    señal_modificada = np.append(señal_modificada, min_val)
    
    picos_idx_mod, _ = find_peaks(señal_modificada, prominence=prominencia)
    picos_idx = picos_idx_mod - 1
    picos_idx = picos_idx[(picos_idx >= 0) & (picos_idx < len(señal_analisis))]
    
    repeticiones = []
    for i in range(len(picos_idx) - 1):
        frame_inicio = frames_activos[picos_idx[i]]
        frame_fin = frames_activos[picos_idx[i+1]]
        repeticiones.append((frame_inicio, frame_fin))
        
    return repeticiones