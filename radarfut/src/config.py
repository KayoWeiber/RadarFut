"""Configuração central do RadarFut.

Todos os parâmetros ajustáveis do protótipo ficam neste arquivo para
facilitar experimentação sem precisar mexer na lógica.
"""

# Região da tela a ser capturada (em pixels, coordenadas absolutas do monitor).
# Ajuste esses valores para cobrir a área onde o vídeo/jogo está sendo exibido.
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

# Cores dos times no minimapa (formato BGR, padrão OpenCV).
TEAM_A_COLOR = (0, 0, 255)     # vermelho
TEAM_B_COLOR = (255, 200, 0)   # azul claro
UNKNOWN_COLOR = (0, 255, 255)  # amarelo, usado quando não dá para classificar o time

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
