from src.utils.cleaning import normalize_column_names, remove_duplicates, to_numeric


def transform_enemdu(df):
    df = normalize_column_names(df)
    id_vars = [col for col in ['encuesta', 'periodo', 'indicadores'] if col in df.columns]
    area_cols = [col for col in ['nacional', 'urbana', 'rural'] if col in df.columns]
    if area_cols:
        df = df.melt(id_vars=id_vars, value_vars=area_cols, var_name='area', value_name='valor')
        df['valor'] = to_numeric(df['valor'])
    if 'periodo' in df.columns:
        df['anio'] = df['periodo'].astype(str).str[:4]
        df['anio'] = to_numeric(df['anio'])
    if 'indicadores' in df.columns:
        df = df.rename(columns={'indicadores': 'indicador'})
    return remove_duplicates(df)


def transform_censo_ocupacion(df):
    df = normalize_column_names(df)
    if 'personas_ocupadas' in df.columns:
        df['personas_ocupadas'] = to_numeric(df['personas_ocupadas'])
    return remove_duplicates(df)
