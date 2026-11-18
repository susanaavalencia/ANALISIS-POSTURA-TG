# utils.py
import numpy as np

def normalize_skeleton(row):
    coords = row.values.reshape(-1,3)
    center = coords.mean(axis=0)
    coords = coords - center
    scale = np.linalg.norm(coords[0] - coords[-1])
    if scale < 1e-6:
        scale = 1e-6
    coords = coords / scale
    return coords.flatten()

def calcular_angulo(a, b, c):
    ba = a - b
    bc = c - b
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
    return np.degrees(angle)

def calcular_simetria(p1, p2):
    return np.linalg.norm(p1 - p2)

def get_label(video):
    return 1 if "bien" in video.lower() else 0

def get_person(video):
    return video.split("_")[1]