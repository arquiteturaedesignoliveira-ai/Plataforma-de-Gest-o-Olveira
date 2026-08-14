"""Ponto de entrada do Macro Recorder.

Uso:
    python main.py
"""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import messagebox

from gui import MacroRecorderApp


def main() -> None:
    if not sys.platform.startswith("win"):
        # A captura/reproducao global (pynput) e o alvo (Windows) da app;
        # em outros sistemas o app ainda abre para fins de desenvolvimento,
        # mas gravar/executar pode exigir permissoes adicionais do SO.
        pass

    root = tk.Tk()
    try:
        app = MacroRecorderApp(root)
    except Exception as exc:  # falha ao iniciar hooks globais, etc.
        messagebox.showerror("Macro Recorder", f"Falha ao iniciar o aplicativo:\n{exc}")
        raise
    root.mainloop()


if __name__ == "__main__":
    main()
