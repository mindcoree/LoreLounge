from abc import ABC, abstractmethod
from typing import Any

class AbstractMessageBroker(ABC):
    @abstractmethod
    async def publish(self, message: Any, queue: str) -> None:
        pass
