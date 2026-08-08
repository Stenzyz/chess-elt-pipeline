import json
import logging
import time
from datetime import datetime, timezone

import httpx
import psycopg
import tenacity

logger = logging.getLogger(__name__)


def _fetch_with_retry_handling(client_call, username: str):
    """Общая обработка сетевых ошибок вокруг вызова клиента. Возвращает data или None"""
    try:
        return client_call(username)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            logger.debug(f"Запрос для {username} вернул 404")
            return None
        raise
    except json.JSONDecodeError:
        logger.error("Ответ сервера пришел не в формате JSON")
        return None
    except tenacity.RetryError:
        logger.error("Все ретраи получили ошибки")
        return None


def _upsert(db_connection, query: str, params: tuple) -> None:
    """Общая запись с rollback при ошибке."""
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(query, params)
        db_connection.commit()
    except psycopg.Error:
        db_connection.rollback()
        raise


def _throttle(start: float, min_seconds: float = 3) -> None:
    """Досыпает только остаток до min_seconds между запросами."""
    elapsed = time.time() - start
    if elapsed < min_seconds:
        time.sleep(min_seconds - elapsed)


def load_player_month(
    client, db_connection, username: str, year: int, month: int, batch_id: str
) -> None:
    """Загружает партии одного игрока за один месяц в raw.games_raw (upsert)."""
    start = time.time()
    try:
        data = _fetch_with_retry_handling(
            lambda u: client.get_games(u, year, month), username
        )
        if data is None:
            return

        if not data["games"]:
            # пустой месяц - не пишем в базу
            logger.info(
                f"У {username} за период {year}-{month:02d} нету игр, пустой ответ"
            )
            return

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
        _upsert(
            db_connection,
            query,
            (
                username,
                f"{year}-{month}",
                json.dumps(data),
                datetime.now(timezone.utc),
                batch_id,
            ),
        )
        logger.info(f"Загружено: {username}, {year}-{month:02d}")

    finally:
        _throttle(start)


def load_player_stats(
    client, db_connection, username: str, snapshot_date, batch_id: str
) -> None:
    """Загружает снапшот рейтингов игрока в raw.stats_snapshot_raw (upsert)."""
    start = time.time()
    try:
        data = _fetch_with_retry_handling(client.get_stats, username)
        if data is None:
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
        _upsert(
            db_connection,
            query,
            (
                username,
                snapshot_date,
                json.dumps(data),
                datetime.now(timezone.utc),
                batch_id,
            ),
        )
        logger.info(f"Загружена статистика {username}, {snapshot_date}")

    finally:
        _throttle(start)


def load_player_profile(client, db_connection, username: str, batch_id: str) -> None:
    """Загружает профиль игрока в raw.player_profiles_raw (upsert)."""
    start = time.time()
    try:
        data = _fetch_with_retry_handling(client.get_profile, username)
        if data is None:
            return

        query = """
            INSERT INTO raw.player_profiles_raw(
            username, payload, loaded_at, batch_id)
            VALUES (%s, %s::jsonb, %s, %s)
            ON CONFLICT (username)
            DO UPDATE SET
                payload = EXCLUDED.payload,
                loaded_at = EXCLUDED.loaded_at,
                batch_id = EXCLUDED.batch_id
            """
        _upsert(
            db_connection,
            query,
            (username, json.dumps(data), datetime.now(timezone.utc), batch_id),
        )
        logger.info(f"Загружен профиль {username}")

    finally:
        _throttle(start)
