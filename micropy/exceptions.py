# -*- coding: utf-8 -*-

"""Micropy Exceptions"""


class StubError(Exception):
    """Exception for any errors raised by stubs"""

    def __init__(self, stub, message=None):
        self.stub = stub
        self.message = message
        if message is None:
            message = "An error occured with this stub."


class StubValidationError(StubError):
    """Raised when a stub fails validation"""

    def __init__(self, stub, errors):
        errs = '\n'.join(errors)
        msg = f"Stub at [{stub.path}] encountered \
            the following validation errors: {errs}"
        super().__init__(stub, message=msg)

    def __str__(self):
        return self.message
