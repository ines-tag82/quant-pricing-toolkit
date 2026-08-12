from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData
from qpt.models.black_scholes import black_scholes_price
from qpt.pricing.pde import pde_price


def test_pde_converges_to_black_scholes_call():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

    bs_price = black_scholes_price(call, market)
    pde_result = pde_price(call, market, M=200, N=200)

    assert abs(pde_result - bs_price) < 0.05


def test_pde_converges_to_black_scholes_put():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    put = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.PUT)

    bs_price = black_scholes_price(put, market)
    pde_result = pde_price(put, market, M=200, N=200)

    assert abs(pde_result - bs_price) < 0.05