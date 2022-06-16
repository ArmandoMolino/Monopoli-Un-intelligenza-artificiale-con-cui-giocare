import numpy as np

from ReinforcementLearning.Sets.Fuzzy import FIS
from ReinforcementLearning.QLearning import Policy, FQL
import random


class Model(FQL.Model):

    def __init__(self, gamma, alpha, ee_rate, action_set_length, q_initial_value='zeros',
                 fis=FIS.Build(), policy=Policy.epsilon_greedy):

        self.gamma = gamma
        self.alpha = alpha
        self.ee_rate = ee_rate
        self.q_initial_value = q_initial_value
        self.action_set_length = action_set_length
        self.fis = fis
        self.q_tables = [np.matrix([]),  np.matrix([])]

        self.policy = policy
        self.choose_table = 0

        if self.q_initial_value == 'random':
            # contiene le due q-table Q1 e Q2
            self.q_tables = [np.random.random((self.fis.get_number_of_rules(), self.action_set_length)), np.random.random((self.fis.get_number_of_rules(), self.action_set_length))]
        if self.q_initial_value == 'zeros':
            # contiene le due q-table Q1 e Q2
            self.q_tables = [np.zeros((self.fis.get_number_of_rules(), self.action_set_length)),  np.zeros((self.fis.get_number_of_rules(), self.action_set_length))]

    def __str__(self):
        return f'FDQL(gamma={self.gamma},alpha={self.alpha},ee_rate={self.ee_rate})'

    def __repr__(self):
        return f'FDQL(gamma={self.gamma},alpha={self.alpha},ee_rate={self.ee_rate})'

    def ActionSelection(self):
        # utilizza EE policy con l'epsilon-greedy method come primo livello di next_action selection
        self.M = []     # Lista di azioni da effettuare per ogni stato (Stato i = Azione M[i])
        self.policy(self.ee_rate, self.M, self.q_tables[self.choose_table])

    def CalculateQValue(self):
        self.Q = 0
        for index, truth_value in enumerate(self.R):
            self.Q = self.Q + truth_value * self.q_tables[self.choose_table][index, self.M[index]]
        if sum(self.R) == 0:
            self.R[0] = 0.00001
        self.Q = self.Q / sum(self.R)

    def CalculateStateValue(self):
        self.V = 0
        for index, rull in enumerate(self.q_tables[self.choose_table]):
            max_action = np.argmax(rull)
            max_action_value = self.q_tables[(self.choose_table + 1) % 2][index][max_action]
            self.V = (self.R[index] * max_action_value) + self.V
        if sum(self.R) == 0:
            self.R[0] = 0.00001
        self.V = self.V / sum(self.R)

    def UpdateqValue(self):
        for index, truth_value in enumerate(self.R_):
            delta_Q = self.alpha * (self.Error * truth_value)
            self.q_tables[self.choose_table][index][self.M[index]] = self.q_tables[self.choose_table][index][self.M[index]] + delta_Q

    def get_initial_action(self, state):
        self.choose_table = random.randint(0, 1)
        self.CalculateTruthValue(state)
        self.ActionSelection()
        action = self.InferredAction()
        self.CalculateQValue()
        self.KeepStateHistory()
        return action

    def run(self, state, reward):
        self.choose_table = random.randint(0, 1)
        self.CalculateTruthValue(state)
        self.CalculateStateValue()
        self.CalculateQualityVariation(reward)
        self.UpdateqValue()
        self.ActionSelection()
        action = self.InferredAction()
        self.CalculateQValue()
        self.KeepStateHistory()
        return action

    def Policy(self, state):
        self.CalculateTruthValue(state)
        self.M = []
        self.policy(self.ee_rate, self.M, (self.q_tables[0] + self.q_tables[1]) / 2)
        return self.InferredAction()


    def save(self, dir=''):
        with open(f'{dir}q_table1{self}.npy', 'wb') as f:
            np.save(f, self.q_tables[0])
        with open(f'{dir}q_table2{self}.npy', 'wb') as f:
            np.save(f, self.q_tables[1])

    def load(self, dir=''):
        with open(f'{dir}q_table1{self}.npy', 'rb') as f:
            self.q_tables[0] = np.load(f)
        with open(f'{dir}q_table2{self}.npy', 'rb') as f:
            self.q_tables[1] = np.load(f)
