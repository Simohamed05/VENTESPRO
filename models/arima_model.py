from statsmodels.tsa.arima.model import ARIMA

def train_arima(df):
    """Entraîne un modèle ARIMA pour la prévision des ventes."""
    model = ARIMA(df['Ventes'], order=(5,1,0))
    model_fit = model.fit()
    return model_fit
