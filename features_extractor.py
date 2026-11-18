# features_extractor.py
import numpy as np
from utils import calcular_angulo, calcular_simetria

def extraer_features_laterales(row, ejercicio):
    coords = row.values.reshape(-1,3)

    if ejercicio == "sentadilla":
        shoulder, hip, knee, ankle = coords
        ang_knee = calcular_angulo(hip, knee, ankle)
        ang_hip = calcular_angulo(shoulder, hip, knee)
        torso_dist = np.linalg.norm(shoulder - hip)
        return np.array([ang_knee, ang_hip, torso_dist])

    elif ejercicio == "peso muerto":
        shoulder, elbow, hand, hip, knee, ankle = coords
        ang_knee = calcular_angulo(hip, knee, ankle)
        ang_hip = calcular_angulo(shoulder, hip, knee)
        dist_hand_knee = np.linalg.norm(hand - knee)
        return np.array([ang_knee, ang_hip, dist_hand_knee])

    elif ejercicio == "curl biceps":
        shoulder, elbow, wrist, hip = coords
        ang_elbow = calcular_angulo(shoulder, elbow, wrist)
        dist_elbow_shoulder = np.linalg.norm(elbow - shoulder)
        dist_elbow_hip = np.linalg.norm(elbow - hip)
        dist_wrist_shoulder = np.linalg.norm(wrist - shoulder)
        return np.array([ang_elbow, dist_elbow_shoulder, dist_elbow_hip, dist_wrist_shoulder])

    elif ejercicio == "press banca":
        shoulder, elbow, wrist = coords
        ang_elbow = calcular_angulo(shoulder, elbow, wrist)
        wrist_dist = np.linalg.norm(wrist - shoulder)
        return np.array([ang_elbow, wrist_dist])

def extraer_features_frontales(row, ejercicio):
    coords = row.values.reshape(-1,3)

    if ejercicio == "peso muerto":
        shoulder_l, shoulder_r, elbow_l, elbow_r, hand_l, hand_r, hip_l, hip_r, knee_l, knee_r = coords
        return np.array([
            calcular_simetria(shoulder_l, shoulder_r),
            calcular_simetria(hip_l, hip_r),
            calcular_simetria(knee_l, knee_r),
            abs(shoulder_l[1] - shoulder_r[1]),
            abs(hip_l[1] - hip_r[1]),
            abs(knee_l[1] - knee_r[1]),
            abs(hand_l[1] - hand_r[1]),
            np.degrees(np.arctan2(shoulder_r[1]-shoulder_l[1], shoulder_r[0]-shoulder_l[0])),
            np.degrees(np.arctan2(hip_r[1]-hip_l[1], hip_r[0]-hip_l[0])),
            np.degrees(np.arctan2(hand_r[1]-hand_l[1], hand_r[0]-hand_l[0])),
            abs(np.linalg.norm(shoulder_l - hand_l) - np.linalg.norm(shoulder_r - hand_r)),
            abs(np.linalg.norm(hip_l - knee_l) - np.linalg.norm(hip_r - knee_r)),
            abs(((shoulder_l + shoulder_r)/2)[0] - ((hip_l + hip_r)/2)[0])
        ])

    elif ejercicio == "sentadilla":
        shoulder_l, shoulder_r, elbow_l, elbow_r, hand_l, hand_r, hip_l, hip_r, knee_l, knee_r = coords
        return np.array([
            calcular_simetria(shoulder_l, shoulder_r),
            calcular_simetria(hip_l, hip_r),
            calcular_simetria(knee_l, knee_r),
            abs(shoulder_l[1] - shoulder_r[1]),
            abs(hip_l[1] - hip_r[1]),
            abs(knee_l[1] - knee_r[1]),
            np.degrees(np.arctan2(shoulder_r[1]-shoulder_l[1], shoulder_r[0]-shoulder_l[0])),
            np.degrees(np.arctan2(hip_r[1]-hip_l[1], hip_r[0]-hip_l[0])),
            abs(np.linalg.norm(knee_l - hip_l) - np.linalg.norm(knee_r - hip_r))
        ])

    elif ejercicio in ["curl biceps", "press banca"]:
        shoulder_l, shoulder_r, elbow_l, elbow_r, wrist_l, wrist_r = coords
        ang_left = calcular_angulo(shoulder_l, elbow_l, wrist_l)
        ang_right = calcular_angulo(shoulder_r, elbow_r, wrist_r)
        return np.array([
            calcular_simetria(shoulder_l, shoulder_r),
            calcular_simetria(elbow_l, elbow_r),
            calcular_simetria(wrist_l, wrist_r),
            abs(wrist_l[1] - wrist_r[1]),
            abs(ang_left - ang_right)
        ])