from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData
from qpt.models.black_scholes import black_scholes_price
from qpt.calibration.implied_volatility import implied_volatility


def test_implied_vol_recovers_known_volatility():
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

    known_price = black_scholes_price(call, market)
    recovered_vol = implied_volatility(known_price, call, market)

    assert abs(recovered_vol - 0.20) < 1e-4


def test_implied_vol_works_for_put():
    market = MarketData(spot=100, rate=0.05, volatility=0.25)
    put = EuropeanOption(strike=110, maturity=0.5, option_type=OptionType.PUT)

    known_price = black_scholes_price(put, market)
    recovered_vol = implied_volatility(known_price, put, market)

    assert abs(recovered_vol - 0.25) < 1e-4


def test_implied_vol_returns_nan_for_impossible_price():
    """A price below intrinsic value has no valid implied volatility."""
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=50, maturity=1.0, option_type=OptionType.CALL)

    # 1.0 is far below the intrinsic value (spot - strike = 50), impossible price
    result = implied_volatility(1.0, call, market)

    import math
    assert math.isnan(result)