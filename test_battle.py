
import battle
import unittest

class BattleTestCase(unittest.TestCase):

    def test_battle(self):
        pet1 = ["foo", 0.25, 0.0, 0.50, 0.25]
        pet2 = ["foo", 0.25, 0.40, 0.10, 0.25]

        result = battle.do_battle([pet1, pet2], "strength")

        print result


if __name__ == '__main__':
    unittest.main()
