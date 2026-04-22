import random

class Dice:
    def __init__(self, prob, time_roll):
        self.weight = prob
        self.time_roll = time_roll

        self.elements = ['1', '2', '3', '4', '5', '6']

    def roll(self):
        tmp = {}
        ch_ = random.choices(self.elements, weights=self.weight, k=self.time_roll)
        for i in range(1, self.time_roll+1):
            tmp[f'{i}'] =ch_[i-1]
        return tmp