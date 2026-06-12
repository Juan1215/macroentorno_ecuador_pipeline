import argparse
from src.db import test_connection
from src.gold.run_gold_sql import run_gold_views
from src.utils.logger import write_log


def run_pipeline(mode='manual'):
    write_log(f'Inicio de pipeline en modo: {mode}')

    if not test_connection():
        raise ConnectionError('No se pudo conectar a PostgreSQL')

    # TODO: agregar lectura de archivos desde data/raw/manual o data/raw/rpa_inbox
    # TODO: aplicar transformaciones por fuente
    # TODO: cargar tablas Silver con src/load/silver_loader.py
    run_gold_views()

    write_log('Pipeline ejecutado correctamente')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='manual', choices=['manual', 'rpa'])
    args = parser.parse_args()
    run_pipeline(mode=args.mode)
