import os
from pathlib import Path
import sys
from typing import Callable
from pynput import keyboard
from pynput.keyboard import Key
from win32 import win32gui
from win32.lib import win32con
from trayIcon import TrayIcon
from vmwrapper import VoicemeeterWrapper


def _none(*args): pass


def volume_listener(volume_up: Callable[[int], None] = _none,
                    volume_down: Callable[[int], None] = _none,
                    restart_engine: Callable[[], None] = _none,
                    ) -> keyboard.Listener:
    def on_press(key):
        try:
            match key:
                case Key.media_volume_mute:
                    listener.stop()
                    icon.stop()
                case Key.media_volume_up:
                    volume_up(1)
                case Key.media_volume_down:
                    volume_down(1)
                case Key.f24:
                    restart_engine()
        except AttributeError:
            print('Error {0}'.format(key))

    def win32_event_filter(msg, data):
        if data.vkCode in [Key.media_volume_up.value.vk, Key.media_volume_down.value.vk, Key.media_volume_mute.value.vk]:
            listener._suppress = True
        else:
            listener._suppress = False

    listener = keyboard.Listener(
        on_press=on_press,
        win32_event_filter=win32_event_filter
    )

    return listener


def hide():
    wnd = win32gui.GetForegroundWindow()
    wnd_title = win32gui.GetWindowText(wnd)
    if os.path.basename(wnd_title) == "main.exe":
        win32gui.ShowWindow(wnd, win32con.SW_HIDE)


def stop():
    listener.stop()
    icon.stop()


def res_path(res: str) -> str:
    try:
        path = Path(sys._MEIPASS, res)
    except:
        path = Path(res)
    return path


if __name__ == '__main__':
    try:
        vm = VoicemeeterWrapper(VoicemeeterWrapper.Bus.BUS4)
        icon = TrayIcon("VMR", stop=stop, icon=res_path('res/icon_vb_mod.png'))

        vm.login()
        with volume_listener(vm.volume_up, vm.volume_down, vm.restart_engine) as listener:
            icon.run_detached()
            hide()
            listener.join()
    finally:
        stop()
        vm.logout()
