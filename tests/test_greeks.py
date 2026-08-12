from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData
from qpt.models.black_scholes import black_scholes_price
from qpt.greeks.analytical_greeks import delta_call, delta_put, gamma, vega, theta_call, theta_put, rho_call, rho_put
from qpt.greeks.numerical_greeks import numerical_delta, numerical_gamma, numerical_vega


def test_delta_analytical_matches_numerical():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

    ana = delta_call(call, market)
    num = numerical_delta(black_scholes_price, call, market)
    assert abs(ana - num) < 1e-4


def test_gamma_analytical_matches_numerical():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

    ana = gamma(call, market)
    num = numerical_gamma(black_scholes_price, call, market)
    assert abs(ana - num) < 1e-3


def test_vega_analytical_matches_numerical():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

    ana = vega(call, market)
    num = numerical_vega(black_scholes_price, call, market)
    assert abs(ana - num) < 1e-2


def test_put_call_delta_relationship():
    """Delta_call - Delta_put == exp(-q*T), a known identity from put-call parity."""
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)
    put = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.PUT)

    diff = delta_call(call, market) - delta_put(put, market)
    expected = 1.0  # exp(-q*T) with q=0
    assert abs(diff - expected) < 1e-6