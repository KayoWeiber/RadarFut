"""Classificação de jogadores em dois times, com estabilização entre frames.

Não há faixas de cor fixas por time (uniformes variam a cada partida/vídeo):
a cada frame agrupamos as detecções em 2 clusters de cor via k-means. O
problema é que o rótulo do cluster (0 ou 1) não tem identidade estável entre
frames — o k-means pode inverter os rótulos de um frame para o outro. Para
resolver isso, mantemos a cor média de referência de cada time ao longo do
tempo e, a cada frame, associamos cada cluster ao time de referência mais
próximo antes de aplicar o histórico por jogador (que evita o "piscar"
individual de cada detecção).
"""

from collections import deque

import cv2
import numpy as np

import config

_tracked_players: list[dict] = []
_team_reference_colors: dict[str, np.ndarray] = {}


def _dominant_color(frame: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    x, y, w, h = bbox
    roi = frame[y:y + h, x:x + w]
    if roi.size == 0:
        return np.array([0, 0, 0], dtype=np.float32)
    return roi.reshape(-1, 3).mean(axis=0)


def _cluster_colors(colors: np.ndarray) -> np.ndarray:
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(colors, 2, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS)
    return labels.flatten(), centers


def _assign_clusters_to_teams(cluster_centers: np.ndarray) -> dict[int, str]:
    """Decide qual cluster (0 ou 1) corresponde a team_a/team_b.

    Na primeira vez que rodamos, não há referência: usamos a ordem natural do
    k-means. Nas próximas vezes, associamos cada cluster ao time cuja cor de
    referência está mais próxima, evitando que os rótulos invertam de frame
    para frame.
    """
    if "team_a" not in _team_reference_colors or "team_b" not in _team_reference_colors:
        return {0: "team_a", 1: "team_b"}

    ref_a = _team_reference_colors["team_a"]
    ref_b = _team_reference_colors["team_b"]

    dist_0_a = np.linalg.norm(cluster_centers[0] - ref_a)
    dist_0_b = np.linalg.norm(cluster_centers[0] - ref_b)

    if dist_0_a <= dist_0_b:
        return {0: "team_a", 1: "team_b"}
    return {0: "team_b", 1: "team_a"}


def _update_reference_colors(cluster_centers: np.ndarray, cluster_to_team: dict[int, str]) -> None:
    # Média móvel simples para acompanhar mudanças lentas (iluminação) sem
    # perder a identidade do time de um frame para o outro.
    smoothing = 0.8
    for cluster_index, team in cluster_to_team.items():
        new_color = cluster_centers[cluster_index]
        if team in _team_reference_colors:
            _team_reference_colors[team] = (
                smoothing * _team_reference_colors[team] + (1 - smoothing) * new_color
            )
        else:
            _team_reference_colors[team] = new_color


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

    if len(detections) < 2:
        for detection in detections:
            detection["team"] = "unknown"
        _tracked_players = []
        return detections

    colors = np.array(
        [_dominant_color(frame, d["bbox"]) for d in detections],
        dtype=np.float32,
    )
    labels, cluster_centers = _cluster_colors(colors)
    cluster_to_team = _assign_clusters_to_teams(cluster_centers)
    _update_reference_colors(cluster_centers, cluster_to_team)

    updated_tracked = []

    for detection, label in zip(detections, labels):
        team_guess = cluster_to_team[int(label)]

        tracked = _find_tracked_match(detection["center"])
        history = tracked["history"] if tracked else deque(maxlen=config.CLASSIFICATION_HISTORY_SIZE)
        history.append(team_guess)

        stable_team = max(set(history), key=history.count)
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
