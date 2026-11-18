# config.py

EJERCICIOS = {
    1: "sentadilla",
    2: "peso muerto",
    3: "curl biceps",
    4: "press banca"
}

VISTAS = {
    1: "frontal",
    2: "lateral"
}

# NOTA: Cambia las rutas "csv" para que apunten a tu carpeta local 'data/'
CONFIG_DATA = {
    ("sentadilla", "lateral"): {"csv": "./data/sentadilla_lateral.csv", "selected_ids": [12, 24, 26, 28], "mode": "angles"},
    ("sentadilla", "frontal"): {"csv": "./data/sentadilla_frontal.csv", "selected_ids": [11,12,13,14,15,16,23,24,25,26], "mode": "symmetry"},
    ("peso muerto", "lateral"): {"csv": "./data/peso_muerto_lateral.csv", "selected_ids": [12,14,16,24,26,28], "mode": "angles"},
    ("peso muerto", "frontal"): {"csv": "./data/peso_muerto_frontal.csv", "selected_ids": [11,12,13,14,15,16,23,24,25,26], "mode": "symmetry"},
    ("curl biceps", "lateral"): {"csv": "./data/curl_biceps_lateral.csv", "selected_ids": [12,14,16,24], "mode": "angles"},
    ("curl biceps", "frontal"): {"csv": "./data/curl_biceps_frontal.csv", "selected_ids": [11,12,13,14,15,16], "mode": "symmetry"},
    ("press banca", "lateral"): {"csv": "./data/press_banca_lateral.csv", "selected_ids": [12,14,16], "mode": "angles"},
    ("press banca", "frontal"): {"csv": "./data/press_banca_frontal.csv", "selected_ids": [11,12,13,14,15,16], "mode": "symmetry"}
}

FEATURE_NAMES = {
    ("sentadilla", "lateral"): ["angulo_rodilla", "angulo_cadera", "distancia_torso"],
    ("sentadilla", "frontal"): ["simetria_hombros", "simetria_caderas", "simetria_rodillas", "dif_altura_hombros", "dif_altura_caderas", "dif_altura_rodillas", "inclinacion_hombros", "inclinacion_caderas", "diferencia_profundidad"],
    ("peso muerto", "lateral"): ["angulo_rodilla", "angulo_cadera", "distancia_mano_rodilla"],
    ("peso muerto", "frontal"): ["simetria_hombros", "simetria_caderas", "simetria_rodillas", "dif_altura_hombros", "dif_altura_caderas", "dif_altura_rodillas", "dif_altura_manos", "inclinacion_hombros", "inclinacion_caderas", "inclinacion_barra", "asimetria_brazos", "asimetria_piernas", "desplazamiento_lateral"],
    ("curl biceps", "lateral"): ["angulo_codo", "distancia_codo_hombro", "distancia_codo_cadera", "distancia_muneca_hombro"],
    ("curl biceps", "frontal"): ["simetria_hombros", "simetria_codos", "simetria_munecas", "dif_altura_munecas", "diferencia_angulos_codo"],
    ("press banca", "lateral"): ["angulo_codo", "distancia_muneca_hombro"],
    ("press banca", "frontal"): ["simetria_hombros", "simetria_codos", "simetria_munecas", "dif_altura_munecas", "diferencia_angulos_codo"]
}

# config.py (Añadir al final del archivo)

