import math
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData



def binomial_tree_price(option:EuropeanOption, market:MarketData, n_steps: int=200, american: bool=False) -> float:
    dt = option.maturity/n_steps
    u = math.exp(market.volatility*math.sqrt(dt))
    d = 1/u
    p = (math.exp((market.rate - market.dividend_yield)*dt)-d)/(u-d)
    disc = math.exp(-market.rate*dt)
    underlying_prices = [market.spot*(u**j)*(d**(n_steps-j)) for j in range (0, n_steps+1)]
    payoffs = [option.payoff(price) for price in underlying_prices]
    for i in range(n_steps-1, -1, -1):
        for j in range(0, i+1):
            payoffs[j] = disc*(p*payoffs[j+1]+(1-p)*payoffs[j])
            if american:
                spot_at_node = market.spot*(u**j)*(d**(i-j))
                payoffs[j] = max(payoffs[j], option.payoff(spot_at_node))
    return payoffs[0]
if __name__ == "__main__":
    market = MarketData(spot=100, rate=0.05, volatility=0.20)
    call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)
    # convergence into Black-Scholes when n_steps increases :
    print(binomial_tree_price(call, market, n_steps=50))    # must be close to 10.45
    print(binomial_tree_price(call, market, n_steps=500))   # must be even closer to 10.45
    # Comparison American vs European option :  
    put_euro = EuropeanOption(strike=110, maturity=1.0, option_type=OptionType.PUT)
    print(binomial_tree_price(put_euro, market, n_steps=200, american=False))
    print(binomial_tree_price(put_euro, market, n_steps=200, american=True))   # must be >= to the European version