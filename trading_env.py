# NOTE Current implementation is only a "fake" traidng emvironment with
# no real connection to the outside world. Develop an API that lets the bot
# interface with the real API as well.

import pandas as pd
import numpy as np

from data_factory import DataFactory
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple
from collections import defaultdict

# Reward Values for different possible actions
INVALID_BUY  = -0.25
INVALID_SELL = -0.25

VALID_BUY = 0

PROFIT = 1
LOSS   = -1
HOLD = 0

class Actions(Enum):
    BUY = 0
    SELL = 1
    HOLD = 2

class Portfolio:
    # Makes an empty list which will hold a (Company, Stock_value) list
    def __init__(self, amount, securities = defaultdict(lambda: 0)):
        self.balance = amount
        self.bought_securities = securities

    def perform_buy(self, symbol, amount, conversion):
        self.bought_securities[symbol] += amount / conversion
        self.balance -= amount

    def perform_sell(self, symbol, amount, conversion):
        self.bought_securities[symbol] -= amount
        self.balance += amount * conversion

    def __getitem__(self, key):
        return self.bought_securities[key]

class DataIterator:
    def __init__(self, filename):
        self._prices = pd.read_csv(filename).iterrows()
        self._state = None
        self.next_state()

    def next_state(self):
        self._state = next(self._prices)
        return self.current_state()

    def current_state(self):
        return self._state[1]

class TradingEnv:
    def __init__(self, portfolio, filename):
        self.portfolio = portfolio
        self.state_gen = DataIterator(filename)

    def get_conversion(self):
        '''
        Returns the converstion rate from USD to the price per Stock / Coin
        Is the bilinear average of open, close, high and low to get a representative estimate
        '''
        state = self.state_gen.current_state()
        return np.mean([state.open, state.close, state.high, state.low])

    def _trade(self, action, company_symbol = None, amount = 0.00):
        if action == Actions.BUY:
            if company_symbol == None:
                raise ValueError('Symbol not specified')

            if self.portfolio.balance == 0:
                return INVALID_BUY

            if amount > self.portfolio.balance: # TODO Might have to make this invalid
                amount = self.portfolio.balance

            self.portfolio.perform_buy(company_symbol, amount, self.get_conversion())
            return VALID_BUY

        if action == Actions.SELL:
            if company_symbol == None:
                raise ValueError('Symbol not specified')

            if self.portfolio[company_symbol] == 0:
                return INVALID_SELL

            if amount > self.portfolio[company_symbol]:
                # If I am trying to sell more than I have (but I still have some)
                # TODO Might have to make this invalid
                amount = self.portfolio[company_symbol]

            self.portfolio.perform_sell(company_symbol, amount, self.get_conversion())

            # TODO Figure out how you want to check if the sale put you in a net profit or loss
            # For now I am just assuming it is profit to see a DQN Bot which can learn to sell valid stock
            # so that I can check my DQN is working
            return PROFIT

        if action == Actions.HOLD:
            return HOLD

    def trade(self, action, company_symbol= None, amount = 0.00):
        reward = self._trade(action, company_symbol, amount)
        self.state_gen.next_state()
        return reward
