from src.services.auth import AuthService
import pytest
from unittest import mock
from pydantic_extra_types.phone_numbers import PhoneNumber
from fastapi import Request, Response
from datetime import timedelta, datetime, timezone
import phonenumbers  # Убедимся, что импортирован

from src.schemas.users import (
    PhoneInput,
    EmailInput,
    CodeInput,
    RegistrationInput,
    SetNewPasswordAfterResetInput,
    UserWithHashedPassword,
    User,
)
from src.exceptions.service_exceptions import (
    AuthRateLimitServiceException,
    AuthCodeInvalidServiceException,
    AuthCodeExpiredServiceException,
    UserAlreadyExistsServiceException,
    UserNotFoundAuthServiceException,
    RegistrationValidationServiceException,
    AuthTokenMissingServiceException,
    AuthTokenInvalidServiceException,
    AuthTokenExpiredServiceException,
    AuthCodeNotVerifiedServiceException,
)
from src.exceptions.db_exceptions import UserNotFoundException
from src.dependencies.db import DBDep
from src.utils.db_manager import DBManager
from src.repositories.users import UsersRepository


@pytest.fixture
def auth_service():
    """Фикстура для AuthService с мокнутым Redis."""
    with mock.patch(
        "src.services.auth.redis_manager", new_callable=mock.AsyncMock
    ) as mock_redis_manager:
        service = AuthService()
        service.redis = mock_redis_manager
        return service


@pytest.fixture
def mock_db_dep():
    db_mock = mock.AsyncMock(spec=DBManager)
    users_repo_mock = mock.AsyncMock(spec=UsersRepository)
    users_repo_mock.get_one_or_none.return_value = None
    users_repo_mock.get_one.side_effect = UserNotFoundException()
    users_repo_mock.add.return_value = mock.Mock(spec=User, id=1)
    users_repo_mock.edit.return_value = None
    db_mock.users = users_repo_mock
    db_mock.commit = mock.AsyncMock()
    return db_mock


def test_create_tokens(auth_service: AuthService):
    data = {"id": 1, "is_super_user": False}
    access_token, refresh_token = auth_service.create_tokens(data)
    assert access_token
    assert refresh_token
    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)


@pytest.mark.asyncio
async def test_validate_russian_phone_valid(auth_service: AuthService):
    valid_phones = [
        ("89282017042", "+79282017042"),
        ("+79282017042", "+79282017042"),
        ("9282017042", "+79282017042"),
    ]
    for phone_input, phone_expected_e164 in valid_phones:
        phone_number_obj = await auth_service.validate_russian_phone(phone_input)
        assert isinstance(phone_number_obj, phonenumbers.PhoneNumber)
        assert (
            phonenumbers.format_number(
                phone_number_obj, phonenumbers.PhoneNumberFormat.E164
            )
            == phone_expected_e164
        )


@pytest.mark.asyncio
async def test_validate_russian_phone_invalid(auth_service: AuthService):
    invalid_phones = ["123", "+1234567890", "не телефон"]
    for phone_str in invalid_phones:
        with pytest.raises(AuthCodeInvalidServiceException):
            await auth_service.validate_russian_phone(phone_str)


@pytest.mark.asyncio
async def test_send_phone_code_success(auth_service: AuthService):
    phone_str = "+79991234567"
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    action = "registration"
    auth_service.redis.ttl.return_value = 0
    auth_service.redis.set.return_value = None
    with mock.patch.object(
        auth_service, "test_send_sms", new_callable=mock.AsyncMock
    ) as mock_send_sms:
        result = await auth_service.send_phone_code(parsed_phone_obj, action)
        assert result == {"status": "Ok"}
        expected_e164 = phonenumbers.format_number(
            parsed_phone_obj, phonenumbers.PhoneNumberFormat.E164
        )
        auth_service.redis.ttl.assert_called_once_with(
            f"rate_limit_{action}:{expected_e164}"
        )
        auth_service.redis.set.assert_any_call(
            f"rate_limit_{action}:{expected_e164}", "1", expire=120
        )
        args_list = auth_service.redis.set.call_args_list
        code_set_call = next(
            call for call in args_list if call[0][0] == f"{action}:code:{expected_e164}"
        )
        assert len(code_set_call[0][1]) == 4
        assert code_set_call[1]["expire"] == 120
        mock_send_sms.assert_called_once_with(expected_e164, mock.ANY)


