import pandas as pd

def load_data(file):
    """Charge les données avec conversion correcte de la colonne Date."""
    df = pd.read_csv(file, sep=";")  # Lire avec le bon séparateur
    df.columns = df.columns.str.strip()  # Nettoyer les noms de colonnes

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')  # Conversion
        df = df.dropna(subset=["Date"])  # Supprimer les dates invalides
        df = df.set_index("Date")  # Définir la colonne Date comme index
    else:
        raise ValueError(f"⚠️ Colonne 'Date' introuvable ! Colonnes disponibles : {df.columns}")

    return df


