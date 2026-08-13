from qpt.data.market_data_fetcher import fetch_option_chain
from qpt.data.cleaning import clean_option_chain


def test_cleaning_reduces_or_keeps_row_count():
    df_raw = fetch_option_chain("AAPL", max_expiries=8)
    df_clean = clean_option_chain(df_raw)

    assert len(df_clean) <= len(df_raw)


def test_cleaning_respects_moneyness_bounds():
    df_raw = fetch_option_chain("AAPL", max_expiries=8)
    df_clean = clean_option_chain(df_raw, moneyness_bounds=(0.7, 1.3))

    moneyness = df_clean["strike"] / df_clean["spot"]
    assert (moneyness >= 0.7).all()
    assert (moneyness <= 1.3).all()


def test_cleaning_removes_near_zero_prices():
    df_raw = fetch_option_chain("AAPL", max_expiries=8)
    df_clean = clean_option_chain(df_raw, min_price=0.05)

    assert (df_clean["option_price"] >= 0.05).all()