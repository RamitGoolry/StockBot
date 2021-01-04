# NOTE Current implementation is only a "fake" traidng emvironment with
# no real connection to the outside world. Develop an API that lets the bot
# interface with the real API as well.

import pandas as pd
import numpy as np

from enum import Enum
from collections import defaultdict

from debugger import log

# Reward Values for different possible actions
INVALID_BUY  = -0.25
INVALID_SELL = -0.25

VALID_BUY = 0

PROFIT = 1
LOSS   = -1
HELD = 0

# Actions
BUY = 0
SELL = 1
HOLD = 2

class Portfolio:
    # Makes an empty list which will hold a (Company, Stock_value) list
    def __init__(self, amount):
        self.balance = amount
        self.bought_securities = defaultdict(lambda: 0)

    def perform_buy(self, symbol, amount, conversion):
        self.bought_securities[symbol] += amount / conversion
        self.balance -= amount

    def perform_sell(self, symbol, amount, conversion):
        self.bought_securities[symbol] -= amount
        self.balance += amount * conversion

    def __getitem__(self, key):
        return self.bought_securities[key]

class DataIterator:
    def __init__(self, filename, preprocessing = None):
        df = pd.read_csv(filename) # TODO Window for 1 Dimensional Convolution

        if preprocessing != None:
            df = preprocessing(df)

        self._prices = df.iterrows()
        self._state = None
        self.next_state()

    def next_state(self):
        self._state = next(self._prices)
        return self.current_state()

    def current_state(self):
        return self._state[1]

EPISODE_END = True
EPISODE_NOT_END = False
class TradingEnv:
    def __init__(self, portfolio : Portfolio, filename : str, preprocessing = None):
        self.portfolio = portfolio
        self.state_gen = DataIterator(filename, preprocessing)

    def get_conversion(self):
        '''
        Returns the converstion rate from USDs per Stock/Coin
        '''
        state = self.state_gen.current_state()
        return np.mean([state.open, state.close, state.high, state.low])

    def get_state(self):
        state_gen_state = self.state_gen.current_state()
        # State Format : (Stock Price, Stocks Held, Timestep) 
        # TODO Improve based on model (Timestep -> Transformer, No -> RNN, NLP of online data)
        mean_stock_price = np.mean([state_gen_state.open, state_gen_state.close, state_gen_state.high, state_gen_state.low])
        log(f'[*] mean_stock_price - {mean_stock_price}')
        time_str = state_gen_state.name # TODO Use timestamp

        return np.array([mean_stock_price, self.portfolio['BTC'], self.portfolio.balance]) # TODO More currencies
    
    def get_net_worth(self):
        return self.portfolio.balance + self.portfolio['BTC'] * self.get_conversion()

    def _trade(self, action, company_symbol = None, amount = 0.00):
        if action == BUY:
            if company_symbol == None:
                raise ValueError('Symbol not specified')

            if self.portfolio.balance == 0:
                return INVALID_BUY, EPISODE_NOT_END

            if amount > self.portfolio.balance: # TODO Might have to make this invalid
                amount = self.portfolio.balance

            self.portfolio.perform_buy(company_symbol, amount, self.get_conversion())
            return VALID_BUY, EPISODE_NOT_END

        if action == SELL:
            if company_symbol == None:
                raise ValueError('Symbol not specified')

            if self.portfolio[company_symbol] == 0:
                return INVALID_SELL, EPISODE_NOT_END

            if amount > self.portfolio[company_symbol]:
                # If I am trying to sell more than I have (but I still have some)
                # TODO Might have to make this invalid
                amount = self.portfolio[company_symbol]

            self.portfolio.perform_sell(company_symbol, amount, self.get_conversion())

            # TODO Figure out how you want to check if the sale put you in a net profit or loss
            # For now I am just assuming it is profit to see a DQN Bot which can learn to sell valid stock
            # so that I can check my DQN is working
            return PROFIT, EPISODE_END

        if action == HOLD:
            return HELD, EPISODE_NOT_END

    def trade(self, action, company_symbol= None, amount = 0.00):
        reward, done = self._trade(action, company_symbol, amount)
        self.state_gen.next_state()
        return reward, done