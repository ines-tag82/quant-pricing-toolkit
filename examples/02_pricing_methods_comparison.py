from qpt.models.market_data import MarketData
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.black_scholes import black_scholes_price
from qpt.pricing.binomial_tree import binomial_tree_price
from qpt.pricing.monte_carlo import monte_carlo_price
from qpt.pricing.pde import pde_price

market = MarketData(spot=100, rate=0.05, volatility=0.20)
call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

bs = black_scholes_price(call, market)
tree = binomial_tree_price(call, market, n_steps=500)
mc, mc_stderr = monte_carlo_price(call, market, n_paths=200_000, antithetic=True, seed=42)
pde = pde_price(call, market, M=200, N=200)

print(f"Black-Scholes (closed-form): {bs:.4f}")
print(f"Binomial tree (N=500):        {tree:.4f}")
print(f"Monte Carlo (antithetic):     {mc:.4f}  (stderr: {mc_stderr:.4f})")
print(f"PDE (Crank-Nicolson):         {pde:.4f}")