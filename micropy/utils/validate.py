# -*- coding: utf-8 -*-

"""
micropy.utils.validate
~~~~~~~~~~~~~~

This module contains utility functions for MicropyCli
that center on data validation
"""

import json
from pathlib import Path

from jsonschema import Draft7Validator


class Validator:
    """"jsonschema wrapper for file validation.

    Returns:
        object: Validator Instance

    """

    def __init__(self, schema_path):
        schema = self._load_json(schema_path)
        self.schema = Draft7Validator(schema)

    def _load_json(self, path):
        """Loads json data from file.

        Args:
            path (str): path to file

        Returns:
            Loaded JSON data as an array or dict

        """
        file = Path(path).resolve()
        data = json.load(file.open())
        return data

    def validate(self, path):
        """Validates json file against a schema.

        Args:
            path (str): path to json file to validate

        Returns:
            jsonschema.validate

        """
        data = self._load_json(path)
        return self.schema.validate(data)
