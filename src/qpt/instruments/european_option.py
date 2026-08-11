from dataclasses import dataclass
from enum import Enum


class OptionType(Enum):
    """Whether the option is a call (right to buy) or a put (right to sell)."""
    CALL = "call"
    PUT = "put"


@dataclass
class EuropeanOption:
    """Represents a European-style option (exercisable only at maturity)."""

    strike: float           # the price at which the option can be exercised
    maturity: float         # time to expiry, in years (e.g. 0.5 for 6 months)
    option_type: OptionType # OptionType.CALL or OptionType.PUT

    def payoff(self, spot_at_maturity: float) -> float:
        """Compute the option's payoff given the underlying price at maturity."""
        if self.option_type == OptionType.CALL:
            return max(spot_at_maturity - self.strike, 0.0)
        else:
            return max(self.strike - spot_at_maturity, 0.0)