# NOTE Current implementation is only a "fake" traidng emvironment with
# no real connection to the outside world. Develop an API that lets the bot
# interface with the real API as well.

from data_factory import DataFactory
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple
from collections import defaultdict

# Reward Values for different possible actions
INVALID_BUY = 0
INVALID_SELL = 0

VALID_BUY = 0.05

PROFIT_SELL = 1
LOSS_SELL = -1
HOLD = 0

class Actions(Enum):
    BUY = 1
    SELL = 2
    HOLD = 3

class Portfolio:
    # Makes an empty list which will hold a (Company, Stock_value) list
    def __init__(self, amount, securities = defaultdict(lambda: 0)):
        self.amount = amount
        self.bought_securities = securities

    def perform_buy(self, symbol, amount, conversion):
        self.bought_securities[symbol] += amount * conversion
        self.amount -= amount

    def perform_sell(self, symbol, amount, conversion):
        self.bought_securities[symbol] -= amount * conversion
        self.amount += amount

    def __getattr__(self, key):
        return self.bought_securities[key]

class TradingEnv:
    def __init__(self, portfolio):
        self.portfolio = portfolio

    def get_conversion(self):
        '''
        Returns the converstion rate from USD to the price per Stock / Coin
        '''
        raise NotImplementedError("Not implemented conversion")

    def trade(self, company_symbol, action, amount):
        if action == Actions.BUY:
            if self.portfolio.amount == 0:
                return INVALID_BUY

            if amount > self.portfolio.amount:
                amount = self.portfolio.amount

            self.portfolio.perform_buy(company_symbol, amount, self.get_conversion())
            return VALID_BUY

        if action == Actions.SELL:
            if self.portfolio[company_symbol] == 0:
                return INVALID_SELL

            if amount > self.portfolio[company_symbol] / self.get_conversion():
                # If I am trying to sell more than I have (but I still have some)
                amount = self.portfolio[company_symbol] / self.get_conversion()

            self.portfolio.perform_sell(company_symbol, amount, self.get_conversion())

            # TODO Figure out how you want to check if the sale put you in a net profit or loss
            # For now I am just assuming it is profit to see a DQN Bot which can learn to sell valid stock
            # so that I can check my DQN is working
            return PROFIT_SELL

        if aciton == Actions.HOLD:
            return HOLD
