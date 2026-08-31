from pathlib import Path

import pandas as pd


# ============================================================
# 1. CHEMINS DU PROJET
# ============================================================

RAW_FILE = Path("data/raw/data.csv")
PROCESSED_FOLDER = Path("data/processed")

# Crée le dossier s'il n'existe pas
PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CHARGEMENT DES DONNÉES
# ============================================================

df = pd.read_csv(
    RAW_FILE,
    encoding="ISO-8859-1"
)

print("Aperçu des données brutes :")
print(df.head())

print("\nTaille initiale :", df.shape)


# ============================================================
# 3. CONVERSION DES TYPES
# ============================================================

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"],
    errors="coerce"
)

# CustomerID devient un entier nullable :
# il peut contenir des nombres entiers et des valeurs manquantes.
df["CustomerID"] = df["CustomerID"].astype("Int64")


# ============================================================
# 4. SUPPRESSION DES DOUBLONS EXACTS
# ============================================================

exact_duplicates = df.duplicated().sum()

print("\nDoublons exacts détectés :", exact_duplicates)

df = df.drop_duplicates().copy()

print("Doublons exacts après nettoyage :", df.duplicated().sum())


# ============================================================
# 5. CRÉATION DU DATASET ANALYTIQUE
# ============================================================

# On garde uniquement les ventes normales :
# - quantité positive
# - prix positif
df_analytics = df[
    (df["Quantity"] > 0) &
    (df["UnitPrice"] > 0)
].copy()

print("\nTaille des données brutes nettoyées :", df.shape)
print("Taille du dataset analytique :", df_analytics.shape)

# ============================================================
# 6. NORMALISATION DES CLÉS MÉTIER
# ============================================================

df_analytics["StockCode"] = (
    df_analytics["StockCode"]
    .astype("string")
    .str.strip()
    .str.upper()
)


# ============================================================
# 7. CRÉATION DES COLONNES CALCULÉES
# ============================================================

# Chiffre d'affaires d'une ligne de vente
df_analytics["Revenue"] = (
    df_analytics["Quantity"] *
    df_analytics["UnitPrice"]
)

# Date sans l'heure, utilisée pour la relation avec dim_date
df_analytics["Date"] = (
    df_analytics["InvoiceDate"]
    .dt.normalize()
)


# ============================================================
# 7. CRÉATION DE LA DIMENSION PRODUIT
# ============================================================

# On trie par date pour conserver la dernière description connue
# de chaque produit.
dim_product = (
    df_analytics
    .sort_values("InvoiceDate")
    [["StockCode", "Description", "InvoiceDate"]]
    .dropna(subset=["StockCode"])
    .drop_duplicates(
        subset=["StockCode"],
        keep="last"
    )
    [["StockCode", "Description"]]
    .sort_values("StockCode")
    .reset_index(drop=True)
)


# ============================================================
# 8. CRÉATION DE LA DIMENSION CLIENT
# ============================================================

# On exclut les CustomerID inconnus de la dimension.
# On garde la dernière information connue pour chaque client.
dim_customer = (
    df_analytics
    .sort_values("InvoiceDate")
    [["CustomerID", "Country", "InvoiceDate"]]
    .dropna(subset=["CustomerID"])
    .drop_duplicates(
        subset=["CustomerID"],
        keep="last"
    )
    [["CustomerID", "Country"]]
    .sort_values("CustomerID")
    .reset_index(drop=True)
)


# ============================================================
# 9. CRÉATION DE LA DIMENSION DATE
# ============================================================

dim_date = (
    df_analytics[["Date"]]
    .dropna(subset=["Date"])
    .drop_duplicates(subset=["Date"])
    .sort_values("Date")
    .reset_index(drop=True)
)

dim_date["Year"] = dim_date["Date"].dt.year
dim_date["Quarter"] = dim_date["Date"].dt.quarter
dim_date["Month"] = dim_date["Date"].dt.month
dim_date["MonthName"] = dim_date["Date"].dt.month_name()
dim_date["Day"] = dim_date["Date"].dt.day
dim_date["Weekday"] = dim_date["Date"].dt.day_name()


# ============================================================
# 10. CRÉATION DE LA TABLE DE FAITS
# ============================================================

fact_sales = df_analytics[
    [
        "InvoiceNo",
        "StockCode",
        "CustomerID",
        "InvoiceDate",
        "Date",
        "Quantity",
        "UnitPrice",
        "Revenue"
    ]
].copy()


# ============================================================
# 11. VALIDATION DU MODÈLE EN ÉTOILE
# ============================================================

def validate_dimension(
    dataframe: pd.DataFrame,
    key_column: str,
    table_name: str
) -> None:
    """
    Vérifie que la clé d'une dimension est unique
    et ne contient aucune valeur manquante.
    """

    total_rows = len(dataframe)
    unique_keys = dataframe[key_column].nunique(dropna=True)
    null_keys = dataframe[key_column].isna().sum()
    duplicate_keys = dataframe.duplicated(
        subset=[key_column]
    ).sum()

    print(f"\nValidation de {table_name}")
    print(f"Nombre total de lignes : {total_rows}")
    print(f"Nombre de clés uniques : {unique_keys}")
    print(f"Nombre de clés NULL : {null_keys}")
    print(f"Nombre de clés dupliquées : {duplicate_keys}")


validate_dimension(
    dim_product,
    "StockCode",
    "dim_product"
)

validate_dimension(
    dim_customer,
    "CustomerID",
    "dim_customer"
)

validate_dimension(
    dim_date,
    "Date",
    "dim_date"
)


# ============================================================
# 12. AFFICHAGE DES TAILLES FINALES
# ============================================================

print("\nTaille finale des tables :")
print("dim_product :", dim_product.shape)
print("dim_customer :", dim_customer.shape)
print("dim_date :", dim_date.shape)
print("fact_sales :", fact_sales.shape)


# ============================================================
# 13. EXPORT DES FICHIERS
# ============================================================

df_analytics.to_csv(
    PROCESSED_FOLDER / "df_analytics.csv",
    index=False
)

dim_product.to_csv(
    PROCESSED_FOLDER / "dim_product.csv",
    index=False
)

dim_customer.to_csv(
    PROCESSED_FOLDER / "dim_customer.csv",
    index=False
)

dim_date.to_csv(
    PROCESSED_FOLDER / "dim_date.csv",
    index=False
)

fact_sales.to_csv(
    PROCESSED_FOLDER / "fact_sales.csv",
    index=False
)

print("\nTous les fichiers ont été exportés avec succès.")