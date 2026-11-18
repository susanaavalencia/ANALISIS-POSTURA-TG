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
mp_drawing_styles = mp.solutions.drawing_styles  # type: ignore


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
    edges = cv2.normalize(edges, None, 0, 255, cv2.NORM_MINMAX).astype("uint8")  # type: ignore
    edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    rgb = cv2.addWeighted(rgb, 1.0, edges_color, 0.15, 0)

    kernel_sharpen = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    rgb = cv2.filter2D(rgb, -1, kernel_sharpen)

    return rgb


def process_video_and_extract_csv(
    video_path,
    output_csv_path=None,
    generate_skeleton_video=False,
    generate_overlay_video=False,
    vista="lateral",
):
    video_name = os.path.basename(video_path)

    # ⚡ 1. LEER DIMENSIONES Y CONFIGURAR ORIENTACIÓN
    cap_check = cv2.VideoCapture(video_path)
    w_orig = int(cap_check.get(cv2.CAP_PROP_FRAME_WIDTH))
    h_orig = int(cap_check.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_original = cap_check.get(cv2.CAP_PROP_FPS)
    if fps_original == 0:
        fps_original = 30

    es_horizontal = w_orig > h_orig
    tipo_rotacion = (
        None  # None, cv2.ROTATE_90_CLOCKWISE o cv2.ROTATE_90_COUNTERCLOCKWISE
    )
    mirando_a_izquierda = False

    # ⚡ 2. PASO 0: DETECCIÓN ESTRUCTURAL DE ROTACIÓN Y ESPEJO (SIN DEPENDER DE LA CABEZA/OJOS)
    total_frames = int(cap_check.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_inicio_analisis = int(fps_original * 5)

    if frame_inicio_analisis >= total_frames:
        frame_inicio_analisis = max(0, total_frames // 2)

    frames_disponibles = max(1, total_frames - frame_inicio_analisis)
    paso = max(1, frames_disponibles // 20)

    votos_clockwise = 0
    votos_counterclockwise = 0
    votos_sin_rotar = 0
    frames_rot_validos = 0
    es_press_acostado = False

    with mp_pose.Pose(static_image_mode=True, model_complexity=1) as pose_check:
        # --- FASE A: Determinar rotación de 90° usando el eje Hombros-Caderas (torso) ---
        if es_horizontal:
            for f_idx in range(frame_inicio_analisis, total_frames, paso):
                cap_check.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
                ret, frame_chk = cap_check.read()
                if not ret:
                    break

                res_chk = pose_check.process(cv2.cvtColor(frame_chk, cv2.COLOR_BGR2RGB))
                if res_chk.pose_landmarks:
                    lm = res_chk.pose_landmarks.landmark
                    centro_hombros_x = (lm[11].x + lm[12].x) / 2.0
                    centro_hombros_y = (lm[11].y + lm[12].y) / 2.0
                    centro_caderas_x = (lm[23].x + lm[24].x) / 2.0
                    centro_caderas_y = (lm[23].y + lm[24].y) / 2.0

                    dx = abs(centro_hombros_x - centro_caderas_x)
                    dy = abs(centro_hombros_y - centro_caderas_y)

                    if dx >= dy:
                        es_press_acostado = True
                        if centro_hombros_x < centro_caderas_x:
                            # Hombros a la izquierda de caderas -> girar 90° horario deja hombros arriba
                            votos_clockwise += 1
                        else:
                            # Hombros a la derecha de caderas -> girar 90° antihorario deja hombros arriba
                            votos_counterclockwise += 1
                    else:
                        votos_sin_rotar += 1
                    frames_rot_validos += 1

            if frames_rot_validos > 0:
                if (
                    votos_clockwise >= votos_counterclockwise
                    and votos_clockwise > votos_sin_rotar
                ):
                    tipo_rotacion = cv2.ROTATE_90_CLOCKWISE
                    print(
                        "🔄 [Rotación] Video horizontal (hombros a la izq) -> Girando 90° Horario."
                    )
                elif (
                    votos_counterclockwise > votos_clockwise
                    and votos_counterclockwise > votos_sin_rotar
                ):
                    tipo_rotacion = cv2.ROTATE_90_COUNTERCLOCKWISE
                    print(
                        "🔄 [Rotación] Video horizontal (hombros a la der) -> Girando 90° Antihorario."
                    )
            else:
                tipo_rotacion = cv2.ROTATE_90_CLOCKWISE
                print(
                    "🔄 [Rotación] Video horizontal (respaldo) -> Girando 90° Horario."
                )

        if tipo_rotacion is not None:
            w_orig, h_orig = h_orig, w_orig

        # --- FASE B: Detectar orientación lateral usando SOLO estructura corporal (pies, rodillas, brazos) ---
        if vista == "lateral":
            votos_izquierda = 0
            frames_dir_validos = 0

            for f_idx in range(frame_inicio_analisis, total_frames, paso):
                cap_check.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
                ret, frame_chk = cap_check.read()
                if not ret:
                    break

                if tipo_rotacion is not None:
                    frame_chk = cv2.rotate(frame_chk, tipo_rotacion)

                res_dir = pose_check.process(cv2.cvtColor(frame_chk, cv2.COLOR_BGR2RGB))
                if res_dir.pose_landmarks:
                    lm = res_dir.pose_landmarks.landmark

                    centro_hombros_x = (lm[11].x + lm[12].x) / 2.0
                    centro_caderas_x = (lm[23].x + lm[24].x) / 2.0
                    centro_munecas_x = (lm[15].x + lm[16].x) / 2.0
                    centro_rodillas_x = (lm[25].x + lm[26].x) / 2.0

                    if es_press_acostado:
                        # En press de banca rotado 90° (torso vertical):
                        # Las muñecas (barra) y rodillas están siempre hacia el frente del cuerpo
                        es_izq = (centro_munecas_x < centro_hombros_x) or (
                            centro_rodillas_x < centro_caderas_x
                        )
                    else:
                        # En sentadilla, peso muerto y curl de bíceps (de pie):
                        # 1. Referencia fija #1: Pies plantados en el suelo (punta vs talón del pie más visible)
                        vis_pie_izq = min(lm[29].visibility, lm[31].visibility)
                        vis_pie_der = min(lm[30].visibility, lm[32].visibility)

                        if max(vis_pie_izq, vis_pie_der) > 0.5:
                            if vis_pie_izq >= vis_pie_der:
                                es_izq = (
                                    lm[31].x < lm[29].x
                                )  # Punta izq a la izquierda del talón izq
                            else:
                                es_izq = (
                                    lm[32].x < lm[30].x
                                )  # Punta der a la izquierda del talón der
                        else:
                            # 2. Referencia fija #2 (si los pies no salen en cámara, ej. curl de bíceps plano medio):
                            # Los antebrazos/muñecas y rodillas trabajan por delante de los hombros/caderas
                            es_izq = centro_munecas_x < centro_hombros_x

                    if es_izq:
                        votos_izquierda += 1
                    frames_dir_validos += 1

            if frames_dir_validos > 0 and (votos_izquierda / frames_dir_validos) >= 0.5:
                mirando_a_izquierda = True
                print(
                    f"🪞 [Espejo] Cuerpo orientado a la izquierda tras 5s ({votos_izquierda}/{frames_dir_validos} frames) -> Aplicando reflejo horizontal."
                )
            else:
                print(
                    f"➡️ [Orientación] Cuerpo orientado a la derecha tras 5s ({frames_dir_validos - votos_izquierda}/{frames_dir_validos} frames)."
                )

    cap_check.release()

    # ⚡ 3. PROCESAMIENTO PRINCIPAL
    cap = cv2.VideoCapture(video_path)

    saltar_frames = fps_original > 45
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
        out_overlay = cv2.VideoWriter(
            tmp_overlay_path, fourcc, fps_salida, (w_reducido, h_reducido)
        )

    if generate_skeleton_video:
        tmp_skeleton_path = video_path.replace(".mp4", "_raw_black.mp4")
        final_skeleton_path = video_path.replace(".mp4", "_Postura_Black.mp4")
        out_skeleton = cv2.VideoWriter(
            tmp_skeleton_path, fourcc, fps_salida, (w_reducido, h_reducido)
        )

    landmarks_data = []
    frame_idx = 0
    real_frame_idx = 0

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:

        while True:
            ret, frame_original = cap.read()
            if not ret:
                break
            real_frame_idx += 1

            if saltar_frames and real_frame_idx % 2 == 0:
                continue

            # ⚡ 4. APLICAR CORRECCIONES EN MEMORIA EN ORDEN ESTRICTO
            if tipo_rotacion is not None:
                frame_original = cv2.rotate(frame_original, tipo_rotacion)
            if mirando_a_izquierda:
                frame_original = cv2.flip(
                    frame_original, 1
                )  # Reflejo horizontal para mirar a la derecha

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
                        overlay_frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                    )
                if h_orig > max_height:
                    overlay_frame = cv2.resize(overlay_frame, (w_reducido, h_reducido))
                out_overlay.write(overlay_frame)

            if generate_skeleton_video:
                black_frame = np.zeros((h_orig, w_orig, 3), dtype=np.uint8)
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        black_frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                    )
                if h_orig > max_height:
                    black_frame = cv2.resize(black_frame, (w_reducido, h_reducido))
                out_skeleton.write(black_frame)

            if results.pose_landmarks:
                for landmark_id, landmark in enumerate(results.pose_landmarks.landmark):
                    landmarks_data.append(
                        {
                            "video": video_name,
                            "frame": frame_idx,
                            "landmark_id": landmark_id,
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z,
                        }
                    )
            frame_idx += 1

    cap.release()
    if out_overlay:
        out_overlay.release()
    if out_skeleton:
        out_skeleton.release()

    # ⚡ 5. COMPRESIÓN FFMPEG FINAL
    if generate_overlay_video and tmp_overlay_path:
        cmd_overlay = [
            "ffmpeg",
            "-y",
            "-i",
            tmp_overlay_path,
            "-an",
            "-r",
            str(int(fps_salida)),
            "-b:v",
            "900k",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            final_overlay_path,
        ]
        try:
            subprocess.run(
                cmd_overlay, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )
            os.remove(tmp_overlay_path)
        except FileNotFoundError:
            if os.path.exists(final_overlay_path):
                os.remove(final_overlay_path)
            os.rename(tmp_overlay_path, final_overlay_path)

    if generate_skeleton_video and tmp_skeleton_path:
        cmd_skeleton = [
            "ffmpeg",
            "-y",
            "-i",
            tmp_skeleton_path,
            "-an",
            "-r",
            str(int(fps_salida)),
            "-b:v",
            "900k",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            final_skeleton_path,
        ]
        try:
            subprocess.run(
                cmd_skeleton, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )
            os.remove(tmp_skeleton_path)
        except FileNotFoundError:
            if os.path.exists(final_skeleton_path):
                os.remove(final_skeleton_path)
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
    landmark_ref = 12 if ejercicio in ["sentadilla", "peso muerto"] else 16

    datos = df_raw[df_raw["landmark_id"] == landmark_ref].sort_values("frame")
    y_vals = datos["y"].values
    frames = datos["frame"].values

    if len(y_vals) < 15:
        return []

    window_length = min(15, len(y_vals) - 1 if len(y_vals) % 2 == 0 else len(y_vals))
    if window_length < 3:
        y_smooth = y_vals
    else:
        y_smooth = savgol_filter(y_vals, window_length=window_length, polyorder=3)

    # --- 1. DETECCIÓN DE QUIETUD (Filtro de preparación) ---
    velocidad = np.abs(np.diff(y_smooth, prepend=y_smooth[0]))
    volatilidad = (
        pd.Series(velocidad)
        .rolling(window=15, center=True)
        .mean()
        .bfill()
        .ffill()
        .values
    )

    umbral_quietud = 0.004
    es_quieto = volatilidad < umbral_quietud

    inicio_idx = 0
    fin_idx = len(y_smooth) - 1

    en_preparacion = False
    for i in range(len(es_quieto)):
        if es_quieto[i]:
            en_preparacion = True
        elif en_preparacion and not es_quieto[i]:
            inicio_idx = i
            break

    en_finalizacion = False
    for i in range(len(es_quieto) - 1, -1, -1):
        if es_quieto[i]:
            en_finalizacion = True
        elif en_finalizacion and not es_quieto[i]:
            fin_idx = i
            break

    if inicio_idx >= fin_idx or (fin_idx - inicio_idx) < 30:
        inicio_idx = 0
        fin_idx = len(y_smooth) - 1

    # --- 2. RECORTAR SEÑAL A LA FASE ACTIVA ---
    señal_analisis = y_smooth[inicio_idx : fin_idx + 1]
    frames_activos = frames[inicio_idx : fin_idx + 1]

    if ejercicio in ["sentadilla", "peso muerto"]:
        señal_analisis = -señal_analisis
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
        frame_fin = frames_activos[picos_idx[i + 1]]
        repeticiones.append((frame_inicio, frame_fin))

    return repeticiones
