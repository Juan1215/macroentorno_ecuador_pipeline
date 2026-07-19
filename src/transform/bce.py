import pandas as pd

from src.utils.cleaning import normalize_column_names, remove_duplicates, to_numeric


# ---------------------------------------------------------------------------
# Fuente 1: PIB real anual  (archivo: retropolacion_1965_2024p.xlsx, hoja "PIB pc real")
# Fuente 2: PIB per cápita nominal (mismo archivo, hoja "PIB pc nominal")
# Ambas hojas comparten estructura: header en la fila 10 (índice 9 con header=None),
# datos desde la fila 11. Se leen con:
#   read_excel_file(path, sheet_name='PIB pc real', header=9)
# ---------------------------------------------------------------------------

def transform_pib_real(df):
    """df: hoja 'PIB pc real' de retropolacion_*.xlsx, ya leída con header=9."""
    df = normalize_column_names(df)
    df = df.rename(columns={
        'anos': 'anio',
        'pib': 'pib_musd',
        'poblacion': 'poblacion',
        'pib_per_capita': 'pib_percapita',
        'tasa_de_variacion_anual_del_pib_per_capita': 'variacion_pct',
    })
    df['anio'] = to_numeric(df['anio'])
    df = df.dropna(subset=['anio'])          # descarta filas de notas al pie
    df['anio'] = df['anio'].astype('Int64')
    for col in ['pib_musd', 'poblacion', 'pib_percapita', 'variacion_pct']:
        if col in df.columns:
            df[col] = to_numeric(df[col])
    # Convención: cada año anual se ancla al 1-enero para poder construir dim_tiempo
    df['fecha'] = pd.to_datetime(df['anio'].astype(str) + '-01-01').dt.date
    df = df[['fecha', 'anio', 'pib_musd', 'poblacion', 'pib_percapita', 'variacion_pct']]
    return remove_duplicates(df)


def transform_pib_nominal(df):
    """df: hoja 'PIB pc nominal' de retropolacion_*.xlsx, ya leída con header=9."""
    df = normalize_column_names(df)
    df = df.rename(columns={
        'anos': 'anio',
        'pib_per_capita': 'pib_percapita_nominal_usd',
    })
    df['anio'] = to_numeric(df['anio'])
    df = df.dropna(subset=['anio'])          # descarta filas de notas al pie
    df['anio'] = df['anio'].astype('Int64')
    df['pib_percapita_nominal_usd'] = to_numeric(df['pib_percapita_nominal_usd'])
    df['fecha'] = pd.to_datetime(df['anio'].astype(str) + '-01-01').dt.date
    df = df[['fecha', 'anio', 'pib_percapita_nominal_usd']]
    return remove_duplicates(df)


# ---------------------------------------------------------------------------
# Fuente 3: VAB por provincia/cantón e industria (CIIU)
# Archivo: corrientes_2023p.xlsx, hoja "VAB cantonal por secciones CIIU"
# Estructura especial de 3 filas de encabezado (fila 11 = letra CIIU,
# fila 13 = nombre de sección), formato ANCHO -> hay que pasar a LARGO.
# Se lee crudo con: read_excel_file(path, sheet_name=..., header=None)
# ---------------------------------------------------------------------------

