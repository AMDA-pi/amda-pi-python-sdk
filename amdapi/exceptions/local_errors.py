""" This file contains errors associated with retrieving the credentials from the local environment"""

from ..configs.default_configs import CLIENT_ID_ENV_NAME, CLIENT_SECRET_ENV_NAME


class CredentialsNotFoundError(Exception):
    """Error thrown when credentials not found in the correct location in local environment."""

    def __str__(self):
        return f"""
CredentialsNotFoundError: Credentials not found in local environment.
    Credentials required:
        {CLIENT_ID_ENV_NAME}
        {CLIENT_SECRET_ENV_NAME}
Make sure to initialize the credentials in the local environment, or pass them into Client(amdapi_id,amdapi_secret)
    """
