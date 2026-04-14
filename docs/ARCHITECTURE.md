# ARCHITECTURE

Projeto: `asteroids_single-player`

## 1. Objetivo

Este documento descreve a arquitetura atual real do projeto.

Escopo:
- Código Python em `core/`, `client/` e `main.py`
- Documentação em `docs/`
- Assets em `assets/`

Este projeto ainda é single-player.

## 2. Estrutura Atual do Repositório

Estrutura existente hoje:

```text
asteroids_single-player/
├── assets/
│   └── sounds/
├── client/
│   ├── audio.py
│   ├── controls.py
│   ├── game.py
│   └── renderer.py
├── core/
│   ├── commands.py
│   ├── config.py
│   ├── entities.py
│   ├── utils.py
│   └── world.py
├── docs/
│   └── ARCHITECTURE.md
└── main.py
```

Arquivos de áudio atuais em `assets/sounds/`:
- `asteroid_explosion.wav`
- `player_shoot.wav`
- `ship_explosion.wav`
- `thrust_loop.wav`
- `ufo_shoot.wav`
- `ufo_siren_big.wav`
- `ufo_siren_small.wav`

## 3. Responsabilidades por Arquivo

### `main.py`

Ponto de entrada.

Responsabilidades atuais:
- Importa `Game` de `client.game`
- Executa `Game().run()`

### `client/game.py`

Orquestra loop, cenas e integração com pygame.

Responsabilidades atuais:
- Inicialização do pygame e mixer
- Criação de janela, relógio e fontes
- Controle de cenas (`menu`, `play`, `game_over`)
- Leitura de eventos e encerramento do jogo
- Uso de `InputMapper` para converter input em comando
- Chamada de `World.update(dt, commands)`
- Desenho de menu, game over e mundo
- Execução de áudio a partir de `world.events`
- Controle de loops de áudio (thrust e sirene UFO)

### `client/renderer.py`

Renderização do cliente.

Responsabilidades atuais:
- Limpeza da tela
- Desenho das cenas (`menu`, `game_over`)
- Desenho do mundo a partir dos sprites expostos por `World`
- Desenho do HUD

### `client/controls.py`

Mapeamento de input local para comando do jogador.

Responsabilidades atuais:
- Classe `InputMapper`
- Captura de eventos `KEYDOWN` para `shoot` e `hyperspace`
- Leitura de teclas contínuas para rotação e thrust
- Construção de `PlayerCommand`

### `client/audio.py`

Carregamento de efeitos sonoros.

Responsabilidades atuais:
- `SoundPack` com referências de `pygame.mixer.Sound`
- `load_sounds(base_path)` para carregar sons a partir de `core.config`

### `core/world.py`

Núcleo de regras do jogo (`World`).

Responsabilidades atuais:
- Estado do jogo: naves, tiros, asteroides, UFOs, score, vidas, wave
- Spawn de jogador, asteroides e UFO
- Aplicação de comandos por `player_id`
- Atualização da simulação por frame
- Tratamento de colisões
- Regras de pontuação, morte e game over
- Geração de eventos de domínio em `world.events`

### `core/entities.py`

Entidades do jogo baseadas em `pygame.sprite.Sprite`.

Responsabilidades atuais:
- Classes: `Ship`, `Asteroid`, `Bullet`, `UFO`
- Física e atualização local de cada entidade
- Regras de tiro de `Ship` e `UFO`
- Constante `UFO_BULLET_OWNER`

### `core/commands.py`

Contrato de intenção do jogador.

Responsabilidades atuais:
- `dataclass` imutável `PlayerCommand`
- Flags: `rotate_left`, `rotate_right`, `thrust`, `shoot`, `hyperspace`

### `core/utils.py`

Utilitários matemáticos.

Responsabilidades atuais:
- Alias `Vec` (`pygame.math.Vector2`)
- Helpers de vetor e geometria (`wrap_pos`, `angle_to_vec`, etc.)

### `core/config.py`

Configuração central do jogo.

Responsabilidades atuais:
- Constantes de tela, FPS e IDs
- Parâmetros de nave, tiro, asteroide e UFO
- Cores e caminhos de assets
- Nomes dos arquivos de som

### `docs/`

Documentação do projeto.

Estado atual:
- Contém este documento (`ARCHITECTURE.md`)

### `assets/`

Recursos estáticos do jogo.

Estado atual:
- Pasta `sounds/` com efeitos WAV usados pelo cliente pygame

## 4. Dependências Entre Módulos (Atual)

Fluxo principal de imports observado hoje:
- `main.py` -> `client.game`
- `client.game` -> `client.audio`, `client.controls`, `client.renderer`,
  `core.config`, `core.world`
- `client.controls` -> `core.commands`
- `client.audio` -> `core.config`
- `client.renderer` -> `core.config`, `core.entities`
- `core.world` -> `core.config`, `core.commands`, `core.entities`,
  `core.utils`
- `core.entities` -> `core.config`, `core.commands`, `core.utils`
- `core.utils` -> `core.config`

