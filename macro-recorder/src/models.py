"""Modelos de dados do Macro Recorder.

Este modulo nao depende de nenhuma biblioteca externa (apenas stdlib),
para que macros possam ser carregadas, validadas e testadas sem exigir
as dependencias de captura/reproducao (pynput) ou de interface (tkinter).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

# Tipos de evento suportados pela macro.
EVENT_KEY_DOWN = "key_down"
EVENT_KEY_UP = "key_up"
EVENT_MOUSE_DOWN = "mouse_down"
EVENT_MOUSE_UP = "mouse_up"

VALID_EVENT_TYPES = {
    EVENT_KEY_DOWN,
    EVENT_KEY_UP,
    EVENT_MOUSE_DOWN,
    EVENT_MOUSE_UP,
}

SCHEMA_VERSION = 1


@dataclass
class MacroEvent:
    """Uma unica acao gravada (tecla ou clique) com o intervalo desde a
    acao anterior."""

    type: str
    delay: float  # segundos desde o evento anterior (>= 0)
    key: Optional[str] = None       # ex: "ctrl", "j", "enter", "esc"
    button: Optional[str] = None    # ex: "left", "right", "middle"
    x: Optional[int] = None
    y: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None or k in ("type", "delay")}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MacroEvent":
        if data.get("type") not in VALID_EVENT_TYPES:
            raise ValueError(f"Tipo de evento invalido: {data.get('type')!r}")
        return MacroEvent(
            type=data["type"],
            delay=float(data.get("delay", 0.0)),
            key=data.get("key"),
            button=data.get("button"),
            x=data.get("x"),
            y=data.get("y"),
        )


@dataclass
class Macro:
    """Uma macro: nome + sequencia ordenada de eventos."""

    name: str
    events: List[MacroEvent] = field(default_factory=list)
    hotkey: Optional[str] = None            # ex: "ctrl+alt+1" (uso futuro)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    schema_version: int = SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "hotkey": self.hotkey,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "schema_version": self.schema_version,
            "events": [e.to_dict() for e in self.events],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Macro":
        return Macro(
            name=data["name"],
            events=[MacroEvent.from_dict(e) for e in data.get("events", [])],
            hotkey=data.get("hotkey"),
            created_at=float(data.get("created_at", time.time())),
            updated_at=float(data.get("updated_at", time.time())),
            schema_version=int(data.get("schema_version", SCHEMA_VERSION)),
        )

    def total_duration(self) -> float:
        return sum(e.delay for e in self.events)