@pytest.mark.asyncio
async def test_send_phone_code_rate_limited(auth_service: AuthService):
    phone_str = "+79991234567"
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    action = "registration"
    auth_service.redis.ttl.return_value = 60
    with pytest.raises(AuthRateLimitServiceException) as exc_info:
        await auth_service.send_phone_code(parsed_phone_obj, action)
    assert "Отправить код снова вы можете не ранее, чем через 60 секунд." in str(
        exc_info.value
    )
    expected_e164 = phonenumbers.format_number(
        parsed_phone_obj, phonenumbers.PhoneNumberFormat.E164
    )
    auth_service.redis.ttl.assert_called_once_with(
        f"rate_limit_{action}:{expected_e164}"
    )


@pytest.mark.asyncio
async def test_send_email_code_success(auth_service: AuthService):
    email_str = "test@example.com"
    action = "registration"
    auth_service.redis.ttl.return_value = 0
    auth_service.redis.set.return_value = None
    with mock.patch.object(
        auth_service, "test_send_mail", new_callable=mock.AsyncMock
    ) as mock_send_mail:
        result = await auth_service.send_email_code(email_str, action)
        assert result == {"status": "Ok"}
        auth_service.redis.ttl.assert_called_once_with(
            f"rate_limit_{action}:{email_str}"
        )
        auth_service.redis.set.assert_any_call(
            f"rate_limit_{action}:{email_str}", "1", expire=120
        )
        args_list = auth_service.redis.set.call_args_list
        assert len(args_list) == 2
        code_set_call = args_list[1]
        assert code_set_call[0][0] == f"{action}:code:{email_str}"
        assert len(code_set_call[0][1]) == 4
        assert code_set_call[1]["expire"] == 120
        mock_send_mail.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_code_rate_limited(auth_service: AuthService):
    email_str = "test@example.com"
    action = "registration"
    auth_service.redis.ttl.return_value = 30
    with pytest.raises(AuthRateLimitServiceException) as exc_info:
        await auth_service.send_email_code(email_str, action)
    assert "Отправить код снова вы можете не ранее, чем через 30 секунд." in str(
        exc_info.value
    )
    auth_service.redis.ttl.assert_called_once_with(f"rate_limit_{action}:{email_str}")


@pytest.mark.asyncio
async def test_send_registration_email_code_new_user(
    auth_service: AuthService, mock_db_dep: DBDep
):
    data = EmailInput(email="new@example.com")
    mock_db_dep.users.get_one_or_none.return_value = None
    auth_service.redis.ttl.return_value = 0
    with mock.patch.object(
        auth_service, "send_email_code", new_callable=mock.AsyncMock
    ) as mock_send_email_code_method:
        mock_send_email_code_method.return_value = {"status": "Ok"}
        result = await auth_service.send_registration_email_code(data, mock_db_dep)
        assert result == {"status": "Ok"}
        mock_db_dep.users.get_one_or_none.assert_called_once_with(email=data.email)
        mock_send_email_code_method.assert_called_once_with(
            data.email, action="registration"
        )


@pytest.mark.asyncio
async def test_send_registration_email_code_existing_user(
    auth_service: AuthService, mock_db_dep: DBDep
):
    data = EmailInput(email="existing@example.com")
    mock_db_dep.users.get_one_or_none.return_value = mock.Mock()
    with pytest.raises(UserAlreadyExistsServiceException):
        await auth_service.send_registration_email_code(data, mock_db_dep)
    mock_db_dep.users.get_one_or_none.assert_called_once_with(email=data.email)


@pytest.mark.asyncio
async def test_send_registration_phone_code_new_user(
    auth_service: AuthService, mock_db_dep: DBDep
):
    phone_str = "+79031234567"
    data = PhoneInput(phone=phone_str)
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    mock_db_dep.users.get_one_or_none.return_value = None
    auth_service.redis.ttl.return_value = 0
    with (
        mock.patch.object(
            auth_service, "validate_russian_phone", return_value=parsed_phone_obj
        ) as mock_validate,
        mock.patch.object(
            auth_service, "send_phone_code", new_callable=mock.AsyncMock
        ) as mock_send_phone_code_method,
    ):
        _ = mock_validate
        mock_send_phone_code_method.return_value = {"status": "Ok"}
        result = await auth_service.send_registration_phone_code(data, mock_db_dep)
        assert result == {"status": "Ok"}
        expected_e164 = phonenumbers.format_number(
            parsed_phone_obj, phonenumbers.PhoneNumberFormat.E164
        )
        mock_db_dep.users.get_one_or_none.assert_called_once_with(phone=expected_e164)
        mock_send_phone_code_method.assert_called_once_with(
            parsed_phone_obj, "registration"
        )


