""" This file contains classes and functions that contribute to creating a client, to interface with the ADMAPi API"""

from __future__ import annotations

import functools
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BufferedReader
from typing import Dict, Tuple

import requests

from ..configs import (
    ANALYSIS_LANGUAGES,
    ANALYSIS_ORIGINS,
    CLIENT_ID_ENV_NAME,
    CLIENT_SECRET_ENV_NAME,
    ENDPOINT_CLIENT_AUTH,
    ENDPOINT_GET_CALL_W_UUID,
    ENDPOINT_GET_CALLS,
    ENDPOINT_GET_STORAGE,
    REAUTH_SAFETY,
)
from ..exceptions.api_errors import (
    CallNotFoundError,
    InternalServerError,
    PageOutOfRangeError,
    TokenExpiredError,
)
from ..exceptions.auth_errors import AuthorizationError
from ..exceptions.local_errors import CredentialsNotFoundError
from ..utils.audio import get_audio_objects, is_stereo
from ..utils.functions import gen_b64_key
from .call import Call
from .search_result import SearchResult


@dataclass(frozen=True)
class Token:
    """
    Simple Class for Storing Client JWT Token
    """

    value: str
    last_refresh: datetime
    expiration: datetime


# Refresh Token Decorator
def _refresh_token(func):
    functools.wraps(func)

    def __refresh_token(self: Client, *args, **kwargs):
        if datetime.now() >= self.get_token_expiry() - timedelta(seconds=REAUTH_SAFETY):
            self.authenticate()

        try:
            ret = func(self, *args, **kwargs)
        except TokenExpiredError:
            self.authenticate()
            ret = func(self, *args, **kwargs)
        return ret

    return __refresh_token


