# test_pipeline.py
import os
import joblib
import pandas as pd


from config import CONFIG_DATA, EJERCICIOS, VISTAS
# Asegúrate de importar detectar_repeticiones aquí
from video_processor import process_video_and_extract_csv, detectar_repeticiones 
from data_loader import load_and_preprocess_data
from recommender import evaluar_video

def seleccionar_configuracion():
    print("\n--- SELECCIÓN DE PARÁMETROS ---")
    print("EJERCICIOS:")
    for k, v in EJERCICIOS.items():
        print(f"{k}. {v.capitalize()}")
    op_ejercicio = int(input("Seleccione un ejercicio (número): "))
    ejercicio = EJERCICIOS[op_ejercicio]

    print("\nVISTAS:")
    for k, v in VISTAS.items():
        print(f"{k}. {v.capitalize()}")
    op_vista = int(input("Seleccione una vista (número): "))
    vista = VISTAS[op_vista]
    
    return ejercicio, vista

def simular_flujo_app():
    print("🚀 --- SIMULACIÓN DE APP BIOMECÁNICA (MULTI-REP) ---")
    
    ejercicio_prueba, vista_prueba = seleccionar_configuracion()
    
    video_entrada = "video_prueba_1.mp4" 
    csv_temporal = "temp_landmarks.csv"

    print(f"\n⚙️ Configuración: {ejercicio_prueba.upper()} - {vista_prueba.upper()}")
    print(f"📁 Archivo a procesar: {video_entrada}")

    if not os.path.exists(video_entrada):
        print(f"\n❌ Error: No se encontró '{video_entrada}'.")
        print("💡 Pon un video en esta carpeta y nómbralo 'video_prueba_1.mp4'")
        return

    target_dir = os.path.join("saved_models", ejercicio_prueba.replace(" ", "_"), vista_prueba)
    if not os.path.exists(os.path.join(target_dir, "best_model.pkl")):
        print(f"\n❌ Error: No se encontraron los modelos guardados en {target_dir}")
        return

    print("\n[1/5] Procesando video con MediaPipe y FFmpeg...")
    df_raw, ruta_black, ruta_overlay = process_video_and_extract_csv(
        video_path=video_entrada,
        output_csv_path=csv_temporal,
        generate_skeleton_video=True,
        generate_overlay_video=True,
        vista=vista_prueba
    )

    if df_raw.empty:
        print("\n❌ Error: No se detectó ninguna persona en el video.")
        return

    print("\n[2/5] Detectando repeticiones...")
    # Llamamos a nuestra nueva función
    repeticiones = detectar_repeticiones(df_raw, ejercicio_prueba)
    
    if not repeticiones:
        print("⚠️ No se detectaron repeticiones claras (el video puede ser muy corto o el movimiento incompleto).")
        print("Tratando todo el video como una sola repetición por defecto.")
        # Fallback: Evaluamos desde el primer hasta el último frame
        repeticiones = [(df_raw['frame'].min(), df_raw['frame'].max())]
    else:
        print(f"✅ Se detectaron {len(repeticiones)} repeticiones.")

    print("\n[3/5] Cargando modelos de Machine Learning...")
    modelo = joblib.load(os.path.join(target_dir, "best_model.pkl"))
    scaler = joblib.load(os.path.join(target_dir, "scaler.pkl"))
    modelo_referencia = pd.read_pickle(os.path.join(target_dir, "modelo_referencia.pkl"))

    print("\n[4/5] Preprocesando dataset biomecánico global...")
    config_temp = CONFIG_DATA[(ejercicio_prueba, vista_prueba)].copy()
    config_temp["csv"] = csv_temporal
    df_pivot, _ = load_and_preprocess_data(ejercicio_prueba, vista_prueba, config_temp)

    print("\n[5/5] Evaluando cada repetición individualmente...")
    video_name = os.path.basename(video_entrada)
        
    # Constante de fotogramas por segundo (FPS)
    FPS = 30.0
        
    # Bucle que evalúa cada repetición detectada
    for i, (inicio, fin) in enumerate(repeticiones):
        # Convertimos los frames a segundos para mostrarlos en pantalla
        inicio_seg = inicio / FPS
        fin_seg = fin / FPS
        
        print(f"\n=======================================================")
        print(f"🔄 EVALUANDO REPETICIÓN {i+1} (Del segundo {inicio_seg:.2f}s al {fin_seg:.2f}s)")
        print(f"=======================================================")
        
        # Internamente seguimos usando los frames para filtrar los datos exactos
        df_pivot_rep = df_pivot[(df_pivot['frame'] >= inicio) & (df_pivot['frame'] <= fin)]
        
        if df_pivot_rep.empty:
            print("⚠️ Error interno: No hay datos para esta repetición.")
            continue
            
        resultado = evaluar_video(
            video_name, 
            df_pivot_rep, 
            modelo_referencia, 
            modelo, 
            scaler, 
            ejercicio_prueba, 
            vista_prueba
        )

        print(f"Calidad del movimiento : {resultado['calidad']}")
        print(f"Puntuación Biomecánica : {resultado['score_biomecanico']:.2f}/100")
        if resultado['confianza'] is not None:
            print(f"Confianza de la IA     : {resultado['confianza']*100:.2f}%")
        
        print("\n📋 RECOMENDACIONES:")
        if resultado["recomendaciones"].empty or resultado["recomendaciones"].iloc[0]["Parametro"] == "Sin observaciones":
            print("- Excelente ejecución. No hay correcciones.")
        else:
            for idx, row in resultado["recomendaciones"].iterrows():
                print(f"- [{row['Parametro']}]: {row['Recomendacion']}")

    print("\n=======================================================")
    print("✅ ANÁLISIS MULTI-REPETICIÓN FINALIZADO")
    print(f"   Videos generados en disco:")
    print(f"   - {ruta_black}")
    print(f"   - {ruta_overlay}")
    
    # Limpieza
    if os.path.exists(csv_temporal):
        os.remove(csv_temporal)

if __name__ == "__main__":
    simular_flujo_app()