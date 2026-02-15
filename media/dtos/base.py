from pydantic import BaseModel, ConfigDict


# === === === === === === ===
class BaseDTO(BaseModel):
    """
    Базовый DTO для всех доменных моделей.
    """

    # --- --- --- --- --- --- ---
    model_config = ConfigDict(
        extra="ignore",  # игнорировать лишние поля API
        str_strip_whitespace=True,  # автоматически trim строк
    )

    # --- --- --- --- --- --- ---
    @staticmethod
    def parse_int(value) -> int | None:
        if value in (None, ""):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    # --- --- --- --- --- --- ---
    @staticmethod
    def parse_str(value) -> str | None:
        return value.strip() if isinstance(value, str) else value

    # --- --- --- --- --- --- ---
    @staticmethod
    def parse_list(value) -> list | None:
        if value in (None, ""):
            return []
        if isinstance(value, list):
            return value
        return []
