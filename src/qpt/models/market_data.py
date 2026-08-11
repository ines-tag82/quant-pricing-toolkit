from dataclasses import dataclass


@dataclass
class MarketData:
    """Represents the market conditions used to price an option."""

    spot: float          # current price of the underlying asset
    rate: float           # risk-free interest rate (annualized, e.g. 0.03 for 3%)
    volatility: float     # annualized volatility of the underlying (e.g. 0.20 for 20%)
    dividend_yield: float = 0.0  # continuous dividend yield, defaults to 0