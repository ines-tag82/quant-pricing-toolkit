import numpy as np
from scipy.stats import norm
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData

def d1_d2(option: EuropeanOption, market: MarketData):
    d1 = (np.log(market.spot / option.strike) + (market.rate - market.dividend_yield + 0.5 * market.volatility ** 2) * option.maturity) / (market.volatility * np.sqrt(option.maturity))
    d2 = d1 - market.volatility * np.sqrt(option.maturity)
    return d1, d2

def delta_call(option: EuropeanOption, market: MarketData) -> float:
    d1, _ = d1_d2(option, market)       
    return np.exp(-market.dividend_yield * option.maturity) * norm.cdf(d1)

def delta_put(option: EuropeanOption, market: MarketData) -> float:
    d1, _ = d1_d2(option, market)
    return np.exp(-market.dividend_yield * option.maturity) * (norm.cdf(d1) - 1)

def gamma(option: EuropeanOption, market: MarketData) -> float:
    d1, _ = d1_d2(option, market)
    return np.exp(-market.dividend_yield * option.maturity) * norm.pdf(d1) / (market.spot * market.volatility * np.sqrt(option.maturity))

def vega(option: EuropeanOption, market: MarketData) -> float:
    d1, _ = d1_d2(option, market)
    return market.spot * np.exp(-market.dividend_yield * option.maturity) * norm.pdf(d1) * np.sqrt(option.maturity)

def theta_call(option: EuropeanOption, market: MarketData) -> float:
    d1, d2 = d1_d2(option, market)
    return (-market.spot * np.exp(-market.dividend_yield * option.maturity) * norm.pdf(d1) * market.volatility) / (2*np.sqrt(option.maturity)) - market.rate *option.strike * np.exp(-market.rate * option.maturity) * norm.cdf(d2) + market.dividend_yield * market.spot * np.exp(-market.dividend_yield * option.maturity) * norm.cdf(d1)

def theta_put(option: EuropeanOption, market: MarketData) -> float:
    d1, d2 = d1_d2(option, market)
    return ((-market.spot * np.exp(-market.dividend_yield * option.maturity) * norm.pdf(d1) * market.volatility) / (2 * np.sqrt(option.maturity))+ market.rate * option.strike * np.exp(-market.rate * option.maturity) * norm.cdf(-d2)- market.dividend_yield * market.spot * np.exp(-market.dividend_yield * option.maturity) * norm.cdf(-d1))

def rho_call(option: EuropeanOption, market: MarketData) -> float:
    d1, d2 = d1_d2(option, market)
    return option.strike * option.maturity * np.exp(-market.rate * option.maturity) * norm.cdf(d2)

def rho_put(option: EuropeanOption, market: MarketData) -> float:
    d1, d2 = d1_d2(option, market)
    return -option.strike * option.maturity * np.exp(-market.rate * option.maturity) * norm.cdf(-d2)

if __name__ == "__main__":
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)
    
    print(delta_call(call, market))   # ~0.6368
    print(gamma(call, market))        # ~0.0188
    print(vega(call, market))         # ~37.52
    print(theta_call(call, market))   # ~-6.41
    print(rho_call(call, market))     # ~53.23