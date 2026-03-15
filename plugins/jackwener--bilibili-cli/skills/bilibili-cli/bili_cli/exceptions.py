"""Custom exceptions for bilibili-cli."""


class BiliError(Exception):
    """Base exception for bilibili-cli errors."""


class InvalidBvidError(BiliError):
    """Raised when a BV ID cannot be parsed or is malformed."""


class NetworkError(BiliError):
    """Raised when upstream network/API requests fail."""


class AuthenticationError(BiliError):
    """Raised when authentication data is missing or invalid."""
