"""Detecção inicial e simples de jogadores por segmentação de cor.

Estratégia: o gramado ocupa a maior parte da ROI do campo e tem uma faixa de
matiz (verde) bem definida em HSV. Tudo que não é gramado vira candidato a
jogador, e depois filtramos por tamanho/proporção do contorno para reduzir
ruído (linhas do campo, sombras etc).

A busca é restrita à ROI configurada em `config.FIELD_ROI_*` — sem isso, a
arquibancada, o placar e o HUD (que também contrastam com o verde do
gramado) acabam sendo detectados como "jogadores".
"""

import cv2
import numpy as np

import config


def detect_players(frame: np.ndarray) -> list[dict]:
    roi_top, roi_bottom = config.FIELD_ROI_TOP, config.FIELD_ROI_BOTTOM
    roi_left, roi_right = config.FIELD_ROI_LEFT, config.FIELD_ROI_RIGHT
    roi_frame = frame[roi_top:roi_bottom, roi_left:roi_right]

    if roi_frame.size == 0:
        return []

    hsv = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2HSV)

    field_mask = cv2.inRange(hsv, config.FIELD_HSV_LOWER, config.FIELD_HSV_UPPER)
    non_field_mask = cv2.bitwise_not(field_mask)

    kernel = np.ones((3, 3), np.uint8)
    non_field_mask = cv2.morphologyEx(non_field_mask, cv2.MORPH_OPEN, kernel)
    non_field_mask = cv2.dilate(non_field_mask, kernel, iterations=1)

    contours, _ = cv2.findContours(non_field_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detections = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < config.MIN_PLAYER_AREA or area > config.MAX_PLAYER_AREA:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = h / float(w) if w > 0 else 0
        if aspect_ratio < config.MIN_ASPECT_RATIO or aspect_ratio > config.MAX_ASPECT_RATIO:
            continue

        # Bounding box de volta para coordenadas do frame completo, já que a
        # detecção ocorreu sobre o recorte da ROI.
        center_x = roi_left + x + w // 2
        center_y = roi_top + y + h // 2

        detections.append({
            "bbox": (roi_left + x, roi_top + y, w, h),
            "center": (center_x, center_y),
        })

    return detections
