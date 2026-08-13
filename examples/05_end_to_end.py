"""
End-to-end walkthrough of the Quant Pricing Toolkit.

Pipeline: fetch real market data -> clean it -> extract implied volatility ->
calibrate an SVI volatility surface -> price an option under that calibrated
volatility -> compute portfolio risk (VaR/CVaR) using the same underlying.
"""

import numpy as np

from qpt.data.market_data_fetcher import fetch_option_chain
from qpt.data.cleaning import clean_option_chain
from qpt.calibration.smile import compute_smile
from qpt.calibration.svi import calibrate_svi_surface, svi_total_variance
from qpt.models.market_data import MarketData
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.black_scholes import black_scholes_price
from qpt.pricing.binomial_tree import binomial_tree_price
from qpt.pricing.monte_carlo import monte_carlo_price
from qpt.pricing.pde import pde_price
from qpt.greeks.analytical_greeks import delta_call, gamma, vega
from qpt.risk.var import historical_var, historical_cvar, kupiec_test

TICKER = "AAPL"

print("=" * 60)
print(f"STEP 1: Fetch and clean real option data for {TICKER}")
print("=" * 60)

df_raw = fetch_option_chain(TICKER, max_expiries=8)
df_clean = clean_option_chain(df_raw)
df_smile = compute_smile(df_clean, min_vega=10.0)
print(f"Raw options: {len(df_raw)} -> cleaned & vega-filtered: {len(df_smile)}\n")

print("=" * 60)
print("STEP 2: Calibrate SVI volatility surface")
print("=" * 60)

surface = calibrate_svi_surface(df_smile)
first_expiry = list(surface.keys())[0]
params = surface[first_expiry]
print(f"Calibrated SVI params for {first_expiry}:")
for key in ["a", "b", "rho", "m", "sigma"]:
    print(f"  {key}: {params[key]:.4f}")
print()

print("=" * 60)
print("STEP 3: Price an at-the-money option using the calibrated volatility")
print("=" * 60)

spot = params["spot"]
maturity = params["maturity"]

# Read the SVI-implied volatility at-the-money (log-moneyness = 0)
w_atm = svi_total_variance(np.array([0.0]), params["a"], params["b"], params["rho"], params["m"], params["sigma"])
implied_vol_atm = float(np.sqrt(w_atm[0] / maturity))
print(f"SVI-implied ATM volatility for {first_expiry}: {implied_vol_atm:.4f}\n")

market = MarketData(spot=spot, rate=0.05, volatility=implied_vol_atm)
call = EuropeanOption(strike=round(spot), maturity=maturity, option_type=OptionType.CALL)

bs_price = black_scholes_price(call, market)
tree_price = binomial_tree_price(call, market, n_steps=500)
mc_price, mc_stderr = monte_carlo_price(call, market, n_paths=200_000, antithetic=True, seed=42)
pde_price_value = pde_price(call, market, M=200, N=200)

print(f"Call price (strike={call.strike}, maturity={maturity:.4f}y):")
print(f"  Black-Scholes:  {bs_price:.4f}")
print(f"  Binomial tree:  {tree_price:.4f}")
print(f"  Monte Carlo:    {mc_price:.4f} (stderr: {mc_stderr:.4f})")
print(f"  PDE:            {pde_price_value:.4f}\n")

print(f"Greeks: Delta={delta_call(call, market):.4f}, Gamma={gamma(call, market):.4f}, Vega={vega(call, market):.4f}\n")

print("=" * 60)
print("STEP 4: Portfolio risk on the underlying, using the calibrated volatility")
print("=" * 60)

portfolio_value = 100_000
np.random.seed(42)
# Simulate daily returns consistent with the SVI-implied ATM volatility
daily_vol = implied_vol_atm / np.sqrt(252)
returns = np.random.normal(loc=0.0002, scale=daily_vol, size=1000)

var_95 = historical_var(returns, portfolio_value, confidence_level=0.95)
cvar_95 = historical_cvar(returns, portfolio_value, confidence_level=0.95)
kupiec = kupiec_test(returns, var_95, portfolio_value, confidence_level=0.95)

print(f"Historical VaR 95% (1-day): {var_95:,.2f}")
print(f"Historical CVaR 95%:        {cvar_95:,.2f}")
print(f"Kupiec backtest p-value:    {kupiec['p_value']:.4f}")
print()
print("End-to-end pipeline complete.")