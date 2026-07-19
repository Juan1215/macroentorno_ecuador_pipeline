import argparse

from src.config import RAW_MANUAL_DIR
from src.db import get_engine, test_connection
from src.gold.run_gold_sql import run_gold_views
from src.utils.logger import write_log
from src.extract.readers import read_excel_file, read_csv_file, read_bce_html_export
from src.extract.file_registry import is_file_processed, register_file

from src.transform.bce import (
    transform_pib_real, transform_pib_nominal, transform_vab_provincia_industria,
    transform_petroleo, transform_riesgo_pais, merge_petroleo_riesgo, transform_iee,
)
from src.transform.supercias import transform_directorio, transform_ranking
from src.transform.mineduc import transform_amie
from src.transform.inec import transform_enemdu, transform_censo_ocupacion

from src.load.silver_loader import (
    load_fact_pib_real, load_fact_pib_nominal, load_fact_vab,
    load_fact_petroleo_riesgo, load_fact_supercias_ranking,
    load_fact_supercias_directorio, load_fact_mineduc_amie,
    load_fact_iee, load_fact_enemdu, load_fact_censo_ocupacion,
)


# ---------------------------------------------------------------------------
# Nombres de archivo esperados dentro de data/raw/manual/<fuente>/
# Cámbialos aquí si renombras los archivos descargados.
# ---------------------------------------------------------------------------
ARCHIVOS = {
    'pib_retropolacion': RAW_MANUAL_DIR / 'bce' / 'pib_retropolacion_20260702.xlsx',
    'vab_cantonal': RAW_MANUAL_DIR / 'bce' / 'vab_cantonal_2023p_20260702.xlsx',
    'petroleo': RAW_MANUAL_DIR / 'bce' / 'petroleo_wti_20260702.xls',
    'riesgo_pais': RAW_MANUAL_DIR / 'bce' / 'riesgo_pais_20260702.xls',
    'iee': RAW_MANUAL_DIR / 'bce' / 'iee_20260709.xlsx',
    'enemdu': RAW_MANUAL_DIR / 'inec' / 'enemdu_202605_20260709.xlsx',
    'censo_trabajo': RAW_MANUAL_DIR / 'inec' / 'censo_trabajo_20260709.xlsx',
    'bi_compania': RAW_MANUAL_DIR / 'supercias' / 'bi_compania_20260702.csv',
    'bi_ranking': RAW_MANUAL_DIR / 'supercias' / 'bi_ranking_20260702.csv',
    'amie': RAW_MANUAL_DIR / 'mineduc' / 'amie_2023_2024_20260702.csv',
}


def _procesar(engine, nombre_archivo, source_block, cargar_fn):
    """Envuelve cada fuente con el registro de auditoría: si el archivo ya fue
    procesado antes, lo salta (evita duplicar datos si corres el pipeline 2 veces)."""
    if is_file_processed(engine, nombre_archivo):
        write_log(f'[SKIP] {nombre_archivo} ya fue procesado antes')
        return
    try:
        cargar_fn()
        register_file(engine, nombre_archivo, source_block, status='processed')
        write_log(f'[OK] {nombre_archivo} cargado correctamente')
    except Exception as exc:
        register_file(engine, nombre_archivo, source_block, status='error')
        write_log(f'[ERROR] {nombre_archivo}: {exc}')
        raise


