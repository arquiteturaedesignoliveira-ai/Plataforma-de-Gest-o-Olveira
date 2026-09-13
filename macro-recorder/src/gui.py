"""Interface grafica (Tkinter) do Macro Recorder.

Camada fina: toda a logica de gravacao, reproducao e armazenamento vive em
recorder.py / player.py / storage.py / macro_manager.py. Este modulo apenas
conecta esses componentes aos botoes e listas da janela.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Optional

from hotkeys import GlobalHotkeyManager, normalize_combo
from macro_manager import MacroManager
from models import WAIT_MODE_FIXED, WAIT_MODE_SMART, Macro
from player import MacroPlayer
from recorder import MacroRecorder

STATUS_IDLE = ("Pronto", "#2e7d32")
STATUS_STARTING = ("Iniciando gravacao...", "#ef6c00")
STATUS_RECORDING = ("● Gravando...", "#c62828")
STATUS_PLAYING = ("▶ Executando...", "#1565c0")
STATUS_WAITING = ("Aguarde, prepare a janela de destino...", "#ef6c00")

PLAYBACK_START_DELAY = 3.0  # segundos de contagem regressiva antes de executar
RECORD_START_DELAY = 0.5    # atraso antes de comecar a capturar, ao clicar Gravar


class MacroRecorderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Macro Recorder")
        self.root.geometry("640x420")
        self.root.minsize(560, 360)

        self.manager = MacroManager()
        self.recorder = MacroRecorder()
        self.player = MacroPlayer(on_progress=self._on_play_progress)
        self.hotkey_manager = GlobalHotkeyManager()

        self._current_macro: Optional[Macro] = None
        self._record_pending = False  # entre o clique em "Gravar" e o inicio da captura
        self._build_ui()
        self._refresh_list()
        self._register_all_hotkeys()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill=tk.BOTH, expand=True)

        # Status
        status_frame = ttk.Frame(top)
        status_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value=STATUS_IDLE[0])
        self.status_label = tk.Label(
            status_frame, textvariable=self.status_var, fg=STATUS_IDLE[1], font=("Segoe UI", 10, "bold")
        )
        self.status_label.pack(side=tk.LEFT, padx=6)

        # Lista de macros
        list_frame = ttk.Frame(top)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("eventos", "duracao", "espera", "atalho")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", selectmode="browse")
        self.tree.heading("#0", text="Macro")
        self.tree.heading("eventos", text="Acoes")
        self.tree.heading("duracao", text="Duracao (s)")
        self.tree.heading("espera", text="Espera")
        self.tree.heading("atalho", text="Atalho")
        self.tree.column("#0", width=190)
        self.tree.column("eventos", width=70, anchor=tk.CENTER)
        self.tree.column("duracao", width=90, anchor=tk.CENTER)
        self.tree.column("espera", width=100, anchor=tk.CENTER)
        self.tree.column("atalho", width=110, anchor=tk.CENTER)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._update_button_states())

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # Botoes - linha 1: gravar e executar
        btn_row1 = ttk.Frame(top)
        btn_row1.pack(fill=tk.X, pady=(10, 0))

        self.btn_new = ttk.Button(btn_row1, text="Nova Macro", command=self._on_new)
        self.btn_record = ttk.Button(btn_row1, text="Gravar", command=self._on_record)
        self.btn_stop = ttk.Button(btn_row1, text="Parar", command=self._on_stop)
        self.btn_play = ttk.Button(btn_row1, text="Executar", command=self._on_play)

        for b in (self.btn_new, self.btn_record, self.btn_stop, self.btn_play):
            b.pack(side=tk.LEFT, padx=3)

        # Botoes - linha 2: gerenciar a macro selecionada
        btn_row2 = ttk.Frame(top)
        btn_row2.pack(fill=tk.X, pady=(6, 0))

        self.btn_rename = ttk.Button(btn_row2, text="Renomear", command=self._on_rename)
        self.btn_delete = ttk.Button(btn_row2, text="Excluir", command=self._on_delete)
        self.btn_edit = ttk.Button(btn_row2, text="Editar/Revisar", command=self._on_edit)
        self.btn_wait = ttk.Button(btn_row2, text="Modo de Espera", command=self._on_toggle_wait_mode)
        self.btn_hotkey = ttk.Button(btn_row2, text="Definir Atalho", command=self._on_set_hotkey)

        for b in (self.btn_rename, self.btn_delete, self.btn_edit, self.btn_wait, self.btn_hotkey):
            b.pack(side=tk.LEFT, padx=3)

        self._update_button_states()

    def _refresh_list(self, select_name: Optional[str] = None) -> None:
        self.tree.delete(*self.tree.get_children())
        for name in self.manager.list_macros():
            try:
                macro = self.manager.get(name)
            except Exception:
                continue
            espera = "Inteligente" if macro.wait_mode == WAIT_MODE_SMART else "Tempo fixo"
            self.tree.insert(
                "", tk.END, iid=name, text=name,
                values=(
                    len(macro.events),
                    f"{macro.total_duration():.2f}",
                    espera,
                    macro.hotkey or "-",
                ),
            )
        if select_name and self.tree.exists(select_name):
            self.tree.selection_set(select_name)
        self._update_button_states()

    def _selected_name(self) -> Optional[str]:
        sel = self.tree.selection()
        return sel[0] if sel else None

    def _update_button_states(self) -> None:
        busy = self.recorder.is_recording or self.player.is_playing or self._record_pending
        has_selection = self._selected_name() is not None

        self.btn_new.config(state=tk.DISABLED if busy else tk.NORMAL)
        self.btn_record.config(state=tk.DISABLED if busy or not has_selection else tk.NORMAL)
        self.btn_stop.config(state=tk.NORMAL if busy else tk.DISABLED)
        self.btn_play.config(state=tk.DISABLED if busy or not has_selection else tk.NORMAL)
        self.btn_rename.config(state=tk.DISABLED if busy or not has_selection else tk.NORMAL)
        self.btn_delete.config(state=tk.DISABLED if busy or not has_selection else tk.NORMAL)
        self.btn_edit.config(state=tk.DISABLED if busy or not has_selection else tk.NORMAL)
        self.btn_wait.config(state=tk.DISABLED if busy or not has_selection else tk.NORMAL)
        self.btn_hotkey.config(state=tk.DISABLED if busy or not has_selection else tk.NORMAL)

    def _set_status(self, status: tuple[str, str]) -> None:
        text, color = status
        self.status_var.set(text)
        self.status_label.config(fg=color)

    # -------------------------------------------------------------- Acoes
    def _on_new(self) -> None:
        name = simpledialog.askstring("Nova Macro", "Nome da macro:", parent=self.root)
        if not name:
            return
        try:
            self.manager.create_empty(name)
        except (ValueError, FileExistsError) as exc:
            messagebox.showerror("Erro", str(exc))
            return
        self._refresh_list(select_name=name)

    def _on_record(self) -> None:
        name = self._selected_name()
        if not name:
            return
        macro = self.manager.get(name)
        if macro.events:
            if not messagebox.askyesno(
                "Regravar macro",
                f"A macro '{name}' ja possui {len(macro.events)} acao(oes) gravada(s).\n"
                "Deseja regravar do zero (as acoes atuais serao substituidas)?",
            ):
                return
        self._current_macro = macro
        self._record_pending = True
        self._set_status(STATUS_STARTING)
        self._update_button_states()
        # Pequeno atraso para que a soltura do proprio clique no botao
        # "Gravar" nao entre como primeira acao da macro.
        self.root.after(int(RECORD_START_DELAY * 1000), self._begin_recording)

    def _begin_recording(self) -> None:
        if not self._record_pending or self._current_macro is None:
            return  # gravacao cancelada antes de comecar
        self._record_pending = False
        self.recorder.start()
        self._set_status(STATUS_RECORDING)
        self._update_button_states()

    def _on_stop(self) -> None:
        if self._record_pending:
            # Cancelado antes de a captura comecar de fato.
            self._record_pending = False
            self._current_macro = None
            self._set_status(STATUS_IDLE)
        elif self.recorder.is_recording:
            events = self.recorder.stop()
            macro = self._current_macro
            if macro is not None:
                macro.events = events
                self.manager.save(macro)
            self._current_macro = None
            self._set_status(STATUS_IDLE)
            self._refresh_list(select_name=macro.name if macro else None)
            messagebox.showinfo("Gravacao concluida", f"{len(events)} acao(oes) gravada(s) e salva(s).")
        elif self.player.is_playing:
            self.player.stop()
            self._set_status(STATUS_IDLE)
        self._update_button_states()

    def _on_play(self) -> None:
        name = self._selected_name()
        if not name:
            return
        macro = self.manager.get(name)
        if not macro.events:
            messagebox.showwarning("Macro vazia", "Esta macro nao possui acoes gravadas.")
            return
        self._set_status(STATUS_WAITING)
        self._update_button_states()

        def finished():
            self.root.after(0, self._on_play_finished)

        self.player.play(macro, start_delay=PLAYBACK_START_DELAY, on_finished=finished)
        self.root.after(int(PLAYBACK_START_DELAY * 1000), self._mark_playing_if_still_running)

    def _mark_playing_if_still_running(self) -> None:
        if self.player.is_playing:
            self._set_status(STATUS_PLAYING)

    def _on_play_progress(self, done: int, total: int) -> None:
        pass  # reservado para uma futura barra de progresso

    def _on_play_finished(self) -> None:
        self._set_status(STATUS_IDLE)
        self._update_button_states()

    def _on_rename(self) -> None:
        name = self._selected_name()
        if not name:
            return
        new_name = simpledialog.askstring("Renomear Macro", "Novo nome:", initialvalue=name, parent=self.root)
        if not new_name or new_name == name:
            return
        try:
            self.manager.rename(name, new_name)
        except (ValueError, FileExistsError) as exc:
            messagebox.showerror("Erro", str(exc))
            return
        self._refresh_list(select_name=new_name)

    def _on_delete(self) -> None:
        name = self._selected_name()
        if not name:
            return
        if not messagebox.askyesno("Excluir Macro", f"Excluir permanentemente a macro '{name}'?"):
            return
        self.manager.delete(name)
        self._refresh_list()

    def _on_edit(self) -> None:
        name = self._selected_name()
        if not name:
            return
        macro = self.manager.get(name)
        MacroEditWindow(self.root, self.manager, macro, on_saved=lambda: self._refresh_list(select_name=name))

    def _on_toggle_wait_mode(self) -> None:
        name = self._selected_name()
        if not name:
            return
        macro = self.manager.get(name)
        atual = macro.wait_mode
        usar_inteligente = messagebox.askyesno(
            "Modo de Espera",
            f"Macro: {name}\n"
            f"Modo atual: {'Inteligente' if atual == WAIT_MODE_SMART else 'Tempo fixo'}\n\n"
            "SIM = Espera inteligente (recomendado)\n"
            "     Aguarda o programa terminar de processar antes de cada acao.\n"
            "     Os tempos gravados viram apenas referencia.\n\n"
            "NAO = Tempo fixo\n"
            "     Reproduz exatamente os intervalos que foram gravados.",
        )
        macro.wait_mode = WAIT_MODE_SMART if usar_inteligente else WAIT_MODE_FIXED
        self.manager.save(macro)
        self._refresh_list(select_name=name)

    def _on_set_hotkey(self) -> None:
        name = self._selected_name()
        if not name:
            return
        macro = self.manager.get(name)
        combo = simpledialog.askstring(
            "Definir Atalho Global",
            "Combinacao (ex: Ctrl+Alt+1). Deixe em branco para remover:",
            initialvalue=macro.hotkey or "",
            parent=self.root,
        )
        if combo is None:
            return
        combo = combo.strip()
        if macro.hotkey:
            self.hotkey_manager.remove_hotkey(normalize_combo(macro.hotkey))
        macro.hotkey = combo or None
        self.manager.save(macro)
        if macro.hotkey:
            self._register_hotkey(macro.name, macro.hotkey)
        self._refresh_list(select_name=name)

    # ---------------------------------------------------------- Atalhos
    def _register_all_hotkeys(self) -> None:
        for name in self.manager.list_macros():
            try:
                macro = self.manager.get(name)
            except Exception:
                continue
            if macro.hotkey:
                self._register_hotkey(name, macro.hotkey)

    def _register_hotkey(self, macro_name: str, combo: str) -> None:
        try:
            normalized = normalize_combo(combo)
            self.hotkey_manager.set_hotkey(normalized, lambda n=macro_name: self._play_by_name(n))
        except Exception:
            pass

    def _play_by_name(self, name: str) -> None:
        # Disparado pela thread de atalho global; agenda no loop principal.
        self.root.after(0, lambda: self._trigger_play(name))

    def _trigger_play(self, name: str) -> None:
        if self.recorder.is_recording or self.player.is_playing:
            return
        if self.tree.exists(name):
            self.tree.selection_set(name)
        self._on_play()

    def _on_close(self) -> None:
        if self.recorder.is_recording:
            self.recorder.stop()
        if self.player.is_playing:
            self.player.stop()
        self.hotkey_manager.stop()
        self.root.destroy()


class MacroEditWindow(tk.Toplevel):
    """Janela para revisar uma macro gravada: lista as acoes em ordem e
    permite remover passos indesejados antes de salvar."""

    def __init__(self, parent, manager: MacroManager, macro: Macro, on_saved=None):
        super().__init__(parent)
        self.title(f"Editar - {macro.name}")
        self.geometry("560x400")
        self.manager = manager
        self.macro = macro
        self.on_saved = on_saved

        columns = ("tipo", "detalhe", "delay")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("detalhe", text="Detalhe")
        self.tree.heading("delay", text="Intervalo (s)")
        self.tree.column("tipo", width=120)
        self.tree.column("detalhe", width=260)
        self.tree.column("delay", width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        ttk.Button(btn_frame, text="Remover Selecionado(s)", command=self._remove_selected).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Salvar", command=self._save).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT, padx=6)

        self._populate()

    def _populate(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for i, ev in enumerate(self.macro.events):
            if ev.type in ("key_down", "key_up"):
                detail = f"Tecla: {ev.key}"
            else:
                detail = f"Botao: {ev.button} em ({ev.x}, {ev.y})"
            self.tree.insert("", tk.END, iid=str(i), values=(ev.type, detail, f"{ev.delay:.3f}"))

    def _remove_selected(self) -> None:
        indices = sorted((int(iid) for iid in self.tree.selection()), reverse=True)
        for i in indices:
            del self.macro.events[i]
        self._populate()

    def _save(self) -> None:
        self.manager.save(self.macro)
        if self.on_saved:
            self.on_saved()
        self.destroy()
