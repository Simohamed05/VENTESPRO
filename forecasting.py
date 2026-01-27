from typing import Optional, Tuple

import numpy as np
import pandas as pd


def prepare_series(
    df_base: pd.DataFrame,
    target_col: str,
    cat_col: str,
    date_col: Optional[str],
    produit_value: str,
) -> Tuple[Optional[pd.DataFrame], Optional[bool], Optional[str]]:
    """Retourne une série avec DateTimeIndex quotidien + colonne 'Valeurs' (float)."""
    work = df_base.copy()

    if cat_col != "Aucune":
        work = work[work[cat_col] == produit_value].copy()

    work[target_col] = pd.to_numeric(work[target_col], errors="coerce")
    work = work.dropna(subset=[target_col])

    if len(work) == 0:
        return None, None, "Aucune donnée après nettoyage."

    has_date = False
    used_date_col = None
    if date_col and date_col != "Aucune" and date_col in work.columns:
        used_date_col = date_col
        work[used_date_col] = pd.to_datetime(work[used_date_col], errors="coerce")
        work = work.dropna(subset=[used_date_col]).sort_values(used_date_col)
        if len(work) > 0:
            work = work.set_index(used_date_col)
            has_date = True

    if not has_date:
        work = work.reset_index(drop=True)
        work.index = pd.date_range(start="2024-01-01", periods=len(work), freq="D")

    df_ts = work[[target_col]].copy()
    df_ts.columns = ["Valeurs"]
    df_ts["Valeurs"] = pd.to_numeric(df_ts["Valeurs"], errors="coerce")
    df_ts = df_ts.dropna()

    df_ts = df_ts.sort_index()
    df_ts = df_ts.asfreq("D")
    df_ts["Valeurs"] = df_ts["Valeurs"].ffill()

    if len(df_ts) < 14:
        return None, None, "Au moins 14 points de données sont requis pour les prévisions."

    return df_ts, has_date, None


def future_dates(last_date, horizon: int, freq: str = "D") -> pd.DatetimeIndex:
    return pd.date_range(start=last_date, periods=horizon + 1, freq=freq)[1:]


def basic_confidence_band(forecast_values: np.ndarray, std: float):
    lower = np.maximum(forecast_values - 1.96 * std, 0)
    upper = forecast_values + 1.96 * std
    return lower, upper


def build_features(df_ts: pd.DataFrame):
    """Features pour RF/XGB basées sur une vraie colonne date (index) + rolling + lag."""
    tmp = df_ts.copy().reset_index().rename(columns={"index": "Date"})
    tmp["Date"] = pd.to_datetime(tmp["Date"], errors="coerce")

    tmp["Temps"] = np.arange(len(tmp))
    tmp["Jour"] = tmp["Date"].dt.day
    tmp["Mois"] = tmp["Date"].dt.month
    tmp["JourSemaine"] = tmp["Date"].dt.dayofweek
    tmp["JourAnnee"] = tmp["Date"].dt.dayofyear
    tmp["Trimestre"] = tmp["Date"].dt.quarter

    tmp["MA_7"] = tmp["Valeurs"].rolling(7, min_periods=1).mean()
    tmp["MA_30"] = tmp["Valeurs"].rolling(30, min_periods=1).mean()
    tmp["Lag_1"] = tmp["Valeurs"].shift(1)
    tmp["Lag_1"] = tmp["Lag_1"].fillna(tmp["Valeurs"].iloc[0])

    feature_cols = [
        "Temps",
        "Jour",
        "Mois",
        "JourSemaine",
        "JourAnnee",
        "Trimestre",
        "MA_7",
        "MA_30",
        "Lag_1",
    ]
    X = tmp[feature_cols]
    y = tmp["Valeurs"].astype(float)
    return tmp, X, y, feature_cols


def build_future_features(df_feat: pd.DataFrame, feature_cols, horizon: int):
    """Future features cohérentes avec build_features."""
    last_date = pd.to_datetime(df_feat["Date"].iloc[-1])
    future_dates_index = future_dates(last_date, horizon, freq="D")

    future = pd.DataFrame(index=future_dates_index)
    future["Temps"] = np.arange(df_feat["Temps"].iloc[-1] + 1, df_feat["Temps"].iloc[-1] + 1 + horizon)

    future["Jour"] = future.index.day
    future["Mois"] = future.index.month
    future["JourSemaine"] = future.index.dayofweek
    future["JourAnnee"] = future.index.dayofyear
    future["Trimestre"] = future.index.quarter

    future["MA_7"] = df_feat["MA_7"].iloc[-1]
    future["MA_30"] = df_feat["MA_30"].iloc[-1]
    future["Lag_1"] = df_feat["Valeurs"].iloc[-1]

    return future_dates_index, future[feature_cols]
