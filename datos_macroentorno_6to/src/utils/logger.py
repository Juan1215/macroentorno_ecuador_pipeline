from datetime import datetime
from src.config import LOGS_DIR


def write_log(message):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    path = LOGS_DIR / 'pipeline.log'
    with open(path, 'a', encoding='utf-8') as file:
        file.write(f"{datetime.now()} - {message}\n")
