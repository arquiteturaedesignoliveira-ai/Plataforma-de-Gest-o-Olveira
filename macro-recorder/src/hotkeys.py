"""Sistema de atalhos globais do Windows.

Permite (ja preparado para uso futuro) registrar uma combinacao de teclas
global que executa uma macro especifica, mesmo com a janela do aplicativo
em segundo plano. Isolado em seu proprio modulo para nao acoplar a
interface grafica nem o sistema de gravacao/reproducao a essa
funcionalidade.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional

from pynput import keyboard


class GlobalHotkeyManager:
    """Gerencia o registro/remocao de atalhos globais (ex: 'ctrl+alt+1')
    mapeados para callbacks (tipicamente "executar macro X")."""

    def __init__(self):
        self._hotkeys: Dict[str, Callable[[], None]] = {}
        self._listener: Optional[keyboard.GlobalHotKeys] = None

    def set_hotkey(self, combo: str, callback: Callable[[], None]) -> None:
        """Registra/atualiza um atalho. `combo` no formato do pynput,
        ex: '<ctrl>+<alt>+1'."""
        self._hotkeys[combo] = callback
        self._restart_listener()

    def remove_hotkey(self, combo: str) -> None:
        self._hotkeys.pop(combo, None)
        self._restart_listener()

    def clear(self) -> None:
        self._hotkeys.clear()
        self._restart_listener()

    def _restart_listener(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None
        if self._hotkeys:
            self._listener = keyboard.GlobalHotKeys(dict(self._hotkeys))
            self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None


def normalize_combo(human_combo: str) -> str:
    """Converte algo como 'Ctrl+Alt+1' para o formato exigido pelo pynput
    ('<ctrl>+<alt>+1')."""
    parts = [p.strip().lower() for p in human_combo.split("+") if p.strip()]
    modifiers = {"ctrl", "alt", "shift", "cmd", "win"}
    normalized = []
    for part in parts:
        if part == "win":
            part = "cmd"
        normalized.append(f"<{part}>" if part in modifiers else part)
    return "+".join(normalized)
