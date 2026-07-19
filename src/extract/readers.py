import pandas as pd


def read_excel_file(path, sheet_name=0, header=0, skiprows=None):
    return pd.read_excel(
        path, sheet_name=sheet_name, engine='openpyxl',
        header=header, skiprows=skiprows
    )


def read_csv_file(path, sep=',', encoding='utf-8', low_memory=False, nrows=None):
    return pd.read_csv(path, sep=sep, encoding=encoding, low_memory=low_memory, nrows=nrows)


def read_bce_html_export(path):
    """El BCE exporta algunos indicadores diarios (petróleo WTI, riesgo país)
    como HTML de un gráfico Highcharts, aunque el archivo se llame .xls.
    pandas.read_html lo parsea igual que una tabla normal."""
    tablas = pd.read_html(path)
    return tablas[0]
