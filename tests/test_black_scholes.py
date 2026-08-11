from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData
from qpt.models.black_scholes import black_scholes_price


def test_call_price_matches_known_value():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)
    price = black_scholes_price(call, market)
    assert abs(price - 10.4506) < 1e-3


def test_put_price_matches_known_value():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    put = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.PUT)
    price = black_scholes_price(put, market)
    assert abs(price - 5.5735) < 1e-3


def test_put_call_parity():
    """C - P = S*exp(-qT) - K*exp(-rT) -- a no-arbitrage sanity check."""
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=95, maturity=1.0, option_type=OptionType.CALL)
    put = EuropeanOption(strike=95, maturity=1.0, option_type=OptionType.PUT)

    c = black_scholes_price(call, market)
    p = black_scholes_price(put, market)

    lhs = c - p
    rhs = market.spot * (2.718281828 ** (-market.dividend_yield * 1.0)) - 95 * (2.718281828 ** (-market.rate * 1.0))
    assert abs(lhs - rhs) < 1e-3