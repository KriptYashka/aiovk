from typing import Optional, Dict, Any

from aiohttp import ClientResponseError


class VKAPIError(ClientResponseError):
    """
    Базовый класс для всех ошибок VK API.

    Актуально для v.5.199
    """

    def __init__(
            self,
            request_info: Optional[Any] = None,
            history: Optional[tuple] = None,
            *,
            code: int = 0,
            message: str = "",
            headers: Optional[Dict[str, str]] = None,
            vk_error_code: Optional[int] = None,
            vk_error_msg: Optional[str] = None
    ):
        # Если это ошибка VK API, используем её код и сообщение
        if vk_error_code is not None:
            code = vk_error_code
            message = vk_error_msg or self._get_default_message(vk_error_code)

        super().__init__(request_info, history, status=code, message=message, headers=headers)
        self.vk_error_code = vk_error_code or code

    @staticmethod
    def _get_default_message(error_code: int) -> str:
        """Возвращает сообщение по умолчанию для кода ошибки VK"""
        default_messages = {
            1: "Произошла неизвестная ошибка. Попробуйте повторить запрос позже.",
            2: "Приложение выключено. Необходимо включить приложение в настройках https://vk.com/editapp?id={Ваш API_ID} или использовать тестовый режим (test_mode=1)",
            3: "Передан неизвестный метод. Проверьте, правильно ли указано название вызываемого метода: vk.com/dev/methods.",
            4: "Неверная подпись.",
            5: "Авторизация пользователя не удалась. Убедитесь, что Вы используете верную схему авторизации.",
            6: "Слишком много запросов в секунду. Задайте больший интервал между вызовами или используйте метод execute. Подробнее об ограничениях на частоту вызовов см. на странице vk.com/dev/api_requests.",
            7: "Нет прав для выполнения этого действия. Проверьте, получены ли нужные права доступа при авторизации. Это можно сделать с помощью метода account.getAppPermissions.",
            8: "Неверный запрос. Проверьте синтаксис запроса и список используемых параметров (его можно найти на странице с описанием метода).",
            9: "Слишком много однотипных действий. Нужно сократить число однотипных обращений. Для более эффективной работы Вы можете использовать execute или JSONP.",
            10: "Произошла внутренняя ошибка сервера. Попробуйте повторить запрос позже.",
            11: "В тестовом режиме приложение должно быть выключено или пользователь должен быть залогинен. Выключите приложение в настройках https://vk.com/editapp?id={Ваш API_ID}",
            14: "Требуется ввод кода с картинки (Captcha). Процесс обработки этой ошибки подробно описан на отдельной странице.",
            15: "Доступ запрещён. Убедитесь, что Вы используете верные идентификаторы, и доступ к контенту для текущего пользователя есть в полной версии сайта.",
            16: "Требуется выполнение запросов по протоколу HTTPS, т.к. пользователь включил настройку, требующую работу через безопасное соединение. Чтобы избежать появления такой ошибки, в Standalone-приложении Вы можете предварительно проверять состояние этой настройки у пользователя методом account.getInfo.",
            17: "Требуется валидация пользователя. Действие требует подтверждения — необходимо перенаправить пользователя на служебную страницу для валидации.",
            18: "Страница удалена или заблокирована. Страница пользователя была удалена или заблокирована.",
            20: "Данное действие запрещено для не Standalone приложений. Если ошибка возникает несмотря на то, что Ваше приложение имеет тип Standalone, убедитесь, что при авторизации Вы используете redirect_uri=https://oauth.vk.com/blank.html. Подробнее см. vk.com/dev/auth_mobile.",
            21: "Данное действие разрешено только для Standalone и Open API приложений.",
            23: "Метод был выключен. Все актуальные методы ВК API, которые доступны в настоящий момент, перечислены здесь: vk.com/dev/methods.",
            24: "Требуется подтверждение со стороны пользователя.",
            27: "Ключ доступа сообщества недействителен.",
            28: "Ключ доступа приложения недействителен.",
            29: "Достигнут количественный лимит на вызов метода. Подробнее об ограничениях на количество вызовов см. на странице.",
            30: "Профиль является приватным. Информация, запрашиваемая о профиле, недоступна с используемым ключом доступа.",
            100: "Один из необходимых параметров был не передан или неверен. Проверьте список требуемых параметров и их формат на странице с описанием метода.",
            101: "Неверный API ID приложения. Найдите приложение в списке администрируемых на странице http://vk.com/apps?act=settings и укажите в запросе верный API_ID (идентификатор приложения).",
            113: "Неверный идентификатор пользователя. Убедитесь, что Вы используете верный идентификатор. Получить ID по короткому имени можно методом utils.resolveScreenName.",
            150: "Неверный timestamp. Получить актуальное значение Вы можете методом utils.getServerTime.",
            200: "Доступ к альбому запрещён. Убедитесь, что Вы используете верные идентификаторы (для пользователей owner_id положительный, для сообществ — отрицательный), и доступ к запрашиваемому контенту для текущего пользователя есть в полной версии сайта.",
            201: "Доступ к аудио запрещён. Убедитесь, что Вы используете верные идентификаторы (для пользователей owner_id положительный, для сообществ — отрицательный), и доступ к запрашиваемому контенту для текущего пользователя есть в полной версии сайта.",
            203: "Доступ к группе запрещён. Убедитесь, что текущий пользователь является участником или руководителем сообщества (для закрытых и частных групп и встреч).",
            300: "Альбом переполнен. Перед продолжением работы нужно удалить лишние объекты из альбома или использовать другой альбом.",
            500: "Действие запрещено. Вы должны включить переводы голосов в настройках приложения. Проверьте настройки приложения: https://vk.com/editapp?id={Ваш API_ID}&section=payments",
            600: "Нет прав на выполнение данных операций с рекламным кабинетом.",
            603: "Произошла ошибка при работе с рекламным кабинетом.",
        }
        return default_messages.get(error_code, f"Неизвестная ошибка VK API (код {error_code})")


