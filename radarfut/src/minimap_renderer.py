"""Renderização do minimapa 2D com a posição estimada dos jogadores.

A posição de cada jogador é convertida para coordenadas relativas à ROI do
campo (ver `field_mapper.project_to_field`) e depois escalada para o
retângulo do minimapa. Sem homografia, ainda é uma aproximação — a ROI só
evita que torcida, HUD e placar distorçam a proporção.
"""

import cv2
import numpy as np

import config
from field_mapper import project_to_field
from team_classifier import team_color

_PENALTY_AREA_WIDTH_RATIO = 0.16
_PENALTY_AREA_HEIGHT_RATIO = 0.5
_CENTER_CIRCLE_RADIUS_RATIO = 0.09


def _empty_field() -> np.ndarray:
    field = np.zeros((config.MINIMAP_HEIGHT, config.MINIMAP_WIDTH, 3), dtype=np.uint8)
    field[:] = (40, 110, 40)

    margin = config.MINIMAP_MARGIN
    line_color = (255, 255, 255)
    top_left = (margin, margin)
    bottom_right = (config.MINIMAP_WIDTH - margin, config.MINIMAP_HEIGHT - margin)

    cv2.rectangle(field, top_left, bottom_right, line_color, 2)

    mid_x = config.MINIMAP_WIDTH // 2
    cv2.line(field, (mid_x, margin), (mid_x, config.MINIMAP_HEIGHT - margin), line_color, 2)

    center = (mid_x, config.MINIMAP_HEIGHT // 2)
    radius = int(config.MINIMAP_HEIGHT * _CENTER_CIRCLE_RADIUS_RATIO)
    cv2.circle(field, center, radius, line_color, 2)
    cv2.circle(field, center, 3, line_color, -1)

    penalty_w = int((config.MINIMAP_WIDTH - 2 * margin) * _PENALTY_AREA_WIDTH_RATIO)
    penalty_h = int((config.MINIMAP_HEIGHT - 2 * margin) * _PENALTY_AREA_HEIGHT_RATIO)
    penalty_top = config.MINIMAP_HEIGHT // 2 - penalty_h // 2
    penalty_bottom = config.MINIMAP_HEIGHT // 2 + penalty_h // 2

    cv2.rectangle(
        field,
        (margin, penalty_top),
        (margin + penalty_w, penalty_bottom),
        line_color,
        2,
    )
    cv2.rectangle(
        field,
        (config.MINIMAP_WIDTH - margin - penalty_w, penalty_top),
        (config.MINIMAP_WIDTH - margin, penalty_bottom),
        line_color,
        2,
    )

    return field


def _draw_team_counts(field: np.ndarray, detections: list[dict]) -> None:
    count_a = sum(1 for d in detections if d.get("team") == "team_a")
    count_b = sum(1 for d in detections if d.get("team") == "team_b")

    cv2.putText(
        field, f"Time A: {count_a}", (config.MINIMAP_MARGIN, 16),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45, config.TEAM_A_MINIMAP_COLOR, 1, cv2.LINE_AA,
    )
    cv2.putText(
        field, f"Time B: {count_b}", (config.MINIMAP_WIDTH - config.MINIMAP_MARGIN - 90, 16),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45, config.TEAM_B_MINIMAP_COLOR, 1, cv2.LINE_AA,
    )


def render_minimap(detections: list[dict]) -> np.ndarray:
    field = _empty_field()
    margin = config.MINIMAP_MARGIN
    usable_width = config.MINIMAP_WIDTH - 2 * margin
    usable_height = config.MINIMAP_HEIGHT - 2 * margin

    for detection in detections:
        rel_x, rel_y = project_to_field(detection["center"])

        map_x = int(margin + rel_x * usable_width)
        map_y = int(margin + rel_y * usable_height)

        color = team_color(detection.get("team", "unknown"))
        cv2.circle(field, (map_x, map_y), 6, color, -1)
        cv2.circle(field, (map_x, map_y), 6, (20, 20, 20), 1)

    _draw_team_counts(field, detections)

    return field
