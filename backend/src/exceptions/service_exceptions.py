class MadRussianServiceException(Exception):
    status_code = 500
    detail = "Неожиданная ошибка"

    def __init__(self, detail: str | None = None):
        super().__init__(detail or self.detail)
        if detail is not None:
            self.detail = detail

class ReviewNotFoundServiceException(MadRussianServiceException):
    status_code = 404
    detail = "Отзыв не найден"

class ReviewWrongFormatServiceException(MadRussianServiceException):
    status_code = 400
    detail = "Неверный формат: продукты должны быть только ОГЭ или ЕГЭ"

class ReviewIsExistingServiceException(MadRussianServiceException):
    status_code = 409
    detail = "Отзыв уже существует"

class ReviewNoRightsServiceException(MadRussianServiceException):
    status_code = 403
    detail = "Нет прав на работу с этим отзывом"

class UserNotFoundServiceException(MadRussianServiceException):
    status_code = 404
    detail = "Пользователь не найден"

class PurchaseNotFoundServiceException(MadRussianServiceException):
    status_code = 404
    detail = "Покупка не найдена"

class WebhookWrongFormatServiceException(MadRussianServiceException):
    status_code = 400
    detail = "Неверный формат: отсутствует id"

class ProductNotFoundServiceException(MadRussianServiceException):
    status_code = 404
    detail = "Продукт не найден"

class ReviewEditConflictServiceException(MadRussianServiceException):
    status_code = 409
    def __init__(self, detail: str):
        super().__init__(detail=detail)

class AdminNoRightsServiceException(MadRussianServiceException):
    status_code = 403
    detail = "Нет прав администратора для этого действия"

class PaymentValidationServiceException(MadRussianServiceException):
    status_code = 400
    def __init__(self, detail: str):
        super().__init__(detail=detail)

class PaymentAlreadyCreatedServiceException(MadRussianServiceException):
    status_code = 400
    detail = "Платеж уже создан"

class PaymentAlreadyPaidServiceException(MadRussianServiceException):
    status_code = 409
    detail = "Платеж уже оплачен"

class YooKassaServiceException(MadRussianServiceException):
    status_code = 500
    def __init__(self, detail: str):
        super().__init__(detail=detail)

class ProductNotPurchasedServiceException(MadRussianServiceException):
    status_code = 404
    detail = "Продукт не куплен или доступ отсутствует"

class AuthRateLimitServiceException(MadRussianServiceException):
    status_code = 429
    def __init__(self, detail: str):
        super().__init__(detail=detail)

class UserAlreadyExistsServiceException(MadRussianServiceException):
    status_code = 409
    detail = "Пользователь с такими данными уже существует"

class UserNotFoundAuthServiceException(MadRussianServiceException):
    status_code = 404
    detail = "Пользователь не найден"

class AuthCodeInvalidServiceException(MadRussianServiceException):
    status_code = 400
    detail = "Неверный код подтверждения"

class AuthCodeExpiredServiceException(MadRussianServiceException):
    status_code = 400
    detail = "Код подтверждения не найден или истёк"

class AuthPasswordsNotMatchServiceException(MadRussianServiceException):
    status_code = 400
    detail = "Пароли не совпадают"

class AuthCodeNotVerifiedServiceException(MadRussianServiceException):
    status_code = 403
    detail = "Код не подтверждён или устарел"

class AuthPasswordTooWeakServiceException(MadRussianServiceException):
    status_code = 400
    detail = "Пароль должен быть не менее 8 символов, содержать цифру, заглавную букву и специальный символ"

class AuthTokenMissingServiceException(MadRussianServiceException):
    status_code = 401
    def __init__(self, token_type: str = "Access"):
        self.token_type = token_type
        detail = f"{token_type} токен не найден"
        super().__init__(detail=detail)

class AuthTokenExpiredServiceException(MadRussianServiceException):
    status_code = 401
    def __init__(self, token_type: str = "Access"):
        self.token_type = token_type
        detail = f"{token_type} токен истёк"
        super().__init__(detail=detail)

class AuthTokenInvalidServiceException(MadRussianServiceException):
    status_code = 401
    def __init__(self, token_type: str = "Access"):
        self.token_type = token_type
        detail = f"Невалидный {token_type} токен"
        super().__init__(detail=detail)

class RegistrationValidationServiceException(MadRussianServiceException):
    status_code = 400
    def __init__(self, detail: str):
        super().__init__(detail=detail)

class ResetPasswordValidationServiceException(MadRussianServiceException):
    status_code = 400
    def __init__(self, detail: str):
        super().__init__(detail=detail)

class IncorrectPasswordServiceException(MadRussianServiceException):
    status_code = 400
    detail = "Неверный текущий пароль"