# Специализированные классы для каждой ошибки VK API
class VKUnknownError(VKAPIError):
    """Ошибка 1: Неизвестная ошибка"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=1, **kwargs)


class VKAppDisabledError(VKAPIError):
    """Ошибка 2: Приложение выключено"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=2, **kwargs)


class VKMethodNotFoundError(VKAPIError):
    """Ошибка 3: Неизвестный метод"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=3, **kwargs)


class VKInvalidSignatureError(VKAPIError):
    """Ошибка 4: Неверная подпись"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=4, **kwargs)


class VKAuthError(VKAPIError):
    """Ошибка 5: Ошибка авторизации"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=5, **kwargs)


class VKRateLimitError(VKAPIError):
    """Ошибка 6: Слишком много запросов"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=6, **kwargs)


class VKPermissionError(VKAPIError):
    """Ошибка 7: Нет прав"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=7, **kwargs)


class VKInvalidRequestError(VKAPIError):
    """Ошибка 8: Неверный запрос"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=8, **kwargs)


class VKTooManyActionsError(VKAPIError):
    """Ошибка 9: Слишком много однотипных действий"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=9, **kwargs)


class VKServerError(VKAPIError):
    """Ошибка 10: Внутренняя ошибка сервера"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=10, **kwargs)


class VKTestModeError(VKAPIError):
    """Ошибка 11: Ошибка тестового режима"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=11, **kwargs)


class VKCaptchaError(VKAPIError):
    """Ошибка 14: Требуется капча"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=14, **kwargs)


class VKAccessDeniedError(VKAPIError):
    """Ошибка 15: Доступ запрещён"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=15, **kwargs)


class VKHTTPSRequiredError(VKAPIError):
    """Ошибка 16: Требуется HTTPS"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=16, **kwargs)


class VKValidationRequiredError(VKAPIError):
    """Ошибка 17: Требуется валидация"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=17, **kwargs)


class VKPageDeletedError(VKAPIError):
    """Ошибка 18: Страница удалена"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=18, **kwargs)


class VKNonStandaloneError(VKAPIError):
    """Ошибка 20: Действие запрещено для не Standalone приложений"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=20, **kwargs)


class VKStandaloneOnlyError(VKAPIError):
    """Ошибка 21: Только для Standalone и Open API"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=21, **kwargs)


class VKMethodDisabledError(VKAPIError):
    """Ошибка 23: Метод выключен"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=23, **kwargs)


class VKUserConfirmationError(VKAPIError):
    """Ошибка 24: Требуется подтверждение пользователя"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=24, **kwargs)


