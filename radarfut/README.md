# RadarFut

Sistema experimental em Python para leitura visual de partidas de futebol e
geração de um minimapa tático aproximado, semelhante ao radar de jogos como
EA FC.

## Objetivo desta versão

Validar a viabilidade técnica de capturar uma região da tela do computador
em tempo real (jogo, transmissão, replay ou vídeo de futebol), processar os
frames com visão computacional e desenhar um minimapa 2D básico com a
posição aproximada dos jogadores, classificados em dois times por cor.

Esta é uma primeira etapa deliberadamente simples: não há extensão de
navegador, overlay transparente, integração com o jogo, homografia,
rastreamento ou modelos de IA pesados. O foco é apenas processar a imagem
que já está visível na tela.

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
- `TEAM_A_COLOR` / `TEAM_B_COLOR`: cores usadas para representar cada time.
- `FIELD_HSV_LOWER` / `FIELD_HSV_UPPER`: faixa de cor considerada "gramado".
- `MIN_PLAYER_AREA` / `MAX_PLAYER_AREA`: filtro de tamanho de contorno.

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
│   ├── team_classifier.py    # classificação em dois times por cor
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
3. **`team_classifier.py`** calcula a cor média da região de cada detecção
   e agrupa em dois clusters (k-means) para aproximar dois times.
4. **`minimap_renderer.py`** converte a posição de cada jogador dentro do
   frame capturado em uma posição proporcional dentro do retângulo do
   minimapa, desenhando um ponto colorido por time.
5. **`main.py`** orquestra o loop, exibe o frame anotado e o minimapa em
   janelas OpenCV separadas, e controla o encerramento via tecla `q`.

Cada módulo é independente e feito para ser substituído/evoluído
isoladamente (por exemplo, trocar a detecção por cor por um modelo YOLO no
futuro, sem precisar alterar o restante do pipeline).

## Limitações conhecidas

- A detecção de jogadores não usa reconhecimento real de pessoas — é uma
  segmentação simples por contraste de cor com o gramado, então pode
  facilmente confundir linhas do campo, sombras, placar, torcida e outros
  elementos de interface com jogadores.
- A posição no minimapa é proporcional à posição do jogador **dentro do
  frame capturado**, não à posição real dele no campo. Sem homografia, isso
  é apenas uma aproximação visual.
- Câmeras dinâmicas (zoom, corte, replay) distorcem completamente as
  posições relativas, já que não há calibração de perspectiva.
- A classificação de times por cor pode falhar dependendo do uniforme, da
  iluminação da transmissão e da qualidade/compressão do vídeo.
- Não há rastreamento entre frames: cada frame é processado de forma
  independente, então os pontos no minimapa podem "piscar" ou saltar.

## Roadmap

1. MVP com captura da tela e minimapa aproximado (esta versão).
2. Melhorar a detecção de jogadores.
3. Adicionar um seletor visual da região de captura (em vez de valores
   fixos em `config.py`).
4. Adicionar rastreamento simples entre frames.
5. Separar times com maior precisão.
6. Detectar linhas do campo automaticamente.
7. Aplicar homografia para converter posições da imagem em coordenadas
   reais do campo.
8. Criar um overlay desktop transparente.
9. Avaliar uma futura integração com extensão de navegador.
