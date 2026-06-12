from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / '.env')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'macroentorno_ecuador'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

DATA_DIR = BASE_DIR / 'data'
RAW_MANUAL_DIR = DATA_DIR / 'raw' / 'manual'
RPA_INBOX_DIR = DATA_DIR / 'raw' / 'rpa_inbox'
BRONZE_DIR = DATA_DIR / 'bronze'
REJECTED_DIR = DATA_DIR / 'rejected'
LOGS_DIR = BASE_DIR / 'logs'
