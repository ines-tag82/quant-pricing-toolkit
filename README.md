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

## Option Greeks

Both analytical (closed-form, Black-Scholes) and numerical (finite-difference, model-agnostic) 
Greeks are implemented and cross-validated against each other.

```python
from qpt.greeks.analytical_greeks import delta_call, gamma, vega, theta_call, rho_call

delta_call(call, market)   # ~0.6368
gamma(call, market)        # ~0.0188
vega(call, market)         # ~37.52
theta_call(call, market)   # ~-6.41
rho_call(call, market)     # ~53.23
```

Numerical Greeks are computed via finite differences (central difference for Delta/Vega, 
second-order central difference for Gamma) and work with any pricing function, not just 
Black-Scholes:

```python
from qpt.greeks.numerical_greeks import numerical_delta, numerical_gamma, numerical_vega
from qpt.models.black_scholes import black_scholes_price

numerical_delta(black_scholes_price, call, market)  # ~0.6368, matches the analytical value
```

Cross-validation between the two approaches agrees to within `1e-4`–`1e-8`, confirming the 
correctness of both implementations. A put-call parity identity on Delta 
(`Delta_call - Delta_put == exp(-q*T)`) is also tested as an additional no-arbitrage sanity check.

## Volatility surface calibration

Real market data was fetched for AAPL via `yfinance`, cleaned, and used to extract implied 
volatilities and calibrate a parametric SVI (Stochastic Volatility Inspired) model — one 
maturity slice at a time.

### From raw data to a usable smile

The raw option chain contains a lot of noise, and cleaning it properly required an iterative, 
diagnostic approach rather than a single fixed set of filters. Three stages of increasingly 
targeted filtering are compared below:

<table>
<tr>
<td width="33%"><img src="assets/smile_aapl_v1_raw.png" width="100%"></td>
<td width="33%"><img src="assets/smile_aapl_v2_moneyness_filtered.png" width="100%"></td>
<td width="33%"><img src="assets/smile_aapl_v3_vega_filtered.png" width="100%"></td>
</tr>
<tr>
<td align="center"><b>(a)</b> Unfiltered</td>
<td align="center"><b>(b)</b> Moneyness-restricted (0.85–1.15)</td>
<td align="center"><b>(c)</b> Volume + Vega filtered</td>
</tr>
</table>

**(a) Unfiltered**: implied volatilities computed directly from all fetched quotes, with only 
basic liquidity filters (min price, days to expiry). The result is dominated by artifacts — 
implied volatilities of 100–400% on deep in/out-of-the-money strikes, which are not economically 
meaningful.

**(b) Moneyness-restricted**: restricting strikes to 85–115% of spot removes most of the noise, 
but is a somewhat blunt instrument — it discards data based on distance from spot rather than 
the actual reliability of the quote.

**(c) Volume + Vega filtered**: a more principled approach. Implied volatility extraction is 
numerically unstable when Vega (the option's sensitivity to volatility) is low — a small pricing 
error then translates into a large implied volatility error. Filtering directly on Vega (`>= 10`), 
combined with a minimum trading volume filter (`>= 5`), addresses the root cause rather than a 
proxy for it.

*Note: a bid-ask spread filter was initially planned, but `yfinance` returns `bid=0` and `ask=0` 
for 100% of AAPL option quotes at the time of testing — a known limitation of this free data 
source. Trading volume was used as a liquidity proxy instead.*

One residual outlier remains in the final (c) dataset (strike 240, ~150% implied vol, expiry 
2026-08-28) despite Vega and volume filtering — investigation suggests this is driven by the 
option's deep-in-the-money pricing being highly sensitive to the constant risk-free rate 
assumption used across all maturities, an approximation this project does not attempt to fully 
resolve. It was kept in the dataset rather than filtered out by a stricter moneyness bound, to 
keep the analysis honest about the limits of the cleaning pipeline.

### SVI calibration

For each maturity, the raw SVI parametrization (Gatheral) was calibrated by minimizing squared 
error between model and market total implied variance:

```python
from qpt.calibration.svi import calibrate_svi_surface

surface = calibrate_svi_surface(df_smile)
# surface[expiry] -> {"a": ..., "b": ..., "rho": ..., "m": ..., "sigma": ..., "spot": ..., "maturity": ...}
```

![SVI calibrated smile](assets/smile_aapl_svi_calibrated.png)

Slices with enough strikes (e.g. 2026-09-04, 2026-09-18) produce smooth, well-behaved curves 
that closely track the market smile, with a negative `rho` consistently recovered — confirming 
the downward skew typically observed on single-stock equity options.

The 2026-08-28 slice illustrates a limitation of parametric calibration: with very few strikes 
available (including the outlier mentioned above), the 5-parameter SVI curve overfits and 
diverges sharply rather than reflecting a realistic smile shape. This is a known risk when 
calibrating flexible models to sparse data, and was left visible rather than filtered out, to 
document the failure mode honestly.

## Running tests

```bash
pytest tests/ -v
```

## Roadmap

- [x] Black-Scholes closed-form pricing
- [x] Binomial tree pricing (European & American)
- [x] Monte Carlo pricing with variance reduction
- [x] Finite difference (PDE) pricing
- [x] Analytical & numerical Greeks
- [x] Volatility surface calibration (real market data)
- [ ] Risk metrics: VaR, CVaR, backtesting
