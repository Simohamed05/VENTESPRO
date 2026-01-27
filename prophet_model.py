from prophet import Prophet

def train_prophet(df):
    """Entraîne un modèle Prophet."""
    df_prophet = df.reset_index().rename(columns={"Date": "ds", "Ventes": "y"})
    model = Prophet()
    model.add_regressor("Promo")
    model.add_regressor("Holiday")
    model.fit(df_prophet)
    return model
