"""Micropy Exceptions."""


class MicropyException(Exception):
    """Generic MicroPy Exception."""


class StubError(MicropyException):
    """Exception for any errors raised by stubs."""

    def __init__(self, message=None, stub=None):
        super().__init__(message)
        self.stub = stub
        self.message = message
        if message is None:
            message = "An error occurred with this stub."


class StubValidationError(StubError):
    """Raised when a stub fails validation."""

    def __init__(self, path, errors, *args, **kwargs):
        msg = f"Stub at[{str(path)}] encountered" f" the following validation errors: {str(errors)}"
        super().__init__(message=msg, *args, **kwargs)

    def __str__(self):
        return self.message


class StubNotFound(StubError):
    """Raised when a stub cannot be found."""

    def __init__(self, stub_name=None):
        stub_name = stub_name or "Unknown"
        msg = f"{stub_name} is not available!"
        super().__init__(msg)


class RequirementException(MicropyException):
    """A Requirement Exception Occurred."""

    def __init__(self, *args, **kwargs):
        self.package = kwargs.pop("package", None)
        super().__init__(*args, **kwargs)


class RequirementNotFound(RequirementException):
    """A requirement could not be found."""


class PyDeviceError(MicropyException):
    """Generic PyDevice exception."""

    def __init__(self, message: str = None):
        super().__init__(message)
        self.message = message


class PyDeviceConnectionError(PyDeviceError):
    _default_message = "Failed to connect to pydevice @ {location}."

    def __init__(self, location: str):
        super().__init__(self._default_message.format(location=location))