RECOMENDACIONES = {
    # --- ÁNGULOS Y RANGOS DE MOVIMIENTO (ROM) ---
    "angulo_min_rodilla": {
        "exceso": "Falta profundidad. Intente aumentar la flexión de rodilla durante la fase descendente.",
        "defecto": "Está flexionando las rodillas en exceso (bajando demasiado). Controle la profundidad para proteger la articulación."
    },
   "angulo_min_cadera": {
        "exceso": "Falta flexión de cadera. Lleve los glúteos hacia atrás al bajar, como si se sentara en una silla.",
        "defecto": "Está inclinando el tronco demasiado hacia adelante (dominancia de cadera). Mantenga el pecho arriba."
    },
    "rom_codo": {
        "exceso": "Está hiperextendiendo el codo al final del movimiento. Mantenga una micro-flexión articular por seguridad.",
        "defecto": "El rango de movimiento es muy corto (media repetición). Estire y contraiga el brazo completamente."
    },
    "longitud_torso": {
        "exceso": "La distancia entre su hombro y cadera está variando anormalmente (posible rotación del torso). Baje como un bloque sólido.",
        "defecto": "El torso está perdiendo rigidez (encorvándose o arqueándose). Mantenga el abdomen apretado y la espalda neutra."
    },
    "profundidad_descenso": {
        "exceso": "El recorrido es incompleto. Controle la profundidad bajando un poco más.",
        "defecto": "El descenso es demasiado profundo y podría comprometer la técnica pélvica. Reduzca el rango."
    },

    # --- DISTANCIAS Y TRAYECTORIAS ---
    "distancia_mano_rodilla": {
        "exceso": "La barra está muy alejada de las piernas (alto riesgo lumbar). Manténgala raspando o muy pegada al cuerpo.",
        "defecto": "La barra está chocando con sus rodillas. Ajuste la sincronización entre rodilla y cadera."
    },
    "distancia_media_codo_hombro": {
        "exceso": "Los codos están muy separados del torso ('flare'). Acérquelos al cuerpo para proteger los hombros.",
        "defecto": "Los codos están excesivamente rozando el torso, lo que podría limitar su rango natural."
    },
    "distancia_media_codo_cadera": {
        "exceso": "Está adelantando/alejando mucho el brazo del cuerpo (balanceo). Fije los codos a los costados.",
        "defecto": "El brazo está demasiado tenso contra el cuerpo. Permita un movimiento natural del bíceps."
    },
    "desplazamiento_horizontal_barra": {
        "exceso": "La barra se desplaza mucho hacia adelante o atrás. Oblíguese a mantener una trayectoria vertical.",
        "defecto": "Mantenga el control vertical de la barra a lo largo de todo el empuje."
    },
    "trayectoria_horizontal_barra": {
        "exceso": "Evite desplazamientos horizontales innecesarios. La fuerza debe ir en línea recta.",
        "defecto": "Controle la trayectoria recta de la barra."
    },
    "ratio_pecho_abdomen": {
        "exceso": "La barra está bajando muy cerca del cuello/clavícula. Bájela hacia la línea media del pecho.",
        "defecto": "La barra está bajando demasiado hacia el abdomen superior. Suba el punto de contacto."
    },

    # --- VELOCIDAD ---
    "velocidad_media_codo": {
        "exceso": "El movimiento es demasiado rápido por inercia. Realice el movimiento de forma más controlada (sobre todo al bajar).",
        "defecto": "El movimiento es excesivamente lento (posible fatiga o peso excesivo). Mantenga un ritmo fluido."
    },
    
    "ratio_pecho_abdomen": {
        "exceso": "La barra está bajando muy cerca del cuello o clavícula. Bájela hacia la línea media del pecho.",
        "defecto": "La barra está bajando demasiado hacia el estómago. Suba el punto de contacto hacia el pecho medio/bajo."
    },
    "distancia_muneca_hombro": {
        "exceso": "Está bajando la barra hacia el estómago, alejando demasiado las muñecas de los hombros. Apunte al pecho.",
        "defecto": "La barra está bajando hacia su cuello. Aleje un poco el punto de contacto hacia el pecho medio."
    },

    # --- SIMETRÍAS, ALTURAS E INCLINACIONES (El fallo común es el "exceso" de asimetría) ---
    "simetria_hombros": {
        "exceso": "Existe un desbalance notable entre los hombros. Verifique que su agarre sea simétrico y el peso (barra o mancuernas) esté nivelado.",
        "defecto": "Procure mantener ambos hombros alineados y el peso nivelado."
    },
    "simetria_caderas": {
        "exceso": "Su cadera se está desplazando hacia un lado. Mantenga una posición simétrica de la pelvis.",
        "defecto": "Mantenga la pelvis nivelada."
    },
    "simetria_rodillas": {
        "exceso": "Una rodilla colapsa más que la otra (valgo asimétrico). Evite compensaciones y empuje hacia afuera.",
        "defecto": "Evite compensaciones entre ambas rodillas."
    },
    "simetria_codos": {
        "exceso": "Un codo se mueve antes o más que el otro. Mantenga ambos codos trabajando al unísono.",
        "defecto": "Trabaje ambos codos de forma simétrica."
    },
    "simetria_munecas": {
        "exceso": "Las muñecas están desniveladas o giradas de forma distinta. Manténgalas firmes y alineadas.",
        "defecto": "Procure mantener ambas muñecas alineadas."
    },
    "max_inclinacion_barra": {
        "exceso": "La barra está notablemente inclinada (un brazo sube más rápido). Empuje con la misma fuerza y manténgala paralela al suelo.",
        "defecto": "Mantenga la barra paralela al suelo."
    },
    "max_desplazamiento_lateral": {
        "exceso": "Su cuerpo se está yendo de lado durante el esfuerzo. Contraiga el core y evite desplazamientos laterales.",
        "defecto": "Evite desplazamientos laterales del tronco."
    },
    "max_dif_altura_hombros": {"exceso": "Un hombro está más alto que el otro (encogimiento). Baje los hombros y estabilice.", "defecto": "Reduzca las diferencias de altura entre los hombros."},
    "max_dif_altura_caderas": {"exceso": "Está inclinando lateralmente la pelvis ('hip shift'). Distribuya el peso por igual.", "defecto": "Evite inclinaciones laterales de la pelvis."},
    "max_dif_altura_rodillas": {"exceso": "Una rodilla está cediendo. Controle la estabilidad de ambas rodillas.", "defecto": "Controle ambas rodillas."},
    "max_dif_altura_manos": {"exceso": "Una mano empuja o tira por encima de la otra. Mantenga ambas a la misma altura.", "defecto": "Mantenga ambas manos niveladas."},
    "max_dif_altura_munecas": {"exceso": "Las muñecas no están niveladas horizontalmente. Ajuste su agarre.", "defecto": "Mantenga ambas muñecas a la misma altura."},
    "max_inclinacion_hombros": {"exceso": "Evite inclinaciones laterales excesivas del torso y hombros.", "defecto": "Evite inclinarse hacia los lados."},
    "max_inclinacion_caderas": {"exceso": "Su pelvis está rotando. Procure mantenerla nivelada frontalmente.", "defecto": "Procure mantener la pelvis nivelada."},
    "max_asimetria_brazos": {"exceso": "Un brazo está haciendo más fuerza/recorrido que el otro. Mantenga un trabajo uniforme.", "defecto": "Mantenga ambos brazos trabajando uniformemente."},
    "max_asimetria_piernas": {"exceso": "Está apoyando más peso en una pierna. Distribuya la carga de forma equilibrada.", "defecto": "Equilibre la carga en ambas piernas."}
}


