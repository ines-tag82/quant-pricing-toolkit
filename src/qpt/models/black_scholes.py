from dataclasses import dataclass
from enum import Enum
import math
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData
from scipy.stats import norm

def black_scholes_price(option: EuropeanOption, market: MarketData) -> float:
    d1 = (math.log(market.spot / option.strike) + (market.rate - market.dividend_yield + 0.5 * market.volatility ** 2) * option.maturity) / (market.volatility * math.sqrt(option.maturity))
    d2 = d1 - market.volatility * math.sqrt(option.maturity)
    if option.option_type == OptionType.CALL:
            return market.spot*math.exp(-market.dividend_yield * option.maturity) * norm.cdf(d1) - option.strike * math.exp(-market.rate * option.maturity) * norm.cdf(d2)
    else:
            return option.strike * math.exp(-market.rate * option.maturity) * norm.cdf(-d2) - market.spot*math.exp(-market.dividend_yield * option.maturity) * norm.cdf(-d1)


market = MarketData(spot=100, rate=0.05, volatility=0.20)
call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)
put = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.PUT)

print(black_scholes_price(call, market))
print(black_scholes_price(put, market))