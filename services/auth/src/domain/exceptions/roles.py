from .base import DomainError


class RoleRequestAlreadyExistsError(DomainError):
    def __init__(self):
        super().__init__("Активная заявка на роль уже существует.")


class RoleRequestNotFoundError(DomainError):
    def __init__(self, request_id: int | None = None):
        self.request_id = request_id
        msg = f"Заявка на роль {request_id} не найдена." if request_id else "Заявка на роль не найдена."
        super().__init__(msg)


class RoleRequestAlreadyProcessedError(DomainError):
    def __init__(self, request_id: int | None = None):
        self.request_id = request_id
        msg = f"Заявка на роль {request_id} уже обработана." if request_id else "Заявка на роль уже обработана."
        super().__init__(msg)
