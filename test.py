import duckdb_pyo3_example
import polars as pl

database = duckdb_pyo3_example.Database()

df = pl.DataFrame(
    {
        "name": ["Alice", "Ben", "Chloe", "Daniel"],
        "age": [12.0, 15.2, 18.8, 20.4]
    }
)

database.insert(df)

data = database.read()

assert data.is_empty() == False

print(data)