import numpy as np
import random
from dataclasses import dataclass

@dataclass
class Qlearning():

    state_space_size: int
    action_space_size: int        
    
    epsilon: float = 0
    gamma: float = 0.95                            
    learning_rate: float = 0.7      
    max_epsilon:float = 1.0           
    min_epsilon:float = 0.05         
    decay_rate:float = 0.0005        


    def initialize_q_table(self):
        self.Qtable = np.zeros((self.state_space_size, self.action_space_size))
        
    def epsilon_greedy_policy(self, state, actions_size):
        random_int = random.uniform(0,1)
        if random_int > self.epsilon:
            action = np.argmax(self.Qtable[state])
        else:
            action = random.randint(0, actions_size-1)
        return action

    def greedy_policy(self, state):
        action = np.argmax(self.Qtable[state])
        return action
    
    def update_episolon(self, episode):
        self.epsilon = self.min_epsilon + (self.max_epsilon - self.min_epsilon)*np.exp(-self.decay_rate*episode)
        
    def update_qtable(self, state, action, new_state, reward):
        self.Qtable[state][action] = self.Qtable[state][action] + self.learning_rate * (reward + self.gamma * np.max(self.Qtable[new_state]) - self.Qtable[state][action])
    