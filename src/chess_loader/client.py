import os

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.chess.com/pub"


class ApiClient:
    """Тонкий клиент для публичного API Chess.com"""

    def __init__(self) -> None:
        self.user_agent = os.environ.get("CHESS_API_USER_AGENT")
        if not self.user_agent:
            raise ("CHESS_API_USER_AGENT is not set")
        self.timeout = 10.0
        self.client = httpx.Client(
            headers={"User-Agent": self.user_agent}, timeout=self.timeout
        )

    """Общий метод запроса, надстройка над публичными"""

    def _get(self, path: str) -> dict:
        url = f"{BASE_URL}{path}"
        responce = self.client.get(url)
        responce.raise_for_status()
        return responce.json()

    def get_titled(self, title: str) -> dict:
        return self._get(f"/titled/{title}")

    def get_archives(self, username: str) -> dict:
        return self._get(f"/player/{username}/games/archives")

    def get_games(self, username: str, year: int, month: int) -> dict:
        if month < 10:
            formatted_month = f"0{month}"
        else:
            formatted_month = f"{month}"
        return self._get(f"/player/{username}/games/{year}/{formatted_month}")
