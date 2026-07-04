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

A forma recomendada é usar o seletor visual: ele tira um screenshot do
monitor, você arrasta o mouse para marcar a região onde o vídeo/jogo está
sendo exibido e depois marca a área útil do gramado dentro dela. Os valores
são salvos em `src/region_config.json` e carregados automaticamente por
`config.py` (sobrescrevendo os valores fixos do arquivo).

```bash
cd src
python region_selector.py
```

Passo a passo:

1. Uma janela abre com o monitor inteiro. Arraste um retângulo cobrindo a
   janela do vídeo/jogo e pressione ENTER (ou ESPAÇO) para confirmar.
2. Uma segunda janela abre já recortada nessa região. Arraste um retângulo
   cobrindo **apenas o gramado**, excluindo arquibancada, HUD, placar e
   propaganda, e confirme novamente.
3. Os valores são gravados em `region_config.json`. Para recalibrar, basta
   rodar o script de novo (ele sobrescreve o arquivo).

`region_config.json` é local à sua máquina e está no `.gitignore`.

Alternativamente, é possível editar `src/config.py` diretamente e ajustar
os valores manualmente (coordenadas absolutas em pixels do monitor):

```python
CAPTURE_LEFT = 0
CAPTURE_TOP = 0
CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720
```

Note que, se existir um `region_config.json`, ele tem prioridade sobre os
valores escritos em `config.py` — apague o arquivo para voltar a usar os
valores fixos.

Também é possível ajustar em `config.py`:

- `TARGET_FPS`: taxa de captura desejada.
- `DISPLAY_WIDTH` / `DISPLAY_HEIGHT`: tamanho da janela de visualização.
- `MINIMAP_WIDTH` / `MINIMAP_HEIGHT`: tamanho do minimapa.
- `FIELD_HSV_LOWER` / `FIELD_HSV_UPPER`: faixa de cor considerada "gramado".
- `MIN_PLAYER_AREA` / `MAX_PLAYER_AREA`: filtro de tamanho de contorno.

### Região útil do campo (ROI)

Como ainda não há detecção robusta do campo nem homografia, a conversão de
posição para o minimapa — e a própria detecção de jogadores — usa uma área
útil do gramado (`FIELD_ROI_TOP/BOTTOM/LEFT/RIGHT`). O jeito recomendado de
definir isso é o `region_selector.py` (acima); os valores em `config.py`
são apenas o padrão usado quando não há `region_config.json`.

Com `DEBUG_DRAW_FIELD_ROI = True`, a ROI é desenhada em magenta na janela
de captura para facilitar a conferência.

### Cores dos times

Não há faixas de cor fixas por time no `config.py`: a cada frame, os
jogadores detectados são agrupados em 2 clusters de cor via k-means sobre a
cor média do uniforme, o que se adapta automaticamente a qualquer par de
uniformes sem precisar configurar HSV manualmente.

O problema é que o k-means não garante que o "cluster 0" de um frame seja o
mesmo time do "cluster 0" do frame seguinte. Para evitar que as cores dos
times troquem ou "pisquem" na tela, `team_classifier.py`:

- mantém uma cor de referência (média móvel) para `team_a` e `team_b` e
  associa cada cluster do frame atual ao time de referência mais próximo;
- mantém um histórico curto por jogador (pareado entre frames por
  proximidade do centro, via `TRACKING_MAX_DISTANCE`) e usa a classificação
  mais frequente nesse histórico (`CLASSIFICATION_HISTORY_SIZE`) em vez da
  leitura isolada do frame atual.

A cor exibida no minimapa é fixa (`TEAM_A_MINIMAP_COLOR` /
`TEAM_B_MINIMAP_COLOR`), independente da cor real do uniforme.

### Modo debug

As seguintes chaves controlam o que é desenhado na janela de captura:

```python
DEBUG_DRAW_FIELD_LINES = True   # linhas do campo detectadas (Hough)
DEBUG_DRAW_PLAYER_BOXES = True  # bounding boxes e time de cada jogador
DEBUG_DRAW_FIELD_ROI = True     # retângulo da ROI do campo
DEBUG_SHOW_FPS = True           # FPS atual no canto da janela
```

## Como executar

1. Abra o vídeo, transmissão, replay ou jogo de futebol na tela.
2. (Recomendado) Calibre a região rodando `python region_selector.py` uma
   vez — veja a seção acima.
