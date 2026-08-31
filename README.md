# E-commerce Data Engineering Pipeline

An end-to-end data engineering project that turns raw e-commerce data into clean, analytics-ready datasets, using Python, Azure Data Lake Storage and Azure SQL.

The goal was to build something close to a real production pipeline: raw data comes in, gets cleaned and modeled, moves through cloud storage, and lands in a SQL database ready to be queried or plugged into a BI tool.

## What it does

- Ingests raw e-commerce data (customers, products, orders, transactions)
- Cleans and transforms it with Python and Pandas
- Organizes the data through raw → processed → curated layers
- Uploads processed datasets to Azure Data Lake Storage
- Loads curated data into Azure SQL Database
- Builds a dimensional model (star schema) ready for analytics

## Architecture

<img width="806" height="1483" alt="image" src="https://github.com/user-attachments/assets/5709db9a-e850-49dc-8678-6e706e77b069" />

Data moves through three layers:

- **Raw** — the original source data, untouched
- **Processed** — cleaned and transformed with Pandas
- **Curated** — business-ready, modeled as a star schema

## Data model

The curated layer is organized as a star schema, with one fact table surrounded by three dimensions.

<img width="2221" height="907" alt="image" src="https://github.com/user-attachments/assets/f45a5444-44a7-4078-876f-5c6cf6c3d749" />

**fact_sales** holds the transactional data and metrics. **dim_customer**, **dim_product** and **dim_date** hold the descriptive attributes used to slice and filter it.

Output files:


fact_sales.csv
dim_customer.csv
dim_product.csv
dim_date.csv
df_analytics.csv


## Pipeline steps

1. **Exploration** — Python and Pandas are used to check data types, missing values, and overall data quality before any transformation happens.

2. **Transformation** — The raw dataset is reshaped into the star schema above, cleaning and splitting the data into fact and dimension tables.

3. **Upload to Azure Data Lake** — Processed datasets are pushed to Azure Data Lake / Blob Storage using the Azure Python SDK.

4. **Load to Azure SQL** — The curated tables are loaded into Azure SQL Database through SQLAlchemy.

## Tech stack

| Tool | Role |
|---|---|
| Python | Pipeline logic |
| Pandas | Cleaning & transformation |
| Azure Data Lake Storage | Cloud storage |
| Azure Blob Storage | Dataset staging |
| Azure SQL Database | Analytical database |
| SQLAlchemy | Python ↔ SQL |
| python-dotenv | Environment variables |
## Project structure

```
ecommerce-data-engineering-project/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── curated/
│
├── scripts/
│   ├── explore_data.py
│   ├── upload_to_adls.py
│   └── load_to_azure_sql.py
│
├── notebooks/
├── docs/
│   ├── pipeline-architecture.svg
│   └── star-schema.svg
│
├── .gitignore
├── .gitattributes
└── README.md
```

## Configuration

Credentials are kept out of the repo entirely and loaded from a local `.env` file:

```env
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_SQL_SERVER=your_server
AZURE_SQL_DATABASE=your_database
AZURE_SQL_USERNAME=your_username
AZURE_SQL_PASSWORD=your_password
```

`.env` is listed in `.gitignore` — no keys or passwords are committed here.

## Example analytics

Once loaded, the data can answer questions like:

- What's total revenue, and how is it trending over time?
- What's the average order value?
- Which products and customers drive the most revenue?
- How does purchasing behavior differ across customer segments?

## Possible next steps

- Orchestrate the pipeline with Azure Data Factory
- Add automated data quality checks
- Support incremental loading instead of full refreshes
- Set up CI/CD with GitHub Actions
- Connect a Power BI dashboard on top of the SQL layer
- Add logging and monitoring

## Author

**Moussa Ahmed**
Data Analyst / Data Engineering

Built as a portfolio project to practice designing and shipping an end-to-end cloud data pipeline.
