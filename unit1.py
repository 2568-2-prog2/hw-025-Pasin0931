import unittest
import random
from dice import Dice

FACES = ['1', '2', '3', '4', '5', '6']


class TestDiceInit(unittest.TestCase):

    def test_custom_probabilities(self):
        probs = [0.1, 0.2, 0.3, 0.1, 0.2, 0.1]
        d = Dice(probs, 10)
        self.assertEqual(d.weight, probs)

    def test_custom_num_rolls(self):
        d = Dice([1/6]*6, 50)
        self.assertEqual(d.time_roll, 50)

    def test_elements_are_strings(self):
        d = Dice([1/6]*6, 10)
        self.assertEqual(d.elements, ['1', '2', '3', '4', '5', '6'])


class TestDiceRoll(unittest.TestCase):

    def setUp(self):
        self.fair = Dice([1/6]*6, 100)
        self.biased = Dice([0.1, 0.2, 0.3, 0.1, 0.2, 0.1], 50)

    def test_roll_returns_dict(self):
        result = self.fair.roll()
        self.assertIsInstance(result, dict)

    def test_roll_correct_length(self):
        result = self.fair.roll()
        self.assertEqual(len(result), 100)

    def test_roll_keys_are_strings(self):
        result = self.fair.roll()
        for key in result.keys():
            self.assertIsInstance(key, str)

    def test_roll_keys_sequential(self):
        result = self.fair.roll()
        expected_keys = [str(i) for i in range(1, 101)]
        self.assertEqual(list(result.keys()), expected_keys)

    def test_roll_faces_in_valid_range(self):
        result = self.biased.roll()
        for face in result.values():
            self.assertIn(face, FACES)

    def test_single_roll_returns_one_result(self):
        d = Dice([1/6]*6, 1)
        result = d.roll()
        self.assertEqual(len(result), 1)
        self.assertIn(result['1'], FACES)


class TestDiceStatisticalBias(unittest.TestCase):

    def test_biased_face_is_most_common(self):
        probs = [0.1, 0.1, 0.5, 0.1, 0.1, 0.1]
        d = Dice(probs, 1000)
        result = d.roll()
        counts = {face: list(result.values()).count(face) for face in FACES}
        most_common = max(counts, key=counts.get)
        self.assertEqual(most_common, '3')

    def test_all_faces_appear_in_large_sample(self):
        d = Dice([1/6]*6, 600)
        result = d.roll()
        values = list(result.values())
        for face in FACES:
            self.assertGreater(values.count(face), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)