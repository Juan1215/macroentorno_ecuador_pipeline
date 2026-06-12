from pathlib import Path
from src.db import get_engine


def run_gold_views():
    sql_path = Path(__file__).resolve().parents[2] / 'database' / 'sql' / '02_create_gold_views.sql'
    engine = get_engine()
    sql = sql_path.read_text(encoding='utf-8')
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)