class Client:
    def __init__(self, amdapi_id: str = None, amdapi_secret: str = None):

        # Check Arguments, if not passed get Local Environment Arguments
        if amdapi_id is None or amdapi_secret is None:
            try:
                amdapi_id = os.environ[CLIENT_ID_ENV_NAME]
                amdapi_secret = os.environ[CLIENT_SECRET_ENV_NAME]
            except KeyError:
                raise CredentialsNotFoundError() from KeyError

        self.__client_id = amdapi_id
        # Generating Bearer Key Based on Credentials
        self.__b64_key = gen_b64_key(amdapi_id, amdapi_secret)

        # Generating Initial Token For Accessing AMDAPI API
        self.__token: Token
        self.authenticate()

    def authenticate(self):
        """This method is used authenticate the client's private token.
        No return

        Raises:
            AuthorizationError: Errors will include bad responses from the Authorization Endpoint
        """
        params = {"grant_type": "client_credentials"}
        headers = {
            "Authorization": f"Basic {self.__b64_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(
            url=ENDPOINT_CLIENT_AUTH, params=params, headers=headers
        )

        # Bad Response Raise AuthorizationError
        if response.status_code != 200:
            raise AuthorizationError(response.status_code, response.reason)

        # Good Response
        response_json = response.json()
        value = f"{response_json['token_type']} {response_json['access_token']}"
        last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expiration = datetime.now() + timedelta(
            seconds=int(response_json["expires_in"])
        )

        self.__token = Token(value, last_refresh, expiration)

    def get_token_expiry(self) -> datetime:
        """Simple Getter Function for Token Expiration.

        Returns:
            datetime: The expiration of the token.
        """
        return self.__token.expiration

    @_refresh_token
    def get_call(self, uuid: str) -> Call:
        """Retrives a call via UUID from the AMDAPi Backend.

        Args:
            uuid (str): Unique Identifier generated by the AMDAPI Backend assigned to a call.

        Raises:
            CallNotFoundError: UUID provided does not match any calls.
            Exception: Any other errors raised by the backend, including 500's.

        Returns:
            Call: A call object containing information retrieved from AMDAPi.
        """
        # Initialise API Request Structure
        url = ENDPOINT_GET_CALL_W_UUID.format(uuid=uuid)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self.__token.value,
        }

        # Send Synchronous Request
        response = requests.get(url, headers=headers)
        if response.status_code == 401:  # Token Expired
            raise TokenExpiredError()
        elif response.status_code == 404:  # Call Not Found
            raise CallNotFoundError()
        elif response.status_code != 200:  # Other Errors (e.g. Internal Errors)
            raise Exception(f"{response.status_code}: {response.reason}")
        else:
            return Call.parse_call(response)

    @_refresh_token
    def search_calls(
        self,
        page_number: int = None,
        agent_id: int = None,
        client_id: int = None,
        start_date: str | datetime = None,
        end_date: str | datetime = None,
    ) -> SearchResult:
        """Allows the client to search for calls whilst supplying search filters.

        Args:
            page_number (int, optional): Pagination Number if search results in > 350 calls. Defaults to None.
            agent_id (int, optional): Agent ID used internally (Supplied when call is initially analyzed). Defaults to None.
            client_id (int, optional): Client ID used internally (Supplied when call is initially analyzed). Defaults to None.
            start_date (str | datetime, optional): Date to start searching for calls. Defaults to None.
            end_date (str | datetime, optional): Date to stop searching for calls. Defaults to None.

        Raises:
            PageOutOfRangeError: If page number supplied exceeds the number of search results.
            InternalServerError: Error raised when the search filters provided do not match the required format.
            Exception: Will contain any other errors that may be raised, due to server errors etc.

        Returns:
            SearchResult: Object containing the search results, as well as the seearch params used that resulted in the search results.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self.__token.value,
        }

        # Converts DateTime type to Correct Formated String
        if isinstance(start_date, datetime):
            start_date = start_date.strftime("%d/%m/%Y")
        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%d/%m/%Y")

        params = {
            "page_number": int(page_number) if page_number else None,
            "agent_id": int(agent_id) if agent_id else None,
            "client_id": int(client_id) if client_id else None,
            "start_date": str(start_date) if start_date else None,
            "end_date": str(end_date) if end_date else None,
        }

        response = requests.get(url=ENDPOINT_GET_CALLS, headers=headers, params=params)

        if response.status_code == 401:  # Token Expired
            raise TokenExpiredError()
        elif (
            response.status_code == 500
            and response.json().get("success", None) == "false"
        ):  # Page out of Bounds Error
            raise PageOutOfRangeError()
        elif response.status_code == 500:  # Page out of Bounds Error
            raise InternalServerError()
        elif response.status_code != 200:  # Other Errors (e.g. Internal Errors)
            raise Exception(f"{response.status_code}: {response.reason}")
        else:
            return SearchResult.parse_search_results(response, params)

    @_refresh_token
    def delete_call(self, uuid: str) -> str:
        """WARNING: This method is destructive and irreversible.
        Function used to delete a call from the AMDAPi Servers.

        Args:
            uuid (str): Unique Identifier generated by the AMDAPI Backend assigned to a call.

        Raises:
            CallNotFoundError: UUID provided does not match any calls.
            Exception: Any other errors raised by the backend, including 500's.

        Returns:
            str: Contains a message that will be displayed when the call has been successful.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self.__token.value,
        }

        response = requests.delete(
            url=ENDPOINT_GET_CALL_W_UUID.format(uuid=uuid), headers=headers
        )

        # Check for valid response to parse into Call Object
        if response.status_code == 404:
            raise CallNotFoundError()
        elif response.status_code == 401:
            raise Exception(f"{response.status_code}: {response.reason}")
        else:
            return response.json()["data"].title()

    def analyze_call(
        self,
        audio_buffer: BufferedReader,
        filename: str,
        call_id: str,
        client_id: int,
        agent_id: int,
        customer_id: int,
        origin="",
        language="",
        summary: bool = False,
        agent_channel: int = None,
    ) -> Call:
        """This function allows you to send an audio file (.wav) to AMDAPi for analysis.

        Args:
            audio (BufferedReader): Audio file for analysis.
            filename (str): filename of the audio file, from your database.
            call_id (str): Identifying Call ID number, from your database.
            client_id (int): Identifying Client ID number, from your database (NOT YOUR AMDAPI Client_ID).
            agent_id (int): Identifying Agent ID number, from your database.
            customer_id (int): Identifying Customer ID number, from your database.
            origin (str): [Inbound/Outbound]. Defaults to "".
            language (str): [en/en-in/fr]. Defaults to "".
            summary (bool): Whether or not you would like a summary of the call to also be included in the analysis. Defaults to False.
            agent_channel (int): Index of the channel that the agent is on (Required for stereo audio only).

        Raises:
            ValueError: Raised when invalid options are passed to 'origin' and 'language'.
            Exception: Handles any exceptions raised when attempting to upload the file to AMDAPi storage location.

        Returns:
            Call: Returns a Call Object that will have contain all the params included as well as the newly generated UUID.
        """

        origin = origin.strip().title()
        if origin not in ANALYSIS_ORIGINS:
            raise ValueError(f"Invalid option for origin. Options: {ANALYSIS_ORIGINS}")

        language = language.strip().lower()
        if language not in ANALYSIS_LANGUAGES:
            raise ValueError(
                f"Invalid option for language. Options: {ANALYSIS_LANGUAGES}"
            )

        call_info = {
            "filename": str(filename),
            "call_id": str(call_id),
            "client_id": int(client_id),
            "agent_id": int(agent_id),
            "customer_id": str(customer_id),
            "origin": str(origin),
            "language": str(language),
            "summary": bool(summary),
        }

        audio_bytes, audio_object = get_audio_objects(audio_buffer)

        if isinstance(agent_channel, int) and (agent_channel in [0, 1]):
            if is_stereo(audio_object):
                call_info["agent_channel"] = int(agent_channel)
            else:
                print(f"{filename} is not a stereo file. agent_channel ignored!")
        else:
            raise IndexError("Agent Channel Out of Range. Allowed Values: [0,1]")

        # Retrieve S3 URL and Call_UUID
        upload_location, call_info["call_uuid"] = self.__get_s3_url(call_info)

        # Try to Upload
        try:
            self.__upload_to_s3(audio_bytes, upload_location)
        except Exception as exc:
            self.delete_call(call_info["call_uuid"])
            raise Exception from exc

        return Call.parse_call(call_info)

    @_refresh_token
    def __get_s3_url(self, call_info: Dict[str, str]) -> Tuple[str, str]:
        """Internal Function for retrieveing S3 Url for file upload.

        Args:
            call_info (Dict[str, str]): Call info passed in for creating table entries for

        Raises:
            TokenExpiredError: Will trigger Reauthorization
            Exception: Other Exceptions caught.

        Returns:
            Tuple[str, str]: [UploadURL, CallUID]
        """

        # Initializing Headers retrieving Signed Bucket URL
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self.__token.value,
        }

        response = requests.post(
            url=ENDPOINT_GET_STORAGE,
            headers=headers,
            data=json.dumps(call_info),
        )

        if response.status_code == 401:
            raise TokenExpiredError()
        elif response.status_code != 200:
            raise Exception(f"{response.status_code}: {response.reason}")
        else:
            return response.json()["data"]["url"], response.json()["data"]["call_uuid"]

    def __upload_to_s3(self, audio_file: BufferedReader, storage_url: str) -> None:
        """Internal function for uploading audio file to backend.

        Args:
            audio_file (BufferedReader): File for upload (must be .wav)
            storage_url (str): Presigned URL for file upload

        Raises:
            Exception: Any exceptions that may be raised during upload.
        """
        headers_audio = {"Content-Type": "audio/wav", "x-amz-acl": "public-read"}
        response = requests.put(storage_url, data=audio_file, headers=headers_audio)

        if response.status_code == 200 and "etag" in response.headers:
            pass
        else:
            raise Exception(f"{response.status_code}: {response.reason}")

    def __repr__(self):
        return f"< amdapi.Client | ClientID: {self.__client_id} | Last Token Refresh: {self.__token.last_refresh} >"
