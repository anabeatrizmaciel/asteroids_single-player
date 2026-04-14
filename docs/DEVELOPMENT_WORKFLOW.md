# ASTEROIDS -- DEVELOPMENT_WORKFLOW.md

## Fluxo de Desenvolvimento via Pull Requests

**Versao:** 1.0
**Data:** 14/04/2026

## 1. Objetivo

Guiar o desenvolvimento do Asteroids por meio de PRs curtos, seguros e testáveis, garantindo qualidade técnica e rastreabilidade.

## 2. Princípios

1. Nada entra em `main` sem Pull Request.
2. Cada PR deve ter escopo pequeno, coeso e validável.
3. O domínio (`core/`) é isolado e não deve importar `client/`.
4. O projeto deve continuar funcional ao final de cada PR.

## 3. Padrão de Branch e Commits

### 3.1 Nomenclatura de branch

- `feat/<descricao-curta>` -- nova funcionalidade
- `fix/<descricao-curta>` -- correção de bug
- `chore/<descricao-curta>` -- manutenção, docs, refatoração

Exemplos:
- `feat/multiplayer-lobby`
- `fix/hyperspace-spawn-inside-asteroid`
- `chore/extract-collision-manager`

### 3.2 Commits

Mensagens no formato:
- `feat: descricao objetiva`
- `fix: correcao especifica`
- `chore: alteracao estrutural`

Commits pequenos, descritivos e alinhados ao objetivo do PR.

## 4. Fluxo Operacional

### 4.1 Preparação

```bash
git checkout main
git pull
git checkout -b feat/nome-da-feature
```

### 4.2 Desenvolvimento

- Implementar apenas o escopo definido do PR.
- Preservar separação `core/` (lógica) e `client/` (apresentação).
- Não introduzir dependências novas sem aprovação.
- Centralizar constantes novas em `core/config.py`.

### 4.3 Validação local

```bash
python main.py
```

Testar manualmente:
- Gameplay funciona (mover, atirar, colisões)
- Menu e game over funcionam
- Sons tocam corretamente
- Nenhuma regressão visível

### 4.4 Publicação

```bash
git add <arquivos-relevantes>
git commit -m "feat: descricao objetiva"
git push origin feat/nome-da-feature
```

## 5. Estrutura do Pull Request

### 5.1 Título

Formato: `feat: descrição objetiva` / `fix: correção` / `chore: alteração`

### 5.2 Descrição

Todo PR deve conter:
- **Objetivo**: problema que o PR resolve
- **O que foi implementado**: lista objetiva de mudanças
- **Decisões técnicas**: justificativas quando relevante
- **Como testar**: passos para validar a mudança

## 6. Checklist de Revisão

### Arquitetura
- [ ] `core/` não importa `client/`
- [ ] Sem imports circulares
- [ ] Constantes em `core/config.py`

### Qualidade
- [ ] Código tipado (type hints)
- [ ] Sem números mágicos fora de `config.py`
- [ ] Funções coesas e legíveis
- [ ] Sem overengineering

### Funcionalidade
- [ ] Jogo roda sem erros (`python main.py`)
- [ ] Gameplay funcional (mover, atirar, colisões)
- [ ] Sem regressões visíveis

## 7. Sincronização Pós-Merge

Após PR aprovada e mergeada:

```bash
git checkout main
git pull
git branch -d <branch-da-pr>
git status
```

Confirmar que o worktree está limpo.

## 8. Estratégia de PR Curto

- Foco em **um objetivo principal** por PR
- Evitar misturar refatoração com feature nova
- Se crescer demais, dividir: `chore` → `feat` → `fix`
- Preferir qualidade com simplicidade sobre velocidade
