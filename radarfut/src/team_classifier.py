"""Classificação de jogadores em dois times, com estabilização entre frames.

A classificação por frame é feita comparando a cor média do uniforme com as
faixas HSV configuradas para cada time. Como isso pode falhar frame a frame
(iluminação, movimento, compressão do vídeo), mantemos um histórico curto
por jogador — pareado entre frames pela proximidade do centro da detecção —
e só trocamos a classificação quando há confiança suficiente. Isso evita o
"piscar" de cor no minimapa.
"""

from collections import deque

import cv2
import numpy as np

import config

_tracked_players: list[dict] = []


def _dominant_color_hsv(frame: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    x, y, w, h = bbox
    roi = frame[y:y + h, x:x + w]
    if roi.size == 0:
        return np.array([0, 0, 0], dtype=np.float32)
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    return hsv_roi.reshape(-1, 3).mean(axis=0)


def _match_score(color: np.ndarray, hsv_min: tuple, hsv_max: tuple) -> float:
    """Retorna quão bem `color` cabe dentro da faixa [hsv_min, hsv_max], em 0..1."""
    hsv_min = np.array(hsv_min, dtype=np.float32)
    hsv_max = np.array(hsv_max, dtype=np.float32)
    center = (hsv_min + hsv_max) / 2.0
    half_range = np.maximum((hsv_max - hsv_min) / 2.0, 1.0)

    normalized_distance = np.abs(color - center) / half_range
    score = 1.0 - np.clip(normalized_distance, 0.0, 1.0).mean()
    return float(score)


def _classify_by_color(color: np.ndarray) -> tuple[str, float]:
    score_a = _match_score(color, config.TEAM_A_HSV_MIN, config.TEAM_A_HSV_MAX)
    score_b = _match_score(color, config.TEAM_B_HSV_MIN, config.TEAM_B_HSV_MAX)

    if score_a >= score_b:
        return "team_a", score_a
    return "team_b", score_b


def _find_tracked_match(center: tuple[int, int]) -> dict | None:
    best_match = None
    best_distance = config.TRACKING_MAX_DISTANCE
    for tracked in _tracked_players:
        distance = np.hypot(center[0] - tracked["center"][0], center[1] - tracked["center"][1])
        if distance <= best_distance:
            best_distance = distance
            best_match = tracked
    return best_match


def classify_teams(frame: np.ndarray, detections: list[dict]) -> list[dict]:
    global _tracked_players

    updated_tracked = []

    for detection in detections:
        color = _dominant_color_hsv(frame, detection["bbox"])
        team_guess, confidence = _classify_by_color(color)

        tracked = _find_tracked_match(detection["center"])
        history = tracked["history"] if tracked else deque(maxlen=config.CLASSIFICATION_HISTORY_SIZE)

        if confidence >= config.CLASSIFICATION_CONFIDENCE_MIN:
            history.append(team_guess)

        if history:
            stable_team = max(set(history), key=history.count)
        else:
            stable_team = "unknown"

        detection["team"] = stable_team

        updated_tracked.append({
            "center": detection["center"],
            "history": history,
        })

    _tracked_players = updated_tracked
    return detections


def team_color(team: str) -> tuple[int, int, int]:
    if team == "team_a":
        return config.TEAM_A_MINIMAP_COLOR
    if team == "team_b":
        return config.TEAM_B_MINIMAP_COLOR
    return config.UNKNOWN_MINIMAP_COLOR
