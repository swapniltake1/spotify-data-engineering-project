# Spotify Data Engineering Project

![Azure](https://img.shields.io/badge/Cloud-Azure-0078D4)
![ADF](https://img.shields.io/badge/Orchestration-Azure%20Data%20Factory-FF7F00)
![Databricks](https://img.shields.io/badge/Compute-Databricks-EA4335)
![Delta](https://img.shields.io/badge/Storage-Delta%20Lake-0F9D58)
![Status](https://img.shields.io/badge/Status-Active-success)

An end-to-end data engineering project that ingests Spotify-style dimensional/fact data from Azure SQL, incrementally lands it in ADLS Gen2, and curates silver/gold models in Databricks using streaming CDC patterns.

---

## 1) Project Overview

This repository demonstrates a modern Azure-native analytics pipeline with:

- **Incremental ingestion from Azure SQL** using Azure Data Factory (ADF).
- **Bronze landing in ADLS Gen2** in Parquet format.
- **CDC watermark tracking** per table using JSON metadata files.
- **Silver/Gold processing in Databricks** with Delta Live Tables (DLT)-style transformations.
- **SCD Type 2 handling** for dimensions and fact stream updates.

The primary business entities in the model are:

- `DimUser`
- `DimArtist`
- `DimTrack`
- `DimDate`
- `FactStream`

---

## 2) High-Level Architecture

```text
Azure SQL (source tables)
        |
        v
Azure Data Factory (incremental copy + CDC control)
        |
        v
ADLS Gen2 / bronze (Parquet data + cdc.json)
        |
        v
Databricks (silver tables)
        |
        v
Databricks DLT / gold tables (SCD Type 2)
```

### Key platform components

- **Azure Data Factory** for orchestration and incremental extraction.
- **Azure SQL Database** as operational source.
- **Azure Data Lake Storage Gen2** as landing and metadata store.
- **Databricks Asset Bundle** for reproducible pipeline/job deployment.

---

## 3) Repository Structure

```text
.
├── pipeline/                     # ADF pipelines (single-table + loop versions)
├── dataset/                      # ADF dataset definitions (dynamic Parquet/JSON)
├── linkedService/                # ADF linked services (Azure SQL + ADLS)
├── files/                        # Utility files such as cdc.json templates
├── sql/                          # Source schema + sample load scripts
└── databricks/
    ├── resources/                # Databricks pipeline/job resource definitions
    ├── src/gold/dlt/transformations/
    │   ├── DimArtist.py
    │   ├── DimDate.py
    │   ├── DimTrack.py
    │   ├── DimUser.py
    │   └── FactStream.py
    ├── tests/                    # Pytest sample tests
    ├── pyproject.toml            # Python project + developer dependencies
    └── databricks.yml            # Bundle targets (dev/prod)
```

---

## 4) Data Model

The project uses a star-schema-like model:

- **Dimensions**: `DimUser`, `DimArtist`, `DimTrack`, `DimDate`
- **Fact**: `FactStream`

`sql/spotify_initial_load.sql` contains DDL for all tables and large seed datasets for initial testing. `sql/spotify_incremental_load.sql` provides additional inserts to simulate incremental arrivals.

---

## 5) Incremental Ingestion (ADF)

The ADF pipelines implement watermark-based ingestion with CDC metadata files:

### Core behavior

1. Read last watermark (`cdc`) from `bronze/<table>_CDC/cdc.json`.
2. Extract only rows where `cdc_col > last_watermark` from Azure SQL.
3. Write the increment to `bronze/<table>/<table>_<utc_timestamp>` in Parquet.
4. If rows were ingested, compute latest source max(cdc_col) and overwrite `cdc.json`.
5. If no rows were ingested, delete the empty landing artifact.

### Pipeline variants

- `pipeline/incremental_ingestion.json`: parameterized single-table flow.
- `pipeline/incremental_ingestion_loop.json`: `ForEach` loop over multiple tables.
- `pipeline/incremental_ingestion_loop_webactivity.json`: loop + failure Web Activity callback.

Default loop input includes all five core tables with table-specific CDC columns (`updated_at`, `date`, `stream_timestamp`).

---

## 6) Databricks Processing

Gold DLT transformation modules in `databricks/src/gold/dlt/transformations/`:

- Read streaming data from `spotify-catalog.silver.*` source tables.
- Create streaming target tables (`dimuser`, `dimartist`, `dimtrack`, `dimdate`, `factstream`).
- Apply `create_auto_cdc_flow(...)` with:
  - business keys (`user_id`, `artist_id`, etc.)
  - sequence columns (`updated_at`, `date`, `stream_timestamp`)
  - `stored_as_scd_type = 2`

`DimUser.py` also enforces a quality expectation (`user_id is not null`) using `dlt.expect_all_or_drop`.

---

## 7) Deployment and Execution

### A) SQL source setup

- Run `sql/spotify_initial_load.sql` once to create and seed tables.
- Run `sql/spotify_incremental_load.sql` to simulate later increments.

### B) ADF setup

1. Import linked services from `linkedService/`.
2. Import datasets from `dataset/`.
3. Import pipeline JSON from `pipeline/`.
4. Create initial CDC files in ADLS using `files/cdc.json` / `files/empty.json` conventions.
5. Trigger pipeline with table parameters or loop array.

### C) Databricks setup

From `databricks/`:

```bash
uv sync --dev

databricks bundle deploy --target dev
# or
# databricks bundle deploy --target prod

databricks bundle run
```

The bundle defines both **dev** and **prod** targets and deploys resources declared in `databricks/resources/`.

---

## 8) Testing and Quality

A sample pytest test is included under `databricks/tests/` to validate local Databricks-connected execution patterns.

```bash
cd databricks
uv run pytest
```

You can extend tests to validate schema drift handling, CDC idempotency, and expectation metrics.

---

## 9) Productionization Recommendations

To harden this project for enterprise use:

- Move secrets/credentials to **Azure Key Vault** + managed identities.
- Add CI/CD for ADF JSON and Databricks bundle deployments.
- Add data quality dashboards (expectation pass/fail trends).
- Introduce partitioning/OPTIMIZE/ZORDER strategies for large `FactStream` volumes.
- Add observability for ADF + Databricks runs (alerts, SLA checks, retries).

---

## 10) Authoring Notes

This project combines ADF metadata-driven ingestion with Databricks CDC/SCD processing to illustrate a complete medallion-style analytics workflow for music streaming behavior. Thanks for visiting
