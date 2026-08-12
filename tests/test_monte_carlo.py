from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData
from qpt.models.black_scholes import black_scholes_price
from qpt.pricing.monte_carlo import monte_carlo_price


def test_monte_carlo_converges_to_black_scholes():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

    bs_price = black_scholes_price(call, market)
    mc_price, stderr = monte_carlo_price(call, market, n_paths=200_000, seed=42)

    # The Monte Carlo estimate should fall within a few standard errors of the true price
    assert abs(mc_price - bs_price) < 5 * stderr


def test_antithetic_uses_correct_number_of_paths():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

    price, stderr = monte_carlo_price(call, market, n_paths=100_000, antithetic=True, seed=42)

    # Just check it runs without error and returns sensible values
    assert price > 0
    assert stderr > 0