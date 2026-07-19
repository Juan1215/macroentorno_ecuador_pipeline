from sqlalchemy import create_engine, text
from src.config import DB_CONFIG


def get_engine():
    url = (
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(url)


def test_connection():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1 AS ok'))
            return result.fetchone()[0] == 1
    except Exception:
        return False
