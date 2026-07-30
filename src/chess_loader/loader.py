import json
import logging
import re
import time
from datetime import datetime, timezone

import httpx
import psycopg

logger = logging.getLogger(__name__)


def load_player_month(
    client, db_connection, username: str, year: int, month: int, batch_id: str
) -> None:
    """Загружает партии одного игрока за один месяц в raw.games_raw (upsert)."""

    try:
        start = time.time()  # для троттлинга, засекаем время до запроса
        data = client.get_games(username, year, month)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            logger.info("Аккаунт пользователя удален, либо не выгружается!")
            return
        else:
            raise
    except json.JSONDecodeError:
        # сервер ответил 200, но тело не распарсилось как json
        logger.error("Ответ сервера пришел не в формате JSON")
        return

    if not data["games"]:
        # пустой месяц - не пишем в базу
        logger.info(
            f"У пользователя {username} нет партий за этот месяц, ошибка вызова"
        )
        return

    # upsert, чтобы повторный запуск за тот же период не плодил дубли
    query = """
        INSERT INTO raw.games_raw(username, archive_month, payload, loaded_at, batch_id)
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

    # троттлинг, досыпаем только остаток до 1 секунды между запросами
    elapsed = time.time() - start
    if elapsed < 1:
        time.sleep(1 - elapsed)

    return


def load_all_archives_for_player(
    client, db_connection, username: str, batch_id: str
) -> None:
    """Проходит по всем архивам игрока и грузит только последние 24 месяца."""

    archives = client.get_archives(username)
    if not archives["archives"]:
        logger.info(f"У пользователя {username} нету игр на аккаунте")
        return

    for url in archives["archives"]:
        # достаем год и месяц прямо из ссылки на архив
        match = re.search(r"(\d{4})/(\d{2})", url)
        year = int(match.group(1))
        month = int(match.group(2))

        now = datetime.now(timezone.utc)
        current_year = now.year
        current_month = now.month

        # переводим в общее число месяцев, чтобы просто сравнить разницу
        url_total_months = (year * 12) + month
        current_total_months = (current_year * 12) + current_month

        if current_total_months - url_total_months > 24:
            continue

        load_player_month(client, db_connection, username, year, month, batch_id)
    return
