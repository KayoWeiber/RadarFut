# RadarFut

Sistema experimental em Python para leitura visual de partidas de futebol e
geração de um minimapa tático aproximado, semelhante ao radar de jogos como
EA FC.

## Objetivo desta versão

Validar a viabilidade técnica de capturar uma região da tela do computador
em tempo real (jogo, transmissão, replay ou vídeo de futebol), processar os
frames com visão computacional e desenhar um minimapa 2D básico com a
posição aproximada dos jogadores, classificados em dois times por cor.

Esta etapa ainda é deliberadamente simples: não há extensão de navegador,
overlay transparente, integração com o jogo ou modelos de IA pesados. O
foco continua sendo processar a imagem já visível na tela — agora com um
primeiro mapeamento do campo (ROI e linhas detectadas) e classificação de
times mais estável entre frames. Homografia real ainda não foi
implementada, mas a estrutura já está preparada para essa evolução.

## Instalação

Requer Python 3.11+.

```bash
cd radarfut
pip install -r requirements.txt
```

## Configurando a região de captura

Abra `src/config.py` e ajuste os valores conforme a posição/tamanho da
janela onde o vídeo ou jogo está sendo exibido na sua tela:

```python
CAPTURE_LEFT = 0
CAPTURE_TOP = 0
CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720
```

Esses valores são coordenadas absolutas em pixels do monitor. Uma forma
simples de descobrir os valores certos é usar uma ferramenta de captura de
tela (como a Ferramenta de Captura do Windows) para identificar a posição e
o tamanho da janela do vídeo/jogo.

Também é possível ajustar em `config.py`:

- `TARGET_FPS`: taxa de captura desejada.
- `DISPLAY_WIDTH` / `DISPLAY_HEIGHT`: tamanho da janela de visualização.
- `MINIMAP_WIDTH` / `MINIMAP_HEIGHT`: tamanho do minimapa.
- `FIELD_HSV_LOWER` / `FIELD_HSV_UPPER`: faixa de cor considerada "gramado".
- `MIN_PLAYER_AREA` / `MAX_PLAYER_AREA`: filtro de tamanho de contorno.

### Região útil do campo (ROI)

Como ainda não há detecção robusta do campo nem homografia, a conversão de
posição para o minimapa usa uma área útil do gramado configurada
manualmente:

```python
FIELD_ROI_TOP = 180
FIELD_ROI_BOTTOM = 720
FIELD_ROI_LEFT = 0
FIELD_ROI_RIGHT = 1280
```

Ajuste esses valores para cobrir apenas o gramado visível no frame
capturado, excluindo torcida, HUD, placar e propaganda. Com
`DEBUG_DRAW_FIELD_ROI = True`, a ROI é desenhada em magenta na janela de
captura para facilitar o ajuste.

### Cores dos times

Os times são classificados comparando a cor média do uniforme com faixas
HSV configuráveis:

```python
TEAM_A_HSV_MIN = (0, 90, 60)
TEAM_A_HSV_MAX = (10, 255, 255)

TEAM_B_HSV_MIN = (0, 0, 180)
TEAM_B_HSV_MAX = (180, 60, 255)
```

Os valores padrão são apenas um ponto de partida (tons avermelhados vs.
tons claros/brancos) e devem ser ajustados conforme os uniformes reais da
partida ou vídeo. A cor exibida no minimapa é fixa
(`TEAM_A_MINIMAP_COLOR` / `TEAM_B_MINIMAP_COLOR`), independente da cor real
detectada, para manter a leitura visual estável.

Para reduzir o "piscar" de classificação entre frames, a detecção atual é
pareada com detecções do frame anterior por proximidade
(`TRACKING_MAX_DISTANCE`) e mantém um pequeno histórico
(`CLASSIFICATION_HISTORY_SIZE`), só trocando de time quando a confiança da
cor (`CLASSIFICATION_CONFIDENCE_MIN`) é suficiente.

### Modo debug

As seguintes chaves controlam o que é desenhado na janela de captura:

```python
DEBUG_DRAW_FIELD_LINES = True   # linhas do campo detectadas (Hough)
DEBUG_DRAW_PLAYER_BOXES = True  # bounding boxes e time de cada jogador
DEBUG_DRAW_FIELD_ROI = True     # retângulo da ROI do campo
DEBUG_SHOW_FPS = True           # FPS atual no canto da janela
```

## Como executar

1. Abra o vídeo, transmissão, replay ou jogo de futebol na tela, na região
   configurada em `config.py`.
2. Execute o script principal:

```bash
cd src
python main.py
```

