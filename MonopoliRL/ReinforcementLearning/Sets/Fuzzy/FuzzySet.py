import numpy as np


class Trapeziums(object):
    def __init__(self, left, left_top, right_top, right):
        self.left = left
        self.right = right
        self.left_top = left_top
        self.right_top = right_top

    def membership_value(self, input_value):
        if (input_value >= self.left_top) and (input_value <= self.right_top):
            membership_value = 1.0
        elif (input_value <= self.left) or (input_value >= self.right):
            membership_value = 0.0
        elif input_value < self.left_top:
            membership_value = (input_value - self.left) / (self.left_top - self.left)
        elif input_value > self.right_top:
            membership_value = (input_value - self.right) / (self.right_top - self.right)
        else:
            membership_value = 0.0
        return membership_value


class Triangles(object):

    def __init__(self, left, top, right):
        self.left = left
        self.right = right
        self.top = top

    def membership_value(self, input_value):
        if input_value == self.top:
            membership_value = 1.0
        elif input_value <= self.left or input_value >= self.right:
            membership_value = 0.0
        elif input_value < self.top:
            membership_value = (input_value - self.left) / (self.top - self.left)
        elif input_value > self.top:
            membership_value = (input_value - self.right) / (self.top - self.right)
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
            if not input_value:
                return 1.0
            else:
                return 0

        input_value = input_value.intersection(self.set)
        if self.set == input_value:
            membership_value = 1.0
        elif self.set.isdisjoint(input_value):
            membership_value = 0.0
        else:
            membership_value = len(input_value) / self.lenght

        return membership_value


class Houses(object):

    def __init__(self, input, type: str):
        if type in 'triangles':
            try:
                self.fuzzy = Triangles(input[0], input[1], input[2])
            except:
                print("Invalid input")
        elif type in 'trapeziums':
            try:
                self.fuzzy = Trapeziums(input[0], input[1], input[2], input[3])
            except:
                print("Invalid input")
        else:
            raise Exception("Invalid Fuzzy set")

    def membership_value(self, input_value):
        if isinstance(input_value, list):
            input_value = list(input_value)
        if len(input_value) == 0:
            return 0

        membership_value = 0
        for index, value in enumerate(input_value):
            membership_value += (index + 1) * self.fuzzy.membership_value(value)
        return membership_value / sum(np.arange(len(input_value) + 1))

