import os
from pathlib import Path

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv


# Charger les variables du fichier .env
load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

if not AZURE_STORAGE_CONNECTION_STRING:
    raise ValueError(
        "AZURE_STORAGE_CONNECTION_STRING est absente du fichier .env"
    )


# Dossier local contenant les fichiers générés par l'ETL
LOCAL_FOLDER = Path("data/processed")

# Conteneur ADLS dans lequel seront envoyés les fichiers
CONTAINER_NAME = "curated"

FILES_TO_UPLOAD = [
    "dim_customer.csv",
    "dim_product.csv",
    "dim_date.csv",
    "fact_sales.csv",
]


blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)

container_client = blob_service_client.get_container_client(
    CONTAINER_NAME
)


for filename in FILES_TO_UPLOAD:
    local_file_path = LOCAL_FOLDER / filename

    if not local_file_path.exists():
        raise FileNotFoundError(
            f"Le fichier local est introuvable : {local_file_path}"
        )

    blob_client = container_client.get_blob_client(
        blob=filename
    )

    with open(local_file_path, "rb") as file_data:
        blob_client.upload_blob(
            file_data,
            overwrite=True
        )

    print(
        f"{filename} uploaded successfully "
        f"to container '{CONTAINER_NAME}'"
    )


print("All processed files uploaded to ADLS successfully!")