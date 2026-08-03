import json
import logging
import time
from datetime import datetime, timezone

import httpx
import psycopg
import tenacity

logger = logging.getLogger(__name__)


def load_player_month(
    client, db_connection, username: str, year: int, month: int, batch_id: str
) -> None:
    """Загружает партии одного игрока за один месяц в raw.games_raw (upsert)."""
    start = time.time()  # для троттлинга, засекаем время до запроса
    try:
        try:
            data = client.get_games(username, year, month)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                logger.debug(f"Запрос для {username} вернул 404")
                return
            else:
                raise
        except json.JSONDecodeError:
            # сервер ответил 200, но тело не распарсилось как json
            logger.error("Ответ сервера пришел не в формате JSON")
            return
        except tenacity.RetryError:
            logger.error("Все ретраи получили ошибки")
            return

        if not data["games"]:
            # пустой месяц - не пишем в базу
            logger.info(
                f"У {username} за период {year}-{month:02d} нету игр, пустой ответ"
            )
            return

        # upsert, чтобы повторный запуск за тот же период не плодил дубли
        query = """
            INSERT INTO raw.games_raw(
            username, archive_month, payload, loaded_at, batch_id)
            VALUES (%s, TO_DATE(%s, 'YYYY-MM'), %s::jsonb, %s, %s)
            ON CONFLICT (username, archive_month)
            DO UPDATE SET
                payload = EXCLUDED.payload,
                loaded_at = EXCLUDED.loaded_at,
                batch_id = EXCLUDED.batch_id
            """

        try:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        username,
                        f"{year}-{month}",
                        json.dumps(data),
                        datetime.now(timezone.utc),
                        batch_id,
                    ),
                )
            db_connection.commit()
            logger.info(f"Загружено: {username}, {year}-{month}")
        except psycopg.Error:
            db_connection.rollback()
            raise

    finally:
        # троттлинг, досыпаем только остаток до 3 секунды между запросами
        elapsed = time.time() - start
        if elapsed < 3:
            time.sleep(3 - elapsed)
