"""Renderização de um minimapa 2D básico com a posição aproximada dos jogadores.

A posição de cada jogador no minimapa é calculada proporcionalmente à posição
dele dentro do frame capturado (não do campo real). Sem homografia, isso é
apenas uma aproximação — está documentado como limitação no README.
"""

import numpy as np

import config


def _empty_field() -> np.ndarray:
    field = np.zeros((config.MINIMAP_HEIGHT, config.MINIMAP_WIDTH, 3), dtype=np.uint8)
    field[:] = (40, 120, 40)

    margin = config.MINIMAP_MARGIN
    field_color = (255, 255, 255)

    import cv2

    cv2.rectangle(
        field,
        (margin, margin),
        (config.MINIMAP_WIDTH - margin, config.MINIMAP_HEIGHT - margin),
        field_color,
        2,
    )
    cv2.line(
        field,
        (config.MINIMAP_WIDTH // 2, margin),
        (config.MINIMAP_WIDTH // 2, config.MINIMAP_HEIGHT - margin),
        field_color,
        2,
    )
    center = (config.MINIMAP_WIDTH // 2, config.MINIMAP_HEIGHT // 2)
    cv2.circle(field, center, 40, field_color, 2)

    return field


def render_minimap(detections: list[dict], frame_width: int, frame_height: int) -> np.ndarray:
    import cv2
    from team_classifier import team_color

    field = _empty_field()
    margin = config.MINIMAP_MARGIN
    usable_width = config.MINIMAP_WIDTH - 2 * margin
    usable_height = config.MINIMAP_HEIGHT - 2 * margin

    for detection in detections:
        cx, cy = detection["center"]
        rel_x = cx / float(frame_width)
        rel_y = cy / float(frame_height)

        map_x = int(margin + rel_x * usable_width)
        map_y = int(margin + rel_y * usable_height)

        color = team_color(detection.get("team", "unknown"))
        cv2.circle(field, (map_x, map_y), 6, color, -1)
        cv2.circle(field, (map_x, map_y), 6, (0, 0, 0), 1)

    return field
