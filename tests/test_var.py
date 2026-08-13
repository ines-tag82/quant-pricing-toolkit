import numpy as np
from qpt.risk.var import historical_var, parametric_var, monte_carlo_var, historical_cvar, kupiec_test


def test_var_99_greater_than_var_95():
    np.random.seed(42)
    returns = np.random.normal(loc=0.0005, scale=0.02, size=1000)
    portfolio_value = 100_000

    var_95 = historical_var(returns, portfolio_value, confidence_level=0.95)
    var_99 = historical_var(returns, portfolio_value, confidence_level=0.99)

    assert var_99 > var_95


def test_parametric_var_close_to_historical_for_normal_data():
    np.random.seed(42)
    returns = np.random.normal(loc=0.0005, scale=0.02, size=10_000)  # large sample, true normal
    portfolio_value = 100_000

    hist = historical_var(returns, portfolio_value, confidence_level=0.95)
    param = parametric_var(returns, portfolio_value, confidence_level=0.95)

    # With a large sample of genuinely normal data, both methods should roughly agree
    assert abs(hist - param) / hist < 0.10  # within 10%


def test_monte_carlo_var_is_positive_and_reasonable():
    mc_var = monte_carlo_var(
        spot=100, drift=0.0005 * 252, volatility=0.02 * np.sqrt(252), horizon=1/252,
        portfolio_value=100_000, confidence_level=0.95, seed=42
    )
    assert mc_var > 0
    assert mc_var < 100_000  # sanity check: loss shouldn't exceed full portfolio value on a 1-day horizon


def test_cvar_greater_than_or_equal_to_var():
    np.random.seed(42)
    returns = np.random.normal(loc=0.0005, scale=0.02, size=1000)
    portfolio_value = 100_000

    var_95 = historical_var(returns, portfolio_value, confidence_level=0.95)
    cvar_95 = historical_cvar(returns, portfolio_value, confidence_level=0.95)

    assert cvar_95 >= var_95

def test_kupiec_test_passes_on_well_calibrated_var():
    np.random.seed(42)
    returns = np.random.normal(loc=0.0005, scale=0.02, size=1000)
    portfolio_value = 100_000

    var_95 = historical_var(returns, portfolio_value, confidence_level=0.95)
    result = kupiec_test(returns, var_95, portfolio_value, confidence_level=0.95)

    # In-sample historical VaR should almost exactly match the expected exception rate
    assert abs(result["exception_rate"] - result["expected_rate"]) < 0.01
    assert result["p_value"] > 0.05  # fail to reject H0: well-calibrated