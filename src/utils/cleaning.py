import unicodedata
import pandas as pd


def strip_accents(text):
    """Quita tildes/diéresis pero conserva la ñ (útil para nombres de columnas)."""
    text = str(text)
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def normalize_column_names(df):
    """Normaliza nombres de columnas: sin tildes, minúsculas, snake_case,
    sin saltos de línea (los reportes del BCE traen \n dentro del encabezado)."""
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .map(strip_accents)
        .str.strip()
        .str.lower()
        .str.replace('\n', ' ', regex=False)
        .str.replace(r'\(.*?\)', '', regex=True)   # quita "(Millones de USD)" etc.
        .str.replace(r'[^a-z0-9ñ]+', '_', regex=True)
        .str.strip('_')
    )
    return df


def clean_numeric_locale(series):
    """Convierte strings numéricos que pueden venir con separador de miles '.'
    o coma decimal, típico de exportes de portales de gobierno."""
    s = series.astype(str).str.strip()
    s = s.str.replace(r'[^\d,.\-]', '', regex=True)
    return pd.to_numeric(s, errors='coerce')


def to_numeric(series):
    return pd.to_numeric(series, errors='coerce')


def to_date(series):
    return pd.to_datetime(series, errors='coerce').dt.date


def remove_duplicates(df):
    return df.drop_duplicates().reset_index(drop=True)
