import numpy as np
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData

def monte_carlo_price(option:EuropeanOption, market:MarketData, n_paths: int=100000, antithetic: bool=False, seed:int=None) -> tuple[float,float]:
    if seed is not None:
        np.random.seed(seed)
    if antithetic:
        z = np.random.standard_normal(n_paths // 2)
        z = np.concatenate((z, -z))
    else:
        z = np.random.standard_normal(n_paths)
    S_T = market.spot * np.exp((market.rate - market.dividend_yield -0.5*market.volatility**2)*option.maturity+market.volatility*np.sqrt(option.maturity)*z)
    if option.option_type == OptionType.CALL:
        payoffs = np.maximum(S_T - option.strike, 0.0)
    else:
        payoffs = np.maximum(option.strike - S_T, 0.0)
    price = np.exp(-market.rate*option.maturity) * np.mean(payoffs)
    std_error = np.exp(-market.rate*option.maturity) * np.std(payoffs) / np.sqrt(len(payoffs))
    return price, std_error

if __name__ == "__main__":
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

    price, stderr = monte_carlo_price(call, market, n_paths=100_000, seed=42)
    #print(price, stderr)  # price must be close to 10.45 (± a few cents), stderr must be small (~0.03-0.05)

    price1, err1 = monte_carlo_price(call, market, n_paths=100_000, antithetic=False, seed=42)
    price2, err2 = monte_carlo_price(call, market, n_paths=100_000, antithetic=True, seed=42)
    print("Standard:  ", price1, err1)
    print("Antithetic:", price2, err2)

    call_otm = EuropeanOption(strike=150, maturity=1.0, option_type=OptionType.CALL)
    p1, e1 = monte_carlo_price(call_otm, market, n_paths=100_000, antithetic=False, seed=42)
    p2, e2 = monte_carlo_price(call_otm, market, n_paths=100_000, antithetic=True, seed=42)
    print("Standard OTM:  ", p1, e1)
    print("Antithetic OTM:", p2, e2)