from src.utils.cleaning import normalize_column_names, remove_duplicates, to_date, to_numeric


def transform_pib_real(df):
    df = normalize_column_names(df)
    df = remove_duplicates(df)
    for col in ['pib_musd', 'poblacion', 'pib_percapita', 'variacion_pct']:
        if col in df.columns:
            df[col] = to_numeric(df[col])
    return df


def transform_pib_nominal(df):
    df = normalize_column_names(df)
    if 'período' in df.columns:
        df['periodo'] = to_date(df['período'])
    elif 'periodo' in df.columns:
        df['periodo'] = to_date(df['periodo'])
    if 'pib_percapita_nominal_usd' in df.columns:
        df['pib_percapita_nominal_usd'] = to_numeric(df['pib_percapita_nominal_usd'])
    return remove_duplicates(df)


def transform_vab(df):
    df = normalize_column_names(df)
    if 'vab_miles_usd' in df.columns:
        df['vab_miles_usd'] = to_numeric(df['vab_miles_usd'])
    return remove_duplicates(df)


def transform_petroleo_riesgo(df):
    df = normalize_column_names(df)
    if 'periodo' in df.columns:
        df['periodo'] = to_date(df['periodo'])
    for col in ['precio_petroleo_wti', 'riesgo_pais_pb']:
        if col in df.columns:
            df[col] = to_numeric(df[col])
    return remove_duplicates(df)


def transform_iee(df):
    df = normalize_column_names(df)
    if 'fecha' in df.columns:
        df['fecha'] = to_date(df['fecha'])
    for col in ['iee_global', 'comercio', 'construccion', 'manufactura']:
        if col in df.columns:
            df[col] = to_numeric(df[col])
    return remove_duplicates(df)
