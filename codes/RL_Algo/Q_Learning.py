from codes.InformationProvider.Single_agent_information import Infromation
from .Single_agent_reward import SingleAgentReward
from .RLAlgorithm import RLAlgorithm
from matplotlib import animation
import matplotlib.pyplot as plt
from tqdm import tqdm
import seaborn as sns
import numpy as np
import random
import time
import os

class Qlearning:

    def __init__(self,id,lr=0.1,gamma=0.9, epsilon=0.1, decay=0.01, min_epsilon=0):
        """
        This function initializes the Q-learning algorithm with default and user-defined parameters,
        creates a Q-table, and defines the state transition table for a 2-action, 4-state environment.
        
        :param lr: learning rate, which determines how much the Q-values are updated at each iteration
        :param gamma: discount factor for future rewards
        :param epsilon: The probability of choosing a random action instead of the action with the
        highest Q-value during the exploration phase of the Q-learning algorithm. It is used to balance
        exploration and exploitation
        :param decay: The decay parameter is used to decrease the value of epsilon over time. It
        determines the rate at which the epsilon value decreases during training. A higher decay value
        means that the epsilon value will decrease faster, leading to a more exploitation-focused policy
        :param min_epsilon: The minimum value that the epsilon parameter can reach during the decay
        process, defaults to 0 (optional)
        """
        self.lr, self.gamma, self.epsilon, self.decay, self.min_epsilon =  lr, gamma, epsilon, decay, min_epsilon
        self.id=id
        self.q_table = np.zeros((4, 2)) # 4 is the number of state, 2 is the number of action
        self.reward_calculater = SingleAgentReward(self.id)
        self.rewards = []
        self.q_table_snapshots = []
        self.algorithm_name = "Q-learning"
        self.fig = plt.figure()
        self.state_space = [0,1,2,3]
        self.State_transition_table={
            0:{0:[1, 2, 3],1:[1, 3]},
            1:{0:[0, 2, 3],1:[0, 2]},
            2:{0:[0, 1, 3],1:[1, 3]},
            3:{0:[0, 1, 2],1:[0, 2]},}

    
    def get_next_state(self,state,action):
        """
        This function returns the index of the next state with the minimum number of available places in
        a lane, given the current state and action.
        
        :param state: The current state of the system
        :param action: The action to be taken in the current state
        :return: the index of the next state with the minimum number of places available in the lane,
        given the current state and action.
        """
        temp =  self.State_transition_table.get(state, "nothing")
        if temp == "nothing":
            return [0,1,2,3]
        next_states = temp.get(action,[0,1,2,3]) # type: ignore
        number_of_places_available = list(map(lambda s: self.reward_calculater.infromation.get_number_of_places_available_in_lane(self.reward_calculater.infromation.dic_number2lane[s]), next_states))
        return next_states.index(min(number_of_places_available)) # type: ignore
    
    def apply_action(self,state,action):
        """
        This function takes in a state and an action, gets the next state, calculates the reward, and
        returns the reward and next state.
        
        :param state: The current state of the environment. It could be any data structure that
        represents the current state of the environment
        :param action: The action parameter represents the action taken by an agent in a particular
        state. It is used to determine the next state and the reward obtained by the agent after taking
        that action
        :return: a tuple containing the reward calculated by the reward_calculater and the next state
        obtained by applying the given action to the current state.
        """
        return self.reward_calculater.reward(), self.get_next_state(state,action)
    
    def policy(self,state):
        """
        This function implements an epsilon-greedy policy for selecting actions based on a Q-table.
        
        :param state: The current state of the environment, represented as a numerical value or array.
        The policy function uses this state to determine the action to take
        :return: The function `policy` returns an action based on the epsilon-greedy policy. If a random
        number generated is less than the exploration rate (epsilon), a random action is returned.
        Otherwise, the action with the highest Q-value for the given state is returned.
        """
        result = np.random.uniform() # type: ignore
        if result < self.epsilon:return np.random.randint(0, 2) # type: ignore
        else:return np.argmax(self.q_table[state])

    def fit(self,state):
        """
        The "fit" function updates the Q-table based on the current state, selected action, and
        resulting reward and next state, while also updating the exploration rate and storing snapshots
        of the Q-table and rewards.
        
        :param state: The current state of the environment, represented as a tuple or list of values
        :return: the updated state after applying the action and updating the Q-table, rewards list, and
        epsilon value.
        """
        action = self.policy(state)
        reward, next_state = self.apply_action(state, action)
        self.q_table[state][action] = reward + self.gamma*max(self.q_table[next_state])
        state = next_state
        self.q_table_snapshots.append(self.q_table.copy())
        self.epsilon = max(self.epsilon * self.decay, self.min_epsilon)
        self.rewards.append(reward)
        return state
    
    def print_q_table(self):
        """
        This function prints the Q-learning table.
        """
        print("------------------- Q LEARNING TABLE ------------------\n",
              self.q_table, "\n-------------------------------------------------------")
        
    def init(self):
        """
        This function initializes a heatmap with a 10x10 matrix of zeros using the Seaborn library in
        Python.
        """
        sns.heatmap(np.zeros((10, 10)), vmax=.8, square=True, cbar=False)

    def gen(self):
        """
        The function "gen" generates a sequence of snapshots from a Q-table.
        """
        for snap_shot in self.q_table_snapshots:
            yield snap_shot

    def animate(self, i):
        """
        This function creates an animated heatmap using the input data.
        
        :param i: The parameter "i" is a variable that represents the data that will be visualized in
        the heatmap. It is usually a 2-dimensional array or a pandas DataFrame. The "animate" function
        is likely part of an animation loop that iterates through a sequence of data frames to create an
        animated heatmap
        """
        sns.heatmap(i, square=True, cbar=False, annot=False)

    def animate_q_table_changes(self):
        """
        This function creates an animation of changes in a Q-table.
        """
        self.anim = animation.FuncAnimation(
            self.fig, self.animate, self.gen, init_func=self.init)