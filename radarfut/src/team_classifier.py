"""Classificação simples de jogadores em dois times por cor dominante.

Não há reconhecimento real de uniforme: pegamos a cor média da região do
jogador e agrupamos em dois clusters via k-means. É frágil, mas suficiente
para validar a ideia nesta primeira etapa.
"""

import cv2
import numpy as np

import config


def _dominant_color(frame: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    x, y, w, h = bbox
    roi = frame[y:y + h, x:x + w]
    if roi.size == 0:
        return np.array([0, 0, 0], dtype=np.float32)
    return roi.reshape(-1, 3).mean(axis=0)


def classify_teams(frame: np.ndarray, detections: list[dict]) -> list[dict]:
    if len(detections) < 2:
        for detection in detections:
            detection["team"] = "unknown"
        return detections

    colors = np.array(
        [_dominant_color(frame, d["bbox"]) for d in detections],
        dtype=np.float32,
    )

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, _ = cv2.kmeans(colors, 2, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS)

    for detection, label in zip(detections, labels.flatten()):
        detection["team"] = "team_a" if label == 0 else "team_b"

    return detections


def team_color(team: str) -> tuple[int, int, int]:
    if team == "team_a":
        return config.TEAM_A_COLOR
    if team == "team_b":
        return config.TEAM_B_COLOR
    return config.UNKNOWN_COLOR
