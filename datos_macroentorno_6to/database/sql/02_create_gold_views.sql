-- 02_create_gold_views.sql
-- Vistas Gold obligatorias y adicionales para 6to ciclo

CREATE OR REPLACE VIEW gold.gold_pib_tendencia AS
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

CREATE OR REPLACE VIEW gold.gold_petroleo_30dias AS
SELECT
    t.fecha,
    p.precio_petroleo_wti,
    p.riesgo_pais_pb,
    AVG(p.precio_petroleo_wti) OVER (ORDER BY t.fecha ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS promedio_wti_30dias
FROM silver.fact_petroleo_riesgo p
JOIN silver.dim_tiempo t ON p.id_tiempo = t.id_tiempo;

CREATE OR REPLACE VIEW gold.gold_empleo_tendencia AS
SELECT
    anio,
    periodo,
    indicador,
    area,
    valor
FROM silver.fact_enemdu;

CREATE OR REPLACE VIEW gold.gold_empresas_provincia AS
SELECT
    g.provincia,
    COUNT(d.id) AS empresas_registradas,
    SUM(CASE WHEN LOWER(d.situacion_legal) LIKE '%activa%' THEN 1 ELSE 0 END) AS empresas_activas
FROM silver.fact_supercias_directorio d
JOIN silver.dim_geografia g ON d.id_geo = g.id_geo
GROUP BY g.provincia;

CREATE OR REPLACE VIEW gold.gold_bachilleres_vs_empresas AS
SELECT
    g.provincia,
    SUM(m.total_estudiantes) AS total_bachilleres,
    COALESCE(e.empresas_activas, 0) AS empresas_activas,
    CASE
        WHEN COALESCE(e.empresas_activas, 0) = 0 THEN NULL
        ELSE ROUND(SUM(m.total_estudiantes)::numeric / e.empresas_activas, 2)
    END AS ratio_bachilleres_empresas
FROM silver.fact_mineduc_amie m
JOIN silver.dim_geografia g ON m.id_geo = g.id_geo
LEFT JOIN gold.gold_empresas_provincia e ON g.provincia = e.provincia
WHERE LOWER(m.nivel_educacion) LIKE '%bachillerato%'
GROUP BY g.provincia, e.empresas_activas;

-- Vista adicional 6to ciclo 1
CREATE OR REPLACE VIEW gold.gold_productividad_vab_empleo AS
SELECT
    g.provincia,
    c.ciiu,
    SUM(v.vab_miles_usd) AS vab_total_miles_usd,
    SUM(co.personas_ocupadas) AS personas_ocupadas,
    CASE
        WHEN SUM(co.personas_ocupadas) = 0 THEN NULL
        ELSE ROUND(SUM(v.vab_miles_usd)::numeric / SUM(co.personas_ocupadas), 2)
    END AS vab_por_persona_ocupada
FROM silver.fact_vab_provincia_industria v
JOIN silver.dim_geografia g ON v.id_geo = g.id_geo
JOIN silver.dim_ciiu c ON v.id_ciiu = c.id_ciiu
LEFT JOIN silver.fact_censo_ocupacion co ON co.id_geo = g.id_geo AND co.id_ciiu = c.id_ciiu
GROUP BY g.provincia, c.ciiu;

-- Vista adicional 6to ciclo 2
CREATE OR REPLACE VIEW gold.gold_oportunidad_utpl_provincia AS
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
