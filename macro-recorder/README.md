# Macro Recorder

Gravador universal de macros para Windows. Grava sequências de teclas e
cliques do mouse feitas pelo usuário em **qualquer programa** e permite
reproduzi-las depois, respeitando a ordem e os intervalos de tempo
originais.

O aplicativo **não depende do Archicad nem de nenhum outro software
específico**: ele apenas grava e reproduz eventos de teclado/mouse do
Windows, sem interpretar o que cada tecla ou atalho significa.

## Fluxo principal

```
Nova Macro → Gravar → (usar o programa normalmente) → Parar → Executar
```

1. **Nova Macro**: dá um nome à macro (ex: "Juntar e Salvar") e a cria vazia.
2. **Gravar**: inicia a captura global de teclado e mouse.
3. Durante a gravação, o usuário usa qualquer programa normalmente
   (Archicad, Explorer, navegador, etc.).
4. **Parar**: encerra a gravação e salva automaticamente a sequência
   capturada na macro selecionada.
5. **Executar**: reproduz a macro na ordem gravada, respeitando os
   intervalos de tempo entre cada ação (com uma contagem de ~3s antes de
   começar, para o usuário poder trocar de janela).

Também é possível **Renomear**, **Excluir** e **Editar/Revisar** (remover
passos indesejados) qualquer macro salva, e opcionalmente **Definir
Atalho** (ex: `Ctrl+Alt+1`) para executá-la sem abrir a interface.

## Arquitetura

O código é dividido em camadas independentes, como pedido:

| Módulo               | Responsabilidade                                              |
|-----------------------|----------------------------------------------------------------|
| `src/gui.py`          | Interface gráfica (Tkinter): botões, lista de macros, status. |
| `src/recorder.py`     | Sistema de gravação: hooks globais de teclado/mouse (pynput). |
| `src/player.py`       | Sistema de reprodução: executa os eventos respeitando delays. |
| `src/storage.py`      | Armazenamento: cada macro é um arquivo `.json` na biblioteca.  |
| `src/macro_manager.py`| Gerenciamento (CRUD) das macros, com validações.                |
| `src/waiting.py`      | Espera inteligente: detecta quando o programa alvo está ocupado.|
| `src/keymap.py`       | Conversão tecla física ⇄ texto do JSON.                        |
| `src/hotkeys.py`      | Atalhos globais do Windows para executar macros diretamente.   |
| `src/models.py`       | Estruturas de dados (`Macro`, `MacroEvent`) e serialização.     |

`gui.py` é a única camada que conhece Tkinter; `recorder.py`/`player.py`/
`hotkeys.py` são as únicas que dependem do `pynput`. `models.py`,
`storage.py` e `macro_manager.py` usam apenas a biblioteca padrão do
Python, o que permite testá-los sem instalar dependência alguma (veja
`tests/test_core.py`).

## Espera inteligente (em vez de tempo fixo)

O tempo que um programa leva para concluir uma operação **varia de projeto
para projeto**. Reproduzir a macro com os tempos exatos da gravação dispara
a ação seguinte cedo demais em um projeto pesado — e desperdiça segundos em
um projeto leve.

Por isso cada macro tem um **modo de espera** (botão *Modo de Espera*):

| Modo | Comportamento |
|------|----------------|
| **Inteligente** (padrão) | O tempo gravado é só referência. Antes de cada ação, a macro espera o programa em foco parar de sinalizar que está ocupado. |
| **Tempo fixo** | Reproduz exatamente os intervalos gravados. |

Como o modo inteligente sabe que o programa está ocupado, sem usar API nem
plugin do programa alvo (`src/waiting.py`):

1. **A janela em primeiro plano responde a mensagens do Windows?** Enquanto
   processa uma operação pesada, o loop de mensagens do programa trava — é
   o mesmo sinal que faz o Windows exibir "Não respondendo".
2. **O cursor está no estado de espera** (ampulheta / círculo girando)?

Enquanto qualquer um dos dois indicar "ocupado", a macro aguarda. Detalhes:

- Intervalos curtos (< 0,25s) são ritmo de digitação, não espera por
  operação: continuam sendo reproduzidos como gravados, sem verificação.
