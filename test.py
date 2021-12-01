import yfinance as yf

msft = yf.Ticker("AAPL")

# get stock info
print(msft.quarterly_cashflow)

msft.cashflow