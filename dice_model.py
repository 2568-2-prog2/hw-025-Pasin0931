import random

FACES = [1, 2, 3, 4, 5, 6]


class RollResult:
    def __init__(self, results: list, num_rolls: int):
        self.results = results
        self.num_rolls = num_rolls
        self.counts = {face: results.count(face) for face in FACES}
        self.frequencies = {
            face: round(self.counts[face] / num_rolls, 4) for face in FACES
        }

    def to_dict(self):
        return {
            "results": self.results,
            "num_rolls": self.num_rolls,
            "counts": self.counts,
            "frequencies": self.frequencies,
        }

class Dice:
    def __init__(self, probabilities=None, num_rolls=1):
        if probabilities is None:
            probabilities = [1 / 6] * 6
        self._validate_probabilities(probabilities)
        self._validate_num_rolls(num_rolls)
        self.probabilities = probabilities
        self.num_rolls = num_rolls

    @staticmethod
    def _validate_probabilities(probs):
        if not isinstance(probs, list):
            raise TypeError("probabilities must be a list")
        if len(probs) != 6:
            raise ValueError("probabilities must have exactly 6 elements")
        if any(p < 0 for p in probs):
            raise ValueError("all probabilities must be non-negative")
        if not abs(sum(probs) - 1.0) < 1e-6:
            raise ValueError("probabilities must sum to 1")

    @staticmethod
    def _validate_num_rolls(n):
        if n <= 0:
            raise ValueError("num_rolls must be a positive integer")

    def set_probabilities(self, probabilities):
        self._validate_probabilities(probabilities)
        self.probabilities = probabilities

    def set_num_rolls(self, num_rolls):
        self._validate_num_rolls(num_rolls)
        self.num_rolls = num_rolls

    def roll(self, num_rolls=None):
        if num_rolls is None:
            num_rolls = self.num_rolls
        self._validate_num_rolls(num_rolls)
        results = random.choices(FACES, weights=self.probabilities, k=num_rolls)
        return RollResult(results, num_rolls)