from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData
from qpt.models.black_scholes import black_scholes_price
from qpt.pricing.binomial_tree import binomial_tree_price


def test_binomial_converges_to_black_scholes():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

    bs_price = black_scholes_price(call, market)
    tree_price = binomial_tree_price(call, market, n_steps=500, american=False)

    assert abs(tree_price - bs_price) < 0.01


def test_american_put_at_least_as_valuable_as_european():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    put = EuropeanOption(strike=110, maturity=1.0, option_type=OptionType.PUT)

    european_price = binomial_tree_price(put, market, n_steps=200, american=False)
    american_price = binomial_tree_price(put, market, n_steps=200, american=True)

    assert american_price >= european_price