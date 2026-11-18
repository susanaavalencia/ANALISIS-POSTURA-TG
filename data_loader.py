# data_loader.py
import pandas as pd
from utils import normalize_skeleton, get_label, get_person
from features_extractor import extraer_features_laterales, extraer_features_frontales
from config import FEATURE_NAMES

def load_and_preprocess_data(ejercicio, vista, config_data):
    csv_path = config_data["csv"]
    selected_ids = config_data["selected_ids"]
    mode = config_data["mode"]

    df = pd.read_csv(csv_path)

    # Pivoteo
    df_pivot = df.pivot_table(index=["video","frame"], columns="landmark_id", values=["x","y","z"])
    df_pivot.columns = [f"{coord}_{lm}" for coord, lm in df_pivot.columns]
    df_pivot = df_pivot.reset_index().fillna(0)

    # Extraer columnas deseadas
    feature_cols = [f"{coord}_{lm}" for lm in selected_ids for coord in ["x","y","z"]]

    # Normalización
    df_pivot[feature_cols] = df_pivot[feature_cols].apply(normalize_skeleton, axis=1, result_type="expand")

    # Extracción de características biomecánicas
    if mode == "angles":
        features = df_pivot[feature_cols].apply(lambda row: extraer_features_laterales(row, ejercicio), axis=1, result_type="expand")
    else:
        features = df_pivot[feature_cols].apply(lambda row: extraer_features_frontales(row, ejercicio), axis=1, result_type="expand")

    # Nombrar e integrar features
    features.columns = FEATURE_NAMES[(ejercicio, vista)]
    df_pivot = pd.concat([df_pivot, features], axis=1)

    # Etiquetado
    df_pivot["label"] = df_pivot["video"].apply(get_label)
    df_pivot["person"] = df_pivot["video"].apply(get_person)

    temporal_features = list(features.columns)
    
    return df_pivot, temporal_features