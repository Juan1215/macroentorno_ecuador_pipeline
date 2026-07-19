from src.utils.cleaning import normalize_column_names, remove_duplicates, to_numeric


# ---------------------------------------------------------------------------
# Fuente 9: MINEDUC AMIE 2023-2024
# Archivo: 2_MINEDUC_RegistrosAdministrativos_2023-2024Inicio.csv
# Se lee con: read_csv_file(path, sep=';', encoding='latin-1')
# ---------------------------------------------------------------------------

def transform_amie(df):
    df = normalize_column_names(df)
    df = df.rename(columns={
        'ano_lectivo': 'anio_lectivo',
        'canton': 'canton',
        'cod_canton': 'cod_canton',
        'cod_provincia': 'cod_provincia',
    })
    df['total_estudiantes'] = to_numeric(df['total_estudiantes'])
    df['provincia'] = df['provincia'].astype(str).str.strip().str.title()
    df['canton'] = df['canton'].astype(str).str.strip().str.title()

    # Filtro que pide el reto: solo instituciones que ofrecen Bachillerato
    df = df[df['nivel_educacion'].astype(str).str.lower().str.contains('bachillerato', na=False)]

    cols = ['anio_lectivo', 'amie', 'nombre_institucion', 'provincia', 'cod_provincia',
            'canton', 'cod_canton', 'nivel_educacion', 'sostenimiento', 'total_estudiantes']
    df = df[[c for c in cols if c in df.columns]]
    return remove_duplicates(df)
