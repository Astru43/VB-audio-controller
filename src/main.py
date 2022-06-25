import json
import os
from pathlib import Path
import sys
from typing import Callable
from pynput import keyboard
from pynput.keyboard import Key
from win32 import win32gui, win32console
from win32.lib import win32con
from menu_builder import menu_builder
from trayIcon import TrayIcon
from vmwrapper import VoicemeeterWrapper


def _none(*args): pass


def volume_listener(volume_up: Callable[[int], None] = _none, volume_down: Callable[[int], None] = _none) -> keyboard.Listener:
    def on_press(key):
        try:
            match key:
                case Key.media_volume_mute:
                    stop()
                case Key.media_volume_up:
                    volume_up(1)
                case Key.media_volume_down:
                    volume_down(1)
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
    wnd = win32console.GetConsoleWindow()
    cmd: str = os.path.basename(sys.argv[0])
    if cmd.endswith('.exe') and not cmd.startswith('debug_'):
        win32gui.ShowWindow(wnd, win32con.SW_HIDE)


def show():
    wnd = win32console.GetConsoleWindow()
    cmd: str = os.path.basename(sys.argv[0])
    if cmd.endswith('.exe'):
        win32gui.ShowWindow(wnd, win32con.SW_SHOW)


def stop():
    if 'icon' in globals() and icon._running:
        icon.stop()
    if 'listener' in globals() and listener.running:
        listener.stop()


def res_path(res: str) -> str:
    try:
        path = Path(sys._MEIPASS, res)
    except:
        path = Path(res)
    return path


def load_channel(config):
    if config:
        ret = VoicemeeterWrapper.Bus.BUS4
        channel: str = config['channel']
        match channel[0:-1]:
            case 'BUS':
                ret = VoicemeeterWrapper.Bus[channel]
            case 'STRIP':
                ret = VoicemeeterWrapper.Strip[channel]
    else:
        ret = VoicemeeterWrapper.Bus.BUS4
    return ret


def load_config():
    try:
        config = None
        path = Path(os.path.dirname(sys.argv[0]), 'config.json')
        if path.exists():
            with open(path) as file:
                config = json.load(file)
    finally:
        return config


def save_config(config):
    try:
        with open(Path(os.path.dirname(sys.argv[0]), 'config.json'), 'w') as file:
            json.dump(config, file)
    except:
        os.remove(Path('config.json'))


if __name__ == '__main__':
    try:
        config = load_config()
        channel = load_channel(config)
        vm = VoicemeeterWrapper(channel)
        menu = menu_builder(vm, stop)
        icon = TrayIcon("VMR", title='Cunt Muffin', menu=menu,
                        icon=res_path('res/icon_vb_mod.png'))

        vm.login()
        with volume_listener(vm.volume_up, vm.volume_down) as listener:
            icon.run_detached()
            hide()
            listener.join()
    finally:
        show()
        vm.logout()
        stop()
        save_config({'channel': vm.channel.name})
