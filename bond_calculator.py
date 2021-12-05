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
    if end.year % 4 == 0:
        day_in_year = 366

    diff = end - start
    result = diff.days / day_in_year
    return(result)

class BondCalculator(object):

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

        return(cf)

    def calc_one_period_discount_factor(self, bond, yld):

        cf = self.compound_freq(bond, yld);
        gf = 1 + (yld/cf);
        df = 1/gf;
        return(df);

    def calc_clean_price(self, bond, yld):

        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        cf = self.compound_freq(bond, yld)
        cashFlow = bond.coupon_payment

        DF = [math.pow(one_period_factor, cf*bond.payment_times_in_year[i])
                        for i in range(len(bond.payment_times_in_year))]

        presVals = [cashFlow[i]*DF[i] for i in range(len(DF))]
        presVals[-1] += (bond.principal * DF[-1])
        totPV = sum(presVals)
        percentage = 100 * (totPV/bond.principal)

        return(percentage);

    def calc_accrual_interest(self, bond, settle_date):

        prev_pay_date = bond.get_previous_payment_date(settle_date);
        end_date = settle_date;

        if (bond.day_count == DayCount.DAYCOUNT_30360):
            frac = get_30360_daycount_frac(prev_pay_date, settle_date)
        elif (bond.day_count == DayCount.DAYCOUNT_ACTUAL_360):
            frac = get_actual360_daycount_frac(prev_pay_date, settle_date)
        elif (bond.day_count == DayCount.DAYCOUNT_ACTUAL_ACTUAL):
            frac = get_actualactual_daycount_frac(prev_pay_date, settle_date)
        else:
            raise Exception("Unsupported Day Count")

        result = frac * bond.coupon * bond.principal/100

        return(result)

    def calc_macaulay_duration(self, bond, yld):
        cf = self.compound_freq(bond, yld);
        cashFlow = bond.coupon_payment;

        presVals = [cashFlow[i]* math.exp(-1 * yld *
            bond.payment_times_in_year[i]) for i in range(len(cashFlow))];

        presVals[-1] += (bond.principal *
                    math.exp(-1 * yld * bond.payment_times_in_year[-1]));

        totPV = sum(presVals);
        weight = [presVals[i]/totPV for i in range(len(presVals))];
        timeWeight = [weight[i]*bond.payment_times_in_year[i] for i in range(len(weight))];
        totTW = sum(timeWeight);
        return(totTW)

    def calc_modified_duration(self, bond, yld):

        cf = self.compound_freq(bond, yld);
        macDuration = self.calc_macaulay_duration(bond, yld);
        newYld = cf * (math.pow(math.exp(yld), (1 / cf)) - 1);
        modDuration = macDuration / (1 + (newYld / cf));
        return(modDuration);

    def calc_yield(self, bond, bond_price):

        def match_price(yld):
            calculator = BondCalculator(self.pricing_date)
            px = calculator.calc_clean_price(bond, yld)
            return(px - bond_price)

        yld, n_iteractions = bisection(match_price, 0, 1000, eps=1.0e-6)

        return(yld)

    def calc_convexity(self, bond, yld):
        cashFlow = bond.coupon_payment;

        presVals = [cashFlow[i]* math.exp(-1 * yld *
            bond.payment_times_in_year[i]) for i in range(len(cashFlow))];

        presVals[-1] += (bond.principal *
                    math.exp(-1 * yld * bond.payment_times_in_year[-1]));

        totPV = sum(presVals);
        weight = [presVals[i]/totPV for i in range(len(presVals))];

        convexity = [math.pow(bond.payment_times_in_year[i], 2) *
                        weight[i] for i in range(len(weight))];

        totConvexity = sum(convexity);
        return(totConvexity);

##########################  MY TEST CASES ###################

