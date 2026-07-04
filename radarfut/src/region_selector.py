"""Ferramenta de calibração visual: selecionar a região de captura e a ROI do campo.

Fluxo:
1. Tira um screenshot do monitor inteiro.
2. Usuário arrasta o mouse para marcar a região de captura (onde está o vídeo/jogo).
3. Usuário arrasta o mouse novamente, agora sobre o recorte da região de
   captura, para marcar a ROI do gramado (excluindo torcida, HUD, placar).
4. Salva os valores em region_config.json, na raiz do projeto `src/`.

Rodar como script: `python select_region.py`.
"""

import json
import os

import cv2
import mss
import numpy as np

REGION_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "region_config.json")


def _select_rectangle(image: np.ndarray, window_title: str) -> tuple[int, int, int, int]:
    """Abre uma janela e deixa o usuário arrastar um retângulo com o mouse.

    Retorna (left, top, width, height) relativos a `image`. Usa a própria
    seleção interativa do OpenCV, que já lida com arrastar/soltar do mouse.
    """
    display_scale = 1.0
    max_display_height = 900
    if image.shape[0] > max_display_height:
        display_scale = max_display_height / image.shape[0]

    display_image = cv2.resize(image, None, fx=display_scale, fy=display_scale)

    box = cv2.selectROI(window_title, display_image, showCrosshair=True)
    cv2.destroyWindow(window_title)

    x, y, w, h = box
    return (
        int(x / display_scale),
        int(y / display_scale),
        int(w / display_scale),
        int(h / display_scale),
    )


def main():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = np.array(sct.grab(monitor))[:, :, :3]

    print("Passo 1: arraste um retângulo sobre a região onde o vídeo/jogo está sendo exibido.")
    print("Pressione ENTER ou ESPAÇO para confirmar, ESC para cancelar.")
    capture_left, capture_top, capture_width, capture_height = _select_rectangle(
        screenshot, "RadarFut - Selecione a regiao de captura"
    )

    if capture_width == 0 or capture_height == 0:
        print("Seleção cancelada. Nenhum arquivo foi salvo.")
        return

    captured_region = screenshot[
        capture_top:capture_top + capture_height,
        capture_left:capture_left + capture_width,
    ]

    print("Passo 2: dentro dessa região, arraste um retângulo cobrindo apenas o gramado")
    print("(excluindo torcida, HUD, placar e propaganda).")
    print("Pressione ENTER ou ESPAÇO para confirmar, ESC para cancelar.")
    field_left, field_top, field_width, field_height = _select_rectangle(
        captured_region, "RadarFut - Selecione a ROI do campo"
    )

    if field_width == 0 or field_height == 0:
        print("Seleção da ROI cancelada. Nenhum arquivo foi salvo.")
        return

    region_config = {
        "CAPTURE_LEFT": capture_left,
        "CAPTURE_TOP": capture_top,
        "CAPTURE_WIDTH": capture_width,
        "CAPTURE_HEIGHT": capture_height,
        "FIELD_ROI_LEFT": field_left,
        "FIELD_ROI_TOP": field_top,
        "FIELD_ROI_RIGHT": field_left + field_width,
        "FIELD_ROI_BOTTOM": field_top + field_height,
    }

    with open(REGION_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(region_config, f, indent=2, ensure_ascii=False)

    print(f"Configuração salva em {REGION_CONFIG_PATH}")
    print(region_config)


if __name__ == "__main__":
    main()
