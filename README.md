# Duckdb Pyo3 Example

This repository shows how to use embedded DuckDB and call it from Python, by compiling it as a python package with Pyo3 in a Rust.

**Benchmark for Apache Arrow Flight and JSON communication can be found in the [benchmark/server](benchmark/server/readme.md) folder.**

The repo is covering examples for:
- Configuring a Docker Container for building Rust with Pyo3 on Windows.
- Configuring a Docker Container for building Rust with Pyo3 on Linux (Debian).
- Embedding DuckDB in Python package with Pyo3 and Rust.
- Using r2d2 pools to manage DuckDB connections in Rust.
- Passing data between Python and Rust using Polars Data Frames.
- Storing Polars Data Frame data in rust using DuckDB, with Apache Arrow DuckDB Appender, by converting Polars Data Frame to Record Batch.
- Reading data from DuckDB in Rust as Polars Data Frame, with Apache Arrow query, by converting Record Batch to Polars Data Frame.

As the goal is to show how to work with DuckDB, Polars and Python, the example does not cover Python pip publish, only local development version is built. For such details, please check [Maturin](https://www.maturin.rs/) documentation.

## Test

- You can check the examples by executing the unit test in the Rust code.
- You can check the examples by executing the Python code `test.py` after build was successful.

For building please check [Maturin](https://www.maturin.rs/) and the tools required in the next session. Or check the Docker files reference.

For installing Python dependencies, please use [Poetry](https://python-poetry.org/). It is not used for building the package, but it is used for downloading Python dependencies (`poetry install --no-interaction --no-root`).

## Docker

Build Linux Docker container:

    docker build -f container.linux.Dockerfile -t duckdb_pyo3_example_linux .
    docker run -it --rm duckdb_pyo3_example_linux


Build Window Docker container:

    docker build -f container.win.Dockerfile -t duckdb_pyo3_example_win .
    docker run -it --rm duckdb_pyo3_example_win

## Tools an Libs

- [Rust](https://www.rust-lang.org/): Rust programming language.
- [rustup.rs](https://rustup.rs/): Rust installer.
- [DuckDB](https://duckdb.org/): Embedded database.
- [duckdb-rs](https://github.com/duckdb/duckdb-rs): Rust bindings for DuckDB.
- [Pyo3](https://pyo3.rs/): Rust bindings for Python.
- [Maturin](https://www.maturin.rs/): Compiler tool for Python packages written ir Rust with Pyo3 . Check the tutorial for more details.
- [Polars](https://pola.rs/): Data manipulation library in Rust.

## References

### Rust and Pyo3

References for the implemented example Python package in Rust with Pyo3.

- Stack Overflow questions:
  - [Arrow RecordBatch as Polars DataFrame](https://stackoverflow.com/questions/78084066/arrow-recordbatch-as-polars-dataframe)
  - [Convert Arrow Data to Polars DataFrame](https://stackoverflow.com/questions/78959357/convert-arrow-data-to-polars-dataframe)
  - [How to get a polars Series from an arrow_rs FixedSizeList?](https://stackoverflow.com/questions/78916421/how-to-get-a-polars-series-from-an-arrow-rs-fixedsizelist)
  - [What are use cases for "poetry install --no-root"?](https://stackoverflow.com/questions/77757777/what-are-use-cases-for-poetry-install-no-root)
- https://docs.rs/pyo3-polars/latest/pyo3_polars/
- [Rust polars crate Module polars_core::utils](https://docs.rs/polars-core/latest/polars_core/utils/index.html): Polars utils documentation, covering:
  - `accumulate_dataframes_vertical_unchecked`
  - `accumulate_dataframes_vertical_unchecked_optional`
- [DuckDB Rust API](https://duckdb.org/docs/api/rust.html): DuckDB Rust API documentation.
- [DuckDB Appender](https://duckdb.org/docs/data/appender.html): DuckDB Appender documentation.
- [Rust duckdb crate Struct Appender](https://docs.rs/duckdb/latest/duckdb/struct.Appender.html): DuckDB Appender Rust API documentation.
- Apache Arrow And Polars documentation:
  - [Apache Arrow IPC](https://arrow.apache.org/docs/python/ipc.html)
  - [Polars IPC](https://docs.rs/polars-io/latest/polars_io/ipc/index.html)
  - [Rust Arrow IPC](https://arrow.apache.org/rust/arrow_ipc/index.html)

### Windows Container

References for building the Python package with Rust and Pyo3 in a Windows Container.

- [Windows Container](https://docs.microsoft.com/en-us/virtualization/windowscontainers/quick-start/quick-start-windows-server): Windows Container quick start guide.
- [Windows Container Python Dockerfile](https://github.com/MicrosoftDocs/Virtualization-Documentation/blob/main/windows-container-samples/python/Dockerfile): Used as example for installing Python.
- [Deploying Rust with Windows Containers on Kubernetes](https://tech.fpcomplete.com/blog/rust-kubernetes-windows/): Used as example for installing Rust.
- [Visual Studio download page](https://visualstudio.microsoft.com/downloads/): Used to find the URL for Build Tools for Visual Studio 2022.
- [Visual Studio Build Tools component directory](https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools?view=vs-2022): Used to find the latest version of Windows SDK.
- [Installing PyArrow / Using Pip](https://arrow.apache.org/docs/python/install.html): "If you encounter any importing issues of the pip wheels on Windows, you may need to install the [Visual C++ Redistributable for Visual Studio 2015](https://www.microsoft.com/en-us/download/details.aspx?id=48145)."
- [Stack Overflow: Install pyarrow in VS Code for Windows](https://stackoverflow.com/questions/74296856/install-pyarrow-in-vs-code-for-windows): Python version is limited to 3.10.x.