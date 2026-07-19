-- 02_create_gold_views.sql
-- Vistas Gold obligatorias y adicionales para 6to ciclo
-- Script idempotente: puede correrse las veces que sea necesario sin fallar.

-- Evita el bug de memoria compartida en workers paralelos (Windows/Postgres 18)
SET max_parallel_workers_per_gather = 0;

-- =========================================================
-- gold_pib_tendencia
-- =========================================================
DROP VIEW IF EXISTS gold.gold_pib_tendencia CASCADE;
CREATE VIEW gold.gold_pib_tendencia AS
SELECT
    t.anio,
    p.pib_musd,
    p.pib_percapita,
    p.variacion_pct,
    CASE
        WHEN p.variacion_pct > 2 THEN 'Crecimiento fuerte'
        WHEN p.variacion_pct > 0 THEN 'Crecimiento moderado'
        WHEN p.variacion_pct = 0 THEN 'Estancamiento'
        ELSE 'Contracción'
    END AS clasificacion
FROM silver.fact_pib_real_anual p
JOIN silver.dim_tiempo t ON p.id_tiempo = t.id_tiempo
ORDER BY t.anio;

-- =========================================================
-- gold_petroleo_30dias
-- =========================================================
DROP VIEW IF EXISTS gold.gold_petroleo_30dias CASCADE;
CREATE VIEW gold.gold_petroleo_30dias AS
SELECT
    t.fecha,
    p.precio_petroleo_wti,
    p.riesgo_pais_pb,
    AVG(p.precio_petroleo_wti) OVER (ORDER BY t.fecha ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS promedio_wti_30dias
FROM silver.fact_petroleo_riesgo p
JOIN silver.dim_tiempo t ON p.id_tiempo = t.id_tiempo;

-- =========================================================
-- gold_empleo_tendencia
-- =========================================================
DROP VIEW IF EXISTS gold.gold_empleo_tendencia CASCADE;
CREATE VIEW gold.gold_empleo_tendencia AS
SELECT
    anio,
    periodo,
    indicador,
    area,
    valor
FROM silver.fact_enemdu;

-- =========================================================
-- gold_empresas_provincia
-- CORREGIDA: Se eliminó id_geo del GROUP BY para asegurar
-- estrictamente 1 fila por provincia y evitar problemas de cruce.
-- =========================================================
DROP VIEW IF EXISTS gold.gold_empresas_provincia CASCADE;
CREATE VIEW gold.gold_empresas_provincia AS
SELECT
    g.provincia,
    COUNT(d.id) AS empresas_registradas,
    CASE
        WHEN COUNT(d.situacion_legal) = 0 THEN COUNT(d.id)
        ELSE SUM(CASE WHEN LOWER(d.situacion_legal) LIKE '%activa%' THEN 1 ELSE 0 END)
    END AS empresas_activas
FROM silver.fact_supercias_directorio d
JOIN silver.dim_geografia g ON d.id_geo = g.id_geo
GROUP BY g.provincia;

-- =========================================================
-- gold_bachilleres_vs_empresas
-- CORREGIDA: Se usan subconsultas para pre-agregar los datos
-- antes del JOIN. Hacer el JOIN a nivel de millones de registros 
-- y luego agrupar causaba un escaneo anidado infinito en Postgres.
-- =========================================================
DROP VIEW IF EXISTS gold.gold_bachilleres_vs_empresas CASCADE;
CREATE VIEW gold.gold_bachilleres_vs_empresas AS
SELECT
    m.provincia,
    m.total_bachilleres,
    COALESCE(e.empresas_activas, 0) AS empresas_activas,
    CASE
        WHEN COALESCE(e.empresas_activas, 0) = 0 THEN NULL
        ELSE ROUND(m.total_bachilleres::numeric / e.empresas_activas, 2)
    END AS ratio_bachilleres_empresas
FROM (
    SELECT g.provincia, SUM(a.total_estudiantes) AS total_bachilleres
    FROM silver.fact_mineduc_amie a
    JOIN silver.dim_geografia g ON a.id_geo = g.id_geo
    WHERE LOWER(a.nivel_educacion) LIKE '%bachillerato%'
    GROUP BY g.provincia
) m
LEFT JOIN gold.gold_empresas_provincia e ON m.provincia = e.provincia;

-- =========================================================
-- Vista adicional 6to ciclo 1: gold_productividad_vab_empleo
-- CORREGIDA: JOIN por provincia (texto) y ciiu (texto) en lugar de
-- id_geo/id_ciiu, porque VAB y Censo entran con distinto nivel de
-- detalle geográfico (cantón), produciendo id_geo distintos para la
-- misma provincia.
-- =========================================================
DROP VIEW IF EXISTS gold.gold_productividad_vab_empleo CASCADE;
CREATE VIEW gold.gold_productividad_vab_empleo AS
SELECT
    gv.provincia,
    gv.ciiu,
    gv.vab_total_miles_usd,
    COALESCE(gc.personas_ocupadas, 0) AS personas_ocupadas,
    CASE
        WHEN COALESCE(gc.personas_ocupadas, 0) = 0 THEN NULL
        ELSE ROUND(gv.vab_total_miles_usd::numeric / gc.personas_ocupadas, 2)
    END AS vab_por_persona_ocupada
FROM (
    SELECT g.provincia, c.ciiu, SUM(v.vab_miles_usd) AS vab_total_miles_usd
    FROM silver.fact_vab_provincia_industria v
    JOIN silver.dim_geografia g ON v.id_geo = g.id_geo
    JOIN silver.dim_ciiu c ON v.id_ciiu = c.id_ciiu
    GROUP BY g.provincia, c.ciiu
) gv
LEFT JOIN (
    SELECT g.provincia, c.ciiu, SUM(co.personas_ocupadas) AS personas_ocupadas
    FROM silver.fact_censo_ocupacion co
    JOIN silver.dim_geografia g ON co.id_geo = g.id_geo
    JOIN silver.dim_ciiu c ON co.id_ciiu = c.id_ciiu
    GROUP BY g.provincia, c.ciiu
) gc ON gv.provincia = gc.provincia AND gv.ciiu = gc.ciiu;

-- =========================================================
-- Vista adicional 6to ciclo 2: gold_oportunidad_utpl_provincia
-- =========================================================
DROP VIEW IF EXISTS gold.gold_oportunidad_utpl_provincia CASCADE;
CREATE VIEW gold.gold_oportunidad_utpl_provincia AS
SELECT
    provincia,
    total_bachilleres,
    empresas_activas,
    ratio_bachilleres_empresas,
    CASE
        WHEN ratio_bachilleres_empresas >= 50 THEN 'Alta oportunidad'
        WHEN ratio_bachilleres_empresas >= 20 THEN 'Oportunidad media'
        ELSE 'Oportunidad baja'
    END AS nivel_oportunidad
FROM gold.gold_bachilleres_vs_empresas;