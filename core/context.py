from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class AppContext:
    df: pd.DataFrame
    target_col: str
    cat_col: str
    date_col: str
    region_col: Optional[str]
    promo_col: Optional[str]
    stock_col: Optional[str]