@pytest.mark.asyncio
async def test_send_registration_phone_code_existing_user(
    auth_service: AuthService, mock_db_dep: DBDep
):
    phone_str = "+79031234568"
    data = PhoneInput(phone=phone_str)
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    mock_db_dep.users.get_one_or_none.return_value = mock.Mock()
    with mock.patch.object(
        auth_service, "validate_russian_phone", return_value=parsed_phone_obj
    ) as mock_validate:
        with pytest.raises(UserAlreadyExistsServiceException):
            await auth_service.send_registration_phone_code(data, mock_db_dep)
        mock_validate.assert_called_once_with("tel:+7-903-123-45-68")
        expected_e164 = phonenumbers.format_number(
            parsed_phone_obj, phonenumbers.PhoneNumberFormat.E164
        )
        mock_db_dep.users.get_one_or_none.assert_called_once_with(phone=expected_e164)


@pytest.mark.asyncio
async def test_send_reset_phone_code_user_exists(
    auth_service: AuthService, mock_db_dep: DBDep
):
    phone_str = "+79031234569"
    data = PhoneInput(phone=phone_str)
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    mock_db_dep.users.get_one.side_effect = None
    mock_db_dep.users.get_one.return_value = mock.Mock(id=1)
    auth_service.redis.ttl.return_value = 0
    with (
        mock.patch.object(
            auth_service, "validate_russian_phone", return_value=parsed_phone_obj
        ) as mock_validate,
        mock.patch.object(
            auth_service, "send_phone_code", new_callable=mock.AsyncMock
        ) as mock_send_phone_code_method,
    ):
        mock_send_phone_code_method.return_value = {"status": "Ok"}
        result = await auth_service.send_reset_phone_code(data, mock_db_dep)
        assert result == {"status": "Ok"}
        mock_validate.assert_called_once_with("tel:+7-903-123-45-69")
        expected_e164 = phonenumbers.format_number(
            parsed_phone_obj, phonenumbers.PhoneNumberFormat.E164
        )
        mock_db_dep.users.get_one.assert_called_once_with(phone=expected_e164)
        mock_send_phone_code_method.assert_called_once_with(parsed_phone_obj, "reset")


@pytest.mark.asyncio
async def test_send_reset_phone_code_user_not_found(
    auth_service: AuthService, mock_db_dep: DBDep
):
    phone_str = "+79031234510"
    data = PhoneInput(phone=phone_str)
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    mock_db_dep.users.get_one.side_effect = UserNotFoundException()
    with mock.patch.object(
        auth_service, "validate_russian_phone", return_value=parsed_phone_obj
    ) as mock_validate:
        with pytest.raises(UserNotFoundAuthServiceException):
            await auth_service.send_reset_phone_code(data, mock_db_dep)
        mock_validate.assert_called_once_with("tel:+7-903-123-45-10")
        expected_e164 = phonenumbers.format_number(
            parsed_phone_obj, phonenumbers.PhoneNumberFormat.E164
        )
        mock_db_dep.users.get_one.assert_called_once_with(phone=expected_e164)


@pytest.mark.asyncio
async def test_verify_code_phone_success(auth_service: AuthService):
    phone_str = "+79031112233"
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    code_to_verify = 1234  # Передаем int
    action = "registration"
    stored_code_on_redis = "1234"
    auth_service.redis.get.return_value = stored_code_on_redis.encode("utf-8")
    auth_service.redis.set.return_value = None
    # Передаем code_to_verify (int) вместо объекта CodeInput
    result = await auth_service.verify_code_phone(
        parsed_phone_obj, code_to_verify, action
    )
    assert result == {"status": "Код подтверждён"}
    expected_e164 = phonenumbers.format_number(
        parsed_phone_obj, phonenumbers.PhoneNumberFormat.E164
    )
    auth_service.redis.get.assert_called_once_with(f"{action}:code:{expected_e164}")
    auth_service.redis.set.assert_called_once_with(
        f"{action}:code_verified:{expected_e164}", "true", expire=300
    )


