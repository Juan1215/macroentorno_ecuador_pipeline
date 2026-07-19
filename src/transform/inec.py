import pandas as pd

from src.utils.cleaning import normalize_column_names, remove_duplicates, to_numeric


# ---------------------------------------------------------------------------
# Fuente 6: ENEMDU - Indicadores laborales
# Archivo: 202605_Tabulados_Mercado_Laboral_EXCEL.XLSX, hoja "2. Tasas"
# Encabezado en 2 filas (fila 2 = grupo, fila 3 = subcategoría), datos desde fila 4.
# Se lee crudo con: read_excel_file(path, sheet_name='2. Tasas', header=None)
# ---------------------------------------------------------------------------

def transform_enemdu(df_raw):
    """df_raw: hoja '2. Tasas' leída con header=None (sin procesar)."""
    data = df_raw.iloc[3:].reset_index(drop=True)
    data.columns = ['encuesta', 'periodo', 'indicadores', 'nacional', 'urbana', 'rural',
                     'hombre', 'mujer'] + list(data.columns[8:])
    data = data.dropna(subset=['encuesta'])

    id_vars = ['encuesta', 'periodo', 'indicadores']
    area_cols = ['nacional', 'urbana', 'rural']
    long_df = data.melt(id_vars=id_vars, value_vars=area_cols, var_name='area', value_name='valor')
    long_df['valor'] = to_numeric(long_df['valor'])
    long_df = long_df.rename(columns={'indicadores': 'indicador'})
    long_df['anio'] = long_df['periodo'].astype(str).str[-2:]
    long_df['anio'] = '20' + long_df['anio']
    long_df['anio'] = to_numeric(long_df['anio']).astype('Int64')

    long_df = long_df.dropna(subset=['valor'])
    cols = ['encuesta', 'periodo', 'anio', 'indicador', 'area', 'valor']
    return remove_duplicates(long_df[cols])


# ---------------------------------------------------------------------------
# Fuente 7: Censo 2022 - Población ocupada por rama de actividad
# Archivo: 2022_CPV_Trabajo.xlsx, hoja "5.1" (provincia + cantón + sexo + edad + rama)
# Formato ANCHO (una columna por rama CIIU) -> se pasa a LARGO con melt().
# Se lee crudo con: read_excel_file(path, sheet_name='5.1', header=None)
# ---------------------------------------------------------------------------

# Orden de las 21 secciones CIIU (Rev.4) + "No clasificado", tal como vienen
# las columnas G:AB de la hoja 5.1 (columnas 7 a 28 en índice 1-based de Excel).
CIIU_SECCIONES = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', None,  # None = "No clasificado"
]


def transform_censo_ocupacion(df_raw):
    """df_raw: hoja '5.1' de 2022_CPV_Trabajo.xlsx, leída con header=None (sin procesar).
    Las columnas B:E (índice 1:4 en el df ya recortado) traen la jerarquía
    Provincia/Cantón/Sexo/Grupo de edad, F el total, y G:AB las 22 ramas de actividad."""
    nombres_rama = [df_raw.iloc[9, c] for c in range(6, 28)]   # fila 10 real (índice 9)
    data = df_raw.iloc[11:].reset_index(drop=True)             # datos desde fila 12 real
    data = data.iloc[:, 1:28]
    data.columns = ['provincia', 'canton', 'sexo', 'grupo_edad', 'total'] + nombres_rama

    # Solo detalle atómico: Hombres/Mujeres (no el agregado "Total"), edad real (no
    # el agregado "Total <cantón>"), y cantón real (no fila de totales provinciales).
    data = data[
        data['sexo'].isin(['Hombres', 'Mujeres']) &
        (~data['grupo_edad'].astype(str).str.startswith('Total')) &
        (data['provincia'] != 'Total Nacional') &
        (~data['canton'].astype(str).str.startswith('Total'))
    ]

    mapa_ciiu = dict(zip(nombres_rama, CIIU_SECCIONES))
    long_df = data.melt(
        id_vars=['provincia', 'canton', 'sexo', 'grupo_edad'],
        value_vars=nombres_rama, var_name='rama_desc', value_name='personas_ocupadas'
    )
    long_df['ciiu'] = long_df['rama_desc'].map(mapa_ciiu)
    long_df['personas_ocupadas'] = to_numeric(long_df['personas_ocupadas'])
    long_df['provincia'] = long_df['provincia'].astype(str).str.strip().str.title()
    long_df['canton'] = long_df['canton'].astype(str).str.strip().str.title()
    long_df = long_df.dropna(subset=['personas_ocupadas', 'ciiu'])

    cols = ['provincia', 'canton', 'sexo', 'grupo_edad', 'ciiu', 'personas_ocupadas']
    return remove_duplicates(long_df[cols])
