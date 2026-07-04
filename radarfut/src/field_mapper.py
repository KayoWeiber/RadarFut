"""Mapeamento inicial do campo dentro do frame capturado.

Responsabilidades:
- Detectar linhas brancas do campo (debug visual), como uma primeira base
  para uma futura homografia.
- Definir a área útil do gramado (ROI) usada para converter a posição de
  um jogador na imagem em uma posição proporcional no minimapa.

Não há homografia real aqui: a conversão é uma projeção proporcional dentro
da ROI configurada. É uma aproximação intencional para esta etapa.
"""

import cv2
import numpy as np

import config


def detect_field_lines(frame: np.ndarray) -> list[tuple[int, int, int, int]]:
    roi_frame = frame[
        config.FIELD_ROI_TOP:config.FIELD_ROI_BOTTOM,
        config.FIELD_ROI_LEFT:config.FIELD_ROI_RIGHT,
    ]
    if roi_frame.size == 0:
        return []

    hsv = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2HSV)
    blurred = cv2.GaussianBlur(hsv, (5, 5), 0)

    # Linhas do campo são quase brancas: baixa saturação e alto valor. Usar
    # HSV em vez de só limiar em cinza evita confundir gramado claro/brilhoso
    # com as linhas de fato.
    white_mask = cv2.inRange(blurred, (0, 0, 180), (180, 60, 255))
    edges = cv2.Canny(white_mask, 50, 150)

    raw_lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=40,
        minLineLength=60,
        maxLineGap=15,
    )

    if raw_lines is None:
        return []

    offset_x, offset_y = config.FIELD_ROI_LEFT, config.FIELD_ROI_TOP
    lines = []
    for line in raw_lines:
        x1, y1, x2, y2 = line[0]
        lines.append((x1 + offset_x, y1 + offset_y, x2 + offset_x, y2 + offset_y))

    return lines


def draw_field_lines(frame: np.ndarray, lines: list[tuple[int, int, int, int]]) -> np.ndarray:
    output = frame
    for x1, y1, x2, y2 in lines:
        cv2.line(output, (x1, y1), (x2, y2), (0, 255, 255), 1)
    return output


def draw_field_roi(frame: np.ndarray) -> np.ndarray:
    cv2.rectangle(
        frame,
        (config.FIELD_ROI_LEFT, config.FIELD_ROI_TOP),
        (config.FIELD_ROI_RIGHT, config.FIELD_ROI_BOTTOM),
        (255, 0, 255),
        2,
    )
    return frame


def project_to_field(point: tuple[int, int]) -> tuple[float, float]:
    """Converte um ponto do frame em coordenadas relativas (0..1) à ROI do campo.

    Pontos fora da ROI são grampeados (clamped) na borda mais próxima, já que
    ainda não existe homografia para lidar com perspectiva/câmera dinâmica.
    """
    x, y = point
    roi_width = config.FIELD_ROI_RIGHT - config.FIELD_ROI_LEFT
    roi_height = config.FIELD_ROI_BOTTOM - config.FIELD_ROI_TOP

    rel_x = (x - config.FIELD_ROI_LEFT) / float(roi_width) if roi_width else 0.0
    rel_y = (y - config.FIELD_ROI_TOP) / float(roi_height) if roi_height else 0.0

    rel_x = min(max(rel_x, 0.0), 1.0)
    rel_y = min(max(rel_y, 0.0), 1.0)

    return rel_x, rel_y
