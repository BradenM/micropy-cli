# -*- coding: utf-8 -*-

"""Handles Stub Firmwares"""


class Firmware:
    """MicroPython Firmware"""

    _FIRMWARES = {
        "micropython": {
            "name": "MicroPython Official",
            "repo": "micropython/micropython",
            "module_path": "ports/{}/modules"
        },
        "esp32_lobo": {
            "name": "MicroPython ESP32 LoBo",
            "repo": "loboris/MicroPython_ESP32_psRAM_LoBo",
            "module_path": "MicroPython_BUILD/components/micropython\
                /esp32/modules"
        }
    }

    def __init__(self, name, tag, port, **kwargs):
        self.tag = tag
        self.port = port
        firm_info = self._FIRMWARES.get(name, None)
        if firm_info:
            self.__dict__.update(firm_info)
            self.module_path = self.module_path.format(self.port)

    @classmethod
    def from_stub(self, stub, name=None):
        """Get Firmware Instance from Stub"""
        pass
