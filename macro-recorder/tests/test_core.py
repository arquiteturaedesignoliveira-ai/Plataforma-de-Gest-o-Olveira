"""Testes das camadas puras (models, storage, macro_manager) que nao
dependem de pynput/tkinter, para poder rodar em qualquer ambiente,
incluindo CI headless.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from models import Macro, MacroEvent, EVENT_KEY_DOWN, EVENT_KEY_UP  # noqa: E402
from storage import MacroStorage, sanitize_filename  # noqa: E402
from macro_manager import MacroManager  # noqa: E402
from keymap import vk_to_name, name_to_vk  # noqa: E402


def test_keymap_letters_and_digits():
    # A tecla fisica M (vk 77) deve virar 'm' e voltar a ser 77, mesmo que
    # o Windows reporte um caractere de controle quando Ctrl esta pressionado.
    assert vk_to_name(77) == "m"
    assert name_to_vk("m") == 77
    assert vk_to_name(74) == "j"
    assert vk_to_name(49) == "1"
    assert name_to_vk("1") == 49


def test_keymap_numpad_and_unknown():
    assert vk_to_name(97) == "num_1"
    assert name_to_vk("num_1") == 97
    assert vk_to_name(107) == "num_add"
    assert vk_to_name(255) is None          # sem nome legivel conhecido
    assert name_to_vk("vk_255") == 255      # mas ainda reproduzivel
    assert name_to_vk("enter") is None      # tecla especial, tratada a parte


def test_macro_roundtrip_json():
    macro = Macro(name="Juntar e Salvar", events=[
        MacroEvent(type=EVENT_KEY_DOWN, delay=0.0, key="ctrl"),
        MacroEvent(type=EVENT_KEY_DOWN, delay=0.01, key="alt"),
        MacroEvent(type=EVENT_KEY_DOWN, delay=0.02, key="j"),
        MacroEvent(type=EVENT_KEY_UP, delay=0.05, key="j"),
        MacroEvent(type=EVENT_KEY_UP, delay=0.01, key="alt"),
        MacroEvent(type=EVENT_KEY_UP, delay=0.01, key="ctrl"),
    ])
    data = macro.to_dict()
    restored = Macro.from_dict(data)
    assert restored.name == macro.name
    assert len(restored.events) == 6
    assert restored.events[2].key == "j"
    assert restored.total_duration() == sum(e.delay for e in macro.events)


def test_sanitize_filename():
    assert sanitize_filename("Publicar PDF") == "Publicar PDF"
    assert sanitize_filename('a/b\\c:d*e?f"g<h>i|j') == "a_b_c_d_e_f_g_h_i_j"


def test_storage_crud():
    with tempfile.TemporaryDirectory() as tmp:
        storage = MacroStorage(Path(tmp))
        macro = Macro(name="Publicar PDF", events=[MacroEvent(type=EVENT_KEY_DOWN, delay=0, key="enter")])
        storage.save(macro, overwrite=False)

        assert storage.exists("Publicar PDF")
        assert storage.list_macro_names() == ["Publicar PDF"]

        loaded = storage.load("Publicar PDF")
        assert loaded.events[0].key == "enter"

        storage.rename("Publicar PDF", "Publicar PDF v2")
        assert not storage.exists("Publicar PDF")
        assert storage.exists("Publicar PDF v2")

        storage.delete("Publicar PDF v2")
        assert storage.list_macro_names() == []


def test_macro_manager_validations():
    with tempfile.TemporaryDirectory() as tmp:
        manager = MacroManager(MacroStorage(Path(tmp)))
        manager.create_empty("Importar Objeto")

        try:
            manager.create_empty("Importar Objeto")
            assert False, "deveria ter levantado FileExistsError"
        except FileExistsError:
            pass

        try:
            manager.create_empty("   ")
            assert False, "deveria ter levantado ValueError"
        except ValueError:
            pass

        macro = manager.get("Importar Objeto")
        macro.events.append(MacroEvent(type=EVENT_KEY_DOWN, delay=0.3, key="enter"))
        manager.save(macro)
        assert len(manager.get("Importar Objeto").events) == 1


if __name__ == "__main__":
    test_keymap_letters_and_digits()
    test_keymap_numpad_and_unknown()
    test_macro_roundtrip_json()
    test_sanitize_filename()
    test_storage_crud()
    test_macro_manager_validations()
    print("OK - todos os testes passaram")
