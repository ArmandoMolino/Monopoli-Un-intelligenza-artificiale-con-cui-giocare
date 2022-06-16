import numpy as np


class Square(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def membership_value(self, input_value):
        membership_value = 0
        if (input_value >= self.left) and (input_value < self.right):
            membership_value = 1
        return membership_value


class Estate(object):

    def __init__(self, input_set):
        if isinstance(input_set, list):
            input_set = set(input_set)

        self.set = input_set
        self.lenght = len(input_set)

    def membership_value(self, input_value):
        if isinstance(input_value, list):
            input_value = set(input_value)
        if not self.set:
            return 1

        membership_value = 0
        input_value = input_value.intersection(self.set)
        if self.set == input_value:
            membership_value = 1

        return membership_value


class Houses(object):

    def __init__(self, left, right):
        self.crisp = Square(left, right)

    def membership_value(self, input_value):
        if isinstance(input_value, list):
            input_value = list(input_value)
        if len(input_value) == 0:
            return 0

        membership_value = 0
        for index, value in enumerate(input_value):
            membership_value += self.crisp.membership_value(value)
        membership_value = membership_value / len(input_value)
        if membership_value == 1:
            return 1
        return 0

