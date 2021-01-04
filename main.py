import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import numpy as np
import tensorflow as tf
from trading_env import TradingEnv, Portfolio, BUY, SELL, HOLD
from q_learning import DQNAgent
from tqdm import tqdm

from time import sleep
from debugger import log, DEBUG

def preprocess(df):
    df2 = df.set_index('timestamp')
    df2 = df2.drop('ignore', axis = 1)
    return df2

STARTING_AMT = 1000
FILEPATH = 'data/BTCUSDT_MinuteBars.csv'

EPISODES = 200
RISK = 0.15 # TODO Tune

epsilon = 0.1

def main():
    env = TradingEnv(Portfolio(STARTING_AMT), FILEPATH, preprocess)
    agent = DQNAgent() 

    with tqdm(range(1, EPISODES + 1), unit=' Episode') as episodes:
        for episode in episodes:
            # agent.tensorboard.step = episode

            episode_reward = 0

            # TODO reset environment -> Set to a random timestep, from which agent has to train

            done = False
            while not done:
                state = env.get_state()
                state = state.reshape(-1)

                action = agent.epsilon_greedy_policy(state, epsilon)

                if action == BUY:
                    balance = env.portfolio.balance
                    reward, done = env.trade(action, 'BTC', balance * RISK)
                elif action == SELL:
                    balance = env.portfolio['BTC']
                    reward, done = env.trade(action, 'BTC', balance * RISK)
                else: # HOLD
                    reward, done = env.trade(action)

                new_state = env.get_state()

                episode_reward += reward

                agent.update_replay_memory((state, action, reward, new_state, done))
                agent.train(done)
            
            episodes.set_postfix({'Episode Reward' : episode_reward, 'Net Worth' : env.get_net_worth()})

if __name__ == '__main__':
    main()