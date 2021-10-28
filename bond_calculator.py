'''
@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang

@Group Name    : The Goldman Bros
@Student Name  : Ensar Dogrusoz

@Date          : Fall 2021

A Bond Calculator Class

'''

import math
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from bisection_method import bisection

import enum
import calendar

from datetime import date

from bond import Bond, DayCount, PaymentFrequency


def get_actual360_daycount_frac(start, end):
    day_in_year = 360
    day_count = (end - start).days
    return(day_count / day_in_year)

def get_30360_daycount_frac(start, end):
    day_in_year = 360
    day_count = 360*(end.year - start.year) + 30*(end.month - start.month - 1) + \
                max(0, 30 - start.day) + min(30, end.day)
    return(day_count / day_in_year )
    

def get_actualactual_daycount_frac(start, end):
    day_in_year = 365
    day_count = (end - start).days
    try:
        if (day_count > 365): raise
    except Exception as err:
        return print('try again, daycount cant be a year apart')
    return((day_count / day_in_year))

class BondCalculator(object):
    '''
    Bond Calculator class for pricing a bond
    '''

    def __init__(self, pricing_date):
        self.pricing_date = pricing_date

    def compound_freq(self, bond, yld):
        cf = 0
        if(bond.payment_freq == PaymentFrequency.ANNUAL):
            cf = 1
        elif(bond.payment_freq == PaymentFrequency.SEMIANNUAL):
            cf = 2
        elif(bond.payment_freq == PaymentFrequency.QUARTERLY):
            cf = 4
        elif(bond.payment_freq == PaymentFrequency.MONTHLY):
            cf = 12
        elif(bond.payment_freq == PaymentFrequency.CONTINUOUS):
            cf = math.exp(-yld,bond.term)
        #print("Hello Compound Frequency")
        return(cf)

    def calc_one_period_discount_factor(self, bond, yld):
        # calculate the future cashflow vectors
        # TODO: calculate the one period discount factor
        # hint: need to use if else statement for different payment frequency cases
        # cf = 0

        # if(bond.payment_freq == PaymentFrequency.ANNUAL):
        #     cf = 1
        # elif(bond.payment_freq == PaymentFrequency.SEMIANNUAL):
        #     cf = 2
        # elif(bond.payment_freq == PaymentFrequency.MONTHLY):
        #     cf = 12
        # elif(bond.payment_freq == PaymentFrequency.QUARTERLY):
        #     cf = 4
        # elif(bond.payment_freq == PaymentFrequency.CONTINUOUS):
        #     cf = math.exp(-yld,bond.term)

        # gf = 1 + yld/cf

        # df = 1/gf
        # # print(df)
        # return(df)

        #1 Period Discount Factor =  1 / Period Growth Factor
        #1 Period Growth Factor =  1 + Annualized Rate / Compounding Frequency

        #getting the compounding frequency
        cf = self.compound_freq(bond, yld)
        
        #getting the 1 Period Growth Factor
        gf = 1 + (yld/cf)

        #getting the 1 Period Discount Factor
        df = 1/gf
        df = round(df, 4)
        return(df)


    def calc_clean_price(self, bond, yld):
        '''
        Calculate bond price as of the pricing_date for a given yield
        bond price should be expressed in percentage eg 100 for a par bond
        '''
        #result = none;
        #get 1 Period Discount Factor
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)

        #getting the compounding frequency
        cf = self.compound_freq(bond, yld)
        
        #calculating the Cash Flow
        cashFlow = [bond.principal * (bond.coupon/cf) for i in range(1, cf*bond.term + 1)]

        #calculating the Discount Factors
        DF = [math.pow(one_period_factor, i) for i in range(1, cf * bond.term + 1)]

        #calculating the Present Values
        presVals = [cashFlow[i]*DF[i] for i in range(len(DF))]

        #calculating sum of Present Values 
        totPV = sum(presVals) + (bond.principal * DF[-1])

        #bond price should be expressed in percentage eg 100 for a par bond
        percentage = round(100 * (totPV/bond.principal), 4)
        return(percentage)
        


    def calc_accrual_interest(self, bond, settle_date):
        '''
        calculate the accrual interest on given a settle_date
        by calculating the previous payment date first and use the date count
        from previous payment date to the settle_date
        '''
        prev_pay_date = bond.get_previous_payment_date(settle_date)
        end_date = settle_date
        
        if (bond.day_count == DayCount.DAYCOUNT_30360):
            frac = get_30360_daycount_frac(prev_pay_date, end_date)
        elif (bond.day_count == DayCount.DAYCOUNT_ACTUAL_360):
            frac = get_actual360_daycount_frac(prev_pay_date, end_date)
        elif (bond.day_count == DayCount.DAYCOUNT_ACTUAL_ACTUAL):
            frac = get_actualactual_daycount_frac(prev_pay_date, end_date) 
        
        result = round(frac * bond.coupon * bond.principal/100, 4)
        return(result)

    def calc_macaulay_duration(self, bond, yld):
        '''
        time to cashflow weighted by PV
        '''
        cf = self.compound_freq(bond, yld)
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        #calculating the Cash Flow
        cashFlow = [bond.principal * (bond.coupon/cf) for i in range(1, cf*bond.term + 1)]

        #calculating the Discount Factors
        DF = [math.pow(one_period_factor, i) for i in range(1, cf * bond.term + 1)]

        #calculating the Present Values
        presVals = [cashFlow[i]*DF[i] for i in range(len(DF))]

        #calculating sum of Present Values 
        totPV = sum(presVals) + (bond.principal * DF[-1])
        #calculating sum of weights
        weight = [presVals[i]/totPV for i in range(len(DF))]
        time = [i * (1/cf) for i in range(1,cf*bond.term+1)]
        #calculating time * weight
        timeWeight = [weight[i]*time[i] for i in range(len(DF))]
        # summing of everything
        sumTimeWeight = 0
        for i in range(len(timeWeight)):
            sumTimeWeight += timeWeight[i]

        #result =( sum(wavg) / sum(PVs))
        result = round(sumTimeWeight/totPV,4)
        
        return(result)

    def calc_modified_duration(self, bond, yld):
        '''
        calculate modified duration at a certain yield yld
        '''
        D = self.calc_macaulay_duration(bond, yld)

        # TODO: implement details here
        # end TODO:
        return(result)

    def calc_yield(self, bond, bond_price):
        '''
        Calculate the yield to maturity on given a bond price using bisection method
        '''

        def match_price(yld):
            calculator = BondCalculator(self.pricing_date)
            px = calculator.calc_clean_price(bond, yld)
            return(px - bond_price)

        # TODO: implement details here
        #yld, n_iteractions = bisection( ....)
        # end TODO:
        return(yld)

    def calc_convexity(self, bond, yld):
        # calculate convexity of a bond at a certain yield yld

        # TODO: implement details here
        # result = sum(wavg) / sum(PVs))
        return( result)


