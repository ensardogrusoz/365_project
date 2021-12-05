'''
@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang
@Date          : June 2021

@Student Name  : 

@Date          : Nov 2021

'''
import pandas as pd
import datetime

from stock import Stock
from DCF_model import DiscountedCashFlowModel
from TA import *

def run():
    ''' 
    Read in the input file. 
    Call the DCF to compute its DCF value and add the following columns to the output file.
    You are welcome to add additional valuation metrics as you see fit

    RSI

    '''
    input_fname = "StockUniverse.csv"
    output_fname = "StockUniverseOutput.csv"


    as_of_date = datetime.date(2021, 12, 1)
    df = pd.read_csv(input_fname)
    df['Current Price'] = 0
    df['Sector'] = 0
    df['Market Cap'] = 0
    df['Beta'] = 0
    df['Total Assets'] = 0
    df['Total Debt'] = 0
    df['Free Cash Flow'] = 0
    df['Price to Sales Ratio'] = 0
    df['RSI'] = 0
    df['10 Day EMA'] = 0
    df['20 Day SMA'] = 0
    df['50 Day SMA'] = 0
    df['200 Day SMA'] = 0
    pd.options.mode.chained_assignment = None

    # TODO
    results = []
    for index, row in df.iterrows():

        stock = Stock(row['Symbol'], 'annual')
        model = DiscountedCashFlowModel(stock, as_of_date)

        short_term_growth_rate = float(row['EPS Next 5Y in percent'])/100
        medium_term_growth_rate = short_term_growth_rate/2
        long_term_growth_rate = 0.04

        model.set_FCC_growth_rate(short_term_growth_rate, medium_term_growth_rate, long_term_growth_rate)

        today = str( datetime.date.today() )
        prices = stock.get_daily_hist_price(today, today)

        data = stock.yfinancial.get_stock_quote_type_data()
        quoteType = data[ row['Symbol'] ]['quoteType'][0]

        smas = SimpleMovingAverages(stock.ohlcv_df, [1])
        smas.run()
        s1 = smas.get_series(1)

        data = stock.yfinancial.get_summary_data()
        marketCap = data[ row['Symbol'] ]['marketCap']
        beta = data[ row['Symbol'] ]['beta']
        totalAssets = data[ row['Symbol'] ]['totalAssets']

        earnings_per_share = stock.yfinancial.get_earnings_per_share()

        days = datetime.timedelta(400)
        new_date = str(datetime.date.today() - days)
        stock.get_daily_hist_price(new_date, today)

        rsi_indicator = RSI(stock.ohlcv_df)
        rsi_indicator.run()

        periods = [10]
        emas = ExponentialMovingAverages(stock.ohlcv_df, periods)
        emas.run()
        emas_10 = emas.get_series(10)

        periods = [20, 50, 200]
        smas = SimpleMovingAverages(stock.ohlcv_df, periods)
        smas.run()
        smas_20 = smas.get_series(20)
        smas_50 = smas.get_series(50)
        smas_200 = smas.get_series(200)

        df['Current Price'][index] = s1
        df['Sector'][index] = quoteType
        df['Market Cap'][index] = marketCap
        df['Total Assets'][index] = totalAssets
        df['Total Debt'][index] = stock.get_total_debt()
        df['Free Cash Flow'][index] = stock.get_free_cashflow()
        df['Price to Sales Ratio'][index] = stock.yfinancial.get_price_to_sales()
        df['RSI'][index] = rsi_indicator.rsi
        df['10 Day EMA'][index] = emas_10
        df['20 Day SMA'][index] = smas_20
        df['50 Day SMA'][index] = smas_50
        df['200 Day SMA'][index] = smas_200


    df.to_csv(output_fname)
    print(df)


    # save the output into a StockUniverseOutput.csv file

    # ....

    # end TODO


if __name__ == "__main__":
    run()