Duas janelas serão abertas: a captura com as detecções desenhadas, e o
minimapa 2D. Pressione `q` em qualquer uma das janelas para encerrar.

## Estrutura de pastas

```
radarfut/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py               # ponto de entrada
│   ├── config.py             # configuração central
│   ├── screen_capture.py     # captura de tela via MSS
│   ├── player_detector.py    # detecção de jogadores por cor/contorno
│   ├── team_classifier.py    # classificação em dois times, com estabilização
│   ├── field_mapper.py       # ROI do campo, linhas detectadas e projeção
│   ├── minimap_renderer.py   # desenho do minimapa 2D
│   └── utils.py              # funções utilitárias compartilhadas
└── samples/                  # espaço reservado para imagens/vídeos de teste
```

## Arquitetura inicial

Fluxo por frame, executado em loop dentro de `main.py`:

1. **`screen_capture.py`** captura a região configurada da tela via MSS e
   converte para um array BGR compatível com OpenCV.
2. **`player_detector.py`** converte o frame para HSV, isola tudo que não
   corresponde à cor do gramado, encontra contornos e filtra por área e
   proporção para reduzir ruído. Retorna bounding boxes e centros
   aproximados dos "jogadores" detectados.
3. **`team_classifier.py`** compara a cor média de cada detecção com as
   faixas HSV configuradas para cada time, e usa um histórico curto
   (pareado entre frames por proximidade do centro) para manter a
   classificação estável mesmo quando a leitura de cor do frame atual é
   incerta.
4. **`field_mapper.py`** define a ROI do gramado (excluindo torcida, HUD e
   placar), detecta linhas brancas do campo via Hough para fins de debug, e
   projeta a posição de um jogador para coordenadas relativas (0..1) dentro
   dessa ROI — a base para uma futura homografia.
5. **`minimap_renderer.py`** desenha o campo (bordas, linha central, círculo
   central, áreas), escala a posição relativa de cada jogador para o
   retângulo do minimapa e mostra a contagem de jogadores por time.
6. **`main.py`** orquestra o loop, exibe o frame anotado (com debug opcional
   de linhas/ROI/FPS) e o minimapa em janelas OpenCV separadas, e controla o
   encerramento via tecla `q`.

Cada módulo é independente e feito para ser substituído/evoluído
isoladamente (por exemplo, trocar a detecção por cor por um modelo YOLO, ou
substituir a projeção proporcional por homografia real, sem precisar
alterar o restante do pipeline).

## Limitações conhecidas

- A detecção de jogadores não usa reconhecimento real de pessoas — é uma
  segmentação simples por contraste de cor com o gramado, então pode
  facilmente confundir linhas do campo, sombras, placar, torcida e outros
  elementos de interface com jogadores.
- A posição no minimapa é proporcional à posição do jogador **dentro da ROI
  configurada do campo**, não à posição real dele no gramado. Sem
  homografia, isso ainda é uma aproximação visual, apenas menos distorcida
  por elementos fora do campo.
- Câmeras dinâmicas (zoom, corte, replay) ainda distorcem as posições
  relativas, já que não há calibração de perspectiva nem homografia.
- A detecção de linhas do campo depende da qualidade da imagem e serve por
  enquanto apenas como referência visual de debug — ainda não é usada para
  calibrar a projeção automaticamente.
- HUD, placar, torcida e propagandas fora da ROI configurada não entram no
  cálculo, mas a ROI em si é definida manualmente e pode precisar de ajuste
  por transmissão/jogo.
- A classificação de times por cor depende da configuração correta das
  faixas HSV de cada uniforme; times com cores muito próximas, iluminação
  ruim ou compressão de vídeo podem gerar classificações erradas mesmo com
  o histórico de estabilização.
- O rastreamento entre frames usado para estabilizar a cor é ingênuo
  (pareamento por distância do centro) e pode confundir jogadores próximos
  entre si.

## Roadmap

1. MVP com captura da tela e minimapa aproximado.
2. Melhorar a detecção de jogadores.
3. Mapeamento inicial do campo: ROI configurável, detecção de linhas em modo
   debug e classificação de times estabilizada por histórico (esta versão).
4. Adicionar um seletor visual da região de captura e da ROI do campo (em
   vez de valores fixos em `config.py`).
5. Adicionar rastreamento mais robusto entre frames.
6. Separar times com maior precisão (ex.: clustering combinado com faixas
   HSV, ou pequenos modelos de classificação).
7. Usar as linhas do campo detectadas para calibrar a projeção
   automaticamente.
8. Aplicar homografia real para converter posições da imagem em
   coordenadas do campo.
9. Criar um overlay desktop transparente.
10. Avaliar uma futura integração com extensão de navegador.
