import ctypes
import ctypes.wintypes
import wave
import logging


""" 
record desktop audio
"""

directsound_library = ctypes.windll.LoadLibrary("dsound.dll")
# DSEnumCallback prototype 
ds_enum_callback_prototype = ctypes.WINFUNCTYPE( 
    ctypes.wintypes.BOOL,
    ctypes.wintypes.LPVOID,
    ctypes.wintypes.LPCWSTR,
    ctypes.wintypes.LPCWSTR,
    ctypes.wintypes.LPCVOID,
)


class DirectSound(): 
    class CaptureDevices():
        @classmethod
        def get_devices(cls):
            devices = []
            def cb_enum(lpGUID, lpszDesc, lpszDrvName, _unused):
                dev = ""
                if lpGUID is not None:
                    buf = ctypes.create_unicode_buffer(500)
                    if ctypes.oledll.ole32.StringFromGUID2(
                        ctypes.c_int64(lpGUID), ctypes.byref(buf), 00
                    ):
                        dev = buf.value

                devices.append((dev, lpszDesc, lpszDrvName))
                return True

            directsound_library.DirectSoundEnumerateW(ds_enum_callback_prototype(cb_enum), None)

            return devices


logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    logging.info("done!")
