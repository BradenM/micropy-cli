# -*- coding: utf-8 -*-

import json
from pathlib import Path

from jsonschema import Draft7Validator


class Validator:
    """jsonschema wrapper for file validation"""

    def __init__(self, schema_path):
        schema = self._load_json(schema_path)
        self.schema = Draft7Validator(schema)

    def _load_json(self, path):
        """get file object"""
        file = Path(path).resolve()
        data = json.load(file.open())
        return data

    def validate(self, path):
        """validate file"""
        data = self._load_json(path)
        return self.schema.validate(data)