3. Execute o script principal:

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
│   ├── region_selector.py    # calibração visual da captura e da ROI do campo
│   ├── screen_capture.py     # captura de tela via MSS
│   ├── player_detector.py    # detecção de jogadores por cor/contorno (dentro da ROI)
│   ├── team_classifier.py    # classificação em dois times, com estabilização
│   ├── field_mapper.py       # ROI do campo, linhas detectadas e projeção
│   ├── minimap_renderer.py   # desenho do minimapa 2D
│   └── utils.py              # funções utilitárias compartilhadas
└── samples/                  # espaço reservado para imagens/vídeos de teste
```

## Arquitetura inicial

Fluxo por frame, executado em loop dentro de `main.py`:

1. **`region_selector.py`** (rodado uma vez, separado do loop principal)
   deixa o usuário marcar visualmente a região de captura e a ROI do
   gramado, salvando em `region_config.json`.
2. **`screen_capture.py`** captura a região configurada da tela via MSS e
   converte para um array BGR compatível com OpenCV.
3. **`player_detector.py`** recorta o frame pela ROI do campo, converte para
   HSV, isola tudo que não corresponde à cor do gramado, encontra contornos
   e filtra por área e proporção para reduzir ruído. Retorna bounding boxes
   e centros aproximados dos "jogadores" detectados, já em coordenadas do
   frame completo.
4. **`team_classifier.py`** agrupa as detecções do frame em 2 clusters de
   cor (k-means), associa cada cluster ao time de referência mais próximo
   (para não inverter os rótulos entre frames) e usa um histórico curto por
   jogador (pareado entre frames por proximidade do centro) para manter a
   classificação estável.
5. **`field_mapper.py`** define a ROI do gramado (excluindo torcida, HUD e
   placar), detecta linhas brancas do campo via Hough para fins de debug, e
   projeta a posição de um jogador para coordenadas relativas (0..1) dentro
   dessa ROI — a base para uma futura homografia.
6. **`minimap_renderer.py`** desenha o campo (bordas, linha central, círculo
   central, áreas), escala a posição relativa de cada jogador para o
   retângulo do minimapa e mostra a contagem de jogadores por time.
7. **`main.py`** orquestra o loop, exibe o frame anotado (com debug opcional
   de linhas/ROI/FPS) e o minimapa em janelas OpenCV separadas, e controla o
   encerramento via tecla `q`.

Cada módulo é independente e feito para ser substituído/evoluído
isoladamente (por exemplo, trocar a detecção por cor por um modelo YOLO, ou
substituir a projeção proporcional por homografia real, sem precisar
alterar o restante do pipeline).

## Limitações conhecidas

- A detecção de jogadores não usa reconhecimento real de pessoas — é uma
  segmentação simples por contraste de cor com o gramado, então pode
  confundir linhas do campo, sombras e outros elementos de contraste com
  jogadores, mesmo estando restrita à ROI do gramado.
- A posição no minimapa é proporcional à posição do jogador **dentro da ROI
  do campo**, não à posição real dele no gramado. Sem homografia, isso
  ainda é uma aproximação visual — a câmera dinâmica (zoom, corte, replay,
  movimento de acompanhamento da bola) distorce a proporção real entre
  distância na tela e distância no campo, e essa versão não corrige isso.
- A ROI do campo é fixa por execução: se a câmera mudar de enquadramento de
  forma relevante durante a partida/vídeo, pode ser necessário recalibrar
  com `region_selector.py`.
- A detecção de linhas do campo depende da qualidade da imagem e serve por
  enquanto apenas como referência visual de debug — ainda não é usada para
  calibrar a projeção automaticamente.
- A classificação de times por k-means depende de os dois uniformes terem
  cores razoavelmente distintas; uniformes muito parecidos, iluminação ruim
  ou compressão de vídeo podem gerar classificações erradas mesmo com a
  estabilização por histórico e cor de referência.
- O rastreamento entre frames usado para estabilizar a cor é ingênuo
  (pareamento por distância do centro) e pode confundir jogadores muito
  próximos entre si ou que se movem rápido demais entre frames.

## Roadmap

1. MVP com captura da tela e minimapa aproximado.
2. Melhorar a detecção de jogadores.
3. Mapeamento inicial do campo: ROI configurável, detecção de linhas em modo
   debug e classificação de times estabilizada por histórico.
4. Seletor visual da região de captura e da ROI do campo, e classificação de
   times por k-means com cor de referência estável (esta versão).
5. Adicionar rastreamento mais robusto entre frames (ex.: Hungarian
   matching, filtros de movimento).
6. Separar times com maior precisão (ex.: considerar goleiro/árbitro como
   categorias à parte).
7. Usar as linhas do campo detectadas para calibrar a projeção
   automaticamente, incluindo adaptação a mudanças de câmera.
8. Aplicar homografia real para converter posições da imagem em
   coordenadas do campo.
9. Criar um overlay desktop transparente.
10. Avaliar uma futura integração com extensão de navegador.
