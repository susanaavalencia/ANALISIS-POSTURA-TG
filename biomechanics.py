# biomechanics.py
import numpy as np
import pandas as pd

def extraer_indicadores_video(data, ejercicio, vista):
    if ejercicio == "sentadilla" and vista == "lateral":
        return {
            "angulo_min_rodilla": data["angulo_rodilla"].min(),
            "angulo_min_cadera": data["angulo_cadera"].min(),
            "longitud_torso": data["distancia_torso"].mean()
        }
    elif ejercicio == "sentadilla" and vista == "frontal":
        return {
            "simetria_hombros": data["simetria_hombros"].mean(),
            "simetria_caderas": data["simetria_caderas"].mean(),
            "simetria_rodillas": data["simetria_rodillas"].mean(),
            "max_dif_altura_hombros": data["dif_altura_hombros"].max(),
            "max_dif_altura_caderas": data["dif_altura_caderas"].max(),
            "max_dif_altura_rodillas": data["dif_altura_rodillas"].max(),
            "max_inclinacion_hombros": np.abs(data["inclinacion_hombros"]).max(),
            "max_inclinacion_caderas": np.abs(data["inclinacion_caderas"]).max(),
            "max_diferencia_profundidad": data["diferencia_profundidad"].max()
        }
    elif ejercicio == "peso muerto" and vista == "lateral":
        return {
            "angulo_min_rodilla": data["angulo_rodilla"].min(),
            "angulo_min_cadera": data["angulo_cadera"].min(),
            "distancia_mano_rodilla": data["distancia_mano_rodilla"].min()
        }
    elif ejercicio == "peso muerto" and vista == "frontal":
        return {
            "simetria_hombros": data["simetria_hombros"].mean(),
            "simetria_caderas": data["simetria_caderas"].mean(),
            "simetria_rodillas": data["simetria_rodillas"].mean(),
            "max_dif_altura_hombros": data["dif_altura_hombros"].max(),
            "max_dif_altura_caderas": data["dif_altura_caderas"].max(),
            "max_dif_altura_rodillas": data["dif_altura_rodillas"].max(),
            "max_dif_altura_manos": data["dif_altura_manos"].max(),
            "max_inclinacion_hombros": np.abs(data["inclinacion_hombros"]).max(),
            "max_inclinacion_caderas": np.abs(data["inclinacion_caderas"]).max(),
            "max_inclinacion_barra": np.abs(data["inclinacion_barra"]).max(),
            "max_asimetria_brazos": data["asimetria_brazos"].max(),
            "max_asimetria_piernas": data["asimetria_piernas"].max(),
            "max_desplazamiento_lateral": data["desplazamiento_lateral"].max()
        }
    elif ejercicio == "curl biceps" and vista == "lateral":
        angulo_codo = data["angulo_codo"]
        vel_codo = np.diff(angulo_codo)
        return {
            "angulo_min_codo": angulo_codo.min(),
            "angulo_max_codo": angulo_codo.max(),
            "rom_codo": angulo_codo.max() - angulo_codo.min(),
            "std_angulo_codo": angulo_codo.std(),
            "distancia_media_codo_hombro": data["distancia_codo_hombro"].mean(),
            "std_codo_hombro": data["distancia_codo_hombro"].std(),
            "distancia_media_codo_cadera": data["distancia_codo_cadera"].mean(),
            "std_codo_cadera": data["distancia_codo_cadera"].std(),
            "std_muneca_hombro": data["distancia_muneca_hombro"].std(),
            "velocidad_media_codo": np.mean(np.abs(vel_codo))
        }
    elif ejercicio == "curl biceps" and vista == "frontal":
        return {
            "simetria_hombros": data["simetria_hombros"].mean(),
            "simetria_codos": data["simetria_codos"].mean(),
            "simetria_munecas": data["simetria_munecas"].mean(),
            "max_dif_altura_munecas": data["dif_altura_munecas"].max(),
            "max_diferencia_angulos": data["diferencia_angulos_codo"].max()
        }
    elif ejercicio == "press banca" and vista == "lateral":
        angulo_codo = data["angulo_codo"]
        distancia_muneca_hombro = data["distancia_muneca_hombro"]
        velocidad_codo = np.diff(angulo_codo)
        idx_bottom = data["y_16"].idxmax()
        x_hombro_bottom, y_hombro_bottom = data.loc[idx_bottom, "x_12"], data.loc[idx_bottom, "y_12"]
        x_muneca_bottom, y_muneca_bottom = data.loc[idx_bottom, "x_16"], data.loc[idx_bottom, "y_16"]
        
        desplazamiento_horizontal_barra = abs(x_muneca_bottom - x_hombro_bottom)
        profundidad_descenso = abs(y_muneca_bottom - y_hombro_bottom)
        ratio_pecho_abdomen = desplazamiento_horizontal_barra / (profundidad_descenso + 1e-6)
        trayectoria_horizontal_barra = data["x_16"].max() - data["x_16"].min()
        
        return {
            "angulo_min_codo": angulo_codo.min(),
            "angulo_max_codo": angulo_codo.max(),
            "rom_codo": angulo_codo.max() - angulo_codo.min(),
            "std_angulo_codo": angulo_codo.std(),
            "distancia_media_muneca_hombro": distancia_muneca_hombro.mean(),
            "std_distancia_muneca_hombro": distancia_muneca_hombro.std(),
            "desplazamiento_codo": np.sqrt((data["x_14"].max()-data["x_14"].min())**2 + (data["y_14"].max()-data["y_14"].min())**2),
            "desplazamiento_muneca": np.sqrt((data["x_16"].max()-data["x_16"].min())**2 + (data["y_16"].max()-data["y_16"].min())**2),
            "velocidad_media_codo": np.mean(np.abs(velocidad_codo)),
            "velocidad_maxima_codo": np.max(np.abs(velocidad_codo)),
            "aceleracion_media": np.mean(np.abs(np.diff(angulo_codo, n=2))),
            "desplazamiento_horizontal_barra": desplazamiento_horizontal_barra,
            "profundidad_descenso": profundidad_descenso,
            "ratio_pecho_abdomen": ratio_pecho_abdomen,
            "trayectoria_horizontal_barra": trayectoria_horizontal_barra
        }
    elif ejercicio == "press banca" and vista == "frontal":
        return {
            "simetria_hombros": data["simetria_hombros"].mean(),
            "simetria_codos": data["simetria_codos"].mean(),
            "simetria_munecas": data["simetria_munecas"].mean(),
            "max_dif_altura_munecas": data["dif_altura_munecas"].max(),
            "max_diferencia_angulos": data["diferencia_angulos_codo"].max()
        }

