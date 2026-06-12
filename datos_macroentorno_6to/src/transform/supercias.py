from src.utils.cleaning import normalize_column_names, remove_duplicates, to_numeric


def transform_ranking(df):
    df = normalize_column_names(df)
    for col in ['ingresos', 'activos']:
        if col in df.columns:
            df[col] = to_numeric(df[col])
    return remove_duplicates(df)


def transform_directorio(df):
    df = normalize_column_names(df)
    return remove_duplicates(df)
