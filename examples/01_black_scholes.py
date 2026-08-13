from qpt.models.market_data import MarketData
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.black_scholes import black_scholes_price
from qpt.greeks.analytical_greeks import delta_call, gamma, vega, theta_call, rho_call

market = MarketData(spot=100, rate=0.05, volatility=0.20)
call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)
put = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.PUT)

print(f"Market: spot={market.spot}, rate={market.rate}, volatility={market.volatility}")
print(f"Option: strike={call.strike}, maturity={call.maturity} years\n")

print(f"Call price: {black_scholes_price(call, market):.4f}")
print(f"Put price:  {black_scholes_price(put, market):.4f}\n")

print("Call Greeks:")
print(f"  Delta: {delta_call(call, market):.4f}")
print(f"  Gamma: {gamma(call, market):.4f}")
print(f"  Vega:  {vega(call, market):.4f}")
print(f"  Theta: {theta_call(call, market):.4f}")
print(f"  Rho:   {rho_call(call, market):.4f}")