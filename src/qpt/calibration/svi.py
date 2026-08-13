import numpy as np
import pandas as pd
from scipy.optimize import minimize
from qpt.data.market_data_fetcher import fetch_option_chain
from qpt.data.cleaning import clean_option_chain
from qpt.calibration.smile import compute_smile


def svi_total_variance(k: np.ndarray, a: float, b: float, rho: float, m: float, sigma: float) -> np.ndarray:
    return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma ** 2))

def calibrate_svi_slice(log_moneyness: np.ndarray, total_variance: np.ndarray) -> dict:
    def loss(params):
        a, b, rho, m, sigma = params
        var_predicted = svi_total_variance(log_moneyness, a, b, rho, m, sigma)
        sum_squared_error = np.sum((var_predicted - total_variance) ** 2)
        return sum_squared_error
    initial_guess = [0.05, 0.1, -0.3, 0.0, 0.1]  # a, b, rho, m, sigma -- reasonable departure point
    bounds = [(None, None), # a: no strict bound
        (0.0, None),    # b >= 0
        (-0.999, 0.999),  # rho between -1 and 1
        (None, None),   # m: no strict bound
        (0.001, None),  # sigma > 0
    ]
    result = minimize(loss, initial_guess, bounds=bounds)
    result_dict = { "a": result.x[0], "b": result.x[1],"rho": result.x[2], "m": result.x[3], "sigma": result.x[4]}
    return result_dict

def calibrate_svi_surface(df_smile: pd.DataFrame) -> dict:
    surface = {}
    for expiry, group in df_smile.groupby("expiry"):
        group_sorted = group.sort_values("strike")
        spot = group_sorted["spot"].iloc[0]
        maturity = group_sorted["days_to_expiry"].iloc[0] / 365
        log_moneyness = np.log(group_sorted["strike"] / spot).values
        total_variance = (group_sorted["implied_vol"] ** 2 * maturity).values
        params = calibrate_svi_slice(log_moneyness, total_variance)
        params["spot"] = spot
        params["maturity"] = maturity
        surface[expiry] = params
    return surface

if __name__ == "__main__":
    df_raw = fetch_option_chain("AAPL", max_expiries=8)
    df_clean = clean_option_chain(df_raw)
    df_smile = compute_smile(df_clean, min_vega=10.0)

    # Take the first expiry for this initial test
    first_expiry = df_smile["expiry"].unique()[0]
    slice_df = df_smile[df_smile["expiry"] == first_expiry].sort_values("strike")

    spot = slice_df["spot"].iloc[0]
    maturity = slice_df["days_to_expiry"].iloc[0] / 365

    log_moneyness = np.log(slice_df["strike"] / spot)
    total_variance = (slice_df["implied_vol"] ** 2) * maturity

    params = calibrate_svi_slice(log_moneyness.values, total_variance.values)
    print(f"Calibrated SVI params for {first_expiry}: {params}")
