import numpy as np
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.market_data import MarketData
from scipy.linalg import solve_banded


def build_grid(option: EuropeanOption, market: MarketData, M: int = 200, N: int = 200, S_max_multiplier: float = 4.0):
    S_max = option.strike * S_max_multiplier
    S_grid = np.linspace(0, S_max, M + 1) 
    dS = S_max/M
    dt = option.maturity/N
    if option.option_type == OptionType.CALL:
        V = np.maximum(0, S_grid - option.strike)
    else:
        V = np.maximum(0, option.strike - S_grid)
    return S_grid, dS, dt, V

def boundary_values(option: EuropeanOption, market: MarketData, S_max: float, t: float) -> tuple[float, float]:
    time_to_maturity = option.maturity - t
    if option.option_type == OptionType.CALL:
        V_at_S0 = 0.0
        V_at_Smax = S_max*np.exp(-market.dividend_yield * time_to_maturity) - option.strike * np.exp(-market.rate * time_to_maturity)
    else:
        V_at_S0 = option.strike * np.exp(-market.rate * time_to_maturity)
        V_at_Smax = 0.0
    return V_at_S0, V_at_Smax

def crank_nicolson_step(V, i_grid, dt, sigma, r, q):
    a = 0.25 * dt * (sigma**2 * i_grid**2 - (r - q) * i_grid)
    b = -0.5 * dt * (sigma**2 * i_grid**2 + r)
    c = 0.25 * dt * (sigma**2 * i_grid**2 + (r - q) * i_grid)
    M_minus_1 = len(i_grid)
    rhs = a * V[0:M_minus_1] + (1 + b) * V[1:M_minus_1+1] + c * V[2:M_minus_1+2]
    ab = np.zeros((3, M_minus_1))
    ab[0, 1:] = -c[:-1]      # upper diagonal
    ab[1, :] = 1 - b          # main diagonal
    ab[2, :-1] = -a[1:]       # lower diagonal
    V_new_interior = solve_banded((1, 1), ab, rhs)
    return V_new_interior

def pde_price(option: EuropeanOption, market: MarketData, M: int = 200, N: int = 200, S_max_multiplier: float = 4.0) -> float:
    S_grid, dS, dt, V = build_grid(option, market, M, N, S_max_multiplier)
    S_max = S_grid[-1]
    i_grid = np.arange(1, M)
    for n in range(N - 1, -1, -1):
        t = n * dt
        V_at_S0, V_at_Smax = boundary_values(option, market, S_max, t)
        V_new_interior = crank_nicolson_step(V, i_grid, dt, market.volatility, market.rate, market.dividend_yield)
        V = np.concatenate(([V_at_S0], V_new_interior, [V_at_Smax]))
    price = np.interp(market.spot, S_grid, V)
    return price

market = MarketData(spot=100, rate=0.05, volatility=0.20)
call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)
put = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.PUT)

print(pde_price(call, market, M=200, N=200))  # must be close to 10.45
print(pde_price(put, market, M=200, N=200))   # must be close to 5.57