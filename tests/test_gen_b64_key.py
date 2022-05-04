import pytest
from amdapi.utils.functions import gen_b64_key


def test_correct_input():
    client_id = "client_id"
    client_secret = "client_secret"
    expected = "Y2xpZW50X2lkOmNsaWVudF9zZWNyZXQ="

    assert gen_b64_key(client_id, client_secret) == expected


def test_no_input():
    client_id = ""
    client_secret = ""

    with pytest.raises(Exception) as e_info:
        gen_b64_key(client_id, client_secret)

    assert str(e_info.value) == "No Credentials Passed In"


def test_bad_input():
    client_id = 1
    client_secret = 2

    with pytest.raises(Exception) as e_info:
        gen_b64_key(client_id, client_secret)
    assert str(e_info.value) == "Client ID and Client Secret must be Strings"
