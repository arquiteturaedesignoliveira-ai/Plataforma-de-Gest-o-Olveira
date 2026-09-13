"""Espera inteligente entre as acoes de uma macro.

Problema: o tempo que um programa leva para concluir uma operacao varia de
projeto para projeto e de maquina para maquina. Reproduzir a macro com o
tempo exato que foi gravado dispara a acao seguinte cedo demais (quando o
projeto e mais pesado) ou desperdica segundos (quando e mais leve).

Solucao: em vez de esperar um tempo fixo, esperar ate o programa em foco
estar PRONTO para receber a proxima acao. Isso e feito sem nenhuma API ou
plugin do programa alvo, usando dois sinais do proprio Windows:

1. A janela em primeiro plano responde a mensagens? Enquanto um programa
   processa uma operacao pesada, seu loop de mensagens fica bloqueado e
   ele para de responder (e o que faz o Windows exibir "Nao respondendo").
2. O cursor esta no estado de espera (ampulheta / circulo girando)?

Enquanto qualquer um dos dois indicar "ocupado", a reproducao aguarda.

As funcoes de politica (plan_wait) nao dependem do Windows e podem ser
testadas em qualquer ambiente; as chamadas ao Win32 ficam isoladas e, fora
do Windows, degradam para a espera de tempo fixo.
"""
from __future__ import annotations

import sys
import time
from typing import Callable, Optional, Tuple

IS_WINDOWS = sys.platform.startswith("win")

# --- Politica de espera -------------------------------------------------

# Intervalos curtos sao ritmo de digitacao (soltar/pressionar teclas de um
# atalho), nao espera por uma operacao: sao reproduzidos como gravados.
SMART_MIN_GAP = 0.25
# Espera minima antes de comecar a verificar se o programa esta pronto.
SMART_BASE_WAIT = 0.15
# O programa precisa ficar "pronto" por este tempo continuo para a macro
# seguir (evita disparar durante uma pausa momentanea do processamento).
SMART_STABLE_FOR = 0.25
# Limite maximo de espera, para a macro nunca travar indefinidamente.
SMART_MAX_FLOOR = 10.0
SMART_MAX_FACTOR = 5.0
SMART_MAX_CEILING = 120.0

WAIT_MODE_SMART = "smart"
WAIT_MODE_FIXED = "fixed"
VALID_WAIT_MODES = (WAIT_MODE_SMART, WAIT_MODE_FIXED)


def plan_wait(delay: float, smart: bool = True) -> Tuple[bool, float, float]:
    """Define como esperar antes de uma acao.

    Retorna (usar_espera_inteligente, espera_minima, espera_maxima).
    Em modo fixo - ou para intervalos muito curtos - reproduz o tempo
    gravado tal como esta.
    """
    delay = max(0.0, delay)
    if not smart or delay < SMART_MIN_GAP:
        return (False, delay, delay)
    max_wait = min(SMART_MAX_CEILING, max(SMART_MAX_FLOOR, delay * SMART_MAX_FACTOR))
    return (True, SMART_BASE_WAIT, max_wait)


# --- Deteccao de "programa ocupado" (Windows) ---------------------------

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    _user32 = ctypes.windll.user32

    WM_NULL = 0x0000
    SMTO_ABORTIFHUNG = 0x0002
    IDC_WAIT = 32514
    IDC_APPSTARTING = 32650
    CURSOR_SHOWING = 0x0001

    class _CURSORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("flags", wintypes.DWORD),
            ("hCursor", wintypes.HANDLE),
            ("ptScreenPos", wintypes.POINT),
        ]

    # As assinaturas precisam ser declaradas: sem elas, o ctypes trunca
    # handles de 64 bits e as chamadas falham silenciosamente.
    _user32.GetForegroundWindow.restype = wintypes.HWND
    _user32.GetForegroundWindow.argtypes = []

    _user32.IsHungAppWindow.restype = wintypes.BOOL
    _user32.IsHungAppWindow.argtypes = [wintypes.HWND]

    _user32.SendMessageTimeoutW.restype = ctypes.c_ssize_t
    _user32.SendMessageTimeoutW.argtypes = [
        wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM,
        wintypes.UINT, wintypes.UINT, ctypes.POINTER(ctypes.c_size_t),
    ]

    _user32.GetCursorInfo.restype = wintypes.BOOL
    _user32.GetCursorInfo.argtypes = [ctypes.POINTER(_CURSORINFO)]

    _user32.LoadCursorW.restype = wintypes.HANDLE
    _user32.LoadCursorW.argtypes = [wintypes.HINSTANCE, ctypes.c_void_p]

    def _busy_cursor_handles():
        return {
            _user32.LoadCursorW(None, ctypes.c_void_p(IDC_WAIT)),
            _user32.LoadCursorW(None, ctypes.c_void_p(IDC_APPSTARTING)),
        }

    def is_wait_cursor() -> bool:
        info = _CURSORINFO()
        info.cbSize = ctypes.sizeof(_CURSORINFO)
        if not _user32.GetCursorInfo(ctypes.byref(info)):
            return False
        if not (info.flags & CURSOR_SHOWING):
            return False
        return info.hCursor in _busy_cursor_handles()

    def is_foreground_responsive(timeout_ms: int = 150) -> bool:
        hwnd = _user32.GetForegroundWindow()
        if not hwnd:
            return True
        if _user32.IsHungAppWindow(hwnd):
            return False
        result = ctypes.c_size_t(0)
        ok = _user32.SendMessageTimeoutW(
            hwnd, WM_NULL, 0, 0, SMTO_ABORTIFHUNG, timeout_ms, ctypes.byref(result)
        )
        return bool(ok)

    def is_app_busy() -> bool:
        """True enquanto o programa em foco parecer ocupado processando."""
        try:
            return (not is_foreground_responsive()) or is_wait_cursor()
        except Exception:
            # Qualquer falha na deteccao: assume pronto e deixa a macro seguir.
            return False

else:  # pragma: no cover - fora do Windows nao ha deteccao

    def is_wait_cursor() -> bool:
        return False

    def is_foreground_responsive(timeout_ms: int = 150) -> bool:
        return True

    def is_app_busy() -> bool:
        return False


def wait_until_ready(
    max_wait: float,
    is_cancelled: Optional[Callable[[], bool]] = None,
    poll: float = 0.08,
    stable_for: float = SMART_STABLE_FOR,
) -> bool:
    """Aguarda ate o programa em foco parar de sinalizar "ocupado".

    Retorna True se ficou pronto dentro do limite, False se estourou o
    tempo maximo ou se a reproducao foi cancelada.
    """
    deadline = time.monotonic() + max_wait
    ready_since: Optional[float] = None
    while True:
        if is_cancelled and is_cancelled():
            return False
        now = time.monotonic()
        if is_app_busy():
            ready_since = None
        else:
            if ready_since is None:
                ready_since = now
            elif now - ready_since >= stable_for:
                return True
        if now >= deadline:
            return False
        time.sleep(min(poll, max(0.0, deadline - now)))
