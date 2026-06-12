def load_dataframe(df, table_name, engine, schema='silver', if_exists='append'):
    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists=if_exists,
        index=False
    )
