import base64


def gen_b64_key(c_id: str, c_secret: str) -> str:
    """Function that returns a base64 encoded string

    Args:
        c_id (str): client_id
        c_secret (str): client_secret

    Raises:
        Exception: No Credentials Passed In
        TypeError: c_id and c_secret must be Strings

    Returns:
        str: base64encoded string format -> c_id:c_secret
    """

    if not (c_id or c_secret):
        raise Exception("No Credentials Passed In")

    if not (isinstance(c_id, str) or isinstance(c_secret, str)):
        raise TypeError("Client ID and Client Secret must be Strings")

    access_key = ":".join([c_id, c_secret])
    access_key_bytes = access_key.encode("ascii")
    return base64.b64encode(access_key_bytes).decode("ascii")
