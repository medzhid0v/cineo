from abc import ABC, abstractmethod
from typing import Generic, TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")


class BaseUsecase(ABC, Generic[Input, Output]):
    @abstractmethod
    def execute(self, data: Input) -> Output:
        """Выполняет бизнес-логику usecase."""
        pass
