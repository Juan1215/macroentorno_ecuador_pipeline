# Pipeline de Datos del Macroentorno Ecuador — 6to ciclo

Repositorio privado para el reto final de la línea de Datos: Ingeniería, Analítica y Visualización.

## Objetivo
Construir un pipeline reproducible para procesar fuentes públicas del macroentorno ecuatoriano, cargarlas en PostgreSQL bajo un modelo relacional Silver, generar vistas Gold y conectar un dashboard de Power BI con tres páginas analíticas.

## Alcance de 6to ciclo

- PostgreSQL como base de datos.
- Tres bloques completos de fuentes: BCE, INEC, Supercias y MINEDUC.
- Mínimo doce tablas Silver.
- Vistas Gold base más dos vistas adicionales.
- Integración con RPA desde `data/raw/rpa_inbox/`.
- Dashboard de tres páginas con filtros, KPIs y análisis ejecutivo.
- Documentación técnica y acuerdo de integración con RPA.

## Estructura del proyecto

```text
datos_macroentorno_6to/
├── data/
│   ├── raw/manual/           # Archivos descargados manualmente
│   ├── raw/rpa_inbox/        # Archivos enviados por el equipo RPA
│   ├── bronze/               # Copia controlada de crudos recibidos
│   ├── rejected/             # Archivos rechazados por validación
│   └── catalog/              # Diccionario de fuentes y columnas esperadas
├── database/
│   ├── sql/                  # DDL, vistas Gold, validaciones y permisos
│   └── er/                   # Diagrama entidad-relación
├── src/
│   ├── extract/              # Lectura de Excel/CSV y registro de archivos
│   ├── transform/            # Limpieza por fuente
│   ├── load/                 # Carga a PostgreSQL
│   ├── gold/                 # Ejecución de vistas Gold
│   ├── watchers/             # Detección de archivos nuevos de RPA
│   └── utils/                # Funciones comunes
├── dashboard/                # Power BI y capturas
├── docs/                     # Arquitectura, limpieza, integración e informe
├── tests/                    # Pruebas simples
└── logs/                     # Registro de ejecuciones
```

## Instalación

```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash en Windows
pip install -r requirements.txt
```

## Configuración

Copia `.env.example` como `.env` y completa tus datos de PostgreSQL:

```bash
cp .env.example .env
```

## Crear base de datos

Ejecuta los scripts SQL en este orden:

```text
database/sql/00_create_schema.sql
database/sql/01_create_silver_tables.sql
database/sql/02_create_gold_views.sql
database/sql/03_validation_queries.sql
database/sql/04_roles_permissions.sql
```

## Ejecutar pipeline manual

```bash
python -m src.pipeline --mode manual
```

## Ejecutar monitoreo RPA

```bash
python -m src.watchers.rpa_watcher
```

## Dashboard

El archivo `.pbix` debe guardarse en:

```text
dashboard/powerbi/
```

Power BI debe conectarse a las vistas Gold, no directamente a archivos Excel o CSV.

## Entregables relacionados

Este repositorio cubre el entregable: **Repositorio GitHub privado con módulos ETL, DDL SQL y README**.
