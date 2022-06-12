import numpy as np

from FuzzyQLearning.Fuzzy import FIS
from FuzzyQLearning.QLearning import Policy
import operator
import itertools
import functools
import copy


class Model(object):
    L = []
    R = []
    R_= []
    M = []
    Q = 0
    V = 0
    Error = 0
    q_table = np.matrix([])

    def __init__(self, gamma, alpha, ee_rate, action_set_length, q_initial_value='zeros',
                 fis=FIS.Build(), policy=Policy.epsilon_greedy):

        self.gamma = gamma
        self.alpha = alpha
        self.ee_rate = ee_rate
        self.q_initial_value = q_initial_value
        self.action_set_length = action_set_length
        self.fis = fis

        self.policy = policy

        if self.q_initial_value == 'random':
            self.q_table = np.random.random((self.fis.get_number_of_rules(), self.action_set_length))
        if self.q_initial_value == 'zeros':
            self.q_table = np.zeros((self.fis.get_number_of_rules(), self.action_set_length))

    def __str__(self):
        return f'FQL(gamma={self.gamma},alpha={self.alpha},ee_rate={self.ee_rate})'

    def __repr__(self):
        return f'FQL(gamma={self.gamma},alpha={self.alpha},ee_rate={self.ee_rate})'

    def CalculateTruthValue(self, state_value):
        self.R = []
        self.L = []
        input_variables = self.fis.list_of_input_variable
        for index, variable in enumerate(input_variables):
            # Calcola il grado di appartenenza dello stato(state_value[index]) nel corrispettivo fuzzy set
            X = []
            fuzzy_sets = variable.get_fuzzy_sets()
            for set in fuzzy_sets:
                membership_value = set.membership_value(state_value[index])
                X.append(membership_value)
            self.L.append(X)
        # Calcola il degree of truth effettuando la produttoria di L
        for element in itertools.product(*self.L):
            self.R.append(functools.reduce(operator.mul, element, 1))

    def ActionSelection(self):
        # utilizza EE policy con l'epsilon-greedy method come primo livello di next_action selection
        self.M = []     # Lista di azioni da effettuare per ogni stato (Stato i = Azione M[i])
        self.policy(self.ee_rate, self.M, self.q_table)

    def InferredAction(self):
        # Secondo livello di next_action selection
        action = self.M[np.argmax(self.R)]
        return action

    def CalculateQValue(self):
        self.Q = 0
        for index, truth_value in enumerate(self.R):
            self.Q = self.Q + truth_value * self.q_table[index, self.M[index]]
        if sum(self.R) == 0:
            self.R[0] = 0.00001
        self.Q = self.Q / sum(self.R)

    def CalculateStateValue(self):
        self.V = 0
        for index, rull in enumerate(self.q_table):
            max_action = max(rull)
            self.V = (self.R[index] * max_action) + self.V
        if sum(self.R) == 0:
            self.R[0] = 0.00001
        self.V = self.V / sum(self.R)

    def CalculateQualityVariation(self, reward):
        self.Error = reward + ((self.gamma * self.V) - self.Q)

    def UpdateqValue(self):
        for index, truth_value in enumerate(self.R_):
            delta_Q = self.alpha * (self.Error * truth_value)
            self.q_table[index][self.M[index]] = self.q_table[index][self.M[index]] + delta_Q

    def KeepStateHistory(self):
        self.R_ = copy.copy(self.R)

    def get_initial_action(self, state):
        self.CalculateTruthValue(state)
        self.ActionSelection()
        action = self.InferredAction()
        self.CalculateQValue()
        self.KeepStateHistory()
        return action

    def run(self, state, reward):
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
        self.ActionSelection()
        return self.InferredAction()


    def save(self, dir=''):
        with open(f'{dir}q_table{self}.npy', 'wb') as f:
            np.save(f, self.q_table)

    def load(self, dir=''):
        with open(f'{dir}q_table{self}.npy', 'rb') as f:
            self.q_table = np.load(f)
