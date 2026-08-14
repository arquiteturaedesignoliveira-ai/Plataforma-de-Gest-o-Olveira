"""Sistema de reproducao: executa a sequencia de eventos de uma macro,
respeitando os intervalos de tempo gravados entre cada acao.
"""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional

from pynput import keyboard, mouse

from models import (
    EVENT_KEY_DOWN,
    EVENT_KEY_UP,
    EVENT_MOUSE_DOWN,
    EVENT_MOUSE_UP,
    Macro,
    MacroEvent,
)

# Mapa de nomes especiais (keyboard.Key) usados na gravacao -> objeto pynput.
_SPECIAL_KEYS = {k.name: k for k in keyboard.Key}


def _str_to_key(name: str):
    if name in _SPECIAL_KEYS:
        return _SPECIAL_KEYS[name]
    if name.startswith("vk_"):
        return keyboard.KeyCode(vk=int(name[3:]))
    return keyboard.KeyCode.from_char(name)


class MacroPlayer:
    """Reproduz uma macro gravada, em uma thread separada, respeitando os
    delays originais. Pode ser interrompida com stop()."""

    def __init__(self, on_progress: Optional[Callable[[int, int], None]] = None):
        self._on_progress = on_progress
        self._stop_flag = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._playing = False
        self._keyboard = keyboard.Controller()
        self._mouse = mouse.Controller()

    @property
    def is_playing(self) -> bool:
        return self._playing

    def play(self, macro: Macro, start_delay: float = 0.0, repeat: int = 1,
              on_finished: Optional[Callable[[], None]] = None) -> None:
        if self._playing:
            raise RuntimeError("Ja existe uma macro em execucao.")
        self._stop_flag.clear()
        self._playing = True
        self._thread = threading.Thread(
            target=self._run, args=(macro, start_delay, repeat, on_finished), daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_flag.set()

    def _run(self, macro: Macro, start_delay: float, repeat: int,
              on_finished: Optional[Callable[[], None]]) -> None:
        try:
            if start_delay > 0:
                self._sleep(start_delay)
            total = len(macro.events)
            for _ in range(max(1, repeat)):
                for index, event in enumerate(macro.events):
                    if self._stop_flag.is_set():
                        return
                    if event.delay > 0:
                        self._sleep(event.delay)
                    if self._stop_flag.is_set():
                        return
                    self._execute(event)
                    if self._on_progress:
                        self._on_progress(index + 1, total)
        finally:
            self._playing = False
            if on_finished:
                on_finished()

    def _sleep(self, seconds: float) -> None:
        # Divide o sleep em pequenos passos para permitir interrupcao rapida.
        end = time.monotonic() + seconds
        while not self._stop_flag.is_set():
            remaining = end - time.monotonic()
            if remaining <= 0:
                return
            time.sleep(min(0.05, remaining))

    def _execute(self, event: MacroEvent) -> None:
        if event.type == EVENT_KEY_DOWN:
            self._keyboard.press(_str_to_key(event.key))
        elif event.type == EVENT_KEY_UP:
            self._keyboard.release(_str_to_key(event.key))
        elif event.type == EVENT_MOUSE_DOWN:
            self._mouse.position = (event.x, event.y)
            self._mouse.press(getattr(mouse.Button, event.button))
        elif event.type == EVENT_MOUSE_UP:
            self._mouse.position = (event.x, event.y)
            self._mouse.release(getattr(mouse.Button, event.button))
