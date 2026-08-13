import pandas as pd
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData
from qpt.calibration.implied_volatility import implied_volatility
from qpt.data.market_data_fetcher import fetch_option_chain
from qpt.data.cleaning import clean_option_chain
from qpt.greeks.analytical_greeks import vega

def compute_smile(df: pd.DataFrame, rate: float = 0.05, min_vega: float =1.0) -> pd.DataFrame:
    result = df.copy()
    implied_vols = []
    vegas = []
    for _, row in result.iterrows():
        market = MarketData(spot=row["spot"], rate=rate, volatility=0.20)
        option = EuropeanOption(strike=row["strike"], maturity=row["days_to_expiry"] / 365, option_type=OptionType.CALL)
        iv = implied_volatility(row["option_price"], option, market)
        implied_vols.append(iv)
        if pd.notna(iv):
            market_solved = MarketData(spot=row["spot"], rate=rate, volatility=iv)
            vegas.append(vega(option, market_solved))
        else:
            vegas.append(float('nan'))
    result["implied_vol"] = implied_vols
    result["vega"] = vegas
    result = result.dropna(subset=["implied_vol", "vega"])
    result = result[result["vega"] >= min_vega]
    return result

if __name__ == "__main__":
    df_raw = fetch_option_chain("AAPL", max_expiries=8)
    df_clean = clean_option_chain(df_raw)
    df_smile = compute_smile(df_clean)

    print(df_smile[["strike", "days_to_expiry", "option_price", "implied_vol"]].head(15))
    print(df_smile["implied_vol"].describe())