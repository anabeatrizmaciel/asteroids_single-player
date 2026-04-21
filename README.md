<h1 align="center">☄️ Asteroids Gameplay</h1>

<p align="center">
  <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXFyc2F1OWx2aGl4ZXg3ZXp6YnhlM3ZwNzByZDZuaGw3djdrMm9yNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0IzkM6q0rqdtZuNbly/giphy.gif" width="260">
</p>

<p align="center">
  Projeto de evolução do jogo <strong>Asteroids</strong> em <strong>Pygame</strong>, com foco na criação e implementação de novas mecânicas de gameplay.<br>
</p>

---

<h2 align="center">📝 Descrição do Projeto</h2>

Este repositório tem como objetivo expandir o projeto-base **Asteroids em Pygame**, propondo melhorias de jogabilidade, novas mecânicas e organização do desenvolvimento em equipe.

O trabalho foi estruturado a partir de cinco frentes principais:

- **Proposição de 5 novas mecânicas** interessantes e divertidas para o jogo;
- **Documentação das mecânicas** em apresentação no Google Presentations;
- **Modelagem da solução** com apoio do **modelo C4**;
- **Divisão do desenvolvimento** entre os membros da equipe;

---

<h2 align="center">🎯 Objetivos da Atividade</h2>

- Evoluir o projeto original `asteroids_pygame`;
- Tornar a experiência do jogador mais dinâmica e divertida;
- Planejar as mudanças antes da implementação;
- Documentar tecnicamente a arquitetura e as decisões do grupo;

---

<h2 align="center">🕹️ Novas Mecânicas Propostas</h2>

As mecânicas abaixo representam a proposta de evolução do jogo.

### 1. Escudo Temporário
O jogador pode coletar um item especial que ativa um escudo por alguns segundos, protegendo a nave contra colisões ou disparos inimigos.

### 2. Tiro Dividido / Espalhado
O jogador pode coletar um item que permite disparar múltiplos tiros simultâneos por um tempo limitado, aumentando significativamente o poder de fogo contra grandes hordas de asteroides.

### 3. ❄️ Freeze Time
Ao destruir asteroides, um coletável azul aparece na tela. Tocá-lo com a nave congela todos os asteroides por 5 segundos, dando tempo para eliminar os restantes com segurança.

### 4. Buraco Negro
Um buraco negro aparece em um ponto aleatório e dura entre 5 a 10 segundos. Afeta a movimentação da nave do jogador, puxando em sua direção com força variável conforme a distância. Caso o jogador encoste no buraco negro, é fim de jogo.

### 5. Power-Ups
Itens coletáveis que concedem bônus ao jogador.
 Nessa mecânica, ao destruir com tiro um fragmento especial S, surge um power-up de vida extra no local; se a nave coletar a tempo, ganha +1 vida.

---

<h2 align="center">🤖 Tecnologias Utilizadas</h2>

<p align="center">
  <a href="https://www.python.org"><img alt="Python" src="https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python"></a>
  <a href="https://www.pygame.org"><img alt="Pygame" src="https://img.shields.io/badge/pygame-✔-green?style=for-the-badge"></a>
  <a href="https://git-scm.com/"><img alt="Git" src="https://img.shields.io/badge/git-✔-orange?style=for-the-badge&logo=git"></a>
  <a href="https://github.com"><img alt="GitHub" src="https://img.shields.io/badge/github-✔-black?style=for-the-badge&logo=github"></a>
  <a href="https://c4model.com/"><img alt="C4 Model" src="https://img.shields.io/badge/C4_Model-Documentado-purple?style=for-the-badge"></a>
</p>

---

<h2 align="center">📁 Estrutura do Projeto</h2>

```bash
📦 asteroids_single-player
├── 📄 main.py                      # ponto de entrada do projeto
├── 📄 requirements.txt
├── 📄 Makefile                     # atalhos para venv, install e run
├── 📁 assets/
│   └── 📁 sounds/                  # arquivos de áudio (.wav)
├── 📁 client/                      # integração com Pygame
│   ├── 📄 game.py                  # loop principal e cenas
│   ├── 📄 renderer.py              # desenho de sprites e HUD
│   ├── 📄 controls.py              # mapeamento de teclado
│   ├── 📄 audio.py                 # carregamento de sons
│   └── 📄 audio_manager.py         # reprodução de áudio
├── 📁 core/                        # regras do jogo (sem dependência de Pygame)
│   ├── 📄 config.py                # constantes e configurações
│   ├── 📄 entities.py              # nave, asteroides, UFO, FreezePickup
│   ├── 📄 world.py                 # estado do mundo e lógica de ondas
│   ├── 📄 collisions.py            # detecção e resolução de colisões
│   ├── 📄 commands.py              # contrato de entrada do jogador
│   ├── 📄 scene.py                 # enum de estados de cena
│   └── 📄 utils.py                 # funções auxiliares
└── 📁 docs/
    ├── 📄 c4_nivel1_contexto.puml     # diagrama C4 Nível 1 (Contexto)
    ├── 📄 c4_nivel2_containers.puml   # diagrama C4 Nível 2
    ├── 🖼️ Asteroids_Diagrama C4 Contexto.drawio.png  # imagem do diagrama de contexto
    ├── 📄 ARCHITECTURE.md
    └── 📄 DEVELOPMENT_WORKFLOW.md
```

