class MadRussianServiceException(Exception):
    status_code = 500
    detail = "Неожиданная ошибка"

    def __init__(self):
        super().__init__(self.detail)

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