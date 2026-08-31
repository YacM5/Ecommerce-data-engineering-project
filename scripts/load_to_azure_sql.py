import os
import urllib
from io import StringIO
from pathlib import Path

import pandas as pd
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# 1. CHARGER LE FICHIER .ENV
# ============================================================

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

print("ENV PATH:", env_path)
print("ENV EXISTS:", env_path.exists())


# ============================================================
# 2. RÉCUPÉRER LES VARIABLES ADLS
# ============================================================

azure_connection_string = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

print(
    "AZURE STRING FOUND:",
    azure_connection_string is not None
)

if not azure_connection_string:
    raise ValueError(
        "AZURE_STORAGE_CONNECTION_STRING not found in .env"
    )

container_name = "curated"


# ============================================================
# 3. RÉCUPÉRER LES VARIABLES AZURE SQL
# ============================================================

server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
username = os.getenv("SQL_USERNAME")
password = os.getenv("SQL_PASSWORD")

missing_variables = [
    variable_name
    for variable_name, variable_value in {
        "SQL_SERVER": server,
        "SQL_DATABASE": database,
        "SQL_USERNAME": username,
        "SQL_PASSWORD": password,
    }.items()
    if not variable_value
]

if missing_variables:
    raise ValueError(
        "Variables SQL manquantes dans .env : "
        + ", ".join(missing_variables)
    )


# ============================================================
# 4. CRÉER LE MOTEUR SQL
# ============================================================

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=yes;"
)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}"
)


# ============================================================
# 5. TESTER LA CONNEXION AZURE SQL
# ============================================================

with engine.connect() as conn:
    print("Connexion Azure SQL réussie !")

    result = conn.execute(
        text("SELECT @@VERSION")
    )

    print(result.fetchone())


# ============================================================
# 6. CRÉER LA CONNEXION ADLS
# ============================================================

blob_service_client = (
    BlobServiceClient.from_connection_string(
        azure_connection_string
    )
)


# ============================================================
# 7. FONCTION DE LECTURE DES CSV DEPUIS ADLS
# ============================================================

def read_csv_from_adls(blob_name: str) -> pd.DataFrame:
    """
    Télécharge un fichier CSV depuis ADLS
    et le transforme en DataFrame pandas.
    """

    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name
    )

    csv_content = (
        blob_client
        .download_blob()
        .readall()
        .decode("utf-8")
    )

    return pd.read_csv(
        StringIO(csv_content)
    )


# ============================================================
# 8. TABLES À CHARGER
# ============================================================

tables = {
    "dim_customer": "dim_customer.csv",
    "dim_product": "dim_product.csv",
    "dim_date": "dim_date.csv",
    "fact_sales": "fact_sales.csv",
}


# ============================================================
# 9. CHARGEMENT ADLS → AZURE SQL
# ============================================================

for table_name, file_name in tables.items():

    print(f"\nReading {file_name} from ADLS...")

    dataframe = read_csv_from_adls(
        file_name
    )

    print(
        f"Loading {table_name} to Azure SQL..."
    )

    dataframe.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=5000
    )

    print(
        f"{table_name} loaded successfully: "
        f"{dataframe.shape[0]} rows"
    )


print(
    "\nAll curated tables loaded from ADLS "
    "to Azure SQL successfully!"
)