class VKInvalidCommunityTokenError(VKAPIError):
    """Ошибка 27: Недействительный ключ сообщества"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=27, **kwargs)


class VKInvalidAppTokenError(VKAPIError):
    """Ошибка 28: Недействительный ключ приложения"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=28, **kwargs)


class VKMethodLimitError(VKAPIError):
    """Ошибка 29: Лимит на вызов метода"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=29, **kwargs)


class VKPrivateProfileError(VKAPIError):
    """Ошибка 30: Приватный профиль"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=30, **kwargs)


class VKMissingParameterError(VKAPIError):
    """Ошибка 100: Отсутствует параметр"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=100, **kwargs)


class VKInvalidAppIdError(VKAPIError):
    """Ошибка 101: Неверный API ID"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=101, **kwargs)


class VKInvalidUserIdError(VKAPIError):
    """Ошибка 113: Неверный ID пользователя"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=113, **kwargs)


class VKInvalidTimestampError(VKAPIError):
    """Ошибка 150: Неверный timestamp"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=150, **kwargs)


class VKAlbumAccessError(VKAPIError):
    """Ошибка 200: Доступ к альбому запрещён"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=200, **kwargs)


class VKAudioAccessError(VKAPIError):
    """Ошибка 201: Доступ к аудио запрещён"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=201, **kwargs)


class VKGroupAccessError(VKAPIError):
    """Ошибка 203: Доступ к группе запрещён"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=203, **kwargs)


class VKAlbumFullError(VKAPIError):
    """Ошибка 300: Альбом переполнен"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=300, **kwargs)


class VKVoicesDisabledError(VKAPIError):
    """Ошибка 500: Переводы голосов выключены"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=500, **kwargs)


class VKAdsPermissionError(VKAPIError):
    """Ошибка 600: Нет прав на операции с рекламой"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=600, **kwargs)


class VKAdsError(VKAPIError):
    """Ошибка 603: Ошибка рекламного кабинета"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, vk_error_code=603, **kwargs)


# Словарь для маппинга кодов ошибок на классы исключений
VK_ERROR_MAPPING = {
    1: VKUnknownError,
    2: VKAppDisabledError,
    3: VKMethodNotFoundError,
    4: VKInvalidSignatureError,
    5: VKAuthError,
    6: VKRateLimitError,
    7: VKPermissionError,
    8: VKInvalidRequestError,
    9: VKTooManyActionsError,
    10: VKServerError,
    11: VKTestModeError,
    14: VKCaptchaError,
    15: VKAccessDeniedError,
    16: VKHTTPSRequiredError,
    17: VKValidationRequiredError,
    18: VKPageDeletedError,
    20: VKNonStandaloneError,
    21: VKStandaloneOnlyError,
    23: VKMethodDisabledError,
    24: VKUserConfirmationError,
    27: VKInvalidCommunityTokenError,
    28: VKInvalidAppTokenError,
    29: VKMethodLimitError,
    30: VKPrivateProfileError,
    100: VKMissingParameterError,
    101: VKInvalidAppIdError,
    113: VKInvalidUserIdError,
    150: VKInvalidTimestampError,
    200: VKAlbumAccessError,
    201: VKAudioAccessError,
    203: VKGroupAccessError,
    300: VKAlbumFullError,
    500: VKVoicesDisabledError,
    600: VKAdsPermissionError,
    603: VKAdsError,
}


def create_vk_error(
        error_code: int,
        error_msg: Optional[str] = None,
        request_info: Optional[Any] = None,
        history: Optional[tuple] = None,
        headers: Optional[Dict[str, str]] = None
) -> VKAPIError:
    """
    Фабрика для создания соответствующего класса исключения по коду ошибки

    Args:
        error_code: Код ошибки VK API
        error_msg: Сообщение об ошибке (опционально)
        request_info: Информация о запросе aiohttp
        history: История редиректов aiohttp
        headers: Заголовки ответа

    Returns:
        Соответствующий класс исключения
    """
    error_class = VK_ERROR_MAPPING.get(error_code, VKAPIError)
    return error_class(
        request_info=request_info,
        history=history,
        vk_error_msg=error_msg,
        headers=headers
    )
