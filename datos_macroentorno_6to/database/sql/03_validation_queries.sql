-- 03_validation_queries.sql
-- Consultas simples para validar cargas Silver y vistas Gold

SELECT 'dim_tiempo' AS tabla, COUNT(*) AS registros FROM silver.dim_tiempo;
SELECT 'dim_geografia' AS tabla, COUNT(*) AS registros FROM silver.dim_geografia;
SELECT 'dim_ciiu' AS tabla, COUNT(*) AS registros FROM silver.dim_ciiu;
SELECT 'fact_pib_real_anual' AS tabla, COUNT(*) AS registros FROM silver.fact_pib_real_anual;
SELECT 'fact_enemdu' AS tabla, COUNT(*) AS registros FROM silver.fact_enemdu;

SELECT * FROM gold.gold_pib_tendencia LIMIT 10;
SELECT * FROM gold.gold_bachilleres_vs_empresas LIMIT 10;
