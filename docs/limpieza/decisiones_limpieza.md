# Decisiones de limpieza y transformación de datos

Este documento detalla las reglas de Ingeniería de Datos (Data Wrangling) aplicadas a cada fuente para estructurar la capa Silver en PostgreSQL.

## Reglas Generales (Aplicadas a todas las fuentes)
- **Normalización de columnas:** Se estandarizan los nombres de columnas a formato `snake_case`, eliminando mayúsculas, espacios, tildes y diéresis (conservando la `ñ`), y caracteres especiales (ej. "(Millones de USD)").
- **Limpieza de strings geográficos:** Todas las columnas de `provincia` y `canton` se limpian de espacios sobrantes y se formatean en formato Título (`Title Case`) para asegurar consistencias en los cruces (joins) de bases.
- **Conversión Numérica:** Se estandarizan strings numéricos que vienen con comas o puntos (típico de exportes web gubernamentales) para poder ser insertados como `NUMERIC` o `INTEGER` en la base de datos.

## BCE (Banco Central del Ecuador)
- **PIB (Real y Nominal):** Se descartaron las filas iniciales de metadata (`header=9`) y las filas finales de "notas al pie". Se generó una columna `fecha` anclada al 1 de enero de cada año para estandarizar la dimensión temporal.
- **VAB (Valor Agregado Bruto):** La base venía en formato ancho (Wide) con las 21 ramas CIIU como columnas. Se aplicó un des-pivotado masivo con la función `melt()` de Pandas para pasarla a formato largo (Long).
- **Petróleo WTI y Riesgo País:** Los archivos tienen extensión `.xls` pero internamente son tablas HTML exportadas del portal del BCE. Se desarrolló una función especial de lectura (`read_bce_html_export`) y luego se hizo un cruce (`merge`) por fecha para consolidarlos en una sola tabla de hechos.
- **IEE:** Se filtraron las filas iniciales de metadata (`header=7`) y se consolidó su eje temporal.

## INEC (Instituto Nacional de Estadística y Censos)
- **ENEMDU:** Los indicadores laborales venían pivotados. Se aplicó la función `melt()` para pasar las áreas ('nacional', 'urbana', 'rural') a filas, generando la columna `area` y la columna `valor`.
- **Censo 2022 (Ramas de Actividad):** Al igual que VAB, venía con 22 columnas de ramas de actividad CIIU. Se des-pivotó con `melt()`. Además, se filtraron estrictamente las filas que contenían agregaciones previas (como "Total Nacional" o "Total Hombres") para conservar únicamente el detalle atómico de la encuesta y evitar doble contabilización.

## Supercias (Superintendencia de Compañías)
- **Ranking vs. Directorio:** El ranking financiero carece de ciertos identificadores geográficos detallados. Se utilizó el archivo del Directorio de Compañías como tabla puente (Lookup Table) para enriquecer el Ranking con la `provincia` correcta antes de cargarla a la base de datos.

## MINEDUC (Ministerio de Educación)
- **Filtro de Bachillerato:** El dataset original AMIE contiene todos los niveles de educación. Se aplicó un filtro en la columna `nivel_educacion` buscando el string 'bachillerato' para conservar únicamente las instituciones de interés para el análisis de captación universitaria de la UTPL.
