use arrow_array::ArrayRef;
use arrow_schema::{Field, Schema, SchemaRef};
use duckdb::arrow::record_batch::RecordBatch;
use duckdb::{params, DuckdbConnectionManager};
use polars::prelude::*;
use polars_core::utils::accumulate_dataframes_vertical_unchecked;
use pyo3::prelude::*;
use pyo3_polars::PyDataFrame;
use r2d2::Pool;
use std::sync::Arc;

#[pyclass]
struct Database {
    connection_pool: Arc<Pool<DuckdbConnectionManager>>
}

#[pymethods]
impl Database {
    #[new]
    fn new() -> Self {
        let duckdb = DuckdbConnectionManager::memory().unwrap();
        let connection_pool = Pool::new(duckdb).unwrap();

        connection_pool.get().unwrap().execute(
            r"CREATE TABLE person (
                      name            TEXT PRIMARY KEY,
                      age             DOUBLE NOT NULL
                  )
            ", params![]).unwrap();

        Self {
            connection_pool: Arc::new(connection_pool)
        }
    }

    pub fn insert(&self, data: PyDataFrame) {
        let conn = self.connection_pool.get().unwrap();
        // https://duckdb.org/docs/api/rust.html#appender
        // https://docs.rs/duckdb/latest/duckdb/struct.Appender.html
        let mut appender = conn.appender("person").unwrap();

        // https://stackoverflow.com/questions/78084066/arrow-recordbatch-as-polars-dataframe
        // https://stackoverflow.com/questions/78959357/convert-arrow-data-to-polars-dataframe
        // https://stackoverflow.com/questions/78916421/how-to-get-a-polars-series-from-an-arrow-rs-fixedsizelist
        let schema = Schema::new(data.0.schema().to_arrow(CompatLevel::oldest()).into_iter().map(|(_, field)| field.into()).collect::<Vec<Field>>());
        let schema = SchemaRef::new(schema);

        for chunk in data.0.iter_chunks(CompatLevel::oldest(), false) {
            let chunk = chunk.columns().into_iter().map(|array| ArrayRef::from(&**array) ).collect::<Vec<_>>();
            let batch = RecordBatch::try_new(schema.clone(), chunk).unwrap();
            appender.append_record_batch(batch).unwrap();
        }
    }

    pub fn read(&self) -> PyResult<PyDataFrame> {
        let conn = self.connection_pool.get().unwrap();
        let mut stmt = conn.prepare("SELECT name, age FROM person").unwrap();

        // https://stackoverflow.com/questions/78084066/arrow-recordbatch-as-polars-dataframe
        let record_batches = stmt.query_arrow(params![]).unwrap().map(|batch| record_batch_to_dataframe(&batch)).collect::<Result<Vec<_>,PolarsError>>().unwrap();

        // https://docs.rs/polars-core/latest/polars_core/utils/index.html
        let df = accumulate_dataframes_vertical_unchecked(record_batches);

        // https://docs.rs/pyo3-polars/latest/pyo3_polars/
        Ok(PyDataFrame(df))
    }
}

// https://stackoverflow.com/questions/78084066/arrow-recordbatch-as-polars-dataframe
// https://stackoverflow.com/questions/78959357/convert-arrow-data-to-polars-dataframe
// https://stackoverflow.com/questions/78916421/how-to-get-a-polars-series-from-an-arrow-rs-fixedsizelist
fn record_batch_to_dataframe(batch: &RecordBatch) -> Result<DataFrame, PolarsError> {
    let schema = batch.schema();
    let mut columns = Vec::with_capacity(batch.num_columns());
    for (i, column) in batch.columns().iter().enumerate() {
        columns.push(Series::from_arrow_rs(PlSmallStr::from(schema.fields().get(i).unwrap().name().clone()), column)?);
    }
    Ok(DataFrame::from_iter(columns))
}

#[pymodule]
fn duckdb_pyo3_example(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<Database>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_database() {
        let database = Database::new();

        let df = df!("name" => ["Alice", "Bob", "Charlie"], "age" =>[42.2, 43.5, 44.0]).unwrap();

        database.insert(PyDataFrame(df.clone()));

        let result = database.read().unwrap().0;

        assert_eq!(df, result);

        println!("{:?}", result);
    }
}