import yfinance as yf
import pandas as pd

def fetch_option_chain(ticker: str, max_expiries: int = 3) -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    spot = stock.history(period="1d")["Close"].iloc[-1]
    expiries_dates = stock.options[:max_expiries] 
    all_data = []
    dataframe = [stock.option_chain(date).calls for date in expiries_dates]
    for i in range(len(dataframe)):
        strike, option_price, expiry= dataframe[i]["strike"], dataframe[i]["lastPrice"], expiries_dates[i]
        r = pd.to_datetime(expiries_dates[i]) - pd.Timestamp.now()
        days_to_expiry = r.days
        for j in range(len(strike)):
            all_data.append({"strike": strike.iloc[j], "option_price": option_price.iloc[j], "expiry": expiry, "spot": spot, "days_to_expiry": days_to_expiry})
    result = pd.DataFrame(all_data)
    return result

df = fetch_option_chain("AAPL", max_expiries=2)
print(df.head())
print(df.tail())
print(df.shape)
print(df["expiry"].unique())
