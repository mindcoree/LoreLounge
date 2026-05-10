"""
Перечисления (enums) для домена auth.

READER
    читает новеллы
    сохраняет в библиотеку
    комментирует
    ставит оценки
    базовый пользователь

AUTHOR
    публикует оригинальные новеллы
    управляет своими главами
    видит статистику

TRANSLATOR
    переводит главы
    может работать с AI-переводами
    отправляет на проверку

MODERATOR
    удаляет комментарии
    банит пользователей
    проверяет переводы/главы

ADMIN
    всё выше
    управление ролями
    системные настройки
"""

from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    READER = "reader"
    AUTHOR = "author"
    TRANSLATOR = "translator"
    MODERATOR = "moderator"


class DesiredRole(str, Enum):
    """Роли, на которые можно подать заявку при регистрации."""
    READER = "reader"
    AUTHOR = "author"
    TRANSLATOR = "translator"
    MODERATOR = "moderator"


class RoleRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
