import matplotlib.pyplot as plt
from qpt.data.market_data_fetcher import fetch_option_chain
from qpt.data.cleaning import clean_option_chain
from qpt.calibration.smile import compute_smile

TICKER = "AAPL"


def plot_smile(df, title, filename):
    fig, ax = plt.subplots(figsize=(10, 6))
    for expiry, group in df.groupby("expiry"):
        group_sorted = group.sort_values("strike")
        ax.plot(group_sorted["strike"], group_sorted["implied_vol"], marker="o", markersize=3, label=f"Expiry: {expiry}")
    ax.set_xlabel("Strike")
    ax.set_ylabel("Implied volatility")
    ax.set_title(title)
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close(fig)
    print(f"Saved: {filename}\n")


print(f"Fetching option chain for {TICKER}...")
df_raw = fetch_option_chain(TICKER, max_expiries=8)
print(f"Raw options fetched: {len(df_raw)}\n")

# --- v1: raw, no vega filtering, broad moneyness ---
df_clean_v1 = clean_option_chain(df_raw, moneyness_bounds=(0.5, 2.0))
df_smile_v1 = compute_smile(df_clean_v1, min_vega=0.0)  # no vega filter
print(f"v1 (raw): {len(df_smile_v1)} options")
plot_smile(df_smile_v1, f"{TICKER} implied volatility smile — v1: unfiltered", "assets/smile_aapl_v1_raw.png")

# --- v2: moneyness-restricted only ---
df_clean_v2 = clean_option_chain(df_raw, moneyness_bounds=(0.85, 1.15))
df_smile_v2 = compute_smile(df_clean_v2, min_vega=0.0)  # still no vega filter
print(f"v2 (moneyness-filtered): {len(df_smile_v2)} options")
plot_smile(df_smile_v2, f"{TICKER} implied volatility smile — v2: moneyness filtered", "assets/smile_aapl_v2_moneyness_filtered.png")

# --- v3: vega filtering (final, most reliable) ---
df_clean_v3 = clean_option_chain(df_raw)  # default moneyness
df_smile_v3 = compute_smile(df_clean_v3, min_vega=10.0)
print(f"v3 (vega-filtered): {len(df_smile_v3)} options")
plot_smile(df_smile_v3, f"{TICKER} implied volatility smile — v3: vega filtered", "assets/smile_aapl_v3_vega_filtered.png")

print("Implied volatility summary (v3, final):")
print(df_smile_v3["implied_vol"].describe().round(4))