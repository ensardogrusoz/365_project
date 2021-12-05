'''
@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang

@Student Name  : 

@Date          : Nov 2021

Technical Indicators

'''
import enum
import calendar
import math
import pandas as pd
import numpy as np

from datetime import date
from scipy.stats import norm

from math import log, exp, sqrt

from stock import *

class SimpleMovingAverages(object):
    '''
    On given a OHLCV data frame, calculate corresponding simple moving averages
    '''
    def __init__(self, ohlcv_df, periods):
        #
        self.ohlcv_df = ohlcv_df
        self.periods = periods
        self._sma = {}

    def _calc(self, period, price_source):
        '''
        for a given period, calc the SMA as a pandas series from the price_source
        which can be  open, high, low or close
        '''
        
        size = self.ohlcv_df[price_source].size 
        total = 0
        for i in range(0, period):
            total += self.ohlcv_df[price_source][size - i - 1]

        result = total / period

        return(result)
        
    def run(self, price_source = 'close'):
        '''
        Calculate all the simple moving averages as a dict
        '''
        for period in self.periods:
            self._sma[period] = self._calc(period, price_source)
    
    def get_series(self, period):
        return(self._sma[period])

    
class ExponentialMovingAverages(object):
    '''
    On given a OHLCV data frame, calculate corresponding simple moving averages
    '''
    def __init__(self, ohlcv_df, periods):
        #
        self.ohlcv_df = ohlcv_df
        self.periods = periods
        self._ema = {}

    def _calc(self, period):
        '''
        for a given period, calc the SMA as a pandas series
        '''
        
        size = self.ohlcv_df['close'].size
        total = 0
        for i in range(0, period):
            total += self.ohlcv_df['close'][size - i - 1 - period]

        first_day = total / period
        smoothing_factor = 2


        for i in range(0, period):
            first_day *= (1 - smoothing_factor/(1 + period))
            first_day += self.ohlcv_df['close'][size - 1 - period + i] * smoothing_factor/(1 + period)


        result = first_day

        return(result)
        
    def run(self):
        '''
        Calculate all the exponential moving averages as a dict
        '''
        for period in self.periods:
            self._ema[period] = self._calc(period)


    def get_series(self, period):
        return(self._ema[period])


class RSI(object):

    def __init__(self, ohlcv_df, period = 14):
        self.ohlcv_df = ohlcv_df
        self.period = period
        self.rsi = None

    def get_series(self):
        return(self.rsi)

    def run(self):
        size = self.ohlcv_df['close'].size
        up = 0
        down = 0
        for i in range(0, self.period):
            if (self.ohlcv_df['close'][size - i - 1] > self.ohlcv_df['close'][size - i - 2]): 
                up += 1
            if (self.ohlcv_df['close'][size - i - 1] < self.ohlcv_df['close'][size - i - 2]): 
                down += 1

        result = 100 - 100/(1 + (up/self.period)/(down/self.period) )

        self.rsi = result
        return(result)

class VWAP(object):

    def __init__(self, ohlcv_df):
        self.ohlcv_df = ohlcv_df
        self.vwap = None

    def get_series(self):
        return(self.vwap)

    def run(self):
        size = self.ohlcv_df['volume'].size
        total_volume = 0
        total_price = 0
        for i in range(0, size):
            total_volume += self.ohlcv_df['volume'][size - i - 1]
            total_price += self.ohlcv_df['close'][size - i - 1]

        result = total_price * self.ohlcv_df['volume'][size - 1] / total_volume

        return(result)



def _test():
    # simple test cases
    symbol = 'AAPL'
    stock = Stock(symbol)
    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date.today()

    stock.get_daily_hist_price("2020-01-01", "2021-11-01")

    periods = [9, 20, 50, 100, 200]
    smas = SimpleMovingAverages(stock.ohlcv_df, periods)
    smas.run()
    emas = ExponentialMovingAverages(stock.ohlcv_df, periods)
    emas.run()
    s1 = smas.get_series(9)

    rsi_indicator = RSI(stock.ohlcv_df)
    rsi_indicator.run()

    #print(f"RSI for {symbol} is {rsi_indicator.rsi}")

    vwap = VWAP(stock.ohlcv_df)
    vwap.run()
    

if __name__ == "__main__":
    _test()