@pytest.mark.asyncio
async def test_verify_code_phone_invalid_code(auth_service: AuthService):
    phone_str = "+79031112244"
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    code_input_val = 1234  # Валидное значение для CodeInput
    stored_code_on_redis = "5678"  # Код, который якобы сохранен в Redis (не совпадает)
    auth_service.redis.get.return_value = stored_code_on_redis.encode("utf-8")

    with pytest.raises(
        AuthCodeInvalidServiceException, match="Неверный код подтверждения"
    ):
        # Передаем значение, а не объект CodeInput, если функция ожидает int
        await auth_service.verify_code_phone(
            parsed_phone_obj, code_input_val, "registration"
        )


@pytest.mark.asyncio
async def test_verify_code_phone_code_not_found(auth_service: AuthService):
    phone_str = "+79031112255"
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    code_input = CodeInput(code="1234")
    action = "registration"
    auth_service.redis.get.return_value = None
    with pytest.raises(AuthCodeExpiredServiceException):
        await auth_service.verify_code_phone(parsed_phone_obj, code_input, action)
    expected_e164 = phonenumbers.format_number(
        parsed_phone_obj, phonenumbers.PhoneNumberFormat.E164
    )
    auth_service.redis.get.assert_called_once_with(f"{action}:code:{expected_e164}")


@pytest.mark.asyncio
async def test_verify_registration_phone_success(
    auth_service: AuthService, mock_db_dep: DBDep
):
    phone_str = "+79998887766"
    data = RegistrationInput(
        phone=phone_str,
        phone_code=1234,  # Используем phone_code
        password="PasswordValid8!",
        password_repeat="PasswordValid8!",  # Добавляем password_repeat
    )
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    auth_service.redis.get.return_value = b"true"  # Мокаем, что код верифицирован
    mock_db_dep.users.get_one_or_none.return_value = None  # Пользователя нет
    mock_db_dep.users.add.return_value = User(
        id=1, is_super_user=False, phone=PhoneNumber(phone_str), email=None
    )

    with (
        mock.patch.object(
            auth_service, "validate_russian_phone", return_value=parsed_phone_obj
        ),
        mock.patch.object(  # noqa: F841
            auth_service, "verify_code_phone"
        ) as mock_verify_code_phone,
        mock.patch.object(
            auth_service, "delete_verified_phone_code"
        ) as mock_delete_code,
    ):
        mock_verify_code_phone.return_value = {
            "status": "Код подтверждён"
        }  # Мокаем успешную верификацию

        result = await auth_service.verify_registration(data, mock_db_dep)
        assert result == {"status": "OK, user created"}
        mock_verify_code_phone.assert_called_once_with(
            mock.ANY, data.phone_code, "registration"
        )
        mock_db_dep.users.add.assert_called_once()
        mock_delete_code.assert_called_once()


@pytest.mark.asyncio
async def test_verify_registration_user_already_exists_phone(
    auth_service: AuthService, mock_db_dep: DBDep
):
    phone_str = "+79991112233"
    data = RegistrationInput(
        phone=phone_str,
        phone_code=1234,  # Используем phone_code
        password="PasswordValid8!",
        password_repeat="PasswordValid8!",  # Добавляем password_repeat
    )
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    mock_db_dep.users.get_one_or_none.return_value = User(
        id=1, is_super_user=False, phone=PhoneNumber(phone_str)
    )  # Пользователь существует

    with mock.patch.object(
        auth_service, "validate_russian_phone", return_value=parsed_phone_obj
    ) as mock_validate:
        with pytest.raises(UserAlreadyExistsServiceException):
            await auth_service.verify_registration(data, mock_db_dep)
        mock_validate.assert_called_once_with(data.phone)


