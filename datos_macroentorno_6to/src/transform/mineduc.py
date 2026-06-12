from src.utils.cleaning import normalize_column_names, remove_duplicates, to_numeric


def transform_amie(df):
    df = normalize_column_names(df)
    if 'ao_lectivo' in df.columns:
        df = df.rename(columns={'ao_lectivo': 'anio_lectivo'})
    if 'total_estudiantes' in df.columns:
        df['total_estudiantes'] = to_numeric(df['total_estudiantes'])
    if 'nivel_educacion' in df.columns:
        df = df[df['nivel_educacion'].astype(str).str.lower().str.contains('bachillerato', na=False)]
    return remove_duplicates(df)
