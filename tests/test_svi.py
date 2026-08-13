import numpy as np
from qpt.calibration.svi import svi_total_variance, calibrate_svi_slice


def test_svi_calibration_returns_valid_params():
    # Synthetic smile-like data
    log_moneyness = np.linspace(-0.3, 0.3, 10)
    total_variance = 0.04 + 0.1 * log_moneyness**2  # simple symmetric smile shape

    params = calibrate_svi_slice(log_moneyness, total_variance)

    assert params["b"] >= 0
    assert -1 < params["rho"] < 1
    assert params["sigma"] > 0


def test_svi_total_variance_is_computable():
    k = np.array([-0.1, 0.0, 0.1])
    w = svi_total_variance(k, a=0.05, b=0.1, rho=-0.3, m=0.0, sigma=0.1)
    assert (w > 0).all()