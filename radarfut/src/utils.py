"""Funções utilitárias pequenas e compartilhadas entre os módulos."""

import cv2
import numpy as np

import config


def draw_detections(frame: np.ndarray, detections: list[dict]) -> np.ndarray:
    from team_classifier import team_color

    output = frame.copy()
    for detection in detections:
        x, y, w, h = detection["bbox"]
        color = team_color(detection.get("team", "unknown"))
        cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
    return output


def resize_for_display(frame: np.ndarray) -> np.ndarray:
    return cv2.resize(frame, (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT))
