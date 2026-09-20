# Spotify Data Engineering Project

![Azure](https://img.shields.io/badge/Cloud-Azure-0078D4)
![ADF](https://img.shields.io/badge/Orchestration-Azure%20Data%20Factory-FF7F00)
![Databricks](https://img.shields.io/badge/Compute-Databricks-EA4335)
![Delta](https://img.shields.io/badge/Storage-Delta%20Lake-0F9D58)
![DLT](https://img.shields.io/badge/Processing-Delta%20Live%20Tables-8E44AD)
![Status](https://img.shields.io/badge/Status-Active-success)

An end-to-end Azure data engineering project that incrementally ingests Spotify-style dimensional and fact data from Azure SQL, lands it in ADLS Gen2, and processes it in Databricks using streaming CDC patterns and SCD Type 2 transformations.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Data Model](#data-model)
- [Incremental Ingestion](#incremental-ingestion-adf)
- [Databricks Processing](#databricks-processing)
- [Repository Structure](#repository-structure)
- [Deployment and Execution](#deployment-and-execution)
- [Testing and Quality](#testing-and-quality)
- [Productionization](#productionization-recommendations)
- [Future Enhancements](#future-enhancements)
- [Author](#author)

---

## Project Overview

This repository demonstrates a modern Azure-native data platform for music streaming analytics.

The pipeline combines:

- **Azure SQL Database** as the source system.
- **Azure Data Factory** for metadata-driven incremental ingestion.
- **ADLS Gen2** for Bronze landing and CDC control metadata.
- **Azure Databricks** for Silver and Gold processing.
- **Delta Live Tables** for streaming CDC and curated target tables.
- **SCD Type 2** handling for historical dimension and fact changes.
- **Databricks Asset Bundles** for repeatable deployment across environments.

Core business entities:

- `DimUser`
- `DimArtist`
- `DimTrack`
- `DimDate`
- `FactStream`

---

## Architecture

### High-Level Architecture

```mermaid
flowchart LR
    A["Azure SQL Source"] --> B["Azure Data Factory"]
    B --> C["ADLS Gen2 Bronze"]
    C --> D["Databricks Silver"]
    D --> E["Delta Live Tables / Gold"]
    E --> F["SCD Type 2 Tables"]
    F --> G["Analytics / BI"]
    B --> H["CDC Control Metadata"]
    H --> B

    style A fill:#dbeafe,stroke:#333,stroke-width:1px
    style B fill:#bbf,stroke:#333,stroke-width:1px
    style C fill:#eee,stroke:#333,stroke-width:1px
    style D fill:#ffedd5,stroke:#333,stroke-width:1px
    style E fill:#e0e7ff,stroke:#333,stroke-width:1px
    style F fill:#dfd,stroke:#333,stroke-width:1px
    style G fill:#dbeafe,stroke:#333,stroke-width:1px
    style H fill:#fde68a,stroke:#333,stroke-width:1px
```

### End-to-End Data Flow

```mermaid
flowchart TD
    Source["Azure SQL Tables"] --> Lookup["Read Last CDC Watermark"]
    Lookup --> MaxCDC["Read Current Max CDC Value"]
    MaxCDC --> Filter{"New Records Available?"}
    Filter -->|Yes| Copy["ADF Incremental Copy"]
    Copy --> Bronze["ADLS Gen2 Bronze Parquet"]
    Bronze --> Silver["Databricks Silver Tables"]
    Silver --> Gold["DLT Gold Transformations"]
    Gold --> CDC["Auto CDC / SCD Type 2"]
    CDC --> Analytics["Analytics Ready Tables"]
    Analytics --> BI["BI / Reporting"]
    Copy --> Update["Update cdc.json"]
    Update --> Lookup
    Filter -->|No| Skip["No Incremental Data"]

    style Source fill:#dbeafe
    style Lookup fill:#bbf
    style MaxCDC fill:#c7d2fe
    style Filter fill:#fde68a
    style Copy fill:#bbf
    style Bronze fill:#eee
    style Silver fill:#ffedd5
    style Gold fill:#e0e7ff
    style CDC fill:#dfd
    style Analytics fill:#ecfdf5
    style BI fill:#dbeafe
    style Update fill:#fff7ed
    style Skip fill:#fee2e2
```

### Detailed Platform Architecture

```mermaid
flowchart TD
    subgraph Source["Source Layer"]
        SQL["Azure SQL Database"]
        Initial["spotify_initial_load.sql"]
        Increment["spotify_incremental_load.sql"]
    end

    subgraph ADF["Azure Data Factory"]
        Single["incremental_ingestion"]
        Loop["incremental_ingestion_loop"]
        Callback["Loop + Failure Web Activity"]
    end

    subgraph Storage["ADLS Gen2"]
        Bronze["Bronze Table Folders"]
        CDC["cdc.json Control Files"]
    end

    subgraph DBX["Azure Databricks"]
        Silver["Silver Tables"]
        DLT["Delta Live Tables"]
        User["DimUser"]
        Artist["DimArtist"]
        Track["DimTrack"]
        Date["DimDate"]
        Fact["FactStream"]
        Bundle["Databricks Asset Bundle"]
    end

    subgraph Consumption["Consumption"]
        Analytics["SQL / Analytics"]
        BI["BI / Dashboards"]
    end

    Initial --> SQL
    Increment --> SQL
    SQL --> Single
    SQL --> Loop
    Single --> Bronze
    Loop --> Bronze
    Callback --> Loop
    CDC --> Single
    CDC --> Loop
    Bronze --> Silver
    Silver --> DLT
    DLT --> User
    DLT --> Artist
    DLT --> Track
    DLT --> Date
    DLT --> Fact
    Bundle --> DLT
    User --> Analytics
    Artist --> Analytics
    Track --> Analytics
    Date --> Analytics
    Fact --> Analytics
    Analytics --> BI
    Bronze --> CDC

    style SQL fill:#dbeafe
    style Single fill:#bbf
    style Loop fill:#c7d2fe
    style Callback fill:#fff7ed
    style Bronze fill:#eee
    style CDC fill:#fde68a
    style Silver fill:#ffedd5
    style DLT fill:#e0e7ff
    style User fill:#ecfdf5
    style Artist fill:#ecfdf5
    style Track fill:#ecfdf5
    style Date fill:#ecfdf5
    style Fact fill:#dfd
    style Bundle fill:#eef2ff
    style Analytics fill:#dbeafe
    style BI fill:#dcfce7
```

### Architecture Notes

- **Azure SQL** contains the source dimensional and streaming data.
- **ADF** performs metadata-driven, watermark-based incremental extraction.
- **ADLS Bronze** stores each incremental batch as Parquet.
- **CDC metadata** is maintained in `cdc.json` files for table-level watermark tracking.
- **Databricks Silver** provides the curated processing layer.
- **DLT** builds streaming targets and applies automated CDC handling.
- **SCD Type 2** preserves historical changes for supported entities.
- **Asset Bundles** provide repeatable Databricks resource deployment.
- **Analytics / BI** consumes the curated Gold datasets.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Source | Azure SQL Database |
| Ingestion | Azure Data Factory |
| Data Lake | Azure Data Lake Storage Gen2 |
| Processing | Azure Databricks |
| Transformation | Delta Live Tables |
| Language | Python / PySpark / SQL |
| Storage Format | Parquet / Delta |
| Change Data | CDC / Auto CDC |
| History | SCD Type 2 |
| Deployment | Databricks Asset Bundles |
| Testing | Pytest |

---

## Data Model

The project uses a star-schema-like structure:

### Dimensions

- `DimUser`
- `DimArtist`
- `DimTrack`
- `DimDate`

### Fact

- `FactStream`

```mermaid
erDiagram
    FACTSTREAM }o--|| DIMUSER : user_id
    FACTSTREAM }o--|| DIMARTIST : artist_id
    FACTSTREAM }o--|| DIMTRACK : track_id
    FACTSTREAM }o--|| DIMDATE : date

    DIMUSER {
        string user_id
        string user_name
        string country
    }

    DIMARTIST {
        string artist_id
        string artist_name
        string genre
    }

    DIMTRACK {
        string track_id
        string track_name
        string artist_id
    }

    DIMDATE {
        date date
        int year
        int month
    }

    FACTSTREAM {
        string stream_id
        string user_id
        string artist_id
        string track_id
        timestamp stream_timestamp
    }
```

> The diagram represents the logical model documented by the project. Exact physical column definitions should be validated against the deployed SQL and Databricks schemas.

---

## Incremental Ingestion (ADF)

The ADF layer implements watermark-based incremental ingestion for multiple tables.

### Processing Pattern

1. Read the previous CDC watermark from `bronze/<table>_CDC/cdc.json`.
2. Query Azure SQL using the table-specific CDC column.
3. Extract only rows where `cdc_col > last_watermark`.
4. Write the increment to `bronze/<table>/<timestamp>` in Parquet.
5. Calculate the latest source CDC value when rows are ingested.
6. Overwrite `cdc.json` with the latest watermark.
7. Remove empty landing artifacts when no rows are available.

### Pipeline Variants

- `pipeline/incremental_ingestion.json` - parameterized single-table ingestion.
- `pipeline/incremental_ingestion_loop.json` - metadata-driven multi-table ingestion.
- `pipeline/incremental_ingestion_loop_webactivity.json` - multi-table loop with failure callback handling.

The loop supports table-specific CDC columns such as `updated_at`, `date`, and `stream_timestamp`.

---

## Databricks Processing

The Gold transformation modules are located under:

`databricks/src/gold/dlt/transformations/`

### Processing Pattern

- Read streaming data from `spotify-catalog.silver.*` sources.
- Build streaming target tables for dimensions and facts.
- Apply `create_auto_cdc_flow(...)` for change processing.
- Use business keys and sequence columns for deterministic change application.
- Store changes as **SCD Type 2** where configured.

### Data Quality

`DimUser.py` includes a quality expectation that drops records where `user_id` is null.

---

## Repository Structure

```text
.
├── pipeline/
│   ├── incremental_ingestion.json
│   ├── incremental_ingestion_loop.json
│   └── incremental_ingestion_loop_webactivity.json
├── dataset/
│   └── ... ADF dataset definitions
├── linkedService/
│   └── ... Azure SQL and ADLS connections
├── files/
│   ├── cdc.json
│   └── empty.json
├── sql/
│   ├── spotify_initial_load.sql
│   └── spotify_incremental_load.sql
└── databricks/
    ├── resources/
    ├── src/gold/dlt/transformations/
    │   ├── DimArtist.py
    │   ├── DimDate.py
    │   ├── DimTrack.py
    │   ├── DimUser.py
    │   └── FactStream.py
    ├── tests/
    ├── pyproject.toml
    └── databricks.yml
```

---

## Deployment and Execution

### SQL Source Setup

Run the initial script once:

```bash
sql/spotify_initial_load.sql
```

Use the incremental script to simulate subsequent source arrivals:

```bash
sql/spotify_incremental_load.sql
```

### ADF Setup

1. Import linked services from `linkedService/`.
2. Import datasets from `dataset/`.
3. Import pipelines from `pipeline/`.
4. Create the initial CDC metadata files in ADLS.
5. Trigger the parameterized pipeline or multi-table loop.

### Databricks Setup

From the `databricks/` directory:

```bash
uv sync --dev
databricks bundle deploy --target dev
databricks bundle run
```

For production-style deployment:

```bash
databricks bundle deploy --target prod
```

---

## Testing and Quality

Run the included pytest tests:

```bash
cd databricks
uv run pytest
```

Recommended additional test coverage:

- CDC watermark progression.
- Duplicate and idempotent ingestion.
- Schema drift handling.
- SCD Type 2 history validation.
- Data quality expectation results.
- End-to-end Bronze to Gold verification.

---

## Productionization Recommendations

For production workloads, consider:

- Azure Key Vault and managed identities for secrets.
- Centralized monitoring for ADF and Databricks.
- Retry policies and pipeline failure notifications.
- Data quality scorecards and expectation monitoring.
- Partitioning and optimization for large `FactStream` volumes.
- Automated CI/CD for ADF artifacts and Databricks Bundles.
- Schema evolution and late-arriving data handling.
- Data lineage and governance through Unity Catalog.

---

## Future Enhancements

- Metadata-driven source configuration across additional domains.
- More robust late-arriving CDC handling.
- Automated data quality dashboards.
- Enhanced BI semantic modeling.
- Full CI/CD pipeline for Azure and Databricks components.
- Performance benchmarks for streaming and incremental workloads.

---

## Author

**Swapnil Take**  
Azure Data Engineer | Azure Data Factory | Azure Databricks | PySpark | SQL | ADLS Gen2 | Delta Lake