- O programa precisa ficar pronto por 0,25s contínuos, para a macro não
  disparar durante uma pausa momentânea do processamento.
- Há um **limite máximo** de espera (o maior entre 10s e 5× o tempo
  gravado, com teto de 120s), para a macro nunca travar indefinidamente.

**Limitação:** se o programa fizer o trabalho em uma thread de fundo e
mantiver a interface respondendo normalmente, esses dois sinais não detectam
nada, e a macro segue com a espera mínima. Nesse caso, use *Tempo fixo* para
aquela macro específica.

## Formato da macro (JSON)

Cada macro é salva como um arquivo legível em
`%APPDATA%\MacroRecorder\macros\<nome>.json`:

```json
{
  "name": "Juntar e Salvar",
  "hotkey": "Ctrl+Alt+1",
  "created_at": 1765000000.0,
  "updated_at": 1765000012.0,
  "schema_version": 1,
  "events": [
    { "type": "key_down", "delay": 0.0,  "key": "ctrl" },
    { "type": "key_down", "delay": 0.01, "key": "alt" },
    { "type": "key_down", "delay": 0.02, "key": "j" },
    { "type": "key_up",   "delay": 0.05, "key": "j" },
    { "type": "key_up",   "delay": 0.01, "key": "alt" },
    { "type": "key_up",   "delay": 0.3,  "key": "ctrl" },
    { "type": "mouse_down", "delay": 0.8, "button": "left", "x": 512, "y": 340 },
    { "type": "mouse_up",   "delay": 0.05, "button": "left", "x": 512, "y": 340 }
  ]
}
```

`delay` é sempre o tempo (em segundos) desde o evento anterior. Como
pressionar e soltar cada tecla é gravado separadamente, combinações e
atalhos (ex: `Ctrl+Alt+J`) são reproduzidos naturalmente, sem que o
aplicativo precise "entender" o que aquele atalho faz.

O que se grava é sempre a **tecla física** (pelo virtual-key code do
Windows), não o caractere resultante. Isso é necessário porque, com Ctrl
pressionado, o Windows reporta um caractere de controle — `Ctrl+M` viria
como `\r` e seria reproduzido como Enter. Gravando a tecla física,
`Ctrl+Shift+M` é reproduzido exatamente como foi feito.

## Como abrir no Windows

Requer Windows + [Python 3.10+](https://www.python.org/downloads/)
(marque **"Add Python to PATH"** ao instalar).

**Modo mais simples:** dê duplo clique em `run.bat`. Na primeira vez ele
prepara o ambiente e instala as dependências sozinho; nas próximas, abre
o aplicativo direto.

**Pela linha de comando:**

```bat
cd macro-recorder
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src\main.py
```

> No Windows, a captura global de teclado/mouse (via `pynput`) normalmente
> não exige privilégios de administrador, mas alguns programas protegidos
> (ex: rodando como Administrador) só têm suas teclas capturadas se o
> Macro Recorder também for executado como Administrador.

## Gerando o executável (.exe)

```bat
build.bat
```

Isso gera `dist\MacroRecorder.exe`, um executável único que pode ser
distribuído e usado sem precisar instalar Python.

## Testes

Os módulos que não dependem de `pynput`/`tkinter` têm testes automatizados
que rodam em qualquer ambiente:

```bash
python tests/test_core.py
```

## Limitações da primeira versão / próximos passos

- A gravação de mouse captura apenas cliques (posição + botão), não o
  movimento contínuo do cursor — suficiente para reproduzir a ação, e
  evita arquivos de macro excessivamente grandes.
- Ao clicar em "Parar" pela interface, o próprio clique no botão pode, em
  alguns casos, ser capturado como o último evento; por isso os eventos
  finais ocorridos nos ~0,35s antes do clique em "Parar" são
  automaticamente descartados.
- Atalhos globais (`Definir Atalho`) já funcionam nesta primeira versão,
  mas continuam sendo uma funcionalidade complementar — o fluxo principal
  é gravar, nomear, salvar e executar pela interface.
- Não há qualquer integração, leitura ou dependência do Archicad ou de
  qualquer outro programa: o Macro Recorder apenas grava/reproduz eventos
  brutos do Windows.
