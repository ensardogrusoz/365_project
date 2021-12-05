'''
@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang

@Student Name  : first last

@Date          : June 2021

Discounted Cash Flow Model with Financial Data from Yahoo Financial

https://github.com/JECSand/yahoofinancials


'''
import enum
import calendar
import math
import pandas as pd
import numpy as np

import datetime 
from scipy.stats import norm

from math import log, exp, sqrt

from stock import Stock

class DiscountedCashFlowModel(object):
    '''
    DCF Model:

    FCC is assumed to go have growth rate by 3 periods, each of which has different growth rate
           short_term_growth_rate for the next 5Y
           medium_term_growth_rate from 6Y to 10Y
           long_term_growth_rate from 11Y to 20thY
    '''

    def __init__(self, stock, as_of_date):
        self.stock = stock
        self.as_of_date = as_of_date

        self.short_term_growth_rate = None
        self.medium_term_growth_rate = None
        self.long_term_growth_rate = None


    def set_FCC_growth_rate(self, short_term_rate, medium_term_rate, long_term_rate):
        self.short_term_growth_rate = short_term_rate
        self.medium_term_growth_rate = medium_term_rate
        self.long_term_growth_rate = long_term_rate


    def calc_fair_value(self):
        '''
        calculate the fair_value using DCF model as follows

        1. calculate a yearly discount factor using the WACC
        2. Get the Free Cash flow
        3. Sum the discounted value of the FCC for the 20 years using similar approach as presented in class
        4. Compute the PV as cash + short term investments - total debt + the above sum of discounted free cash flow
        5. Return the stock fair value of the stock
        '''
        
        yearlyDF = 1 / (1 + self.stock.lookup_wacc_by_beta(self.stock.get_beta()))
        FCC = self.stock.get_free_cashflow()
        DCF = 0

        # i represents the years and we are getting the summation throughout those years
        # EPS5y = short term rate 
        for i in range(1, 6): 
            DCF += FCC * math.pow((1 + self.short_term_growth_rate), i) * math.pow(yearlyDF, i)
        # EPS6 to 10 = medium term rate
        CF5 = FCC * math.pow((1 + self.short_term_growth_rate), 5)
        for i in range(1, 6): 
            DCF += CF5 * math.pow((1 + self.medium_term_growth_rate), i) * math.pow(yearlyDF, i + 5)
        # EPS 10 to 20 = long term rate
        CF10 = CF5 * math.pow((1 + self.medium_term_growth_rate), 5)
        for i in range(1, 11): 
            DCF += CF10 * math.pow((1 + self.long_term_growth_rate), i) * math.pow(yearlyDF, i + 10)

        PV = self.stock.get_cash_and_cash_equivalent() - self.stock.get_total_debt() + DCF

        stockFairValue = PV / self.stock.get_num_shares_outstanding()

        return(stockFairValue)


def _test():
    symbol = 'AAPL'
    as_of_date = datetime.date(2021, 11, 1)
    # as_of_date = datetime.date(2021, 4, 19)

    stock = Stock(symbol)
    print(f"*********************SUMMARY FOR {symbol}*********************")
    print("Total debt: ", stock.get_total_debt())
    print("FCC: ", stock.get_free_cashflow())
    print("Cash and Cash Equivalent: ", stock.get_cash_and_cash_equivalent())
    print("Number of Shares: ", stock.get_num_shares_outstanding())
    beta = stock.get_beta()
    wacc = stock.lookup_wacc_by_beta(beta)
    print("Beta: ", beta)
    print("WACC: ", wacc)
    
    #EPS next 5Y from Finviz is 15.43%
    eps5y = 0.1543 #short term rate
    mediumTermRate = eps5y / 2 
    longTermRate = 0.04
    print(f"Short Term Rate: {eps5y}")
    print(f"Medium Term Rate: {mediumTermRate}")
    print(f"Long Term Rate: {longTermRate}")

    dcfModel = DiscountedCashFlowModel(stock, as_of_date)
    
    dcfModel.set_FCC_growth_rate(eps5y, mediumTermRate, longTermRate)

    dcfModelPrice = dcfModel.calc_fair_value()
    print(f"DCF price for {symbol} as of {as_of_date} is {dcfModelPrice}")
    print(f"***************************************************************")
    

if __name__ == "__main__":
    _test()