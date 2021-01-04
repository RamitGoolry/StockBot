import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Imports modules form parent directory

from numpy import isclose

from trading_env import Portfolio, TradingEnv, Actions
from trading_env import INVALID_BUY, VALID_BUY, INVALID_SELL, PROFIT, LOSS, HOLD

TEST_DATA_SOURCE = 'data/BTCUSDT_MinuteBars_test.csv'

def test_portfolio_init():
    p = Portfolio(1000)
    assert p.balance == 1000

def test_trading_env_init():
    te = TradingEnv(Portfolio(1000), TEST_DATA_SOURCE)

def test_trading_env_buy_normal():
    te = TradingEnv(Portfolio(1000), TEST_DATA_SOURCE)
    prev_amount = te.portfolio.balance

    reward = te.trade(Actions.BUY, 'BTC', 100)

    assert reward[0] == VALID_BUY
    assert prev_amount - te.portfolio.balance == 100
    assert te.portfolio.balance == 900

def test_trading_env_buy_under():
    te = TradingEnv(Portfolio(100), TEST_DATA_SOURCE)
    reward = te.trade(Actions.BUY, 'BTC', 105)

    assert reward[0] == VALID_BUY
    assert te.portfolio.balance == 0

def test_trading_env_buy_zero():
    te = TradingEnv(Portfolio(0), TEST_DATA_SOURCE)
    reward = te.trade(Actions.BUY, 'BTC', 105)

    assert reward[0] == INVALID_BUY
    assert te.portfolio.balance == 0

def test_trading_env_buy_securities():
    te = TradingEnv(Portfolio(100000), TEST_DATA_SOURCE)
    ONE_BITCOIN_PRICE = te.get_conversion()
    te.trade(Actions.BUY, 'BTC', ONE_BITCOIN_PRICE)

    assert te.portfolio['BTC'] == 1, 'Incorrect Securities Balance'

    ONE_BITCOIN_PRICE = te.get_conversion()
    te.trade(Actions.BUY, 'BTC', ONE_BITCOIN_PRICE)

    assert te.portfolio['BTC'] == 2, 'Incorrect Securities Balance'

    ONE_BITCOIN_PRICE = te.get_conversion()
    te.trade(Actions.BUY, 'BTC', ONE_BITCOIN_PRICE)

    assert te.portfolio['BTC'] == 3, 'Incorrect Securities Balance'

def test_trading_env_sell_securities():
    te = TradingEnv(Portfolio(100000), TEST_DATA_SOURCE)
    ONE_BITCOIN_PRICE = te.get_conversion()
    te.trade(Actions.BUY, 'BTC', ONE_BITCOIN_PRICE)

    ONE_BITCOIN_PRICE = te.get_conversion()
    te.trade(Actions.SELL, 'BTC', 1)

    assert te.portfolio['BTC'] == 0, 'Incorrect Securities Balance'

def test_trading_env_hold():
    te = TradingEnv(Portfolio(100), TEST_DATA_SOURCE)
    reward = te.trade(Actions.HOLD)

    assert reward[0] == HOLD
    assert te.portfolio.balance == 100

def test_trading_env_sell_normal():
    te = TradingEnv(Portfolio(5000), TEST_DATA_SOURCE)
    ONE_BITCOIN_PRICE = te.get_conversion()

    # Buying 1 coin to set up sale
    te.trade(Actions.BUY, 'BTC', ONE_BITCOIN_PRICE)
    te.trade(Actions.SELL, 'BTC', 1)

    assert isclose(te.portfolio.balance, 5000), 'Incorrect balance after selling'

def test_trading_env_sell_under():
    te = TradingEnv(Portfolio(5000), TEST_DATA_SOURCE)
    ONE_BITCOIN_PRICE = te.get_conversion()

    # Buying some 1 coin to set up sale
    te.trade(Actions.BUY, 'BTC', ONE_BITCOIN_PRICE)

    te.trade(Actions.SELL, 'BTC', 2)

    assert isclose(te.portfolio.balance, 5000), 'Incorrect balance after selling'