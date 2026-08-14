"""Gerenciamento das macros: cria, renomeia, exclui e lista, aplicando
validacoes de negocio sobre o MacroStorage (nomes unicos, nomes vazios etc).
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from models import Macro
from storage import MacroStorage


class MacroManager:
    def __init__(self, storage: Optional[MacroStorage] = None):
        self.storage = storage or MacroStorage()

    def list_macros(self) -> List[str]:
        return self.storage.list_macro_names()

    def get(self, name: str) -> Macro:
        return self.storage.load(name)

    def create_empty(self, name: str) -> Macro:
        name = name.strip()
        if not name:
            raise ValueError("Informe um nome para a macro.")
        if self.storage.exists(name):
            raise FileExistsError(f"Ja existe uma macro chamada '{name}'.")
        macro = Macro(name=name)
        self.storage.save(macro, overwrite=False)
        return macro

    def save(self, macro: Macro) -> Path:
        import time
        macro.updated_at = time.time()
        return self.storage.save(macro)

    def rename(self, old_name: str, new_name: str) -> None:
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Informe um novo nome para a macro.")
        self.storage.rename(old_name, new_name)

    def delete(self, name: str) -> None:
        self.storage.delete(name)
