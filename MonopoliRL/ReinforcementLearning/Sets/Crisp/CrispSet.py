import numpy as np

class Alfa_Cut(object):
    def __init__(self, fuzzy_set, alfa, strong=False):
        self.fuzzy_set = fuzzy_set.membership_value
        self.alfa = alfa
        self.strong = strong

    def membership_value(self, input_value):
        membership_value = self.fuzzy_set(input_value)
        if self.strong:
            if membership_value > self.alfa:
                return 1
        else:
            if membership_value >= self.alfa:
                return 1
        return 0

class Support(object):
    def __init__(self, fuzzy_set):
        self.fuzzy_set = fuzzy_set.membership_value

    def membership_value(self, input_value):
        membership_value = self.fuzzy_set(input_value)
        if membership_value > 0:
                return 1
        return 0

class Core(object):
    def __init__(self, fuzzy_set):
        self.fuzzy_set = fuzzy_set.membership_value

    def membership_value(self, input_value):
        membership_value = self.fuzzy_set(input_value)
        if membership_value == 1:
                return 1
        return 0
