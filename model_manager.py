# model_manager.py
import os

def save_trained_model(model, ejercicio, vista, filename="modelo_final.h5"):
    """
    Crea la ruta dinámica y guarda el modelo en el disco.
    Compatible con modelos de TensorFlow/Keras o Scikit-Learn.
    """
    # Crear estructura: ./saved_models/sentadilla/lateral/
    base_dir = "saved_models"
    target_dir = os.path.join(base_dir, ejercicio.replace(" ", "_"), vista)
    
    # Crear carpetas si no existen
    os.makedirs(target_dir, exist_ok=True)
    
    # Ruta completa del archivo
    file_path = os.path.join(target_dir, filename)
    
    # Aquí asumo que usas TensorFlow por las librerías de tu código
    model.save(file_path)
    print(f"✅ Modelo guardado exitosamente en: {file_path}")
    

# model_manager.py
import os
import joblib

def save_pipeline(modelo, scaler, modelo_referencia, ejercicio, vista):
    """
    Guarda el modelo ML, el scaler y el DataFrame del modelo de referencia en disco.
    """
    base_dir = "saved_models"
    target_dir = os.path.join(base_dir, ejercicio.replace(" ", "_"), vista)
    os.makedirs(target_dir, exist_ok=True)
    
    joblib.dump(modelo, os.path.join(target_dir, "best_model.pkl"))
    joblib.dump(scaler, os.path.join(target_dir, "scaler.pkl"))
    modelo_referencia.to_pickle(os.path.join(target_dir, "modelo_referencia.pkl"))
    
    print(f"✅ Pipeline guardado exitosamente en: {target_dir}")