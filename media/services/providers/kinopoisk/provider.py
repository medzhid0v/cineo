from media.dtos import SeasonsDTO, TitleDTO
from media.services.providers.base import BaseProvider

from .client import KinopoiskClient
from .parser import KinopoiskParser


# === === === === === === ===
class KinopoiskProvider(BaseProvider):
    slug = "kinopoisk"

    # --- --- --- --- --- --- ---
    def __init__(self, client: KinopoiskClient) -> None:
        self.client = client

    # --- --- --- --- --- --- ---
    def get_title(self, external_id: int) -> TitleDTO:
        data = self.client.fetch_film(external_id)
        return KinopoiskParser.parse_title(data=data, external_id=external_id)

    # --- --- --- --- --- --- ---
    def get_seasons(self, external_id: int) -> SeasonsDTO:
        data = self.client.fetch_seasons(external_id)
        return KinopoiskParser.parse_seasons(data=data)
