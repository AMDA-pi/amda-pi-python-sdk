""" This file contains errors associated with API responses."""


class TokenExpiredError(Exception):
    """Error thrown when token has timed out."""

    def __str__(self):
        return "TokenExpiredError: The expiration time has elapsed."


class CallNotFoundError(Exception):
    """Error thrown when Call is not found via UUID"""

    def __str__(self):
        return "CallNotFoundError: Call with supplied UUID does not exist."


class PageOutOfRangeError(Exception):
    """Error thrown when page is out of bounds in Search"""

    def __str__(self):
        return "PageOutOfRangeError: The page supplied is out of bounds."


class InternalServerError(Exception):
    """Error thrown when illegal search_param values are passed in."""

    def __str__(self):
        return "InternalServerError: Internal Server Error. Please check that search_params are of appropriate type."
