import pandas as pd


def read_excel_file(path, sheet_name=0):
    return pd.read_excel(path, sheet_name=sheet_name, engine='openpyxl')


def read_csv_file(path, sep=',', encoding='utf-8'):
    return pd.read_csv(path, sep=sep, encoding=encoding)
