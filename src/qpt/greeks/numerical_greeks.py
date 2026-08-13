from typing import Callable
from dataclasses import replace
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.black_scholes import black_scholes_price
from qpt.greeks.analytical_greeks import delta_call, delta_put, gamma, vega
from qpt.models.market_data import MarketData

def numerical_delta(pricing_func: Callable, option: EuropeanOption, market: MarketData, eps: float = 0.01) -> float:
    market_up = replace(market, spot=market.spot + eps)
    market_down = replace(market, spot=market.spot - eps)
    return (pricing_func(option, market_up) - pricing_func(option, market_down)) / (2 * eps)

def numerical_gamma(pricing_func: Callable, option: EuropeanOption, market: MarketData, eps: float = 0.01) -> float:
    market_up = replace(market, spot=market.spot + eps)
    market_down = replace(market, spot=market.spot - eps)
    market_center = replace(market, spot=market.spot)
    return (pricing_func(option, market_up) - 2 * pricing_func(option, market_center) + pricing_func(option, market_down)) / (eps ** 2)

def numerical_vega(pricing_func: Callable, option: EuropeanOption, market: MarketData, eps: float = 0.0001) -> float:
    market_up = replace(market, volatility=market.volatility + eps)
    market_down = replace(market, volatility=market.volatility - eps)
    return (pricing_func(option, market_up) - pricing_func(option, market_down)) / (2 * eps)

market = MarketData(spot=100, rate=0.05, volatility=0.20)
call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

num_delta = numerical_delta(black_scholes_price, call, market)
ana_delta = delta_call(call, market)
print(num_delta, ana_delta)  # must be very close (~0.6368 both)

num_gamma = numerical_gamma(black_scholes_price, call, market)
ana_gamma = gamma(call, market)
print(num_gamma, ana_gamma)  # must be very close (~0.0188)

num_vega = numerical_vega(black_scholes_price, call, market)
ana_vega = vega(call, market)
print(num_vega, ana_vega)  # must be very close (~37.52)