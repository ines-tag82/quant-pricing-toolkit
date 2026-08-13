import pandas as pd
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData
from qpt.calibration.implied_volatility import implied_volatility
from qpt.data.market_data_fetcher import fetch_option_chain
from qpt.data.cleaning import clean_option_chain

def compute_smile(df: pd.DataFrame, rate: float = 0.05) -> pd.DataFrame:
    result = df.copy()
    implied_vols = []
    for _, row in result.iterrows():
        market = MarketData(spot=row["spot"], rate=rate, volatility=0.20)
        option = EuropeanOption(strike=row["strike"], maturity=row["days_to_expiry"] / 365, option_type=OptionType.CALL)
        implied_vols.append(implied_volatility(row["option_price"], option, market))
        pass
    result["implied_vol"] = implied_vols
    return result


df_raw = fetch_option_chain("AAPL", max_expiries=8)
df_clean = clean_option_chain(df_raw)
df_smile = compute_smile(df_clean)

print(df_smile[["strike", "days_to_expiry", "option_price", "implied_vol"]].head(15))
print(df_smile["implied_vol"].describe())