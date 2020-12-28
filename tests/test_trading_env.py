import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Imports modules form parent directory

from trading_env import Portfolio, TradingEnv, Actions

def test_portfolio_init():
    p = Portfolio(1000)
    assert p.amount == 1000

def test_trading_env_init():
    te = TradingEnv(Portfolio(1000))

def test_trading_env_buy_normal():
    te = TradingEnv(Portfolio(1000))
    prev_amount = te.portfolio.amount

    te.trade('GOOG', Actions.BUY, 100)

    assert te.portfolio.amount - prev_amount == 100

def test_trading_env_buy_under():
    te = TradingEnv(Portfolio(100))
    te.trade('GOOG', Actions.BUY, 105)

    assert te.portfolio.amount == 0
