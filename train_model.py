import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor

def train_model(df, model_type):
    """
    Entraîne un modèle de prévision en fonction du type choisi.

    Paramètres :
    - df : DataFrame contenant les données temporelles (avec 'Date' en index)
    - model_type : str, "ARIMA", "Prophet" ou "Random Forest"

    Retourne :
    - DataFrame avec la colonne 'Prévision'
    """

    df = df.copy()
    
    # Vérification et conversion de la colonne Date
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)
    
    df = df.resample('D').sum()  # Agrégation quotidienne si nécessaire

    # Nombre de jours à prédire
    future_periods = 30

    # Modèle ARIMA
    if model_type == "ARIMA":
        model = ARIMA(df["Ventes"], order=(5,1,0))  # (p,d,q) à ajuster selon tes besoins
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=future_periods)
        forecast_dates = pd.date_range(start=df.index[-1], periods=future_periods+1, freq='D')[1:]
        forecast_df = pd.DataFrame({"Date": forecast_dates, "Prévision": forecast.values})

    # Modèle Prophet
    elif model_type == "Prophet":
        df_prophet = df.reset_index()[["Date", "Ventes"]]
        df_prophet.columns = ["ds", "y"]
        model = Prophet()
        model.fit(df_prophet)
        future = model.make_future_dataframe(periods=future_periods)
        forecast = model.predict(future)
        forecast_df = forecast[["ds", "yhat"]].rename(columns={"ds": "Date", "yhat": "Prévision"})

    # Modèle Random Forest
    elif model_type == "Random Forest":
        df["Jour"] = df.index.dayofweek
        df["Mois"] = df.index.month
        df["Année"] = df.index.year
        X = df[["Jour", "Mois", "Année"]]
        y = df["Ventes"]

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        future_dates = pd.date_range(start=df.index[-1], periods=future_periods+1, freq='D')[1:]
        future_df = pd.DataFrame({
            "Jour": future_dates.dayofweek,
            "Mois": future_dates.month,
            "Année": future_dates.year
        })

        forecast = model.predict(future_df)
        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecast})

    else:
        raise ValueError("Modèle non reconnu. Choisissez 'ARIMA', 'Prophet' ou 'Random Forest'.")

    forecast_df.set_index("Date", inplace=True)
    return forecast_df
