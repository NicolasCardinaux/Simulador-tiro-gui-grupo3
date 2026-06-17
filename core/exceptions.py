class MiddlewareError(Exception):
    """Base exception for Grupo 2 middleware errors."""


class MessageValidationError(MiddlewareError, ValueError):
    """Raised when a message does not satisfy the middleware contract."""


class SerializationError(MiddlewareError, ValueError):
    """Raised when a message cannot be serialized or deserialized."""


class UnsupportedMessageTypeError(MessageValidationError):
    """Raised when a message type is not supported by the middleware."""
