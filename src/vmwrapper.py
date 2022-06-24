from enum import Enum
from os import path
import sys
from threading import Lock, Thread, Timer
from time import sleep
from typing import Union
import winreg
import ctypes
from ctypes import c_char_p, c_float, byref, POINTER


class VoicemeeterWrapper:
    _self_update = False
    _quit = False
    _lock = Lock()
    connected = False
    volume = c_float()
    ref_volume = byref(volume)

    def __init__(self, channel: Union['Bus', 'Strip']) -> None:
        self.channel = channel.value
        if sys.maxsize > 2**32:
            self.voicemeeterDll = 'VoicemeeterRemote64.dll'
        else:
            self.voicemeeterDll = 'VoicemeeterRemote.dll'
        regPath = r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\VB:Voicemeeter {17359A74-1236-5467}'
        try:
            handle = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, regPath)
            self.voicemeeterPath = path.dirname(
                winreg.QueryValueEx(handle, 'UninstallString')[0]
            )
            self.lib = ctypes.CDLL(
                path.join(self.voicemeeterPath, self.voicemeeterDll)
            )
        except OSError as err:
            print('Failed to get VoicemeeterRemote.dll')
            raise err
        else:
            self.lib.VBVMR_GetParameterFloat.argtypes = [
                c_char_p, POINTER(c_float)
            ]
            self.lib.VBVMR_SetParameterFloat.argtypes = [c_char_p, c_float]

            def update(*args, **kwargs):
                while True:
                    sleep(.02)
                    try:
                        if self._lock.locked():
                            continue
                        self._lock.acquire()
                        if self._quit:
                            return
                        elif self.connected:
                            if self._isParametersDirty() > 0:
                                if self._self_update:
                                    self._self_update = False
                                    continue
                                self.getParameterFloat(
                                    self.channel + b'.Gain',
                                    self.ref_volume
                                )
                    finally:
                        if self._lock.locked():
                            self._lock.release()
            self.updater = Thread(target=update)

    def _isParametersDirty(self):
        return self.lib.VBVMR_IsParametersDirty()

    def getParameterFloat(self, param: bytes, pValue: c_float):
        self.lib.VBVMR_GetParameterFloat(param, pValue)

    def setParameterFloat(self, param: bytes, value: c_float):
        self.lib.VBVMR_SetParameterFloat(param, value)

    def login(self):
        ret = self.lib.VBVMR_Login()
        if ret < 0:
            raise Exception('Error Loging in voicemeeter')
        else:
            self.connected = True
            comError = self._isParametersDirty()
            if comError >= 0:
                self.getParameterFloat(
                    self.channel + b'.Gain',
                    self.ref_volume
                )
                print(self.volume)
            self.updater.start()

    def logout(self):
        self._lock.acquire()
        self._quit = True
        self.connected = False
        self.lib.VBVMR_Logout()
        self._lock.release()

    def volume_up(self, value: int):
        try:
            self._lock.acquire()
            if self.connected:
                if self.volume.value < 12:
                    self.volume.value += value
                print(self.volume)
                self.setParameterFloat(self.channel + b'.Gain', self.volume)
                self._self_update = True
        finally:
            if self._lock.locked():
                self._lock.release()

    def volume_down(self, value: int):
        try:
            self._lock.acquire()
            if self.connected:
                if self.volume.value > -60:
                    self.volume.value -= value
                print(self.volume)
                self.setParameterFloat(self.channel + b'.Gain', self.volume)
                self._self_update = True
        finally:
            if self._lock.locked():
                self._lock.release()

    def set_channel(self, channel: Union['Bus', 'Strip']):
        self.channel = channel
        self.getParameterFloat(self._gain, self.ref_volume)

    class Strip(Enum):
        STRIP0 = b'Strip[0]'
        STRIP1 = b'Strip[1]'
        STRIP2 = b'Strip[2]'
        STRIP3 = b'Strip[3]'
        STRIP4 = b'Strip[4]'
        STRIP5 = b'Strip[5]'
        STRIP6 = b'Strip[6]'
        STRIP7 = b'Strip[7]'

    class Bus(Enum):
        BUS0 = b'Bus[0]'
        BUS1 = b'Bus[1]'
        BUS2 = b'Bus[2]'
        BUS3 = b'Bus[3]'
        BUS4 = b'Bus[4]'
        BUS5 = b'Bus[5]'
        BUS6 = b'Bus[6]'
        BUS7 = b'Bus[7]'
