use std::io::Cursor;
use duckdb::{params, DuckdbConnectionManager};
use polars::prelude::*;
use polars_core::utils::accumulate_dataframes_vertical_unchecked;
use pyo3::prelude::*;
use pyo3_polars::PyDataFrame;
use r2d2::Pool;
use std::sync::Arc;
use arrow_schema::ArrowError;
use polars_arrow::io::ipc::read::{read_stream_metadata, StreamState};
use polars_arrow::io::ipc::write::WriteOptions;

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

        polars_dataframe_to_arrow_record_batch(data.0).unwrap().into_iter().for_each(|batch| {
            appender.append_record_batch(batch).unwrap();
        });

    }

    pub fn read(&self) -> PyResult<PyDataFrame> {
        let conn = self.connection_pool.get().unwrap();
        let mut stmt = conn.prepare("SELECT name, age FROM person").unwrap();

        // https://stackoverflow.com/questions/78084066/arrow-recordbatch-as-polars-dataframe
        let record_batches = stmt.query_arrow(params![]).unwrap().map(|batch| record_batch_to_dataframe(batch)).collect::<anyhow::Result<Vec<_>>>().unwrap().into_iter().flatten().collect::<Vec<_>>();

        // https://docs.rs/polars-core/latest/polars_core/utils/index.html
        let df = accumulate_dataframes_vertical_unchecked(record_batches);

        // https://docs.rs/pyo3-polars/latest/pyo3_polars/
        Ok(PyDataFrame(df))
    }
}

// https://stackoverflow.com/questions/78084066/arrow-recordbatch-as-polars-dataframe
// https://stackoverflow.com/questions/78959357/convert-arrow-data-to-polars-dataframe
// https://stackoverflow.com/questions/78916421/how-to-get-a-polars-series-from-an-arrow-rs-fixedsizelist
fn record_batch_to_dataframe(batch: arrow_array::RecordBatch) -> anyhow::Result<Vec<DataFrame>> {
    let batches = arrow_record_batch_to_polars_record_batch(batch)?;
    let x = batches.into_iter().map(|(batch,schema)| DataFrame::try_from((batch,&schema))).collect::<Result<Vec<_>,PolarsError>>()?;
    Ok(x)

}


// Reference for conversions:
// https://arrow.apache.org/docs/python/ipc.html
// https://docs.rs/polars-io/latest/polars_io/ipc/index.html
// https://arrow.apache.org/rust/arrow_ipc/index.html

fn polars_dataframe_to_arrow_record_batch(df: DataFrame) -> anyhow::Result<Vec<arrow_array::RecordBatch>> {
    let arrow_schema = df.schema().to_arrow(CompatLevel::oldest());
    Ok(df.iter_chunks(CompatLevel::oldest(),false).map(|chunk| {
        polars_record_batch_to_arrow_record_batch(chunk, &arrow_schema).unwrap()
    }).flatten().collect())
}

fn arrow_record_batch_to_polars_record_batch(batch: arrow_array::RecordBatch) -> anyhow::Result<Vec<(polars_arrow::record_batch::RecordBatch,ArrowSchema)>> {
    let mut buffer = Vec::new();

    {
        let mut writer = arrow_ipc::writer::StreamWriter::try_new(&mut buffer, &batch.schema())?;
        writer.write(&batch)?;
        writer.finish()?;
    }

    let mut cursor = Cursor::new(buffer);

    let metadata = read_stream_metadata(&mut cursor)?;
    let mut reader = polars_arrow::io::ipc::read::StreamReader::new(cursor, metadata.clone(), None);

    let mut result = Vec::new();

    while let Some(batch) = reader.next() {
        let schema = metadata.schema.clone();
        match batch? {
            StreamState::Waiting => {
                break;
            }
            StreamState::Some(batch) => {
                result.push((batch, schema));
            }
        }

    }

    Ok(result)
}

fn polars_record_batch_to_arrow_record_batch(batch: polars_arrow::record_batch::RecordBatch, schema: &ArrowSchema) -> anyhow::Result<Vec<arrow_array::RecordBatch>> {
    let mut buffer = Vec::new();

    {
        let mut writer = polars_arrow::io::ipc::write::StreamWriter::new(&mut buffer, WriteOptions::default());
        writer.start(&schema, None)?;
        writer.write(&batch, None)?;
        writer.finish()?;
    }

    let cursor = Cursor::new(buffer);

    let reader = arrow_ipc::reader::StreamReader::try_new(cursor,None)?;

    Ok(reader.collect::<Result<Vec<_>,ArrowError>>()?)
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