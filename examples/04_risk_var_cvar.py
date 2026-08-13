import numpy as np
from qpt.risk.var import historical_var, parametric_var, monte_carlo_var, historical_cvar, kupiec_test

np.random.seed(42)

# Simulate a portfolio's historical daily returns (typical equity-like parameters)
returns = np.random.normal(loc=0.0005, scale=0.02, size=1000)
portfolio_value = 100_000
confidence_level = 0.95

print(f"Portfolio value: {portfolio_value:,.0f}")
print(f"Historical sample size: {len(returns)} days")
print(f"Confidence level: {confidence_level:.0%}\n")

# --- VaR: three methods ---
var_hist = historical_var(returns, portfolio_value, confidence_level)
var_param = parametric_var(returns, portfolio_value, confidence_level)
var_mc = monte_carlo_var(
    spot=100, drift=0.0005 * 252, volatility=0.02 * np.sqrt(252), horizon=1/252,
    portfolio_value=portfolio_value, confidence_level=confidence_level, seed=42
)

print("Value at Risk (1-day horizon):")
print(f"  Historical:  {var_hist:,.2f}")
print(f"  Parametric:  {var_param:,.2f}")
print(f"  Monte Carlo: {var_mc:,.2f}\n")

# --- CVaR ---
cvar_hist = historical_cvar(returns, portfolio_value, confidence_level)
print(f"Historical CVaR (Expected Shortfall): {cvar_hist:,.2f}")
print(f"  (>= VaR as expected: {cvar_hist >= var_hist})\n")

# --- Kupiec backtest ---
kupiec_result = kupiec_test(returns, var_hist, portfolio_value, confidence_level)
print("Kupiec backtest (historical VaR, in-sample):")
print(f"  Exceptions observed: {kupiec_result['n_exceptions']} / {len(returns)} ({kupiec_result['exception_rate']:.2%})")
print(f"  Expected rate:       {kupiec_result['expected_rate']:.2%}")
print(f"  LR statistic:        {kupiec_result['lr_statistic']:.4f}")
print(f"  p-value:             {kupiec_result['p_value']:.4f}")