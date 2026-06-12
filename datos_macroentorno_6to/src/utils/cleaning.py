import pandas as pd


def normalize_column_names(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(' ', '_', regex=False)
        .str.replace('-', '_', regex=False)
    )
    return df


def to_numeric(series):
    return pd.to_numeric(series, errors='coerce')


def to_date(series):
    return pd.to_datetime(series, errors='coerce').dt.date


def remove_duplicates(df):
    return df.drop_duplicates().reset_index(drop=True)