---

<h2 align="center">🧩 Modelagem com C4</h2>

O projeto utiliza o **modelo C4** para representar a solução em diferentes níveis de abstração, facilitando o entendimento da arquitetura e da responsabilidade de cada parte do sistema.

### Níveis utilizados

* **C1 – Contexto:** visão externa do sistema, mostrando o jogador, os comandos via teclado e o jogo como sistema principal.
* **C2 – Contêineres:** visão dos principais blocos internos do projeto — Cliente do Jogo (Pygame), Núcleo do Jogo (Python puro) e Assets de Áudio.

Diagramas disponíveis:

- [`docs/c4_nivel1_contexto.puml`](docs/c4_nivel1_contexto.puml)
- [`docs/c4_nivel2_containers.puml`](docs/c4_nivel2_containers.puml)

Os arquivos `.puml` podem ser renderizados com a extensão **PlantUML** no VS Code (`Alt+D`) ou em [plantuml.com/plantuml](https://www.plantuml.com/plantuml/uml/).

---

<h2 align="center">🚀 Como Executar</h2>

### Usando Make (recomendado)

```bash
# 1. Criar venv e instalar dependências
make install

# 2. Rodar o jogo
make run
```

### Manual

```bash
# 1. Clonar o repositório
git clone https://github.com/anabeatrizmaciel/asteroids_single-player.git
cd asteroids_single-player

# 2. Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate      # Linux/Mac
# .venv\Scripts\activate       # Windows

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Executar o jogo
python3 main.py
```

---

<h2 align="center">🎮 Funcionalidades Implementadas</h2>

| Funcionalidade            | Descrição                                              |
| ------------------------- | ------------------------------------------------------ |
| Movimentação da nave      | Controle da nave pelo jogador (setas / WASD)           |
| Disparo padrão            | Ataque básico com limite de 4 balas simultâneas        |
| Asteroides                | Obstáculos com divisão ao ser atingido                 |
| UFO                       | Inimigo que persegue e atira no jogador                |
| Hyperspace                | Teleporte aleatório com custo de 250 pontos            |
| ❄️ Freeze Time             | Coletável que para todos os asteroides por 5 segundos  |
| Power-up de Vida Extra    | Surge ao destruir fragmento especial S e concede +1 vida ao coletar |
| Buraco Negro              | Buraco negro que puxa a nave para perto dele           |
| Sistema de pontuação      | Pontos por asteroide e UFO destruídos                  |
| Progressão por ondas      | Dificuldade aumenta a cada onda                        |

---

<h2 align="center">👥 Divisão da Equipe</h2>

| Integrante                     | Responsabilidade          |
| ------------------------------ | ------------------------- |
| Ana Beatriz Maciel Nunes       | Escudo Temporário         |
| Fernando Luiz Da Silva Freire  | Power-Ups                 |
| Juliana Ballin Lima            | Freeze Time               |
| Marcelo Heitor de Almeida Lira | Tiro Dividido / Espalhado |
| Lucas Carvalho dos Santos      | Buraco Negro              |

---

<h2 align="center">📚 Referências</h2>

- **[Projeto base](https://github.com/jucimarjr/asteroids_pygame)**
- **[C4 Model](https://c4model.com/)**
- **[Documentação do Pygame](https://www.pygame.org/docs/)**

---

<h2 align="center">👥 Equipe</h2>

| Nome                           | Matrícula   |
| ------------------------------ | ----------- |
| Ana Beatriz Maciel Nunes       | 2312030085  |
| Fernando Luiz Da Silva Freire  | 2315310007  |
| Juliana Ballin Lima            | 2315310011  |
| Marcelo Heitor de Almeida Lira | 2315310043  |
| Lucas Carvalho dos Santos      | 2315310012  |

---

<h3 align="center">UEA • Atividade 005 • Asteroids Gameplay</h3>
