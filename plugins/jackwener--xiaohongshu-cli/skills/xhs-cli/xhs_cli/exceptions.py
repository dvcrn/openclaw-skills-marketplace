"""Custom exceptions for xhs-cli."""


class XhsError(Exception):
    """Base exception for xhs-cli."""


class DataFetchError(XhsError):
    """Failed to fetch data from page."""


class LoginError(XhsError):
    """Login failed."""


class CookieError(XhsError):
    """Cookie extraction or validation failed."""