@pytest.mark.asyncio
async def test_verify_registration_code_verification_fails_phone(
    auth_service: AuthService, mock_db_dep: DBDep
):
    phone_str = "+79001234567"
    data = RegistrationInput(
        phone=phone_str,
        phone_code=9999,  # Используем phone_code, пусть будет неверный для логики теста
        password="PasswordValid8!",
        password_repeat="PasswordValid8!",  # Добавляем password_repeat
    )
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    mock_db_dep.users.get_one_or_none.return_value = None  # Пользователя нет

    with (
        mock.patch.object(
            auth_service, "validate_russian_phone", return_value=parsed_phone_obj
        ) as mock_validate,
        mock.patch.object(
            auth_service,
            "verify_code_phone",
            side_effect=AuthCodeInvalidServiceException(detail="Test error"),
        ) as mock_verify_code_phone,
    ):
        _ = mock_validate
        with pytest.raises(
            RegistrationValidationServiceException,
            match="Ошибка верификации телефона: Test error",
        ):
            await auth_service.verify_registration(data, mock_db_dep)
        mock_verify_code_phone.assert_called_once_with(
            mock.ANY, data.phone_code, "registration"
        )


@pytest.fixture
def mock_request_with_token():
    def _mock_request_with_token(
        access_token_val: str | None, refresh_token_val: str | None
    ):
        request_mock = mock.AsyncMock(spec=Request)

        def get_cookie(name):
            if name == "access_token":
                return access_token_val
            if name == "refresh_token":
                return refresh_token_val
            return None

        request_mock.cookies.get = get_cookie
        return request_mock

    return _mock_request_with_token


@pytest.fixture
def mock_response_obj():
    return mock.AsyncMock(spec=Response)


