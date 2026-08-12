# Quant Pricing Toolkit

A Python toolkit for derivatives pricing, volatility calibration, and portfolio risk (VaR/CVaR)

## Overview

This project implements multiple option pricing methods (closed-form, tree-based, Monte Carlo, PDE), 
computes option Greeks, calibrates volatility surfaces to real market data, and provides portfolio 
risk metrics (VaR/CVaR) with statistical backtesting.

## Installation

```bash
git clone https://github.com/ines-tag82/quant-pricing-toolkit.git
cd quant-pricing-toolkit
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Pricing methods

Four independent pricing methods are implemented and cross-validated against each other 
(all converge to the same Black-Scholes value for a European option):

| Method | European options | American options | Notes |
|---|---|---|---|
| Black-Scholes (closed-form) | ✅ | ❌ | Instant, exact under model assumptions |
| Binomial tree (CRR) | ✅ | ✅ | Converges to Black-Scholes as `n_steps` increases |
| Monte Carlo | ✅ | ❌ | Includes antithetic variates for variance reduction |
| PDE (Crank-Nicolson) | ✅ | ❌ | Finite-difference solution of the Black-Scholes PDE |

### Black-Scholes pricing (closed-form)

Analytical pricing for European call/put options.

```python
from qpt.models.market_data import MarketData
from qpt.instruments.european_option import EuropeanOption, OptionType
from qpt.models.black_scholes import black_scholes_price

market = MarketData(spot=100, rate=0.05, volatility=0.20)
call = EuropeanOption(strike=100, maturity=1.0, option_type=OptionType.CALL)

price = black_scholes_price(call, market)  # ~10.45
```

### Binomial tree pricing (CRR)

Tree-based pricing for European and American options, using the Cox-Ross-Rubinstein model.

```python
from qpt.pricing.binomial_tree import binomial_tree_price

# European option (converges to Black-Scholes as n_steps increases)
price = binomial_tree_price(call, market, n_steps=500, american=False)

# American option (allows early exercise)
put = EuropeanOption(strike=110, maturity=1.0, option_type=OptionType.PUT)
american_price = binomial_tree_price(put, market, n_steps=200, american=True)
```

### Monte Carlo pricing

Simulation-based pricing with optional antithetic variates for variance reduction. 
Returns both the price estimate and its standard error.

```python
from qpt.pricing.monte_carlo import monte_carlo_price

price, stderr = monte_carlo_price(call, market, n_paths=100_000, antithetic=True, seed=42)
# price ~10.45, stderr gives the statistical confidence of the estimate
```

### PDE pricing (Crank-Nicolson)

Finite-difference solution of the Black-Scholes partial differential equation, 
using a Crank-Nicolson scheme (unconditionally stable, second-order accurate).

```python
from qpt.pricing.pde import pde_price

price = pde_price(call, market, M=200, N=200)  # ~10.44
```

## Running tests

```bash
pytest tests/ -v
```

## Roadmap

- [x] Black-Scholes closed-form pricing
- [x] Binomial tree pricing (European & American)
- [X] Monte Carlo pricing with variance reduction
- [X] Finite difference (PDE) pricing
- [ ] Analytical & numerical Greeks
- [ ] Volatility surface calibration (real market data)
- [ ] Risk metrics: VaR, CVaR, backtesting

