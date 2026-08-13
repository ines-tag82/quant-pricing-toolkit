from qpt.data.market_data_fetcher import fetch_option_chain
from qpt.data.cleaning import clean_option_chain
from qpt.calibration.smile import compute_smile


def test_compute_smile_adds_column():
    df_raw = fetch_option_chain("AAPL", max_expiries=8)
    df_clean = clean_option_chain(df_raw)
    df_smile = compute_smile(df_clean)

    assert "implied_vol" in df_smile.columns


def test_compute_smile_values_are_reasonable():
    df_raw = fetch_option_chain("AAPL", max_expiries=8)
    df_clean = clean_option_chain(df_raw)
    df_smile = compute_smile(df_clean)

    valid_vols = df_smile["implied_vol"].dropna()
    # Most implied vols for a liquid stock should fall in a plausible range
    assert (valid_vols > 0).all()
    assert valid_vols.median() < 1.0  # median below 100% vol is a sane sanity check