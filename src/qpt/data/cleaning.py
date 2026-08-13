import pandas as pd
from qpt.data.market_data_fetcher import fetch_option_chain

def clean_option_chain(df: pd.DataFrame, min_price: float = 0.05, max_bid_ask_spread_pct: float = 0.20, min_days_to_expiry: int = 7, moneyness_bounds: tuple[float, float] = (0.7, 1.3)) -> pd.DataFrame:
    result = df.copy()
    result = result[result["option_price"] >= min_price] #cleans options with a price below the minimum threshold
    spread = result["ask"] - result["bid"]
    relative_spread = spread/result["option_price"]
    result = result[relative_spread <= max_bid_ask_spread_pct] #cleans options with a bid-ask spread too high
    result = result[result["days_to_expiry"] >= min_days_to_expiry] #cleans options with too short time to expiry
    moneyness = result["strike"] / result["spot"]
    result = result[(moneyness >= moneyness_bounds[0]) & (moneyness <= moneyness_bounds[1])] #cleans options outside the moneyness bounds
    if len(result) == 0:
        print("⚠️ Warning: no options remain after cleaning. Consider relaxing the filter thresholds.")
    return result

df_raw = fetch_option_chain("AAPL", max_expiries=8)
df_clean = clean_option_chain(df_raw)

print("Avant nettoyage:", df_raw.shape)
print("Après nettoyage:", df_clean.shape)
print(df_clean[["strike", "option_price", "days_to_expiry"]].describe())