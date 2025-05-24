from src.services.auth import AuthService


def test_decode_and_encode_tokens():
    data = {"user_id": 1}
    access_token, refresh_token = AuthService().create_tokens(data)

    assert access_token
    assert isinstance(access_token, str)

    assert refresh_token
    assert isinstance(refresh_token, str)


    payload_access = AuthService().decode_access_token(access_token)
    payload_refresh = AuthService().decode_refresh_token(refresh_token)

    assert payload_access, payload_refresh
    assert payload_access["user_id"] == data["user_id"] == payload_refresh["user_id"]

