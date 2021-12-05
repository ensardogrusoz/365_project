'''
@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang

@Group Name    : Goldman Bros
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
    diff = end - start
    if end.year % 4 == 0:
        day_in_year = 366
    result = diff.days / day_in_year
    return(result)

class BondCalculator(object):
    '''
    Bond Calculator class for pricing a bond
    '''

    def __init__(self, pricing_date):
        self.pricing_date = pricing_date

    def calc_one_period_discount_factor(self, bond, yld):
        if bond.payment_freq.name == "ANNUAL":
            df = 1/(1 + yld)
        elif bond.payment_freq.name == "SEMIANNUAL":
            df = 1/(1 + yld/2)
        elif bond.payment_freq.name == "QUARTERLY":
            df = 1/(1 + yld/4)
        elif bond.payment_freq.name == "MONTHLY":
            df = 1/(1 + yld/12)
        else:
            df = 1

        return df

    def calc_clean_price(self, bond, yld):
        '''
        Calculate bond price as of the pricing_date for a given yield
        bond price should be expressed in percentage eg 100 for a par bond
        '''
        result = 0
        cf = bond.coupon * 100

        if bond.payment_freq.name == "ANNUAL":
            cf 
        elif bond.payment_freq.name == "SEMIANNUAL":
            cf = cf / 2
        elif bond.payment_freq.name == "QUARTERLY":
            cf = cf / 4
        elif bond.payment_freq.name == "MONTHLY":
            cf = cf / 12
        else:
            cf

        
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        # TODO: implement calculation here
        for n in range(bond.term):
            df = one_period_factor ** (n + 1)
            if n == (bond.term - 1):
                result += (cf + 100) * df 
            else:
                result += cf * df

        # end TODO:
        
        return(result)

    def calc_accrual_interest(self, bond, settle_date):
        '''
        calculate the accrual interest on given a settle_date
        by calculating the previous payment date first and use the date count
        from previous payment date to the settle_date
        '''
        prev_pay_date = bond.get_previous_payment_date(settle_date)
        end_date = settle_date

        if (bond.day_count == DayCount.DAYCOUNT_30360):
            frac = get_30360_daycount_frac(prev_pay_date, settle_date)
        elif (bond.day_count == DayCount.DAYCOUNT_ACTUAL_360):
            frac = get_actual360_daycount_frac(prev_pay_date, settle_date)

        result = frac * bond.coupon * bond.principal/100

        # end TODO
        return(frac)

    def calc_macaulay_duration(self, bond, yld):
        result = 0
        cf = bond.coupon * 100

        if bond.payment_freq.name == "ANNUAL":
            cf 
        elif bond.payment_freq.name == "SEMIANNUAL":
            cf = cf / 2
        elif bond.payment_freq.name == "QUARTERLY":
            cf = cf / 4
        elif bond.payment_freq.name == "MONTHLY":
            cf = cf / 12
        else:
            cf

        
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        sum_pv = 0
        for n in range(bond.term):
            df = one_period_factor ** (n + 1)
            if n == (bond.term - 1):
                pv = (cf + 100) * df 

            else:
                pv = cf * df
                    
            sum_pv += pv
            result += pv * (n + 1)
      
        result = result / sum_pv
        return(result)

    def calc_modified_duration(self, bond, yld):
        '''
        calculate modified duration at a certain yield yld
        '''

        if bond.payment_freq.name == "ANNUAL":
            n = 1
        elif bond.payment_freq.name == "SEMIANNUAL":
            n = 2
        elif bond.payment_freq.name == "QUARTERLY":
            n = 4
        elif bond.payment_freq.name == "MONTHLY":
            n = 12
        else:
            n = 0

        D = self.calc_macaulay_duration(bond, yld)

        result = D / (1 + (yld / n))

        return(result)

    def calc_yield(self, bond, bond_price):
        '''
        Calculate the yield to maturity on given a bond price using bisection method
        '''

        def match_price(yld):
            calculator = BondCalculator(self.pricing_date)
            px = calculator.calc_clean_price(bond, yld)
            return(px - bond_price)

        yld, n_iteractions = bisection(match_price, 0, 1000, eps=1.0e-6)

        return(yld)


    def calc_convexity(self, bond, yld):
        sum_parts = 0
        cf = bond.coupon * 100

        if bond.payment_freq.name == "ANNUAL":
            cf 
        elif bond.payment_freq.name == "SEMIANNUAL":
            cf = cf / 2
        elif bond.payment_freq.name == "QUARTERLY":
            cf = cf / 4
        elif bond.payment_freq.name == "MONTHLY":
            cf = cf / 12
        else:
            cf

        
        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        for n in range(bond.term):

            if n == (bond.term - 1):
                cf = cf + 100
     
            sum_parts += (cf/(1 + yld) ** (n + 1)) * ((n + 1) ** 2 + (n + 1))
      
        clean_price = self.calc_clean_price(bond, yld)
        result = 1 / (clean_price * (1 + yld) ** 2) * sum_parts
        return(result)


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

    assert( abs(yld - 
    0.04168) < 0.01)
    
def _test():
    # basic test cases
    _example2()
    _example3()
    _example4()

    

if __name__ == "__main__":
   _test()

def _example5():
    issue_date = date(2020, 1, 1)
    pricing_date = date(2020, 1, 1)
    settle_date = date(2021, 5, 10)
    engine = BondCalculator(pricing_date)
    yld = .06
    price = 103.72
    # Example 5
    bond = Bond(issue_date,
                term=5,
                day_count = DayCount.DAYCOUNT_30360,
                payment_freq = PaymentFrequency.SEMIANNUAL,
                coupon = 0.05, 
                principal = 100)

    
    px_bond2 = engine.calc_clean_price(bond, yld)
    print("The clean price of bond 2 is: ", format(px_bond2, '.4f'))
    # assert( abs(px_bond2 - 92.640) < 0.01)

    print("calc_one_period_discount_factor" , engine.calc_one_period_discount_factor(bond, yld))
    print("calc_clean_price" , engine.calc_clean_price(bond, yld))
    print("calc_accrual_interest" , engine.calc_accrual_interest(bond, settle_date))
    print("calc_macaulay_duration" , engine.calc_macaulay_duration(bond, yld))
    print("calc_modified_duration" , engine.calc_modified_duration(bond, yld))
    print("calc_yield" , engine.calc_yield(bond, price))
    print("calc_convexity" , engine.calc_convexity(bond, yld))

# _example5()