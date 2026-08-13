from qpt.data.market_data_fetcher import fetch_option_chain


def test_fetch_option_chain_structure():
    df = fetch_option_chain("AAPL", max_expiries=1)

    expected_columns = {"strike", "option_price", "expiry", "spot", "days_to_expiry"}
    assert expected_columns.issubset(df.columns)
    assert len(df) > 0


def test_fetch_option_chain_spot_is_consistent():
    df = fetch_option_chain("AAPL", max_expiries=1)

    # Spot should be the same for every row (same underlying, fetched once)
    assert df["spot"].nunique() == 1


def test_fetch_option_chain_respects_max_expiries():
    df = fetch_option_chain("AAPL", max_expiries=2)

    assert df["expiry"].nunique() <= 2