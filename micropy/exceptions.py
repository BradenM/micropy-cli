# -*- coding: utf-8 -*-

"""Micropy Exceptions"""


class StubError(Exception):
    """Exception for any errors raised by stubs"""

    def __init__(self, stub=None, message=None):
        self.stub = stub
        self.message = message
        if message is None:
            message = "An error occured with this stub."


class StubValidationError(StubError):
    """Raised when a stub fails validation"""

    def __init__(self, path, errors, *args, **kwargs):
        errs = '\n'.join(errors)
        msg = (f"Stub at[{str(path)}] encountered"
               f" the following validation errors: {errs}")
        super().__init__(message=msg, *args, **kwargs)

    def __str__(self):
        return self.message