@pytest.mark.asyncio
async def test_get_current_user_payload_success_access_token(
    auth_service: AuthService, mock_request_with_token, mock_response_obj: Response
):
    user_id = 10
    user_payload_dict = {
        "sub": str(user_id),
        "id": user_id,
        "is_super_user": False,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    request_mock = mock_request_with_token("fake_access_token", None)
    with (
        mock.patch.object(
            auth_service, "decode_access_token", return_value=user_payload_dict
        ) as mock_decode_access,
        mock.patch.object(auth_service, "decode_refresh_token") as mock_decode_refresh,
    ):
        payload_dict_result = await auth_service.get_current_user_payload(
            request_mock, mock_response_obj
        )
        assert payload_dict_result == user_payload_dict
        mock_decode_access.assert_called_once_with("fake_access_token")
        mock_decode_refresh.assert_not_called()


@pytest.mark.asyncio
async def test_get_current_user_payload_success_refresh_token(
    auth_service: AuthService, mock_request_with_token, mock_response_obj: Response
):
    user_id = 11
    refresh_payload_dict = {
        "sub": str(user_id),
        "id": user_id,
        "is_super_user": True,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    request_mock = mock_request_with_token(
        "expired_or_invalid_access", "fake_refresh_token"
    )
    with (
        mock.patch.object(
            auth_service,
            "decode_access_token",
            side_effect=AuthTokenExpiredServiceException(token_type="Access"),
        ) as mock_decode_access,
        mock.patch.object(
            auth_service, "decode_refresh_token", return_value=refresh_payload_dict
        ) as mock_decode_refresh,
    ):
        payload_dict_result = await auth_service.get_current_user_payload(
            request_mock, mock_response_obj
        )
        assert payload_dict_result == refresh_payload_dict
        mock_decode_access.assert_called_once_with("expired_or_invalid_access")
        mock_decode_refresh.assert_called_once_with("fake_refresh_token")


@pytest.mark.asyncio
async def test_get_current_user_payload_access_token_absent_refresh_absent(
    auth_service: AuthService, mock_request_with_token, mock_response_obj: Response
):
    request_mock = mock_request_with_token(None, None)
    with pytest.raises(AuthTokenMissingServiceException) as exc_info:
        await auth_service.get_current_user_payload(request_mock, mock_response_obj)
    assert exc_info.value.token_type == "Access"


@pytest.mark.asyncio
async def test_get_current_user_payload_access_expired_refresh_absent(
    auth_service: AuthService, mock_request_with_token, mock_response_obj: Response
):
    request_mock = mock_request_with_token("fake_expired_access_token", None)
    with (
        mock.patch.object(
            auth_service,
            "decode_access_token",
            side_effect=AuthTokenExpiredServiceException(token_type="Access"),
        ) as mock_decode_access,
        pytest.raises(AuthTokenMissingServiceException) as exc_info,
    ):
        await auth_service.get_current_user_payload(request_mock, mock_response_obj)
    mock_decode_access.assert_called_once_with("fake_expired_access_token")
    assert exc_info.value.token_type == "Refresh"


@pytest.mark.asyncio
async def test_get_current_user_payload_access_expired_refresh_expired(
    auth_service: AuthService, mock_request_with_token, mock_response_obj: Response
):
    request_mock = mock_request_with_token("fake_access_token", "fake_refresh_token")
    with (
        mock.patch.object(
            auth_service,
            "decode_access_token",
            side_effect=AuthTokenExpiredServiceException(token_type="Access"),
        ) as mock_decode_access,
        mock.patch.object(
            auth_service,
            "decode_refresh_token",
            side_effect=AuthTokenExpiredServiceException(token_type="Refresh"),
        ) as mock_decode_refresh,
        pytest.raises(AuthTokenExpiredServiceException) as exc_info,
    ):
        await auth_service.get_current_user_payload(request_mock, mock_response_obj)
    mock_decode_access.assert_called_once_with("fake_access_token")
    mock_decode_refresh.assert_called_once_with("fake_refresh_token")
    assert exc_info.value.token_type == "Refresh"


@pytest.mark.asyncio
async def test_get_current_user_payload_access_invalid_no_refresh(
    auth_service: AuthService, mock_request_with_token, mock_response_obj: Response
):
    request_mock = mock_request_with_token("invalid_access_token", None)
    with (
        mock.patch.object(
            auth_service,
            "decode_access_token",
            side_effect=AuthTokenInvalidServiceException(token_type="Access"),
        ) as mock_decode_access,
        pytest.raises(AuthTokenInvalidServiceException) as exc_info,
    ):
        await auth_service.get_current_user_payload(request_mock, mock_response_obj)
    mock_decode_access.assert_called_once_with("invalid_access_token")
    assert exc_info.value.token_type == "Access"


@pytest.mark.asyncio
async def test_get_current_user_payload_access_expired_refresh_invalid(
    auth_service: AuthService, mock_request_with_token, mock_response_obj: Response
):
    request_mock = mock_request_with_token("fake_access_token", "invalid_refresh_token")
    with (
        mock.patch.object(
            auth_service,
            "decode_access_token",
            side_effect=AuthTokenExpiredServiceException(token_type="Access"),
        ) as mock_decode_access,
        mock.patch.object(
            auth_service,
            "decode_refresh_token",
            side_effect=AuthTokenInvalidServiceException(token_type="Refresh"),
        ) as mock_decode_refresh,
        pytest.raises(AuthTokenInvalidServiceException) as exc_info,
    ):
        await auth_service.get_current_user_payload(request_mock, mock_response_obj)
    mock_decode_access.assert_called_once_with("fake_access_token")
    mock_decode_refresh.assert_called_once_with("invalid_refresh_token")
    assert exc_info.value.token_type == "Refresh"


# Тест для AuthService.verify_code_phone (action="reset") - Успех
@pytest.mark.asyncio
async def test_verify_reset_code_phone_success(auth_service: AuthService):
    phone_str = "+79112223344"
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    code_to_verify = 1234  # Передаем int
    action = "reset"
    stored_code_on_redis = "1234"
    auth_service.redis.get.return_value = stored_code_on_redis.encode("utf-8")
    auth_service.redis.set.return_value = None

    # Передаем code_to_verify (int) вместо объекта CodeInput
    result = await auth_service.verify_code_phone(
        parsed_phone_obj, code_to_verify, action
    )
    assert result == {"status": "Код подтверждён"}
    expected_e164 = phonenumbers.format_number(
        parsed_phone_obj, phonenumbers.PhoneNumberFormat.E164
    )
    auth_service.redis.get.assert_called_once_with(f"reset:code:{expected_e164}")
    auth_service.redis.set.assert_called_once_with(
        f"reset:code_verified:{expected_e164}", "true", expire=300
    )


# Тест для AuthService.verify_code_phone (action="reset") - Неверный код
@pytest.mark.asyncio
async def test_verify_reset_code_phone_invalid(auth_service: AuthService):
    phone_str = "+79001234500"
    parsed_phone_obj = phonenumbers.parse(phone_str, "RU")
    code_input_val = 1234  # Валидное значение
    stored_code_on_redis = "0000"  # Невалидный или несовпадающий код в Redis
    auth_service.redis.get.return_value = stored_code_on_redis.encode("utf-8")

    with pytest.raises(
        AuthCodeInvalidServiceException, match="Неверный код подтверждения"
    ):
        # Передаем значение, а не объект CodeInput
        await auth_service.verify_code_phone(parsed_phone_obj, code_input_val, "reset")


# Тест для AuthService.set_password_after_reset - Успех (телефон)
@pytest.mark.asyncio
async def test_set_new_password_after_reset_phone_success(
    auth_service: AuthService, mock_db_dep: DBDep
):
    phone_str_input = "tel:+7-955-555-44-33"
    phone_str_e164 = "+79555554433"
    new_password = "newStrongPassword1!"
    # Добавляем new_password_repeat
    data = SetNewPasswordAfterResetInput(
        phone=phone_str_input,
        new_password=new_password,
        new_password_repeat=new_password,  # Добавляем new_password_repeat
    )
    parsed_phone_obj = phonenumbers.parse(phone_str_input, None)
    mock_user_instance = UserWithHashedPassword(
        id=1,
        phone=PhoneNumber(phone_str_e164),
        email=None,
        hashed_password="old_hash",
        is_super_user=False,
    )

    auth_service.redis.get.return_value = b"true"  # Мокаем, что код верифицирован
    # Сначала сбрасываем side_effect, установленный в фикстуре mock_db_dep
    mock_db_dep.users.get_one.side_effect = None
    # Теперь устанавливаем return_value, чтобы пользователь был найден
    mock_db_dep.users.get_one.return_value = mock_user_instance
    mock_db_dep.users.edit.return_value = None

    with (
        mock.patch.object(
            auth_service, "validate_russian_phone", return_value=parsed_phone_obj
        ) as mock_validate,
        mock.patch.object(
            auth_service, "validate_password_strength"
        ) as mock_validate_pass,
        mock.patch.object(
            auth_service, "hash_password", return_value="new_hashed_password"
        ) as mock_hash_pass,
        mock.patch.object(auth_service.redis, "delete") as mock_redis_delete,
    ):
        result = await auth_service.set_password_after_reset(data, mock_db_dep)

        assert result == {"status": "OK, password has been reset"}
        mock_validate.assert_called_once_with(str(data.phone))
        mock_validate_pass.assert_called_once_with(new_password)
        mock_hash_pass.assert_called_once_with(new_password)
        mock_db_dep.users.get_one.assert_called_once_with(phone=phone_str_e164)
        mock_db_dep.users.edit.assert_called_once()

        # Проверяем удаление ключей из Redis
        expected_key_verified = f"reset:code_verified:{phone_str_e164}"
        expected_key_code = f"reset:code:{phone_str_e164}"
        mock_redis_delete.assert_any_call(expected_key_verified)
        mock_redis_delete.assert_any_call(expected_key_code)


# Тест для AuthService.set_password_after_reset - Код не верифицирован
@pytest.mark.asyncio
async def test_set_new_password_after_reset_code_not_verified(
    auth_service: AuthService, mock_db_dep: DBDep
):
    phone_str_input = "tel:+7-955-555-44-34"
    phone_str_e164 = "+79555554434"
    new_password = "newStrongPassword1!"
    # Добавляем new_password_repeat
    data = SetNewPasswordAfterResetInput(
        phone=phone_str_input,
        new_password=new_password,
        new_password_repeat=new_password,  # Добавляем new_password_repeat
    )
    parsed_phone_obj = phonenumbers.parse(phone_str_input, None)
    auth_service.redis.get.return_value = None  # Код не верифицирован

    with mock.patch.object(
        auth_service, "validate_russian_phone", return_value=parsed_phone_obj
    ) as mock_validate:
        with pytest.raises(AuthCodeNotVerifiedServiceException):
            await auth_service.set_password_after_reset(data, mock_db_dep)
        mock_validate.assert_called_once_with(str(data.phone))
        auth_service.redis.get.assert_called_once_with(
            f"reset:code_verified:{phone_str_e164}"
        )


# Конец тестов для AuthService
