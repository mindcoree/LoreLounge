class LoreLoungeError(Exception):
    """Базовое исключение для всего проекта."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DomainError(LoreLoungeError):
    """Базовое исключение для домена."""
    pass