def transform_vab_provincia_industria(df_raw, anio):
    """df_raw: hoja 'VAB cantonal por secciones CIIU' leída con header=None (sin procesar).
    anio: año que representa el archivo (ej. 2023), porque el Excel no trae columna de año."""
    codigos = df_raw.iloc[10]   # fila de letras CIIU (A, B, C, D-E, ...)
    nombres = df_raw.iloc[12]   # fila de nombres de sección
    data = df_raw.iloc[13:].reset_index(drop=True)
    data.columns = nombres.values

    id_cols = list(data.columns[:4])          # CÓDIGO PROVINCIA, PROVINCIA, CÓDIGO CANTÓN, CANTÓN
    ciiu_cols = list(data.columns[4:-1])       # excluye la última columna "ECONOMÍA TOTAL"
    mapa_ciiu = dict(zip(nombres.values[4:-1], codigos.values[4:-1]))

    long_df = data.melt(id_vars=id_cols, value_vars=ciiu_cols,
                         var_name='ciiu_desc', value_name='vab_miles_usd')
    long_df['ciiu'] = long_df['ciiu_desc'].map(mapa_ciiu)

    long_df = normalize_column_names(long_df)
    long_df = long_df.rename(columns={
        'codigo_provincia': 'cod_provincia',
        'codigo_canton': 'cod_canton',
    })
    long_df['anio'] = anio
    long_df['cod_provincia'] = to_numeric(long_df['cod_provincia'])
    long_df['cod_canton'] = to_numeric(long_df['cod_canton'])
    long_df = long_df.dropna(subset=['cod_provincia', 'cod_canton'])
    long_df['cod_provincia'] = long_df['cod_provincia'].astype('Int64')
    long_df['cod_canton'] = long_df['cod_canton'].astype('Int64')
    long_df['vab_miles_usd'] = to_numeric(long_df['vab_miles_usd'])
    long_df['provincia'] = long_df['provincia'].astype(str).str.strip().str.title()
    long_df['canton'] = long_df['canton'].astype(str).str.strip().str.title()
    long_df = long_df.dropna(subset=['vab_miles_usd'])

    cols = ['anio', 'cod_provincia', 'provincia', 'cod_canton', 'canton', 'ciiu', 'vab_miles_usd']
    return remove_duplicates(long_df[cols])


# ---------------------------------------------------------------------------
# Fuente 4: Precio petróleo WTI + Riesgo país
# Ambos archivos vienen como HTML exportado del BCE (aunque el nombre sea .xls),
# se leen con read_bce_html_export(). Estructura: Período | <valor>
# ---------------------------------------------------------------------------

def transform_petroleo(df):
    """df: resultado de read_bce_html_export() sobre el archivo de precio WTI."""
    df = normalize_column_names(df)
    df = df.rename(columns={
        'periodo': 'fecha',
        'precio_petroleo_en_usd_por_barril': 'precio_petroleo_wti',
    })
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce').dt.date
    df['precio_petroleo_wti'] = to_numeric(df['precio_petroleo_wti'])
    return remove_duplicates(df[['fecha', 'precio_petroleo_wti']])


def transform_riesgo_pais(df):
    """df: resultado de read_bce_html_export() sobre el archivo de riesgo país."""
    df = normalize_column_names(df)
    df = df.rename(columns={
        'periodo': 'fecha',
        'riesgo_pais_en_puntos_basicos': 'riesgo_pais_pb',
    })
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce').dt.date
    df['riesgo_pais_pb'] = to_numeric(df['riesgo_pais_pb'])
    return remove_duplicates(df[['fecha', 'riesgo_pais_pb']])


def merge_petroleo_riesgo(df_petroleo, df_riesgo):
    """Combina ambas series por fecha para poblar silver.fact_petroleo_riesgo."""
    merged = pd.merge(df_petroleo, df_riesgo, on='fecha', how='outer')
    return merged.sort_values('fecha').reset_index(drop=True)


# ---------------------------------------------------------------------------
# Fuente 5: IEE - Índice de Expectativas Empresariales (pendiente de descargar)
# Se deja la función lista para cuando llegue el archivo.
# ---------------------------------------------------------------------------

def transform_iee(df):
    """df: hoja 'IEE' de IEE_Nueva_Metodologia.xlsx, leída con header=7
    (fila 8 real del Excel) y ya sin las filas de notas al pie."""
    df = normalize_column_names(df)
    df = df.dropna(subset=['fecha'])
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce').dt.date
    df = df.dropna(subset=['fecha'])
    for col in ['iee_global', 'comercio', 'construccion', 'manufactura', 'servicios']:
        if col in df.columns:
            df[col] = to_numeric(df[col])
    cols = ['fecha', 'iee_global', 'comercio', 'construccion', 'manufactura', 'servicios']
    return remove_duplicates(df[cols])