def run_pipeline(mode='manual'):
    write_log(f'Inicio de pipeline en modo: {mode}')

    if not test_connection():
        raise ConnectionError('No se pudo conectar a PostgreSQL')

    engine = get_engine()

    # ---- Fuente 1: PIB real anual ----
    def _pib_real():
        df = read_excel_file(ARCHIVOS['pib_retropolacion'], sheet_name='PIB pc real', header=9)
        df = transform_pib_real(df)
        load_fact_pib_real(df, engine)
    _procesar(engine, ARCHIVOS['pib_retropolacion'].name + '::pib_real', 'bce', _pib_real)

    # ---- Fuente 2: PIB per cápita nominal ----
    def _pib_nominal():
        df = read_excel_file(ARCHIVOS['pib_retropolacion'], sheet_name='PIB pc nominal', header=9)
        df = transform_pib_nominal(df)
        load_fact_pib_nominal(df, engine)
    _procesar(engine, ARCHIVOS['pib_retropolacion'].name + '::pib_nominal', 'bce', _pib_nominal)

    # ---- Fuente 3: VAB por provincia/cantón e industria ----
    def _vab():
        df_raw = read_excel_file(ARCHIVOS['vab_cantonal'],
                                  sheet_name='VAB cantonal por secciones CIIU', header=None)
        df = transform_vab_provincia_industria(df_raw, anio=2023)
        load_fact_vab(df, engine)
    _procesar(engine, ARCHIVOS['vab_cantonal'].name, 'bce', _vab)

    # ---- Fuente 4: Petróleo WTI + Riesgo país ----
    def _petroleo_riesgo():
        df_pet = transform_petroleo(read_bce_html_export(ARCHIVOS['petroleo']))
        df_ries = transform_riesgo_pais(read_bce_html_export(ARCHIVOS['riesgo_pais']))
        df = merge_petroleo_riesgo(df_pet, df_ries)
        load_fact_petroleo_riesgo(df, engine)
    _procesar(engine, ARCHIVOS['petroleo'].name + '+' + ARCHIVOS['riesgo_pais'].name,
              'bce', _petroleo_riesgo)

    # ---- Fuente 7: Supercias - Ranking (usa Directorio para resolver RUC/Nombre/Provincia) ----
    def _ranking():
        df_dir_raw = read_csv_file(ARCHIVOS['bi_compania'])
        df_rank_raw = read_csv_file(ARCHIVOS['bi_ranking'])
        df = transform_ranking(df_rank_raw, df_dir_raw, anio=2024)
        load_fact_supercias_ranking(df, engine)
    _procesar(engine, ARCHIVOS['bi_ranking'].name, 'supercias', _ranking)

    # ---- Fuente 8: Supercias - Directorio ----
    def _directorio():
        df_raw = read_csv_file(ARCHIVOS['bi_compania'])
        df = transform_directorio(df_raw)
        load_fact_supercias_directorio(df, engine)
    _procesar(engine, ARCHIVOS['bi_compania'].name, 'supercias', _directorio)

    # ---- Fuente 9: MINEDUC AMIE ----
    def _amie():
        df_raw = read_csv_file(ARCHIVOS['amie'], sep=';', encoding='latin-1')
        df = transform_amie(df_raw)
        load_fact_mineduc_amie(df, engine)
    _procesar(engine, ARCHIVOS['amie'].name, 'mineduc', _amie)

    # ---- Fuente 5: IEE ----
    def _iee():
        df = read_excel_file(ARCHIVOS['iee'], sheet_name='IEE', header=7)
        df = transform_iee(df)
        load_fact_iee(df, engine)
    _procesar(engine, ARCHIVOS['iee'].name, 'bce', _iee)

    # ---- Fuente 6: ENEMDU ----
    def _enemdu():
        df_raw = read_excel_file(ARCHIVOS['enemdu'], sheet_name='2. Tasas', header=None)
        df = transform_enemdu(df_raw)
        load_fact_enemdu(df, engine)
    _procesar(engine, ARCHIVOS['enemdu'].name, 'inec', _enemdu)

    # ---- Fuente 7: Censo 2022 - Rama de actividad ----
    def _censo():
        df_raw = read_excel_file(ARCHIVOS['censo_trabajo'], sheet_name='5.1', header=None)
        df = transform_censo_ocupacion(df_raw)
        load_fact_censo_ocupacion(df, engine)
    _procesar(engine, ARCHIVOS['censo_trabajo'].name, 'inec', _censo)

    run_gold_views()
    write_log('Pipeline ejecutado correctamente')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='manual', choices=['manual', 'rpa'])
    args = parser.parse_args()
    run_pipeline(mode=args.mode)