Regra de saúde arquitetural:
- Evitar imports circulares

## 5. Observações Arquiteturais

A separação atual entre `core/` e `client/` já existe e está em uso.

Importante:
- `client/` concentra integração com pygame para input, render e áudio.
- `core/` concentra regras, estado do jogo e entidades.
- `core/` ainda depende de `pygame.sprite` e `pygame.math.Vector2`, então
  não é uma camada totalmente agnóstica de pygame.
- O fluxo de renderização atual passa por `client.renderer`; `World` não é
  responsável por desenhar HUD ou sprites.

## 6. Análise de Qualidade

### 6.1 Coesão (7/10)

Pontos positivos:
- `config.py` tem responsabilidade única perfeita (só constantes)
- `commands.py` é um dataclass puro, sem comportamento
- Cada entidade (`Bullet`, `Asteroid`, `Ship`, `UFO`) tem foco claro

Pontos a melhorar:
- `Game` (client/game.py) acumula responsabilidades demais: loop do jogo,
  inicialização pygame, gerenciamento de canais de áudio, lógica de siren
  do UFO e handling de eventos. Deveria extrair `AudioManager`.
- `World` (core/world.py) mistura estado do jogo com 77 linhas de detecção
  de colisões (5 métodos). Deveria extrair `CollisionManager`.
- `Ship.apply_command` mistura resposta a input com física (rotação, thrust,
  fricção e tiro no mesmo método).

### 6.2 Acoplamento (5/10)

Problema principal: core/ depende diretamente de pygame:
- Entidades herdam de `pygame.sprite.Sprite`
- `World` usa `pygame.sprite.Group`
- `Vec` é alias para `pygame.math.Vector2`
- A separação core/client é parcial — core não é agnóstico de framework

Outros problemas:
- `Renderer` usa cadeia de `isinstance` para decidir como desenhar cada
  entidade — impossível adicionar nova entidade sem modificar Renderer.
- Config global `C.` importado em ~35 referências sem injeção de dependência.
- Lógica de áudio (sirens, canais) misturada diretamente no `Game`.

### 6.3 Manutenibilidade (6/10)

Números mágicos espalhados pelo código:
- `entities.py`: steps do polígono (12/10/8), jitter (0.75-1.2), ângulo
  do ship (140.0), offset de spawn da bala (+6)
- `world.py`: distância mínima de spawn (150), multiplicador de split (1.2),
  contagem de wave (3 + wave)
- `game.py`: config de áudio (44100, -16, 2, 512), font sizes (22, 64)
- `renderer.py`: posições de layout (170, 350, 340, 260)

Duplicação de código:
- Padrão de timer/countdown repetido 5+ vezes sem utility
- 5 métodos de colisão com estrutura repetitiva

Bug identificado:
- Hyperspace pode teleportar o jogador para dentro de um asteroide (sem
  verificação de posição segura).

### 6.4 Legibilidade (7/10)

Pontos positivos:
- Nomes descritivos: `rotate_left`, `spawn_player()`, `_handle_collisions()`
- Type hints presentes na maioria das assinaturas
- Métodos privados com `_` consistente

Pontos a melhorar:
- Comentários inconsistentes: português misturado com inglês
- Docstrings ausentes em métodos complexos do UFO
- Cenas como strings hardcoded ("menu", "play", "game_over") em vez de Enum
- `UFO_BULLET_OWNER = -10` sem comentário explicativo

## 7. Preparação para Multiplayer

### 7.1 O que já está pronto

A arquitetura atual facilita a conversão em vários pontos:

- `World.update(dt, commands: dict[int, PlayerCommand])` já aceita múltiplos
  jogadores por design.
- `World.ships: dict[int, Ship]` indexado por player_id.
- `Bullet.owner` rastreia quem atirou cada bala.
- `PlayerCommand` como dataclass é fácil de serializar para rede.
- Separação core/client já existe (mesmo com acoplamento pygame).

### 7.2 O que precisa mudar

Refatorações necessárias antes da conversão:

1. **Desacoplar core de pygame** -- entidades não devem herdar de
   `pygame.sprite.Sprite`; criar interfaces próprias para que core/
   seja agnóstico de framework.

2. **Extrair CollisionManager** -- 77 linhas de colisão em `World` devem
   ir para classe separada, facilitando testes e modificação de regras.

3. **Score por jogador** -- `self.score` atual é global; precisa ser
   `dict[int, int]` indexado por player_id.

4. **Vidas por jogador** -- `self.lives` precisa ser por player, com
   game over parcial (um jogador morre, outro continua).

5. **Spawn de múltiplos players** -- `spawn_player()` já recebe `pid`,
   mas precisa gerenciar posições iniciais distintas.

6. **Networking** -- serializar `PlayerCommand` (envio) e estado do
   `World` (sincronização entre clientes).

7. **HUD multi-player** -- mostrar score/lives de cada jogador.

8. **Lobby** -- tela de espera antes do jogo iniciar.

9. **Eliminar números mágicos** -- centralizar em `config.py` antes
   de adicionar complexidade multiplayer.
