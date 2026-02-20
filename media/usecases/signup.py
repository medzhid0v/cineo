from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from media.usecases.base_usecase import BaseUsecase

UserModel = get_user_model()


@dataclass(frozen=True)
class SignUpInput:
    username: str
    password: str


class SignUpUsecase(BaseUsecase[SignUpInput, User]):
    """Usecase для регистрации нового пользователя."""

    def execute(self, data: SignUpInput) -> User:
        user = UserModel.objects.create_user(
            username=data.username,
            password=data.password,
        )
        return user
