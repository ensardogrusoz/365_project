'''
@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang

@Student Name  : 

@Date          : Nov 2021


'''
import enum
import calendar
import math
import pandas as pd
import numpy as np

import datetime 
from scipy.stats import norm

from math import log, exp, sqrt

from utils import MyYahooFinancials 

class Stock(object):
    '''
    Stock class for getting financial statements as well as pricing data
    '''
    def __init__(self, symbol, spot_price = None, sigma = None, dividend_yield = 0, freq = 'annual'):
        self.symbol = symbol
        self.spot_price = spot_price
        self.sigma = sigma
        self.dividend_yield = dividend_yield
        self.yfinancial = MyYahooFinancials(symbol, freq)
        self.ohlcv_df = None
        

    def get_daily_hist_price(self, start_date, end_date):
        '''
        Get daily historical OHLCV pricing dataframe
        '''
        # TODO
        data = self.yfinancial.get_historical_price_data(start_date, end_date, 'daily')
        # create a OHLCV data frame
        self.ohlcv_df = pd.DataFrame(data[self.symbol]['prices'])
        # print(self.ohlcv_df)
        #end TODO
        
    def calc_returns(self):
        '''
        '''
        self.ohlcv_df['prev_close'] = self.ohlcv_df['close'].shift(1)
        self.ohlcv_df['returns'] = (self.ohlcv_df['close'] - self.ohlcv_df['prev_close'])/ \
                                        self.ohlcv_df['prev_close']

        # print(self.ohlcv_df['prev_close'])
        # print(self.ohlcv_df['returns'])


    # financial statements related methods
    
    def get_total_debt(self):
        '''
        return Total debt of the company
        '''
        result = None
        long = self.yfinancial.get_long_term_debt()
        shortLong = self.yfinancial._financial_statement_data('balance', 'balanceSheetHistory', 'shortLongTermDebt', "annual")

        result = (long + shortLong) - (self.get_cash_and_cash_equivalent())

        return(result)

    def get_free_cashflow(self):
        '''
        return Free Cashflow of the company
        '''
        cashFlow = self.yfinancial.get_operating_cashflow()
        expenditures = self.yfinancial._financial_statement_data('cash', 'cashflowStatementHistory', 'capitalExpenditures', 'annual')
        result = cashFlow + expenditures
        return(result)

    def get_cash_and_cash_equivalent(self):
        '''
        Return cash and cash equivalent of the company
        '''
        result = None
        cash = self.yfinancial.get_cash()
        assets = self.yfinancial._financial_statement_data('balance', 'balanceSheetHistory', 'totalCurrentAssets', 'annual')
        
        result = cash + assets

        return(result)

    def get_num_shares_outstanding(self):
        '''
        get current number of shares outstanding from Yahoo financial library
        '''
        result = self.yfinancial.get_num_shares_outstanding('current')
        return(result)

    def get_beta(self):
        '''
        get beta from Yahoo financial
        '''
        result = self.yfinancial.get_beta()

        return(result)

    def lookup_wacc_by_beta(self, beta):
        '''
        lookup wacc by using the table in the DiscountedCashFlowModel lecture powerpoint
        '''
        if beta < 0.8:
            result = 5
        elif 0.8 <= beta < 1.0:
            result = 6
        elif 1.0 <= beta < 1.1:
            result = 6.5
        elif 1.1 <= beta < 1.2:
            result = 7
        elif 1.2 <= beta < 1.3:
            result = 7.5
        elif 1.3 <= beta < 1.4:
            result = 8
        elif 1.5 <= beta < 1.6:
            result = 8.5
        elif beta > 1.6:
            result = 9
        
        return(result)
        



def _test():
    # a few basic unit tests
    symbol = 'AAPL'
    stock = Stock(symbol)
    print(f"Free Cash Flow for {symbol} is {stock.get_free_cashflow()}")

    # 
    

    start_date = '2020-1-1'
    end_date = '2021-11-1'
    # print(stock.get_daily_hist_price(start_date, end_date))
    # print(stock.calc_returns())
    # print(stock.get_total_debt())
    # print(stock.get_free_cashflow())
    # print(stock.get_beta())
    # print(stock.get_num_shares_outstanding())

    stock.get_daily_hist_price(start_date, end_date)
    print(type(stock.ohlcv_df))
    print(stock.ohlcv_df.head())



if __name__ == "__main__":
    _test()
    