def construir_modelo_biomecanico(df_pivot, ejercicio, vista):
    videos_bien = df_pivot[df_pivot["video"].str.lower().str.contains("bien")]["video"].unique()
    referencias = []
    
    for video in videos_bien:
        data = df_pivot[df_pivot["video"] == video]
        indicadores = extraer_indicadores_video(data, ejercicio, vista)
        referencias.append(indicadores)
        
    modelo_biomecanico = pd.DataFrame(referencias)
    
    modelo_referencia = pd.DataFrame({
        "Parametro": modelo_biomecanico.columns,
        "Valor ideal": modelo_biomecanico.mean().values,
        "STD": modelo_biomecanico.std().values,
        "Limite inferior": (modelo_biomecanico.mean() - modelo_biomecanico.std()).values,
        "Limite superior": (modelo_biomecanico.mean() + modelo_biomecanico.std()).values
    })
    
    return modelo_referencia

def comparar_con_modelo(valores_video, modelo_referencia):
    resultados = []
    score_total = []
    
    for _, row in modelo_referencia.iterrows():
        parametro = row["Parametro"]
        ideal = row["Valor ideal"]
        inferior = row["Limite inferior"]
        superior = row["Limite superior"]
        valor = valores_video[parametro]
        
        desviacion = abs(valor - ideal)
        cumple = (inferior <= valor <= superior)
        score = max(0, 100 * (1 - desviacion / (abs(ideal) + 1e-6)))
        
        score_total.append(score)
        resultados.append({
            "Parametro": parametro,
            "Valor observado": valor,
            "Valor ideal": ideal,
            "Limite inferior": inferior,
            "Limite superior": superior,
            "Desviacion": desviacion,
            "Cumple": cumple,
            "Score": score
        })
        
    return pd.DataFrame(resultados), np.mean(score_total)