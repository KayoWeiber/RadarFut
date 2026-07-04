"""Funções utilitárias pequenas e compartilhadas entre os módulos."""

import cv2
import numpy as np

import config


def draw_detections(frame: np.ndarray, detections: list[dict]) -> np.ndarray:
    from team_classifier import team_color

    if not config.DEBUG_DRAW_PLAYER_BOXES:
        return frame

    output = frame
    for detection in detections:
        x, y, w, h = detection["bbox"]
        color = team_color(detection.get("team", "unknown"))
        cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
        label = detection.get("team", "unknown")
        cv2.putText(
            output, label, (x, max(y - 5, 0)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA,
        )
    return output


def draw_fps(frame: np.ndarray, fps: float) -> np.ndarray:
    if not config.DEBUG_SHOW_FPS:
        return frame

    cv2.putText(
        frame, f"FPS: {fps:.1f}", (10, frame.shape[0] - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA,
    )
    return frame


def resize_for_display(frame: np.ndarray) -> np.ndarray:
    return cv2.resize(frame, (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT))
