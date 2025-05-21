from src.api.auth import refresh_token
from src.services.auth import AuthService


def test_create_tokens():
    data = {"user_id": 1}
    access_token, refresh_token = AuthService().create_tokens(data)

    assert access_token, refresh_token
    assert isinstance(access_token, str), isinstance(refresh_token, str)
