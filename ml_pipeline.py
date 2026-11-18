# ml_pipeline.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import matthews_corrcoef, accuracy_score, confusion_matrix
from biomechanics import extraer_indicadores_video, comparar_con_modelo

def create_dataset_biomecanico(df_pivot, modelo_referencia, ejercicio, vista):
    X, y, groups = [], [], []
    
    for video in df_pivot["video"].unique():
        data_video = df_pivot[df_pivot["video"] == video]
        indicadores = extraer_indicadores_video(data_video, ejercicio, vista)
        
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
        X.append(feature_vector)
        y.append(1 if "bien" in video.lower() else 0)
        groups.append(data_video["person"].iloc[0])
        
    return np.array(X), np.array(y), np.array(groups)

def train_and_select_best_model(X_ml, y_ml, groups_ml):
    models = {
        "SVM": SVC(kernel="rbf", C=10, gamma="scale", probability=True),
        "Random Forest": RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=500, max_depth=4, learning_rate=0.03, subsample=0.8, colsample_bytree=0.8, random_state=42),
        "MLP": MLPClassifier(hidden_layer_sizes=(128,64), max_iter=500, random_state=42)
    }

    gkf = GroupKFold(n_splits=5)
    results_cv = []

    for model_name, model in models.items():
        fold_mcc = []
        y_true_all = []
        y_pred_all = []
        
        for train_idx, test_idx in gkf.split(X_ml, y_ml, groups_ml):
            X_train, X_test = X_ml[train_idx], X_ml[test_idx]
            y_train, y_test = y_ml[train_idx], y_ml[test_idx]
            
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)
            
            model.fit(X_train, y_train)
            pred = model.predict(X_test)
            
            fold_mcc.append(matthews_corrcoef(y_test, pred))
            y_true_all.extend(y_test)
            y_pred_all.extend(pred)
            
        # ⚡ Calcular y mostrar la matriz de confusión acumulada de los folds
        cm = confusion_matrix(y_true_all, y_pred_all)
        print(f"\n========================================")
        print(f" Matriz de Confusión (Validación Cruzada) - {model_name}")
        print(f"========================================")
        print(cm)
        print("Formato: [[Verdaderos Negativos (TN), Falsos Positivos (FP)],\n          [Falsos Negativos (FN), Verdaderos Positivos (TP)]]\n")
            
        results_cv.append({"Model": model_name, "MCC Mean": np.mean(fold_mcc)})

    # Ranking y selección del mejor
    cv_results_df = pd.DataFrame(results_cv).sort_values(by="MCC Mean", ascending=False)
    best_model_name = cv_results_df.iloc[0]["Model"]
    
    print(f"\nMejor modelo seleccionado automáticamente: {best_model_name}")
    
    # Entrenar el mejor modelo con TODOS los datos para producción
    best_model = models[best_model_name]
    scaler_final = StandardScaler()
    X_ml_scaled = scaler_final.fit_transform(X_ml)
    best_model.fit(X_ml_scaled, y_ml)
    
    return best_model, scaler_final, cv_results_df