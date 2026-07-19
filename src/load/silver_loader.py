from src.load.dimensions import get_or_create_tiempo, build_geo_cache, build_ciiu_cache


def load_dataframe(df, table_name, engine, schema='silver', if_exists='append'):
    """Carga genérica: usar solo para tablas SIN llaves foráneas a dimensiones
    (ej. fact_enemdu, fact_supercias_directorio, fact_mineduc_amie ya resueltos)."""
    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists=if_exists,
        index=False
    )


def load_fact_pib_real(df, engine):
    """df: salida de transform_pib_real (columnas: fecha, anio, pib_musd, poblacion,
    pib_percapita, variacion_pct)."""
    df = df.copy()
    df['id_tiempo'] = df['fecha'].apply(lambda f: get_or_create_tiempo(engine, f))
    cols = ['id_tiempo', 'pib_musd', 'poblacion', 'pib_percapita', 'variacion_pct']
    load_dataframe(df[cols], 'fact_pib_real_anual', engine)


def load_fact_pib_nominal(df, engine):
    """df: salida de transform_pib_nominal (columnas: fecha, anio, pib_percapita_nominal_usd)."""
    df = df.copy()
    df['id_tiempo'] = df['fecha'].apply(lambda f: get_or_create_tiempo(engine, f))
    cols = ['id_tiempo', 'pib_percapita_nominal_usd']
    load_dataframe(df[cols], 'fact_pib_nominal', engine)


def load_fact_vab(df, engine):
    """df: salida de transform_vab_provincia_industria
    (columnas: anio, cod_provincia, provincia, cod_canton, canton, ciiu, vab_miles_usd)."""
    import pandas as pd
    df = df.copy()

    # id_tiempo: se ancla al 1-enero del año del archivo (dato anual)
    df['fecha'] = pd.to_datetime(df['anio'].astype(str) + '-01-01').dt.date
    tiempo_cache = {f: get_or_create_tiempo(engine, f) for f in df['fecha'].unique()}
    df['id_tiempo'] = df['fecha'].map(tiempo_cache)

    geo_cache = build_geo_cache(engine, df, provincia_col='provincia', canton_col='canton',
                                 cod_provincia_col='cod_provincia', cod_canton_col='cod_canton')
    df['id_geo'] = df.apply(lambda r: geo_cache[(r['provincia'], r['canton'])], axis=1)

    ciiu_cache = build_ciiu_cache(engine, df, ciiu_col='ciiu')
    df['id_ciiu'] = df['ciiu'].map(ciiu_cache)

    cols = ['id_tiempo', 'id_geo', 'id_ciiu', 'vab_miles_usd']
    load_dataframe(df[cols], 'fact_vab_provincia_industria', engine)


def load_fact_petroleo_riesgo(df, engine):
    """df: salida de merge_petroleo_riesgo (columnas: fecha, precio_petroleo_wti, riesgo_pais_pb)."""
    df = df.copy()
    df['id_tiempo'] = df['fecha'].apply(lambda f: get_or_create_tiempo(engine, f))
    cols = ['id_tiempo', 'precio_petroleo_wti', 'riesgo_pais_pb']
    load_dataframe(df[cols], 'fact_petroleo_riesgo', engine)


def load_fact_supercias_ranking(df, engine):
    """df: salida de transform_ranking (columnas: anio, ruc, nombre, situacion_legal,
    ingresos, activos, provincia, ciiu)."""
    df = df.copy()
    geo_cache = build_geo_cache(engine, df, provincia_col='provincia', canton_col=None)
    df['id_geo'] = df['provincia'].apply(lambda p: geo_cache.get((str(p).strip().title(), None)))

    ciiu_cache = build_ciiu_cache(engine, df, ciiu_col='ciiu')
    df['id_ciiu'] = df['ciiu'].map(ciiu_cache)

    cols = ['ruc', 'nombre', 'situacion_legal', 'ingresos', 'activos', 'id_geo', 'id_ciiu']
    load_dataframe(df[cols], 'fact_supercias_ranking', engine)


def load_fact_supercias_directorio(df, engine):
    """df: salida de transform_directorio (columnas: expediente, ruc, nombre, provincia,
    situacion_legal)."""
    df = df.copy()
    geo_cache = build_geo_cache(engine, df, provincia_col='provincia', canton_col=None)
    df['id_geo'] = df['provincia'].apply(lambda p: geo_cache.get((str(p).strip().title(), None)))

    cols = ['ruc', 'nombre', 'situacion_legal', 'id_geo']
    load_dataframe(df[cols], 'fact_supercias_directorio', engine)


def load_fact_mineduc_amie(df, engine):
    """df: salida de transform_amie (columnas: anio_lectivo, amie, nombre_institucion,
    provincia, cod_provincia, canton, cod_canton, nivel_educacion, sostenimiento,
    total_estudiantes)."""
    df = df.copy()
    geo_cache = build_geo_cache(engine, df, provincia_col='provincia', canton_col='canton',
                                 cod_provincia_col='cod_provincia', cod_canton_col='cod_canton')
    df['id_geo'] = df.apply(lambda r: geo_cache[(r['provincia'], r['canton'])], axis=1)

    cols = ['anio_lectivo', 'amie', 'nombre_institucion', 'id_geo',
            'nivel_educacion', 'sostenimiento', 'total_estudiantes']
    load_dataframe(df[cols], 'fact_mineduc_amie', engine)


def load_fact_iee(df, engine):
    """df: salida de transform_iee (columnas: fecha, iee_global, comercio,
    construccion, manufactura)."""
    df = df.copy()
    df['id_tiempo'] = df['fecha'].apply(lambda f: get_or_create_tiempo(engine, f))
    cols = ['id_tiempo', 'iee_global', 'comercio', 'construccion', 'manufactura', 'servicios']
    load_dataframe(df[cols], 'fact_iee', engine)


def load_fact_enemdu(df, engine):
    """df: salida de transform_enemdu (columnas: encuesta, periodo, anio, indicador,
    area, valor). Tabla sin FK a dimensiones -> carga directa."""
    load_dataframe(df, 'fact_enemdu', engine)


def load_fact_censo_ocupacion(df, engine):
    """df: salida de transform_censo_ocupacion (columnas: provincia, canton, sexo,
    grupo_edad, ciiu, personas_ocupadas)."""
    df = df.copy()
    geo_cache = build_geo_cache(engine, df, provincia_col='provincia', canton_col='canton')
    df['id_geo'] = df.apply(lambda r: geo_cache[(r['provincia'], r['canton'])], axis=1)

    ciiu_cache = build_ciiu_cache(engine, df, ciiu_col='ciiu')
    df['id_ciiu'] = df['ciiu'].map(ciiu_cache)

    cols = ['id_geo', 'id_ciiu', 'sexo', 'grupo_edad', 'personas_ocupadas']
    load_dataframe(df[cols], 'fact_censo_ocupacion', engine)
