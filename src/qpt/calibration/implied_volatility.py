from dataclasses import replace
from scipy.optimize import brentq
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData
from qpt.models.black_scholes import black_scholes_price


def implied_volatility(market_price: float, option: EuropeanOption, market: MarketData, sigma_bounds: tuple[float, float] = (0.001, 5.0)) -> float:
    def price_difference(sigma: float) -> float:
        market_bumped = replace(market, volatility=sigma)
        return black_scholes_price(option, market_bumped) - market_price
    try :
        result=brentq(price_difference, sigma_bounds[0], sigma_bounds[1])
        return result
    except ValueError:
        return float('nan')

market = MarketData(spot=100, rate=0.05, volatility=0.20)
call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

# We generate a "market" price based on a known volatility (0.20)
known_price = black_scholes_price(call, market)
print("Price generated with sigma=0.20:", known_price)

# We "forget" the true volatility and try to recover it from the price alone
recovered_vol = implied_volatility(known_price, call, market)
print("Recovered volatility:", recovered_vol) #should be close to 0.20
    