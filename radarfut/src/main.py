"""Ponto de entrada do RadarFut.

Captura a região configurada da tela, detecta jogadores por cor, classifica
em dois times aproximados e exibe o frame original com as detecções e um
minimapa 2D em janela separada. Pressione 'q' em qualquer janela para sair.
"""

import time

import cv2

import config
from screen_capture import ScreenCapture
from player_detector import detect_players
from team_classifier import classify_teams
from minimap_renderer import render_minimap
from utils import draw_detections, resize_for_display


def main():
    capture = ScreenCapture()
    frame_interval = 1.0 / config.TARGET_FPS

    window_frame = "RadarFut - Captura"
    window_minimap = "RadarFut - Minimapa"
    cv2.namedWindow(window_frame)
    cv2.namedWindow(window_minimap)

    try:
        while True:
            loop_start = time.time()

            frame = capture.capture_frame()

            detections = detect_players(frame)
            detections = classify_teams(frame, detections)

            annotated_frame = draw_detections(frame, detections)
            minimap = render_minimap(
                detections,
                frame_width=frame.shape[1],
                frame_height=frame.shape[0],
            )

            cv2.imshow(window_frame, resize_for_display(annotated_frame))
            cv2.imshow(window_minimap, minimap)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            elapsed = time.time() - loop_start
            remaining = frame_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)
    finally:
        capture.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
