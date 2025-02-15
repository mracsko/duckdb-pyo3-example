use std::io::Cursor;
use chrono::{TimeDelta, TimeZone, Utc};
use num2words::Num2Words;
use polars::datatypes::{DataType, TimeUnit};
use polars::frame::DataFrame;
use polars::prelude::Column;
use serde_json::Value;
use std::ops::Add;
use polars::prelude::*;
use arrow_schema::ArrowError;
use polars_arrow::io::ipc::read::{read_stream_metadata, StreamState};
use polars_arrow::io::ipc::write::WriteOptions;

#[derive(serde::Serialize, serde::Deserialize)]
pub struct Data {
    pub data: Value,
}

#[derive(Clone)]
pub struct AppState {
    pub data_frame_xxs: DataFrame,
    pub data_frame_xs: DataFrame,
    pub data_frame_s: DataFrame,
    pub data_frame_m: DataFrame,
    pub data_frame_l: DataFrame,
    pub data_frame_xl: DataFrame,
    pub data_frame_xxl: DataFrame,
}

impl AppState {
    pub fn new() -> Self {
        let data_frame_xxs = gen_df(1);
        println!("Generated: `data_frame_xxs`");
        let data_frame_xs = gen_df(10);
        println!("Generated: `data_frame_xs`");
        let data_frame_s = gen_df(100);
        println!("Generated: `data_frame_s`");
        let data_frame_m = gen_df(1000);
        println!("Generated: `data_frame_m`");
        let data_frame_l = gen_df(10000);
        println!("Generated: `data_frame_l`");
        let data_frame_xl = gen_df(100000);
        println!("Generated: `data_frame_xl`");
        let data_frame_xxl = gen_df(1000000);
        println!("Generated: `data_frame_xxl`");

        AppState {
            data_frame_xxs,
            data_frame_xs,
            data_frame_s,
            data_frame_m,
            data_frame_l,
            data_frame_xl,
            data_frame_xxl,
        }
    }
}

pub fn gen_df(lenght: u64) -> DataFrame {
    let date = Utc.with_ymd_and_hms(2021, 1, 1, 0, 0, 0).unwrap();
    let data_frame_column_number =
        Column::new("number".into(), &(1u64..=lenght).collect::<Vec<u64>>());
    let data_frame_column_string = Column::new(
        "string".into(),
        &(1u64..=lenght)
            .map(|i| Num2Words::new(i).to_words().unwrap())
            .collect::<Vec<String>>(),
    );
    let data_frame_column_timestamp = Column::new(
        "timestamp".into(),
        &(1u64..=lenght)
            .map(|_| date.add(TimeDelta::seconds(1)).timestamp_millis())
            .collect::<Vec<i64>>(),
    )
    .cast(&DataType::Datetime(TimeUnit::Milliseconds, None))
    .unwrap();
    DataFrame::new(vec![
        data_frame_column_number,
        data_frame_column_string,
        data_frame_column_timestamp,
    ])
    .unwrap()
}

pub fn polars_dataframe_to_arrow_record_batch(df: DataFrame) -> Vec<arrow_array::RecordBatch> {
    let arrow_schema = df.schema().to_arrow(CompatLevel::oldest());
    let record_batch = df.iter_chunks(CompatLevel::oldest(),false).map(|chunk| {
        polars_record_batch_to_arrow_record_batch(chunk, &arrow_schema).unwrap()
    }).flatten().collect();
    record_batch
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

    let reader = arrow::ipc::reader::StreamReader::try_new(cursor,None)?;

    Ok(reader.collect::<Result<Vec<_>,ArrowError>>()?)
}

pub fn record_batch_to_dataframe(batch: arrow_array::RecordBatch) -> anyhow::Result<Vec<DataFrame>> {
    let batches = arrow_record_batch_to_polars_record_batch(batch)?;
    let x = batches.into_iter().map(|(batch,schema)| DataFrame::try_from((batch,&schema))).collect::<Result<Vec<_>,PolarsError>>()?;
    Ok(x)
}

fn arrow_record_batch_to_polars_record_batch(batch: arrow_array::RecordBatch) -> anyhow::Result<Vec<(polars_arrow::record_batch::RecordBatch,ArrowSchema)>> {
    let mut buffer = Vec::new();

    {
        let mut writer = arrow::ipc::writer::StreamWriter::try_new(&mut buffer, &batch.schema())?;
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
