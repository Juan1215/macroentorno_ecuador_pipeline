-- 01_create_silver_tables.sql
-- Tablas Silver propuestas para 6to ciclo

CREATE TABLE IF NOT EXISTS silver.dim_tiempo (
    id_tiempo SERIAL PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,
    anio INTEGER NOT NULL,
    mes INTEGER,
    trimestre INTEGER
);

CREATE TABLE IF NOT EXISTS silver.dim_geografia (
    id_geo SERIAL PRIMARY KEY,
    provincia VARCHAR(80) NOT NULL,
    cod_provincia INTEGER,
    canton VARCHAR(100),
    cod_canton INTEGER,
    UNIQUE (provincia, canton)
);

CREATE TABLE IF NOT EXISTS silver.dim_ciiu (
    id_ciiu SERIAL PRIMARY KEY,
    ciiu VARCHAR(20) UNIQUE,
    descripcion VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS silver.fact_pib_real_anual (
    id SERIAL PRIMARY KEY,
    id_tiempo INTEGER REFERENCES silver.dim_tiempo(id_tiempo),
    pib_musd NUMERIC(14,2),
    poblacion NUMERIC(14,2),
    pib_percapita NUMERIC(12,2),
    variacion_pct NUMERIC(8,3)
);

CREATE TABLE IF NOT EXISTS silver.fact_pib_nominal (
    id SERIAL PRIMARY KEY,
    id_tiempo INTEGER REFERENCES silver.dim_tiempo(id_tiempo),
    pib_percapita_nominal_usd NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS silver.fact_vab_provincia_industria (
    id SERIAL PRIMARY KEY,
    id_tiempo INTEGER REFERENCES silver.dim_tiempo(id_tiempo),
    id_geo INTEGER REFERENCES silver.dim_geografia(id_geo),
    id_ciiu INTEGER REFERENCES silver.dim_ciiu(id_ciiu),
    vab_miles_usd NUMERIC(16,2)
);

CREATE TABLE IF NOT EXISTS silver.fact_petroleo_riesgo (
    id SERIAL PRIMARY KEY,
    id_tiempo INTEGER REFERENCES silver.dim_tiempo(id_tiempo),
    precio_petroleo_wti NUMERIC(8,2),
    riesgo_pais_pb INTEGER
);

CREATE TABLE IF NOT EXISTS silver.fact_iee (
    id SERIAL PRIMARY KEY,
    id_tiempo INTEGER REFERENCES silver.dim_tiempo(id_tiempo),
    iee_global NUMERIC(10,2),
    comercio NUMERIC(10,2),
    construccion NUMERIC(10,2),
    manufactura NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS silver.fact_enemdu (
    id SERIAL PRIMARY KEY,
    encuesta VARCHAR(80),
    periodo VARCHAR(20),
    anio INTEGER,
    indicador VARCHAR(150),
    area VARCHAR(30),
    valor NUMERIC(14,2)
);

CREATE TABLE IF NOT EXISTS silver.fact_censo_ocupacion (
    id SERIAL PRIMARY KEY,
    id_geo INTEGER REFERENCES silver.dim_geografia(id_geo),
    id_ciiu INTEGER REFERENCES silver.dim_ciiu(id_ciiu),
    sexo VARCHAR(30),
    grupo_edad VARCHAR(60),
    personas_ocupadas INTEGER
);

CREATE TABLE IF NOT EXISTS silver.fact_supercias_ranking (
    id SERIAL PRIMARY KEY,
    ruc VARCHAR(20),
    nombre VARCHAR(255),
    situacion_legal VARCHAR(100),
    ingresos NUMERIC(16,2),
    activos NUMERIC(16,2),
    id_geo INTEGER REFERENCES silver.dim_geografia(id_geo),
    id_ciiu INTEGER REFERENCES silver.dim_ciiu(id_ciiu)
);

CREATE TABLE IF NOT EXISTS silver.fact_supercias_directorio (
    id SERIAL PRIMARY KEY,
    ruc VARCHAR(20),
    nombre VARCHAR(255),
    situacion_legal VARCHAR(100),
    id_geo INTEGER REFERENCES silver.dim_geografia(id_geo)
);

CREATE TABLE IF NOT EXISTS silver.fact_mineduc_amie (
    id SERIAL PRIMARY KEY,
    anio_lectivo VARCHAR(20),
    amie VARCHAR(30),
    nombre_institucion VARCHAR(255),
    id_geo INTEGER REFERENCES silver.dim_geografia(id_geo),
    nivel_educacion VARCHAR(100),
    sostenimiento VARCHAR(100),
    total_estudiantes INTEGER
);

CREATE TABLE IF NOT EXISTS audit.processed_files (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    source_block VARCHAR(50),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) DEFAULT 'processed'
);
