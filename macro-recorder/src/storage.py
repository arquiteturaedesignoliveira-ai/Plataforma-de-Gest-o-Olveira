"""Sistema de armazenamento das macros.

Cada macro e salva como um arquivo JSON individual, legivel e estruturado,
dentro da pasta de biblioteca de macros (por padrao, uma pasta de dados do
usuario no Windows: %APPDATA%\\MacroRecorder\\macros).

Este modulo so usa a stdlib (json/os/re) para poder ser testado sem as
dependencias de captura/reproducao ou de interface grafica.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import List

from models import Macro

_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def default_library_dir() -> Path:
    """Pasta padrao da biblioteca de macros.

    No Windows usa %APPDATA%\\MacroRecorder\\macros. Em outros sistemas
    (usado apenas em desenvolvimento/testes) usa ~/.macro_recorder/macros.
    """
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / "MacroRecorder" / "macros"
    return Path.home() / ".macro_recorder" / "macros"


def sanitize_filename(name: str) -> str:
    """Converte o nome da macro em um nome de arquivo seguro no Windows."""
    cleaned = _INVALID_CHARS.sub("_", name).strip().strip(".")
    if not cleaned:
        raise ValueError("Nome de macro invalido.")
    return cleaned


class MacroStorage:
    """CRUD de macros persistidas como arquivos JSON."""

    def __init__(self, library_dir: Path | None = None):
        self.library_dir = Path(library_dir) if library_dir else default_library_dir()
        self.library_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, name: str) -> Path:
        return self.library_dir / f"{sanitize_filename(name)}.json"

    def list_macro_names(self) -> List[str]:
        names = []
        for path in sorted(self.library_dir.glob("*.json")):
            names.append(path.stem)
        return names

    def exists(self, name: str) -> bool:
        return self._path_for(name).exists()

    def save(self, macro: Macro, overwrite: bool = True) -> Path:
        path = self._path_for(macro.name)
        if not overwrite and path.exists():
            raise FileExistsError(f"Ja existe uma macro chamada '{macro.name}'.")
        path.write_text(
            json.dumps(macro.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def load(self, name: str) -> Macro:
        path = self._path_for(name)
        if not path.exists():
            raise FileNotFoundError(f"Macro '{name}' nao encontrada.")
        data = json.loads(path.read_text(encoding="utf-8"))
        return Macro.from_dict(data)

    def delete(self, name: str) -> None:
        path = self._path_for(name)
        if path.exists():
            path.unlink()

    def rename(self, old_name: str, new_name: str) -> None:
        if old_name == new_name:
            return
        if self.exists(new_name):
            raise FileExistsError(f"Ja existe uma macro chamada '{new_name}'.")
        macro = self.load(old_name)
        macro.name = new_name
        self.save(macro, overwrite=False)
        self.delete(old_name)
