# recommender.py
import numpy as np
import pandas as pd
from biomechanics import extraer_indicadores_video, comparar_con_modelo
from config import RECOMENDACIONES_LEVES, RECOMENDACIONES

def generar_recomendaciones(detalle, calidad):
    # 1. Filtrar los que no cumplen
    fuera_rango = detalle[detalle["Cumple"] == False].copy()
    
    if len(fuera_rango) == 0:
        return pd.DataFrame({
            "Parametro": ["Sin observaciones"],
            "Recomendacion": ["Todos los indicadores biomecánicos se encuentran dentro de los rangos de referencia."]
        })
        
    # 2. Ordenar por la magnitud del error
    fuera_rango = fuera_rango.sort_values(by="Desviacion", ascending=False)
    
    # 3. MAPEO DE ZONAS (Cadena Cinética)
    ZONAS = {
        "hombros_brazos": [
            "simetria_hombros", "max_dif_altura_hombros", "max_inclinacion_hombros", 
            "max_asimetria_brazos", "max_dif_altura_manos", "simetria_codos", 
            "simetria_munecas", "max_dif_altura_munecas", "max_inclinacion_barra", 
            "rom_codo", "distancia_media_codo_hombro", "distancia_media_codo_cadera", 
            "diferencia_angulos_codo"
        ],
        "cadera_core": [
            "simetria_caderas", "max_dif_altura_caderas", "max_inclinacion_caderas", 
            "max_desplazamiento_lateral", "longitud_torso", "angulo_min_cadera", 
            "profundidad_descenso"
        ],
        "rodillas_piernas": [
            "simetria_rodillas", "max_dif_altura_rodillas", "max_asimetria_piernas", 
            "angulo_min_rodilla"
        ],
        "trayectoria": [
            "desplazamiento_horizontal_barra", "trayectoria_horizontal_barra", 
            "ratio_pecho_abdomen", "velocidad_media_codo",
            "distancia_mano_rodilla"
        ],
        
        "punto_contacto": [  # ⚡ NUEVA ZONA EXCLUSIVA
            "ratio_pecho_abdomen", "distancia_muneca_hombro"
        ]
    }

    param_a_zona = {}
    for zona, params in ZONAS.items():
        for p in params:
            param_a_zona[p] = zona
            
    recomendaciones = []
    conteo_zonas = {} # ⚡ NUEVO: Diccionario para llevar el conteo numérico por zona
    
    dict_ref = RECOMENDACIONES_LEVES if calidad == "Correcta" else RECOMENDACIONES
    
    # Aumentamos el límite global para dar espacio a múltiples recomendaciones
    MAX_RECOMENDACIONES = 2 if calidad == "Correcta" else 4 
            
    for _, row in fuera_rango.iterrows():
        if len(recomendaciones) >= MAX_RECOMENDACIONES:
            break
            
        param = row["Parametro"]
        direccion = row.get("Direccion", "exceso")
        zona = param_a_zona.get(param, "general")
        
        # ⚡ NUEVO: Verificamos si esta zona ya alcanzó el límite de 2 recomendaciones
        if conteo_zonas.get(zona, 0) >= 2 and zona != "general":
            continue
            
        if param in dict_ref:
            if isinstance(dict_ref[param], dict):
                texto = dict_ref[param].get(direccion, dict_ref[param].get("exceso"))
            else:
                texto = dict_ref[param]
                
            recomendaciones.append({"Parametro": param, "Recomendacion": texto})
            
            # ⚡ NUEVO: Le sumamos 1 al contador de esta zona
            conteo_zonas[zona] = conteo_zonas.get(zona, 0) + 1
                
    return pd.DataFrame(recomendaciones)

def evaluar_video(video, df_pivot, modelo_referencia, modelo_final, scaler_final, ejercicio, vista):
    data_video = df_pivot[df_pivot["video"] == video]
    indicadores = extraer_indicadores_video(data_video, ejercicio, vista)
    detalle, score_biomecanico = comparar_con_modelo(indicadores, modelo_referencia)
    
    feature_vector = []
    cumple_total = 0
    direcciones = {} # ⚡ NUEVO: Diccionario para guardar el tipo de falla
    
    for _, row in modelo_referencia.iterrows():
        parametro = row["Parametro"]
        ideal = row["Valor ideal"]
        valor = indicadores[parametro]
        
        desviacion = abs(valor - ideal)
        desviacion_relativa = desviacion / (abs(ideal) + 1e-6)
        cumple = int(row["Limite inferior"] <= valor <= row["Limite superior"])
        
        # ⚡ NUEVO: Clasificamos direccionalmente la falla
        if valor > row["Limite superior"]:
            direcciones[parametro] = "exceso"
        elif valor < row["Limite inferior"]:
            direcciones[parametro] = "defecto"
        else:
            direcciones[parametro] = "normal"
            
        feature_vector.extend([valor, desviacion, desviacion_relativa, cumple])
        cumple_total += cumple
        
    # ⚡ NUEVO: Inyectamos la dirección al dataframe de detalle antes de generar recomendaciones
    detalle["Direccion"] = detalle["Parametro"].map(direcciones)
    
    feature_vector.extend([score_biomecanico, cumple_total / len(modelo_referencia)])
    X_video = scaler_final.transform(np.array(feature_vector).reshape(1,-1))
    
    pred = modelo_final.predict(X_video)[0]
    calidad = "Correcta" if pred == 1 else "Incorrecta"
    confianza = np.max(modelo_final.predict_proba(X_video)) if hasattr(modelo_final, "predict_proba") else None
    
    recomendaciones = generar_recomendaciones(detalle, calidad)
    
    return {
        "video": video,
        "score_biomecanico": score_biomecanico,
        "calidad": calidad,
        "confianza": confianza,
        "detalle": detalle,
        "recomendaciones": recomendaciones
    }