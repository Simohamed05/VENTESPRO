
import pandas as pd
def create_time_features(df):
    """Ajoute des variables temporelles aux données."""
    df["Jour de la semaine"] = df.index.dayofweek
    df["Mois"] = df.index.month
    df["Année"] = df.index.year
    df["Weekend"] = df["Jour de la semaine"].apply(lambda x: 1 if x >= 5 else 0)
    df["Holiday"] = df["Holiday"].apply(lambda x: 1 if x == "Yes" else 0)
    return df

def encode_categorical_features(df):
    """Encode les variables catégoriques pour les modèles et les visualisations."""
    df = pd.get_dummies(df, columns=["Produit", "Region", "Weather"], drop_first=True)
    return df
