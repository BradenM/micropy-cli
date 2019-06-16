# -*- coding: utf-8 -*-

"""Handles Stub Firmwares"""

import re


class Firmware:
    """MicroPython Firmware"""

    _FIRMWARES = {
        "micropython": {
            "name": "MicroPython Official",
            "repo": "micropython/micropython",
            "module_path": "ports/{}/modules",
        },
        "esp32_lobo": {
            "name": "MicroPython ESP32 LoBo",
            "repo": "loboris/MicroPython_ESP32_psRAM_LoBo",
            "module_path": "MicroPython_BUILD/components/micropython\
                /esp32/modules"
        }
    }
    # TODO: Confirm sysnames
    _SUPPORTED = frozenset(["esp32", "esp8266", "pyb", "teensy", "nrf"])

    def __init__(self, name, tag, port, **kwargs):
        self.tag = tag
        self.port = port
        firm_info = self._FIRMWARES.get(name, None)
        if firm_info:
            self.__dict__.update(firm_info)
            self.module_path = self.module_path.format(self.port)

    @classmethod
    def from_stub(cls, stub, name=None):
        """Get Firmware Instance from Stub"""
        if not name:
            # TODO: Add prompt here / add find by tag here
            return None
        vreg = re.compile(r"\d\.\d\.\d")
        _tag = iter(vreg.findall(stub.version))
        # TODO: Open PR on createstubs.py to use sys.implementation for version
        tag = next(_tag, 'latest')
        _port_attrs = ['machine', 'sysname', 'nodename']
        _port_ids = [getattr(stub, a).lower().strip() for a in _port_attrs]
        port_ids = set([item for sublist in _port_ids for item in _port_ids])
        port = list(cls._SUPPORTED.intersection(port_ids))[0]
        return cls(name, tag=tag, port=port)
