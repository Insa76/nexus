import pyautogui
import time
import pyperclip


def register(registry):
    registry["type_text"] = type_text


def type_text(text):

    time.sleep(1)  # te da tiempo a enfocar

    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")

    return "Texto escrito"
