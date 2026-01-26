# 🎧 Spotify Data Engineering Project (Azure)

![Azure](https://img.shields.io/badge/Azure-Data%20Engineering-blue)
![ADF](https://img.shields.io/badge/Azure-Data%20Factory-orange)
![Databricks](https://img.shields.io/badge/Databricks-PySpark-red)
![Delta](https://img.shields.io/badge/Delta-Lake-green)
![Status](https://img.shields.io/badge/Status-Inprogress-success)

---

## 📌 Overview
This project showcases an **end-to-end Azure Data Engineering pipeline** built to process **Spotify streaming datasets**.  
The primary focus is on **duplicate data detection, data quality enforcement, and scalable analytics delivery** using **Azure-native services**.

---

## 🏗️ Architecture
The solution follows the **Medallion Architecture** to ensure data reliability and performance.

### 🥉 Bronze Layer
- Raw Spotify data ingestion (CSV/JSON)
- Stored in **Azure Data Lake Storage Gen2**
- Orchestrated via **Azure Data Factory**

### 🥈 Silver Layer
- Data cleansing and schema standardization
- **Duplicate record removal using PySpark**
- Delta Lake used for ACID compliance

### 🥇 Gold Layer
- Aggregated, analytics-ready datasets
- Served via **Azure Synapse Analytics**

---

## ⚙️ Tech Stack
| Layer | Technology |
|-----|-----------|
| Ingestion | Azure Data Factory |
| Storage | Azure Data Lake Storage Gen2 |
| Processing | Azure Databricks (PySpark) |
| Warehouse | Azure Synapse Analytics |
| Format | Delta Lake |

---

## 🔄 Pipeline Flow
1. Ingest raw Spotify data into ADLS Gen2  
2. Validate schema and metadata  
3. Detect and eliminate duplicate records  
4. Store cleansed data in Delta format  
5. Aggregate data for analytics  
6. Query curated datasets using Synapse  

---

## ✨ Key Features
- ✔ End-to-end automated pipeline  
- ✔ Duplicate data detection & removal  
- ✔ Idempotent and re-runnable workflows  
- ✔ Scalable medallion architecture  
- ✔ Enterprise-grade data quality handling  

---

## 📊 Analytics & Use Cases
- Top streamed tracks and artists  
- Popularity trend analysis  
- User listening behavior insights  
- BI-ready datasets for reporting tools  

---

## 📁 Project Structure
```text
spotify-data-engineering-project/
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── adf/
│   └── pipelines/
├── databricks/
│   └── notebooks/
├── synapse/
│   └── sql/
└── README.md
