# api.py
import logging
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import joblib
import pandas as pd
import numpy as np
import uuid

from config import CONFIG_DATA
from video_processor import process_video_and_extract_csv, detectar_repeticiones
from data_loader import load_and_preprocess_data
from recommender import evaluar_video
from biomechanics import extraer_indicadores_video, comparar_con_modelo

app = FastAPI(title="Biomecánica API")

# Configurar el logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Carpeta para guardar los videos renderizados temporalmente
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


def calcular_score_y_calidad_ml(
    df_pivot_rep, modelo_referencia, modelo_ml, scaler, ejercicio, vista
):
    """
    Construye exactamente el mismo vector de características del entrenamiento
    y extrae tanto la etiqueta como el porcentaje (%) directo de la probabilidad del modelo ML.
    """
    indicadores = extraer_indicadores_video(df_pivot_rep, ejercicio, vista)

    # print("\n--- DIAGNÓSTICO INDICADORES (CURL LATERAL) ---")
    # for _, row in modelo_referencia.iterrows():
    #    p = row["Parametro"]
    #    val = indicadores[p]
    #    ok = row["Limite inferior"] <= val <= row["Limite superior"]
    #    print(
    #        f"  {p}: {val:.3f} | Ideal: {row['Valor ideal']:.3f} [{row['Limite inferior']:.3f}, {row['Limite superior']:.3f}] -> {'OK' if ok else 'FALLA'}"

    #    )

    feature_vector = []
    cumple_total = 0

    for _, row in modelo_referencia.iterrows():
        parametro = row["Parametro"]
        ideal = row["Valor ideal"]
        inferior = row["Limite inferior"]
        superior = row["Limite superior"]
        valor = indicadores[parametro]

        desviacion = abs(valor - ideal)
        desviacion_relativa = desviacion / (abs(ideal) + 1e-6)
        cumple = int(inferior <= valor <= superior)

        feature_vector.extend([valor, desviacion, desviacion_relativa, cumple])
        cumple_total += cumple

    porcentaje_cumplimiento = cumple_total / len(modelo_referencia)
    _, score_global = comparar_con_modelo(indicadores, modelo_referencia)

    feature_vector.extend([score_global, porcentaje_cumplimiento])

    X_rep = np.array([feature_vector])
    X_rep_scaled = scaler.transform(X_rep)

    # Obtener probabilidad de la clase 1 ("Correcta")
    if hasattr(modelo_ml, "predict_proba"):
        prob_correcta = float(modelo_ml.predict_proba(X_rep_scaled)[0][1]) * 100.0
        calidad_ml = "Correcta" if prob_correcta >= 50.0 else "Incorrecta"
    else:
        pred = modelo_ml.predict(X_rep_scaled)[0]
        prob_correcta = 100.0 if pred == 1 else 0.0
        calidad_ml = "Correcta" if pred == 1 else "Incorrecta"

    return calidad_ml, round(prob_correcta, 2)


@app.post("/analizar_video")
async def analizar_video(
    request: Request,
    file: UploadFile = File(...),
    ejercicio: str = Form(...),
    vista: str = Form(...),
):
    logger.info(f"\n--- NUEVA PETICIÓN RECIBIDA ---")
    logger.info(f"Ejercicio: {ejercicio} | Vista: {vista}")

    unique_id = str(uuid.uuid4())[:8]
    temp_video_path = f"static/video_in_{unique_id}.mp4"
    temp_csv_path = f"temp_{unique_id}.csv"

    with open(temp_video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logger.info(f"[1/5] Video guardado temporalmente como: {temp_video_path}")

    try:
        logger.info("[2/5] Extrayendo landmarks con MediaPipe (Esto tomará tiempo)...")
        df_raw, ruta_black, ruta_overlay = process_video_and_extract_csv(
            video_path=temp_video_path,
            output_csv_path=temp_csv_path,
            generate_skeleton_video=True,
            generate_overlay_video=True,  # Generamos el sobrepuesto para la app
            vista=vista,
        )

        if df_raw.empty:
            logger.info("ERROR: No se detectó persona.")
            return JSONResponse(
                content={"error": "No se detectó persona en el video."}, status_code=400
            )

        logger.info("[3/5] Landmarks extraídos. Detectando repeticiones...")
        repeticiones = detectar_repeticiones(df_raw, ejercicio)
        logger.info(f"      Se encontraron {len(repeticiones)} repeticiones.")
        if not repeticiones:
            repeticiones = [(df_raw["frame"].min(), df_raw["frame"].max())]

        logger.info("[4/5] Evaluando técnica con Machine Learning...")
        target_dir = os.path.join("saved_models", ejercicio.replace(" ", "_"), vista)
        modelo = joblib.load(os.path.join(target_dir, "best_model.pkl"))
        scaler = joblib.load(os.path.join(target_dir, "scaler.pkl"))
        modelo_referencia = pd.read_pickle(
            os.path.join(target_dir, "modelo_referencia.pkl")
        )

        config_temp = CONFIG_DATA[(ejercicio, vista)].copy()
        config_temp["csv"] = temp_csv_path
        df_pivot, _ = load_and_preprocess_data(ejercicio, vista, config_temp)
        video_name = os.path.basename(temp_video_path)

        resultados_reps = []
        FPS = 30.0

        for i, (inicio, fin) in enumerate(repeticiones):
            df_pivot_rep = df_pivot[
                (df_pivot["frame"] >= inicio) & (df_pivot["frame"] <= fin)
            ]
            if df_pivot_rep.empty:
                continue

            # 1. Usar evaluar_video únicamente para obtener las recomendaciones del modelo de referencia
            res = evaluar_video(
                video_name,
                df_pivot_rep,
                modelo_referencia,
                modelo,
                scaler,
                ejercicio,
                vista,
            )
            recs = (
                res["recomendaciones"].to_dict(orient="records")
                if not res["recomendaciones"].empty
                else []
            )

            # 2. Obtener calidad y porcentaje (%) directamente de la máquina de aprendizaje
            calidad_ml, score_ml = calcular_score_y_calidad_ml(
                df_pivot_rep, modelo_referencia, modelo, scaler, ejercicio, vista
            )

            resultados_reps.append(
                {
                    "rep_num": i + 1,
                    "inicio_seg": round(inicio / FPS, 2),
                    "fin_seg": round(fin / FPS, 2),
                    "calidad": calidad_ml,
                    "score": score_ml,
                    "recomendaciones": recs,
                }
            )

        logger.info(
            "[5/5] Evaluación terminada. Empaquetando resultados y enviando al celular..."
        )
        base_url = str(request.base_url)
        respuesta = {
            "video_url": f"{base_url}{ruta_overlay}",
            "video_url_negro": f"{base_url}{ruta_black}",
            "repeticiones": resultados_reps,
        }

        print(respuesta)
        return JSONResponse(content=respuesta)

    finally:
        logger.info("--- PROCESO FINALIZADO. Limpiando archivos temporales ---")
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if os.path.exists(temp_csv_path):
            os.remove(temp_csv_path)


# Para ejecutar: uvicorn api:app --host 0.0.0.0 --port 8000
