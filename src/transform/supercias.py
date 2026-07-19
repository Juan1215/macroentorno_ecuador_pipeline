from src.utils.cleaning import normalize_column_names, remove_duplicates, to_numeric


# ---------------------------------------------------------------------------
# Fuente 8: Supercias - Directorio de compañías
# Archivo: bi_compania.csv  (columnas: expediente, ruc, nombre, tipo, pro_codigo, provincia)
# NOTA: este archivo no trae "situacion_legal" ni "cantón" — se documenta como
# limitación de la fuente pública en el informe técnico.
# ---------------------------------------------------------------------------

def transform_directorio(df):
    df = normalize_column_names(df)
    df['provincia'] = df['provincia'].astype(str).str.strip().str.title()
    df['nombre'] = df['nombre'].astype(str).str.strip()
    df['situacion_legal'] = None   # no disponible en la fuente pública descargable
    cols = ['expediente', 'ruc', 'nombre', 'provincia', 'situacion_legal']
    return remove_duplicates(df[cols])


# ---------------------------------------------------------------------------
# Fuente 7: Supercias - Ranking de empresas
# Archivo: bi_ranking.csv (financieros, llave "expediente") + bi_compania.csv (identidad)
# El ranking NO trae RUC/Nombre/Provincia directamente: se resuelven con un JOIN
# por "expediente" contra el directorio.
# ---------------------------------------------------------------------------

def transform_ranking(df_ranking, df_directorio, anio=None):
    df = normalize_column_names(df_ranking)
    if anio is not None:
        df = df[df['anio'] == anio]

    directorio = normalize_column_names(df_directorio)[['expediente', 'ruc', 'nombre', 'provincia']].copy()
    directorio['provincia'] = directorio['provincia'].astype(str).str.strip().str.title()
    directorio['nombre'] = directorio['nombre'].astype(str).str.strip()

    merged = df.merge(directorio, on='expediente', how='left')
    merged = merged.rename(columns={
        'ingresos_ventas': 'ingresos',
        'ciiu_n1': 'ciiu',
    })
    merged['ingresos'] = to_numeric(merged['ingresos'])
    merged['activos'] = to_numeric(merged['activos'])
    merged['situacion_legal'] = None   # no disponible en la fuente pública descargable

    cols = ['anio', 'ruc', 'nombre', 'situacion_legal', 'ingresos', 'activos', 'provincia', 'ciiu']
    merged = merged[[c for c in cols if c in merged.columns]]
    merged = merged.dropna(subset=['ruc'])
    return remove_duplicates(merged)
