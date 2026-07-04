"""Configuração central do RadarFut.

Todos os parâmetros ajustáveis do protótipo ficam neste arquivo para
facilitar experimentação sem precisar mexer na lógica.
"""

import json
import os

# Região da tela a ser capturada (em pixels, coordenadas absolutas do monitor).
# Ajuste esses valores para cobrir a área onde o vídeo/jogo está sendo exibido,
# ou gere-os automaticamente rodando `python region_selector.py`.
CAPTURE_LEFT = 0
CAPTURE_TOP = 0
CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720

# FPS alvo da captura. A captura de tela é custosa, então valores muito altos
# podem não ser sustentados dependendo da máquina.
TARGET_FPS = 15

# Tamanho da janela de visualização do frame capturado/processado.
DISPLAY_WIDTH = 960
DISPLAY_HEIGHT = 540

# Tamanho do minimapa (janela separada), em pixels.
MINIMAP_WIDTH = 500
MINIMAP_HEIGHT = 320
MINIMAP_MARGIN = 20

# Faixas de cor HSV usadas para detectar jogadores por contraste com o gramado.
# A lógica é: tudo que NÃO é verde de campo é candidato a jogador/objeto.
FIELD_HSV_LOWER = (35, 40, 40)
FIELD_HSV_UPPER = (85, 255, 255)

# Filtros de área de contorno (em pixels²) para descartar ruído e objetos
# grandes demais para ser um jogador (placar, faixas, torcida em bloco etc).
MIN_PLAYER_AREA = 40
MAX_PLAYER_AREA = 1500

# Proporção altura/largura mínima e máxima esperada para um "blob" de jogador.
MIN_ASPECT_RATIO = 0.8
MAX_ASPECT_RATIO = 4.5

# ROI (region of interest) do gramado dentro do frame capturado, em pixels
# relativos ao frame (não ao monitor). Serve para ignorar torcida, HUD,
# placar e propaganda ao converter posições para o minimapa e para restringir
# a detecção de jogadores. É uma aproximação manual enquanto não há detecção
# robusta do campo — ajuste conforme o enquadramento da transmissão/jogo, ou
# gere automaticamente rodando `python region_selector.py`.
FIELD_ROI_TOP = 180
FIELD_ROI_BOTTOM = 720
FIELD_ROI_LEFT = 0
FIELD_ROI_RIGHT = 1280

# Se existir um region_config.json (gerado por region_selector.py), ele
# sobrescreve os valores de captura e ROI acima. Mantém config.py como fonte
# única de verdade em runtime, sem exigir edição manual após a calibração.
_REGION_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "region_config.json")
if os.path.exists(_REGION_CONFIG_PATH):
    with open(_REGION_CONFIG_PATH, "r", encoding="utf-8") as _f:
        _region_overrides = json.load(_f)
    CAPTURE_LEFT = _region_overrides.get("CAPTURE_LEFT", CAPTURE_LEFT)
    CAPTURE_TOP = _region_overrides.get("CAPTURE_TOP", CAPTURE_TOP)
    CAPTURE_WIDTH = _region_overrides.get("CAPTURE_WIDTH", CAPTURE_WIDTH)
    CAPTURE_HEIGHT = _region_overrides.get("CAPTURE_HEIGHT", CAPTURE_HEIGHT)
    FIELD_ROI_LEFT = _region_overrides.get("FIELD_ROI_LEFT", FIELD_ROI_LEFT)
    FIELD_ROI_TOP = _region_overrides.get("FIELD_ROI_TOP", FIELD_ROI_TOP)
    FIELD_ROI_RIGHT = _region_overrides.get("FIELD_ROI_RIGHT", FIELD_ROI_RIGHT)
    FIELD_ROI_BOTTOM = _region_overrides.get("FIELD_ROI_BOTTOM", FIELD_ROI_BOTTOM)

# Times são classificados automaticamente em 2 clusters de cor por frame
# (k-means sobre a cor média do uniforme de cada detecção), já que faixas
# HSV fixas não se adaptam a uniformes diferentes de cada partida/vídeo.
# Cores fixas de renderização no minimapa (BGR): o cluster não tem uma
# identidade estável entre frames, então mapeamos por histórico (ver
# team_classifier.py) para decidir qual cluster vira "team_a"/"team_b".
TEAM_A_MINIMAP_COLOR = (0, 0, 255)     # vermelho
TEAM_B_MINIMAP_COLOR = (255, 200, 0)   # azul claro
UNKNOWN_MINIMAP_COLOR = (0, 255, 255)  # amarelo

# Quantidade de frames de histórico usada para suavizar a classificação de
# cada jogador rastreado por proximidade entre frames.
CLASSIFICATION_HISTORY_SIZE = 5

# Distância máxima (em pixels) entre o centro de uma detecção no frame atual
# e no frame anterior para considerá-las o "mesmo" jogador ao suavizar a
# classificação de time. Sem isso, não há como saber a quem o histórico
# pertence entre frames.
TRACKING_MAX_DISTANCE = 40

# Chaves de depuração visual, úteis para calibrar ROI, linhas do campo e
# detecção sem precisar alterar código.
DEBUG_DRAW_FIELD_LINES = True
DEBUG_DRAW_PLAYER_BOXES = True
DEBUG_DRAW_FIELD_ROI = True
DEBUG_SHOW_FPS = True
