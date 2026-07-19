from pathlib import Path
from sqlalchemy import text

from src.db import get_engine
from src.utils.logger import write_log


def run_gold_views():
    sql_path = Path(__file__).resolve().parents[2] / 'database' / 'sql' / '02_create_gold_views.sql'
    engine = get_engine()
    raw_sql = sql_path.read_text(encoding='utf-8')

    # Separar en sentencias individuales para mayor robustez
    statements = [s.strip() for s in raw_sql.split(';') if s.strip()]

    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))

    write_log(f'[OK] {len(statements)} sentencias Gold ejecutadas correctamente')

