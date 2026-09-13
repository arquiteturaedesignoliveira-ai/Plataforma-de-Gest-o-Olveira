"""Sistema de gravacao: captura teclas e cliques do mouse em qualquer
programa do Windows usando hooks globais (pynput), de forma totalmente
independente do programa em uso (nao interpreta o significado das teclas).
"""
from __future__ import annotations

import threading
import time
from typing import Callable, List, Optional

from pynput import keyboard, mouse

from keymap import key_to_str
from models import (
    EVENT_KEY_DOWN,
    EVENT_KEY_UP,
    EVENT_MOUSE_DOWN,
    EVENT_MOUSE_UP,
    MacroEvent,
)


class MacroRecorder:
    """Grava a sequencia de teclas e cliques do usuario, com o tempo entre
    cada acao, ate que stop() seja chamado."""

    def __init__(self, on_event: Optional[Callable[[MacroEvent], None]] = None):
        self._on_event = on_event
        self._events: List[MacroEvent] = []
        self._event_ts: List[float] = []  # timestamp monotonico de cada evento
        self._lock = threading.Lock()
        self._last_ts: Optional[float] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        self._recording = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self) -> None:
        if self._recording:
            return
        self._events = []
        self._event_ts = []
        self._last_ts = None
        self._recording = True
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press, on_release=self._on_key_release
        )
        self._mouse_listener = mouse.Listener(on_click=self._on_click)
        self._keyboard_listener.start()
        self._mouse_listener.start()

    def stop(self, trim_seconds: float = 0.35) -> List[MacroEvent]:
        """Encerra a gravacao. `trim_seconds` descarta os eventos finais
        ocorridos nesse intervalo antes do stop(), pois normalmente
        correspondem ao proprio clique no botao "Parar" da interface."""
        if not self._recording:
            return list(self._events)
        self._recording = False
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        if self._mouse_listener:
            self._mouse_listener.stop()
        with self._lock:
            now = time.monotonic()
            while self._event_ts and (now - self._event_ts[-1]) < trim_seconds:
                self._events.pop()
                self._event_ts.pop()
            return list(self._events)

    def _record(self, event: MacroEvent) -> None:
        with self._lock:
            self._events.append(event)
            self._event_ts.append(time.monotonic())
        if self._on_event:
            self._on_event(event)

    def _delay_since_last(self) -> float:
        now = time.monotonic()
        if self._last_ts is None:
            delay = 0.0
        else:
            delay = max(0.0, now - self._last_ts)
        self._last_ts = now
        return delay

    def _on_key_press(self, key) -> None:
        delay = self._delay_since_last()
        self._record(MacroEvent(type=EVENT_KEY_DOWN, delay=delay, key=key_to_str(key)))

    def _on_key_release(self, key) -> None:
        delay = self._delay_since_last()
        self._record(MacroEvent(type=EVENT_KEY_UP, delay=delay, key=key_to_str(key)))

    def _on_click(self, x, y, button, pressed) -> None:
        delay = self._delay_since_last()
        event_type = EVENT_MOUSE_DOWN if pressed else EVENT_MOUSE_UP
        self._record(
            MacroEvent(type=event_type, delay=delay, button=button.name, x=int(x), y=int(y))
        )
