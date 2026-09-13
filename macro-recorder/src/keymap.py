"""Conversao entre teclas do pynput e a representacao em texto salva no
JSON da macro.

Grava-se sempre a TECLA FISICA, nao o caractere resultante. Isso e
essencial no Windows: com Ctrl pressionado, o pynput reporta um caractere
de controle (Ctrl+M -> '\\r'), o que faria a macro reproduzir Enter no
lugar da tecla M. Usando o virtual-key code, 'ctrl+shift+m' e gravado e
reproduzido exatamente como a tecla M.

As funcoes de tabela (vk_to_name / name_to_vk) nao dependem do pynput,
para poderem ser testadas em qualquer ambiente; o import do pynput e
feito apenas dentro das funcoes de conversao.
"""
from __future__ import annotations

from typing import Optional

# Teclas do teclado numerico e outras que merecem um nome legivel.
_VK_NAMES = {
    **{96 + i: f"num_{i}" for i in range(10)},
    106: "num_multiply",
    107: "num_add",
    109: "num_subtract",
    110: "num_decimal",
    111: "num_divide",
}
_NAME_VKS = {name: vk for vk, name in _VK_NAMES.items()}


def vk_to_name(vk: Optional[int]) -> Optional[str]:
    """Nome legivel e estavel para um virtual-key code do Windows."""
    if vk is None:
        return None
    if vk in _VK_NAMES:
        return _VK_NAMES[vk]
    if 65 <= vk <= 90:      # A-Z -> 'a'..'z' (a tecla fisica, sem shift)
        return chr(vk).lower()
    if 48 <= vk <= 57:      # 0-9
        return chr(vk)
    return None


def name_to_vk(name: str) -> Optional[int]:
    """Inverso de vk_to_name."""
    if name in _NAME_VKS:
        return _NAME_VKS[name]
    if len(name) == 1:
        if "a" <= name <= "z":
            return ord(name.upper())
        if "0" <= name <= "9":
            return ord(name)
    if name.startswith("vk_"):
        try:
            return int(name[3:])
        except ValueError:
            return None
    return None


def key_to_str(key) -> str:
    """Converte uma tecla capturada pelo pynput em texto para o JSON."""
    from pynput import keyboard

    if not isinstance(key, keyboard.KeyCode):
        # keyboard.Key.* (ctrl_l, alt_l, shift, enter, esc, f1, ...)
        return key.name

    name = vk_to_name(key.vk)
    if name is not None:
        return name

    char = key.char
    # Caracteres de controle (ord < 32) aparecem quando Ctrl esta pressionado
    # e nao identificam a tecla fisica: preferimos o vk nesse caso.
    if char is not None and ord(char) >= 32:
        return char
    if key.vk is not None:
        return f"vk_{key.vk}"
    return "desconhecida"


def str_to_key(name: str):
    """Converte o texto salvo no JSON de volta para uma tecla do pynput."""
    from pynput import keyboard

    special = {k.name: k for k in keyboard.Key}
    if name in special:
        return special[name]

    vk = name_to_vk(name)
    if vk is not None:
        return keyboard.KeyCode(vk=vk)

    return keyboard.KeyCode.from_char(name)