RECOMENDACIONES_LEVES = {
    # --- ÁNGULOS Y RANGOS DE MOVIMIENTO (ROM) ---
    "angulo_min_rodilla": {
        "exceso": "Podría optimizar el recorrido bajando un poco más (aumente levemente la flexión de rodilla).",
        "defecto": "La ejecución es adecuada, pero podría limitar ligeramente la profundidad final para no forzar la articulación."
    },
    "angulo_min_cadera": {
        "exceso": "La técnica es correcta, aunque bajar un poco más la cadera podría optimizar la activación muscular.",
        "defecto": "Tenga cuidado con no relajar la cadera en el punto más bajo del movimiento."
    },
    "rom_codo": {
        "exceso": "Casi hiperextiende el codo. Mantenga un control articular un poco más estricto al finalizar.",
        "defecto": "Podría aumentar ligeramente el rango de movimiento del codo para una contracción completa."
    },
    "longitud_torso": {
        "exceso": "Se nota una pequeñísima extensión lumbar. Mantenga el core un poco más apretado.",
        "defecto": "Intente sacar un poco más el pecho para evitar que la espalda empiece a encorvarse."
    },
    "profundidad_descenso": {
        "exceso": "Podría ganar un poco más de rango descendiendo un par de centímetros más.",
        "defecto": "Excelente profundidad, solo vigile no pasar su rango natural de flexibilidad."
    },

    # --- DISTANCIAS Y TRAYECTORIAS ---
    "distancia_mano_rodilla": {
        "exceso": "La barra se separó ligeramente de sus muslos/espinillas. Manténgala rozando el cuerpo.",
        "defecto": "La barra pasa muy cerca y puede golpear la rodilla. Suavice la trayectoria."
    },
    "distancia_media_codo_hombro": {
        "exceso": "Los codos se abrieron un poco. Intente mantenerlos ligeramente más cerca del torso.",
        "defecto": "Los codos rozan el torso. Si siente incomodidad, ábralos unos grados."
    },
    "distancia_media_codo_cadera": {
        "exceso": "Se percibe un leve balanceo del brazo. Intente anclar más el codo a las costillas.",
        "defecto": "El movimiento está bien, mantenga esa firmeza."
    },
    "desplazamiento_horizontal_barra": {
        "exceso": "La trayectoria de la barra fue ligeramente curva. Intente empujar en línea totalmente vertical.",
        "defecto": "Buena línea de empuje."
    },
    "trayectoria_horizontal_barra": {
        "exceso": "Reduzca pequeños desplazamientos laterales o frontales de la barra.",
        "defecto": "Trayectoria adecuadamente controlada."
    },
    "ratio_pecho_abdomen": {
        "exceso": "La barra tocó ligeramente alto en el pecho. Ajuste milimétricamente hacia abajo.",
        "defecto": "La barra tocó un poco bajo. Ajuste ligeramente hacia la línea de los pezones."
    },

    # --- VELOCIDAD ---
    "velocidad_media_codo": {
        "exceso": "El ritmo fue un poco acelerado. Priorice sentir el músculo durante la bajada (fase excéntrica).",
        "defecto": "El ritmo fue un poco pausado. Si le cuesta mucho, considere bajar ligeramente el peso."
    },

    # --- SIMETRÍAS, ALTURAS E INCLINACIONES ---
    "simetria_hombros": {"exceso": "Se observa una levísima asimetría en los hombros. Intente mantenerlos parejos.", "defecto": "La ejecución es adecuada; procure alinear un poco mejor los hombros."},
    "simetria_caderas": {"exceso": "Hay un pequeñísimo desbalance pélvico. Concéntrese en la simetría.", "defecto": "Puede mejorar levemente la simetría de la pelvis."},
    "simetria_rodillas": {"exceso": "Una rodilla rotó imperceptiblemente. Mantenga la tensión en ambas por igual.", "defecto": "Existe una pequeña diferencia entre rodillas que puede corregirse."},
    "simetria_codos": {"exceso": "Hubo una pequeña falta de sincronización entre los codos al subir.", "defecto": "Puede mejorar ligeramente la sincronización de los codos."},
    "simetria_munecas": {"exceso": "Revise el agarre; una muñeca se nota ligeramente más flexionada que la otra.", "defecto": "Procure mantener una alineación más uniforme de las muñecas."},
    "max_inclinacion_barra": {"exceso": "La barra presentó una ligerísima inclinación de pocos grados. Vigile el empuje uniforme.", "defecto": "La barra estuvo bastante nivelada."},
    "max_desplazamiento_lateral": {"exceso": "Hubo un micro-desplazamiento lateral del cuerpo. Mantenga fuerte el abdomen.", "defecto": "Buen control del eje central."},
    "max_dif_altura_hombros": {"exceso": "Se observa una leve diferencia de altura entre hombros.", "defecto": "Hombros mayormente estables."},
    "max_dif_altura_caderas": {"exceso": "Puede reducir ligeramente una pequeña inclinación lateral de la pelvis.", "defecto": "Pelvis mayormente estable."},
    "max_dif_altura_rodillas": {"exceso": "Intente mantener ambas rodillas a una altura/flexión más uniforme.", "defecto": "Buena estabilidad de rodillas."},
    "max_dif_altura_manos": {"exceso": "Existe una leve asimetría en el nivel de tracción/empuje de las manos.", "defecto": "Tracción uniforme."},
    "max_dif_altura_munecas": {"exceso": "Puede mejorar la alineación vertical milimétrica de las muñecas.", "defecto": "Muñecas estables."},
    "max_inclinacion_hombros": {"exceso": "Reduzca ligeramente cualquier inclinación lateral del torso.", "defecto": "Torso estable."},
    "max_inclinacion_caderas": {"exceso": "Puede mejorar la estabilidad de rotación de la pelvis.", "defecto": "Rotación pélvica controlada."},
    "max_asimetria_brazos": {"exceso": "Puede mejorar sutilmente la simetría del trabajo entre ambos brazos.", "defecto": "Brazos trabajando bien en conjunto."},
    "max_asimetria_piernas": {"exceso": "Existe una levísima diferencia en la distribución del peso entre los pies.", "defecto": "Carga bien distribuida."}
}