import numpy as np
from scipy.stats import norm
from scipy.stats import chi2


def historical_var(returns: np.ndarray, portfolio_value: float, confidence_level: float = 0.95) -> float:
    pnl = returns * portfolio_value
    quantile = np.percentile(pnl, (1 - confidence_level) * 100)
    return -quantile

def parametric_var(returns: np.ndarray, portfolio_value: float, confidence_level: float = 0.95) -> float:
    mu = np.mean(returns)
    sigma = np.std(returns)
    z_alpha = norm.ppf(1 - confidence_level)
    var_alpha = -(mu + z_alpha * sigma) * portfolio_value
    return var_alpha

def monte_carlo_var( spot: float, drift: float, volatility: float, horizon: float, portfolio_value: float, confidence_level: float = 0.95, n_simulations: int = 100_000, seed: int = None) -> float:
    if seed is not None:
        np.random.seed(seed)
    z = np.random.standard_normal(n_simulations)
    S_T = spot * np.exp((drift - 0.5 * volatility ** 2) * horizon + volatility * np.sqrt(horizon) * z)
    portfolio_value_scenario = (portfolio_value / spot) * S_T
    pnl = portfolio_value_scenario - portfolio_value
    quantile = np.percentile(pnl, (1 - confidence_level) * 100)
    return -quantile

def historical_cvar(returns: np.ndarray, portfolio_value: float, confidence_level: float = 0.95) -> float:
    pnl = returns * portfolio_value
    var_value = historical_var(returns, portfolio_value, confidence_level)
    pnl_extreme = pnl[pnl < -var_value]
    mean_extreme_loss = np.mean(pnl_extreme)
    return -mean_extreme_loss

def kupiec_test(returns: np.ndarray, var_estimate: float, portfolio_value: float, confidence_level: float = 0.95) -> dict:
    N = len(returns)
    pnl = returns * portfolio_value
    exceptions = pnl < -var_estimate
    exceptions_count = np.sum(exceptions)
    exception_rate = exceptions_count / N
    expected_rate = 1 - confidence_level
    if exceptions_count == 0 or exceptions_count == N:
        lr_statistic = 0.0
    else:
        lr_statistic = -2*np.log(((1 - expected_rate) ** (N - exceptions_count) * (expected_rate ** exceptions_count)) / ((1 - exception_rate) ** (N - exceptions_count) * (exception_rate ** exceptions_count)))
    p_value = 1 - chi2.cdf(lr_statistic, df=1)
    return {"n_exceptions": exceptions_count, "exception_rate": exception_rate, "expected_rate": expected_rate, "lr_statistic": lr_statistic, "p_value": p_value}

if __name__ == "__main__":
    np.random.seed(42)
    # Simulate 1000 days of returns, mean 0.0005, std 0.02 (typical for a stock)
    returns = np.random.normal(loc=0.0005, scale=0.02, size=1000)
    portfolio_value = 100_000

    var_95 = historical_var(returns, portfolio_value, confidence_level=0.95)
    var_99 = historical_var(returns, portfolio_value, confidence_level=0.99)

    print(f"VaR 95%: {var_95:.2f}")
    print(f"VaR 99%: {var_99:.2f}")

    param_var_95 = parametric_var(returns, portfolio_value, confidence_level=0.95)
    param_var_99 = parametric_var(returns, portfolio_value, confidence_level=0.99)

    print(f"Parametric VaR 95%: {param_var_95:.2f}")
    print(f"Parametric VaR 99%: {param_var_99:.2f}")

    mc_var_95 = monte_carlo_var( spot=100, drift=0.0005 * 252, volatility=0.02 * np.sqrt(252), horizon=1/252, portfolio_value=100_000, confidence_level=0.95, seed=42)
    print(f"Monte Carlo VaR 95%: {mc_var_95:.2f}")

    cvar_95 = historical_cvar(returns, portfolio_value, confidence_level=0.95)
    print(f"Historical CVaR 95%: {cvar_95:.2f}")
    print(f"(should be >= VaR 95% = {var_95:.2f})")

    kupiec_result = kupiec_test(returns, var_95, portfolio_value, confidence_level=0.95)
    print("Kupiec test results:")
    for key, value in kupiec_result.items():
        print(f"  {key}: {value}")