def _test01():
    '''
    The purpose of this test is for checking the internal structure of our bond
    Using Bond Price Example 3 (excel)
    Testing if the 1 Period Discount Factor is correct
    '''
    print("_myTest01")
    #Setting up our bond
    issue_date = date(2020, 1, 1)
    pricing_date = date(2020, 1, 1)
    yld = .06;
    testBond = Bond(issue_date, 
                term = 2,   
                day_count = DayCount.DAYCOUNT_30360,
                payment_freq = PaymentFrequency.SEMIANNUAL, 
                coupon = 0.08, 
                principal = 100);
    
    #testing the bond and its internal structures.
    print()
    print("TESTBOND DATA INFO: ")
    print("Issue Date", testBond.issue_date)    
    print("Maturity Date", testBond.maturity_date)
    print("Payment Dates:", testBond.payment_dates)
    print("Coupon Payment:", testBond.coupon_payment)
    print("Payment time in year:", testBond.payment_times_in_year)
    print()

    #Creating a Bond Calculator
    testBondCalc = BondCalculator(pricing_date);
    
    # TESTING THE 1 PERIOD DISCOUNT FACTOR
    testOPDF = testBondCalc.calc_one_period_discount_factor(testBond, yld)
    print("1-Period Discount Factor: ", testOPDF) #should be 0.9709
    print()

def _testCP():
    '''
    Testing the Clean Price Method
    Comparing the results to Bond Price Example 02
    '''
    print()
    issue_date = date(2021, 1, 1)
    pricing_date = date(2021, 1, 1)
    yld = .06
    testBond = Bond(issue_date,
                term = 10,
                day_count = DayCount.DAYCOUNT_30360,
                payment_freq = PaymentFrequency.ANNUAL,
                coupon = 0.05)

    testBondCalc = BondCalculator(pricing_date);

    testCP = testBondCalc.calc_clean_price(testBond, yld)
    print("Clean Price:", testCP) #answer should be 92.64
    print()

def _testForMacModConv():
    '''
    Testing for the Macaulay Duration
    Testing for the Modified Duration
    Testing for the Convexity
    Comparing results to Update Duaration Calc Table 4.7
    '''
    print()
    issue_date = date(2021, 1, 1)
    pricing_date = date(2021, 1, 1)
    yld = .12
    testBond = Bond(issue_date,
                term = 3,
                day_count = DayCount.DAYCOUNT_30360,
                payment_freq = PaymentFrequency.SEMIANNUAL,
                coupon = 0.10)

    #Creating a Bond Calculator
    testBondCalc = BondCalculator(pricing_date);

    #TESTING MACAULAY DURATION
    testMacDuration = testBondCalc.calc_macaulay_duration(testBond, yld)
    print("Macaulay Duration:", testMacDuration) #answer should be 2.653
    print()

    #TESTING MODIFIED DURATION
    testModDuration = testBondCalc.calc_modified_duration(testBond, yld)
    print("Modified Duration:", testModDuration) #answer should be 2.4985
    print()

    #TESTING CONVEXITY
    testConvexity = testBondCalc.calc_convexity(testBond, yld)
    print("Convexity: ", testConvexity) #answer should be 7.57003
    print()

def _testForYield():
    '''
    Compared the results to the Yield to Maturity Excel
    '''
    print()
    issue_date = date(2021, 1, 1)
    pricing_date = date(2021, 1, 1)
    yld = 0 
    targetBondPrice = 103.72 
    testBond = Bond(issue_date,
                term = 5,
                day_count = DayCount.DAYCOUNT_30360,
                payment_freq = PaymentFrequency.SEMIANNUAL,
                coupon = 0.05)

    testBondCalc = BondCalculator(pricing_date)
    yld = testBondCalc.calc_yield(testBond, targetBondPrice)
    print("The yield of testBond is : ", yld) #answer should be 0.0416

##########################  PROFESSOR TEST CASES ###################

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


    bond = Bond(issue_date, term = 2, day_count = DayCount.DAYCOUNT_30360,
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


def _myTestCases():
    # basic test cases
    print("My Testing....")
    print("************************")
    _test01()
    print("************************")
    _testCP()
    print("************************")
    _testForMacModConv()
    print("************************")
    _testForYield()
    print("************************")
    
def _professorTestCases():
    print("Professor Testing....")
    print("************************")
    _example2()
    print("************************")
    _example3()
    print("************************")
    _example4()
    print("************************")
if __name__ == "__main__":
    _myTestCases()
    _professorTestCases()