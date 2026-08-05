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
            logger.info(f"Загружено: {username}, {year}-{month:02d}")
        except psycopg.Error:
            db_connection.rollback()
            raise

    finally:
        # троттлинг, досыпаем только остаток до 3 секунды между запросами
        elapsed = time.time() - start
        if elapsed < 3:
            time.sleep(3 - elapsed)


def load_player_stats(
    client, db_connection, username: str, snapshot_date, batch_id: str
) -> None:
    start = time.time()
    try:
        try:
            data = client.get_stats(username)
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

        if data.keys().isdisjoint(["chess_rapid", "chess_bullet", "chess_blitz"]):
            # пустой месяц - не пишем в базу
            logger.info(f"У {username} на момент {snapshot_date} нету статистики")
            return

        query = """
            INSERT INTO raw.stats_snapshot_raw(
            username, snapshot_date, payload, loaded_at, batch_id)
            VALUES (%s, %s, %s::jsonb, %s, %s)
            ON CONFLICT (username, snapshot_date)
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
                        snapshot_date,
                        json.dumps(data),
                        datetime.now(timezone.utc),
                        batch_id,
                    ),
                )
            db_connection.commit()
            logger.info(f"Загруженна статистика {username}, {snapshot_date}")
        except psycopg.Error:
            db_connection.rollback()
            raise

    finally:
        elapsed = time.time() - start
        if elapsed < 3:
            time.sleep(3 - elapsed)
