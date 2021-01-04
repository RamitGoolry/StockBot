import tensorflow as tf
from tensorflow import keras

from collections import deque
import numpy as np
import random

from keras.callbacks import TensorBoard
from tensorflow.python.ops.gen_math_ops import log1p
from debugger import log

INPUT_SHAPE = (3, ) # works, but that is not what I am expecting
OUTPUT_SHAPE = 3

MIN_REPLAY_BUFFER_SIZE = 1000
MINIBATCH_SIZE = 64
UPDATE_TARGET_EVERY = 5

REPLAY_BUFFER_SIZE = 50000

DISCOUNT = 0.95

STATE_IDX = 0
ACTION_IDX = 1
REWARD_IDX = 2
NEXT_STATE_IDX = 3 

# TensorBoard modifified to work for a Deep Q Network instead of Regular Neural Network
class RLTensorBoard(TensorBoard):
    def __init__(self, **kwargs):
        # Overriding init to set initial step and writer (we want one log file for all .fit() calls)
        super().__init__(**kwargs)
        self.step = 1
        self.writer = tf.summary.FileWriter(self.log_dir)

    def set_model(self, model):
        # Overriding this method to stop creating default log writer
        pass

    def on_epoch_end(self, epoch, logs=None):
        # Overrided, saves logs with our step number
        # (otherwise every .fit() will start writing from 0th step)
        self.update_stats(**logs)

    def on_batch_end(self, batch, logs=None):
        # Overrided
        # We train for one batch only, no need to save anything at epoch end
        pass

    def on_train_end(self, _):
        # Overrided, so won't close writer
        pass

    def update_stats(self, **stats):
        # Custom method for saving own metrics
        # Creates writer, writes custom metrics and closes writer
        self._write_logs(stats, self.step)

# TODO Q Learning policy that takes in the state from the trading environment and returns an action
# State Modelling (Recurrent Neural Networks) to using hidden history for state (LSTM to begin)

class DQNAgent:
    def __init__(self):
        self.loss_fn = keras.losses.mean_squared_error
        self.optimizer = keras.optimizers.Adam(learning_rate=1e-3)

        # Main Model - Gets trained every step
        self.model = self._create_model()

        # Target Model - This is what we .predict against every step
        # Used to stabilize main model
        self.target_model = self._create_model()
        self.target_model.set_weights(self.model.get_weights())

        self.replay_buffer = deque(maxlen=REPLAY_BUFFER_SIZE)

        # self.tensorboard = RLTensorBoard() # log_dir = f'logs/{MODEL_NAME}-{int(time.time())}'

        self.target_update_counter = 0

    def _create_model(self) -> keras.Sequential:
        model = keras.Sequential([ # TODO Make better model (Transformers)
            keras.layers.Dense(32, activation = 'relu', input_shape=INPUT_SHAPE),
            keras.layers.Dense(32, activation = 'relu'),
            keras.layers.Dense(OUTPUT_SHAPE)  # Buy, Sell and Hold
        ])

        model.summary(print_fn=log)

        model.compile(loss=self.loss_fn, optimizer=self.optimizer, metrics=['accuracy'])
        return model

    def epsilon_greedy_policy(self, state, epsilon = 0):

        if np.random.rand() < epsilon:
            log(f'\n[*] Exploring')
            return np.random.randint(OUTPUT_SHAPE) # TODO Change when dealing with multiple stocks.
        else:
            log(f'\n[*] Exploiting {state}')
            Q_values = self.model.predict(state.reshape(1, INPUT_SHAPE[0]))
            log(f'[*] {Q_values.shape}')
            return np.argmax(Q_values)

    def update_replay_buffer(self, transition):
        self.replay_buffer.append(transition)

    def sample_experiences(self):
        indices = np.random.randint(len(self.replay_buffer), size = MINIBATCH_SIZE)
        minibatch = [self.replay_buffer[index] for index in indices]

        states, actions, rewards, next_states, dones = [
            np.array([experience[field_index] for experience in minibatch])
            for field_index in range(5)
        ]

        return states, actions, rewards, next_states, dones

    def update_replay_memory(self, transition):
        self.replay_buffer.append(transition)

    def train(self, terminal_state : bool):
        # Start training only if minimum number of certain number of samples are ready
        if len(self.replay_buffer) < MIN_REPLAY_BUFFER_SIZE:
            return  
        
        # Get a minibatch of random samples frommemory replay table
        minibatch = random.sample(self.replay_buffer, MINIBATCH_SIZE)

        # Get current state from minibatch, then use NN to predict next states
        current_states = np.array([transition[STATE_IDX] for transition in minibatch])
        current_Q_values_l = self.model.predict(current_states)


        new_current_states = np.array([transition[NEXT_STATE_IDX] for transition in minibatch])
        future_Q_values_l = self.target_model.predict(new_current_states)

        # Features and Labels to train on
        X, y = [], []

        for idx, (state, action, reward, next_state, done) in enumerate(minibatch):

            # If not a teminal state, get new q from future states, otherwise set it to 0
            # Bellman Optimality for Q Values
            if not done:
                max_future_q = np.max(future_Q_values_l[idx])
                new_Q = reward + DISCOUNT * max_future_q
            else:
                new_Q = reward

            current_Q_values = current_Q_values_l[idx]
            current_Q_values[action] = new_Q

            X.append(state)
            y.append(current_Q_values)
        
            X = np.array(X)
            y = np.array(y)

        self.model.fit(X, y, batch_size=MINIBATCH_SIZE, shuffe = False) # TODO Tensorboard
        # , callbacks = [self.tensorboard] if terminal_state else None)

        # Update target network counter every episode to determine when to update target_model
        if terminal_state:
            self.target_update_counter += 1
        
        # If counter reaches set value, update target network with weights of main network
        if self.target_update_counter > UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0 # Resetting counter