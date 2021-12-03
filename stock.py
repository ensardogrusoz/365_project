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
        
    #function to download daily historical closing price for yahoo
    def get_daily_hist_price(self, start_date, end_date):
        '''
        Get daily historical OHLCV pricing dataframe
        OHLCV - Open, High, Low, Close and Volume
        '''
        time_interval = 'daily'

        #getting the 'daily' historical OHLCV pricing
        data = self.yfinancial.get_historical_price_data(start_date, end_date, time_interval)
        
        #Creating an OHLCV data frame
        self.ohlcv_df = pd.DataFrame(data[self.symbol]['prices'])

        #Pushing the formatted_date column forward and set it as our index
        self.ohlcv_df = self.ohlcv_df.set_index('formatted_date')

    #calc_return is something that we don't need but provided to us     
    def calc_returns(self):
        '''
        '''
        self.ohlcv_df['prev_close'] = self.ohlcv_df['close'].shift(1)
        self.ohlcv_df['returns'] = (self.ohlcv_df['close'] - self.ohlcv_df['prev_close'])/ \
                                        self.ohlcv_df['prev_close']

    #METHODS BELOW ARE RELATED TO FINANCIAL STATEMENTS
    
    def get_total_debt(self):
        '''
        return Total debt of the company

        Total Debt = Long Term Debt + Current(short term) Debt

        Current Debt = Total Current Liabilities - Account Payables - Other Current Liabilities - Current Deferred Liabilities
        '''
        longTermDebt = self.yfinancial.get_long_term_debt()
        totalCurrentLiabilities = self.yfinancial.get_total_current_liabilities()
        accountPayable = self.yfinancial.get_account_payable()
        otherCurrentLiabilities = self.yfinancial.get_other_current_liabilities()
        currentDebt = totalCurrentLiabilities - accountPayable - otherCurrentLiabilities
        totalDebt = longTermDebt + currentDebt
        return(totalDebt)

    def get_free_cashflow(self):
        '''
        return Free Cashflow of the company
        #Free Cash Flow = Operating Cash Flow + Capital Expenditure
        #Capital Expenditure is stated as a negative number
        '''
        operatingCashFlow = self.yfinancial.get_operating_cashflow()
        capitalExpenditure = self.yfinancial.get_capital_expenditures()
        freeCashFlow = operatingCashFlow + capitalExpenditure
        return(freeCashFlow)

    def get_cash_and_cash_equivalent(self):
        '''
        Return cash and cash equivalent of the company
        '''
        cash = self.yfinancial.get_cash()
        assets = self.yfinancial.get_assets

        result = cash + assets
        return(result)

    def get_num_shares_outstanding(self):
        '''
        get current number of shares outstanding from Yahoo financial library
        '''
        numSharesOutstanding = self.yfinancial.get_num_shares_outstanding()
        return(numSharesOutstanding); 

    def get_beta(self):
        '''
        get beta from Yahoo financial
        simple because the library already has get_beta
        '''
        beta = self.yfinancial.get_beta()
        return beta

    def lookup_wacc_by_beta(self, beta):
        '''
        lookup wacc by using the table in the DiscountedCashFlowModel lecture powerpoint
        WACC is also known as the Discount Rate for the Discount Cash Flow
        The WACC here is in percentage 
        '''
        if beta < 0.8:
            WACC = 5
        elif 0.8 <= beta <= 1.0:
            WACC = 6
        elif 1.0 <= beta < 1.1:
            WACC = 6.5
        elif 1.1 <= beta < 1.2:
            WACC = 7
        elif 1.2 <= beta < 1.3:
            WACC = 7.5
        elif 1.3 <= beta < 1.5:
            WACC = 8
        elif 1.5 <= beta < 1.6:
            WACC = 8.5
        elif beta > 1.6:
            WACC = 9
        
        return(WACC)

def _test():
    # a few basic unit tests
    symbol = 'AAPL'
    stock = Stock(symbol)
    # print(f"Free Cash Flow for {symbol} is {stock.get_free_cashflow()}")

    # 
    

    start_date = '2020-1-1'
    end_date = '2021-11-1'
    # print(stock.get_daily_hist_price(start_date, end_date))
    # print(stock.calc_returns())
    # print(stock.get_total_debt())
    # print(stock.get_free_cashflow())
    # print(stock.get_beta())
    # print(stock.get_num_shares_outstanding())

    # stock.get_daily_hist_price(start_date, end_date)
    # print(type(stock.ohlcv_df))
    # print(stock.ohlcv_df.head())



if __name__ == "__main__":
    _test()
    
