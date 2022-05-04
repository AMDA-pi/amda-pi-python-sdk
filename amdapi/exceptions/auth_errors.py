"""This file contains errors associated with the authorization endpoint."""


class AuthorizationError(Exception):
    """General error thrown to deal with specifying errors invoked during authorization."""

    ERRORS = {
        405: "Invalid Auth Endpoint. Please Upgrade Package",
        400: "Invalid Client Credentials. Check your AMDAPI_ID & AMDAPI_SECRET",
        401: "Bad Token, ReAuthenticate the Client.",
    }

    def __init__(self, status_code, reason):
        super().__init__()
        self.status_code = status_code
        self.reason = reason

    def __repr__(self):
        return f"{self.status_code}: {self.ERRORS.get(self.status_code,self.reason)}"

    def __str__(self):
        return f"{self.status_code}: {self.ERRORS.get(self.status_code,self.reason)}"
