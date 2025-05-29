class MadRussianException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(MadRussianException):
    detail = "Объект не найден"


class ReviewNotFoundException(ObjectNotFoundException):
    detail = "Отзыв не найден"


class UserNotFoundException(ObjectNotFoundException):
    detail = "Пользователь не найден"


class PurchaseNotFoundException(ObjectNotFoundException):
    detail = "Покупка не найдена"


class ProductNotFoundException(ObjectNotFoundException):
    detail = "Продукт не найден"
