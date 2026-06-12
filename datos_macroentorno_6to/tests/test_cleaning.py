import pandas as pd
from src.utils.cleaning import normalize_column_names, remove_duplicates


def test_normalize_column_names():
    df = pd.DataFrame({'Nombre Columna': [1]})
    result = normalize_column_names(df)
    assert 'nombre_columna' in result.columns


def test_remove_duplicates():
    df = pd.DataFrame({'a': [1, 1, 2]})
    result = remove_duplicates(df)
    assert len(result) == 2
