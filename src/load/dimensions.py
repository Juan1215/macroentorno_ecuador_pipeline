"""
Resolución de dimensiones compartidas (silver.dim_tiempo, dim_geografia, dim_ciiu).

Las tablas de hechos (fact_*) guardan id_tiempo / id_geo / id_ciiu como llave
foránea, no el dato crudo. Antes de insertar una fila de hechos hay que
buscar si la combinación ya existe en la dimensión; si no, se crea.
Esto se llama patrón "get or create" y es normal en modelos estrella.
"""
from sqlalchemy import text


def get_or_create_tiempo(engine, fecha):
    """fecha: objeto date. Devuelve id_tiempo, creando el registro si no existe."""
    with engine.begin() as conn:
        row = conn.execute(
            text('SELECT id_tiempo FROM silver.dim_tiempo WHERE fecha = :fecha'),
            {'fecha': fecha}
        ).fetchone()
        if row:
            return row[0]

        result = conn.execute(
            text('''
                INSERT INTO silver.dim_tiempo (fecha, anio, mes, trimestre)
                VALUES (:fecha, :anio, :mes, :trimestre)
                RETURNING id_tiempo
            '''),
            {
                'fecha': fecha,
                'anio': fecha.year,
                'mes': fecha.month,
                'trimestre': (fecha.month - 1) // 3 + 1,
            }
        )
        return result.fetchone()[0]


def get_or_create_geografia(engine, provincia, canton=None, cod_provincia=None, cod_canton=None):
    """provincia/canton: texto. Devuelve id_geo, creando el registro si no existe.
    Para datos que solo llegan a nivel provincia, deja canton=None."""
    provincia = (provincia or '').strip().title() or None
    canton = (canton or '').strip().title() or None

    with engine.begin() as conn:
        query = 'SELECT id_geo FROM silver.dim_geografia WHERE provincia = :provincia AND '
        query += 'canton = :canton' if canton else 'canton IS NULL'
        row = conn.execute(
            text(query), {'provincia': provincia, 'canton': canton}
        ).fetchone()
        if row:
            return row[0]

        result = conn.execute(
            text('''
                INSERT INTO silver.dim_geografia (provincia, cod_provincia, canton, cod_canton)
                VALUES (:provincia, :cod_provincia, :canton, :cod_canton)
                RETURNING id_geo
            '''),
            {
                'provincia': provincia,
                'cod_provincia': cod_provincia,
                'canton': canton,
                'cod_canton': cod_canton,
            }
        )
        return result.fetchone()[0]


def get_or_create_ciiu(engine, ciiu, descripcion=None):
    if not ciiu or str(ciiu) == 'nan':
        return None
    with engine.begin() as conn:
        row = conn.execute(
            text('SELECT id_ciiu FROM silver.dim_ciiu WHERE ciiu = :ciiu'),
            {'ciiu': ciiu}
        ).fetchone()
        if row:
            return row[0]

        result = conn.execute(
            text('''
                INSERT INTO silver.dim_ciiu (ciiu, descripcion)
                VALUES (:ciiu, :descripcion)
                RETURNING id_ciiu
            '''),
            {'ciiu': ciiu, 'descripcion': descripcion}
        )
        return result.fetchone()[0]


def build_geo_cache(engine, df, provincia_col='provincia', canton_col=None,
                     cod_provincia_col=None, cod_canton_col=None):
    """Resuelve id_geo para todas las combinaciones ÚNICAS de provincia/cantón
    en un DataFrame de una sola vez (mucho más rápido que fila por fila)."""
    cols = [provincia_col]
    for col in [canton_col, cod_provincia_col, cod_canton_col]:
        if col and col in df.columns and col not in cols:
            cols.append(col)
    unicos = df[cols].drop_duplicates()

    cache = {}
    for _, r in unicos.iterrows():
        provincia = r[provincia_col]
        canton = r[canton_col] if canton_col else None
        cod_provincia = r[cod_provincia_col] if cod_provincia_col in r.index else None
        cod_canton = r[cod_canton_col] if cod_canton_col in r.index else None
        id_geo = get_or_create_geografia(engine, provincia, canton, cod_provincia, cod_canton)
        cache[(provincia, canton)] = id_geo
    return cache


def build_ciiu_cache(engine, df, ciiu_col='ciiu'):
    """Igual que build_geo_cache pero para CIIU."""
    unicos = df[ciiu_col].dropna().unique()
    cache = {}
    for ciiu in unicos:
        cache[ciiu] = get_or_create_ciiu(engine, ciiu)
    return cache
