# main.py
import numpy as np
from config import EJERCICIOS, VISTAS, CONFIG_DATA
from data_loader import load_and_preprocess_data
from biomechanics import construir_modelo_biomecanico
from ml_pipeline import create_dataset_biomecanico, train_and_select_best_model
from recommender import evaluar_video
from model_manager import save_pipeline

def seleccionar_configuracion():
    print("EJERCICIOS")
    for k, v in EJERCICIOS.items():
        print(f"{k}. {v}")
    op_ejercicio = int(input("\nSeleccione un ejercicio: "))
    ejercicio = EJERCICIOS[op_ejercicio]

    print("\nVISTAS")
    for k, v in VISTAS.items():
        print(f"{k}. {v}")
    op_vista = int(input("\nSeleccione una vista: "))
    vista = VISTAS[op_vista]
    
    return ejercicio, vista

def main():
    print("🚀 Iniciando pipeline biomecánico...")
    ejercicio, vista = seleccionar_configuracion()
    config_seleccionada = CONFIG_DATA[(ejercicio, vista)]
    
    # 1. Preprocesamiento de Datos
    print("\n[1/5] Cargando y procesando datos...")
    df_pivot, temporal_features = load_and_preprocess_data(ejercicio, vista, config_seleccionada)
    print(f"Datos listos. Shape: {df_pivot.shape}")

    # 2. Generación del Modelo de Referencia
    print("\n[2/5] Construyendo modelo biomecánico de referencia...")
    modelo_referencia = construir_modelo_biomecanico(df_pivot, ejercicio, vista)
    print("Modelo de referencia creado con éxito.")

    # 3. Construcción del Dataset para Machine Learning
    print("\n[3/5] Extrayendo características y creando dataset ML...")
    X_ml, y_ml, groups_ml = create_dataset_biomecanico(df_pivot, modelo_referencia, ejercicio, vista)
    print(f"Shape del dataset ML: {X_ml.shape}")

    # 4. Entrenamiento y Selección del Mejor Modelo
    print("\n[4/5] Entrenando clasificadores y realizando Cross-Validation...")
    modelo_final, scaler_final, ranking_df = train_and_select_best_model(X_ml, y_ml, groups_ml)
    print("\nRanking de Modelos:")
    print(ranking_df[["Model", "MCC Mean"]])

    # 5. Guardado de los Modelos (Para Inferencia Futura)
    print("\n[5/5] Guardando pipeline en disco...")
    save_pipeline(modelo_final, scaler_final, modelo_referencia, ejercicio, vista)

    # 6. Prueba Dinámica (Simulación de Inferencia)
    print("\n--- PRUEBA CON VIDEO ALEATORIO ---")
    video_prueba = np.random.choice(df_pivot["video"].unique())
    resultado = evaluar_video(video_prueba, df_pivot, modelo_referencia, modelo_final, scaler_final, ejercicio, vista)
    
    print(f"\n🎥 Video evaluado: {resultado['video']}")
    print(f"Puntuación Biomecánica: {resultado['score_biomecanico']:.2f}%")
    print(f"Clasificación ML: {resultado['calidad']}")
    if resultado['confianza'] is not None:
        print(f"Confianza: {100*resultado['confianza']:.2f}%")
    
    print("\n📋 RECOMENDACIONES:")
    print(resultado["recomendaciones"].to_string(index=False))

if __name__ == "__main__":
    main()