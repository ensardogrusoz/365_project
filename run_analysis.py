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
        
        fair_value = model.calc_fair_value()

        # pull additional fields
        # ...


    # save the output into a StockUniverseOutput.csv file
    
    # ....
    
    # end TODO

    
if __name__ == "__main__":
    run()