##########################  some test cases ###################

def _example2():
    pricing_date = date(2021, 1, 1)
    issue_date = date(2021, 1, 1)
    engine = BondCalculator(pricing_date)

    # Example 2
    bond = Bond(issue_date, term=10, day_count = DayCount.DAYCOUNT_30360,
                 payment_freq = PaymentFrequency.ANNUAL, coupon = 0.05)

    yld = 0.06
    px_bond2 = engine.calc_clean_price(bond, yld)
    print("The clean price of bond 2 is: ", format(px_bond2, '.4f'))
    assert( abs(px_bond2 - 92.640) < 0.01)

    
def _example3():
    pricing_date = date(2021, 1, 1)
    issue_date = date(2021, 1, 1)
    engine = BondCalculator(pricing_date)

    
    bond = Bond(issue_date, term = 2, day_count =DayCount.DAYCOUNT_30360,
                 payment_freq = PaymentFrequency.SEMIANNUAL,
                 coupon = 0.08)

    yld = 0.06
    px_bond3 = engine.calc_clean_price(bond, yld)
    print("The clean price of bond 3 is: ", format(px_bond3, '.4f'))
    assert( abs(px_bond3 - 103.717) < 0.01)


def _example4():
    # unit tests
    pricing_date = date(2021, 1, 1)
    issue_date = date(2021, 1, 1)
    engine = BondCalculator(pricing_date)

    # Example 4 5Y bond with semi-annual 5% coupon priced at 103.72 should have a yield of 4.168%
    price = 103.72
    bond = Bond(issue_date, term=5, day_count = DayCount.DAYCOUNT_30360,
                payment_freq = PaymentFrequency.SEMIANNUAL, coupon = 0.05, principal = 100)
    

    yld = engine.calc_yield(bond, price)

    print("The yield of bond 4 is: ", yld)

    assert( abs(yld - 0.04168) < 0.01)
    
def _test():
    # basic test cases
    _example2()
    _example3()
    _example4()

    

if __name__ == "__main__":
    # _test()
    issue_date = date(2020, 1, 1)
    pricing_date = date(2020, 1, 1)
    settle_date = date(2021, 5, 10)
    yld = .06
    testBond = Bond(issue_date, 
                term = 2,   
                day_count = DayCount.DAYCOUNT_30360,
                payment_freq = PaymentFrequency.SEMIANNUAL, 
                coupon = 0.08, 
                principal = 100)
    testBondCalc = BondCalculator(pricing_date)

    #TESTING 1 PERIOD DISCOUNT FACTOR
    testOPDF = testBondCalc.calc_one_period_discount_factor(testBond, yld)
    print(testOPDF) #should be 0.9709

    #TESTING CLEAN PRICE
    #clean price of the bond is the present value of the FV

    testCP = testBondCalc.calc_clean_price(testBond, yld)
    print(testCP)

    testAI = testBondCalc.calc_accrual_interest(testBond, settle_date)
    print(testAI)

    testMD = testBondCalc.calc_macaulay_duration(testBond, yld)
    print(testMD)
    


