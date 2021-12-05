'''
@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang
@Date          : June 2021

@Student Name  : 

@Date          : Nov 2021

'''
import pandas as pd
import datetime
import yfinance as yf
from TA import RSI, VWAP, ExponentialMovingAverages, SimpleMovingAverages

from stock import Stock
from DCF_model import DiscountedCashFlowModel

def run():
    ''' 
    Read in the input file. 
    Call the DCF to compute its DCF value and add the following columns to the output file.
    You are welcome to add additional valuation metrics as you see fit

    Symbol
    EPS Next 5Y in percent
    DCF Value
    Current Price
    Sector
    Market Cap
    Beta
    Total Assets
    Total Debt
    Free Cash Flow
    P/E Ratio
    Price to Sale Ratio
    RSI
    10 day EMA
    20 day SMA
    50 day SMA
    200 day SMA

    '''
    input_fname = "StockUniverse.csv"
    output_fname = "StockUniverseOutput.csv"
    
    as_of_date = datetime.date(2021, 12, 1)
    df = pd.read_csv(input_fname)
    
    # TODO
    results = []
    for index, row in df.iterrows():
        
        stock = Stock(row['Symbol'], 'annual')
        model = DiscountedCashFlowModel(stock, as_of_date)

        short_term_growth_rate = float(row['EPS Next 5Y in percent'])/100
        medium_term_growth_rate = short_term_growth_rate/2
        long_term_growth_rate = 0.04

        model.set_FCC_growth_rate(short_term_growth_rate, medium_term_growth_rate, long_term_growth_rate)
        try:
            fair_value = model.calc_fair_value()
        except:
            fair_value = 'NA'
        curr_price = stock.yfinancial.get_current_price()
        try:
            sector = yf.Ticker(stock.symbol).info['sector']
        except:
            sector = 'NA'
        market_cap = stock.yfinancial.get_market_cap()
        beta = stock.get_beta()
        total_assets = stock.yfinancial.get_assets()
        try:
            total_debt = stock.get_total_debt()
        except:
            total_debt = 'NA'
        try:
            free_cash_flow = stock.get_free_cashflow()
        except:
            free_cash_flow = 'NA'
        pe_ratio = stock.yfinancial.get_pe_ratio()
        price_to_sale_ratio = stock.yfinancial.get_price_to_sales()
        
        stock.get_daily_hist_price("2020-01-01", "2021-11-01")
        periods = [10, 20, 50, 100, 200]
        smas = SimpleMovingAverages(stock.ohlcv_df, periods)
        smas.run()
        emas = ExponentialMovingAverages(stock.ohlcv_df, periods)
        emas.run()
        s1 = smas.get_series(10)
        rsi = RSI(stock.ohlcv_df)
        rsi = rsi.run()
        ten_day_EMA = emas._ema.get(10)
        twenty_day_SMA = smas._sma.get(20)
        fifty_day_SMA = smas._sma.get(50)
        twohundred_day_SMA = smas._sma.get(200)

        results.append(fair_value)
        results.append(curr_price)
        results.append(sector)
        results.append(market_cap)
        results.append(beta)
        results.append(total_assets)
        results.append(total_debt)
        results.append(free_cash_flow)
        results.append(pe_ratio)
        results.append(price_to_sale_ratio)
        results.append(rsi)
        results.append(ten_day_EMA)
        results.append(twenty_day_SMA)
        results.append(fifty_day_SMA)
        results.append(twohundred_day_SMA)

    # print(results)
    # print("\n -------------")

    


    # save the output into a StockUniverseOutput.csv file
    # res_df = pd.DataFrame(results)
    # print(results)
    print('done with program')
    # res_df.to_csv('StockUniverseOutput.csv',index = False, header = False, na_rep = 'NA')

    
if __name__ == "__main__":
    run()
