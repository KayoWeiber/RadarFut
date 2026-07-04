"""Captura da região configurada da tela usando MSS."""

import mss
import numpy as np

import config


class ScreenCapture:
    def __init__(self):
        self._sct = mss.mss()
        self._region = {
            "left": config.CAPTURE_LEFT,
            "top": config.CAPTURE_TOP,
            "width": config.CAPTURE_WIDTH,
            "height": config.CAPTURE_HEIGHT,
        }

    def capture_frame(self) -> np.ndarray:
        shot = self._sct.grab(self._region)
        # MSS retorna BGRA; descartamos o canal alfa para obter BGR (padrão OpenCV).
        frame = np.array(shot)[:, :, :3]
        return frame

    def close(self):
        self._sct.close()
