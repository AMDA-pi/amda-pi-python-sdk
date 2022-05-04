from typing import List

"""This file contains package wide default configurations
    """
# AMDAPi Endpoints
ENDPOINT_CLIENT_AUTH: str = "https://auth.api-amdapi.com/oauth2/token"
ENDPOINT_GET_CALLS: str = "https://api-amdapi.com/v1/calls/"
ENDPOINT_GET_CALL_W_UUID: str = ENDPOINT_GET_CALLS + "{uuid}"
ENDPOINT_GET_STORAGE: str = "https://api-amdapi.com/amda-pi-storage/"

CLIENT_ID_ENV_NAME: str = "AMDAPI-CLIENT-ID"
CLIENT_SECRET_ENV_NAME: str = "AMDAPI-CLIENT-SECRET"

# Current Analysis Defaults
ANALYSIS_LANGUAGES: List[str] = ["en", "en-in", "fr"]
ANALYSIS_ORIGINS: List[str] = ["Inbound", "Outbound"]

# ReAuth Decorator Defaults
REAUTH_SAFETY: int = 120
