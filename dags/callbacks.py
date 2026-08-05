import logging
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def notify_telegram_failure(context):
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    message = f"Во время выполнения {task_id} в составе DAG {dag_id} произошла ошибка"
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {"chat_id": chat_id, "text": message}

    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
    except httpx.HTTPError:
        logger.error(
            f"Не удалось отправить уведомление в Telegram про {dag_id}.{task_id}"
        )
