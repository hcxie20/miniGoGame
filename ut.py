import numpy as np
import unittest
import unittest.mock as mock

from my_player3 import Board, BasePlayer

testboards = [
    [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ],
    [
        [0, 0, 2, 1, 0],
        [1, 2, 1, 2, 1],
        [0, 1, 1, 2, 1],
        [1, 2, 2, 0, 0],
        [0, 1, 1, 0, 0]
    ],
    [
        [0, 0, 2, 0, 2],
        [1, 2, 1, 2, 1],
        [0, 1, 1, 2, 1],
        [1, 2, 2, 0, 0],
        [0, 1, 1, 0, 0]
    ],
]

class testBoard(unittest.TestCase):

    def testEvaLocation(self):
        test_player = BasePlayer()
        ls = [[test_player._location_score(i, j) for j in range(5)] for i in range(5)]

        # [
        #     [1.0, 1.5, 1.0, 1.5, 1.0]
        #     [1.5, 2.0, 1.5, 2.0, 1.5]
        #     [1.0, 1.5, 1.0, 1.5, 1.0]
        #     [1.5, 2.0, 1.5, 2.0, 1.5]
        #     [1.0, 1.5, 1.0, 1.5, 1.0]
        # ]

        # print('\n')
        # for row in ls:
        #     print(row)

    def testEvalScore(self):
        test_board = Board()
        self.assertEqual(test_board.evaluate_score(), [0, 0])
        test_board.board = np.array(testboards[1])
        self.assertEqual(test_board.evaluate_score(), [10, 6])

    def testEvaLiberty(self):
        test_board = Board()
        self.assertEqual(test_board.evaluate_liberty(), [0, 0])
        test_board.board = np.array(testboards[1])
        self.assertEqual(test_board.evaluate_liberty(), [10, 4])

    def testCheckValid(self):
        test_board = Board()
        test_board.board = np.array(testboards[0])
        test_board.prev_board = np.array(testboards[0])

        for i in range(test_board.size):
            for j in range(test_board.size):
                self.assertTrue(test_board.is_valid_place(i, j, 1))

    def testCheckValidNoTaken(self):
        test_board = Board()
        test_board.prev_board = np.array(testboards[0])
        test_board.board = np.array(testboards[1])

        self.assertFalse(test_board.is_valid_place(4, 0, 2))

    def testCheckValidTaken(self):
        test_board = Board()
        test_board.prev_board = np.array(testboards[0])
        test_board.board = np.array(testboards[1])

        self.assertTrue(test_board.is_valid_place(2, 0, 1))
        self.assertTrue(test_board.is_valid_place(2, 0, 2))

    def testCheckValidTakenKORule(self):
        test_board = Board()
        test_board.prev_board = np.array(testboards[2])
        test_board.board = np.array(testboards[1])

        self.assertFalse(test_board.is_valid_place(0, 4, 2))

        self.assertFalse(test_board.is_valid_place(1, 0, 1))

    def testCheckLiberty(self):
        test_board = Board()
        test_board.prev_board = np.array(testboards[2])
        test_board.board = np.array(testboards[1])

        self.assertEqual(test_board.check_liberty(1, 1), 1)
        self.assertEqual(test_board.check_liberty(1, 2), 1)
        self.assertEqual(test_board.check_liberty(1, 3), 1)
        self.assertEqual(test_board.check_liberty(1, 4), 2)

    def testCheckBlockLiberty(self):
        test_board = Board()
        test_board.prev_board = np.array(testboards[2])
        test_board.board = np.array(testboards[1])

        self.assertEqual(test_board.check_block_liberty(test_board.find_ally(1, 1)), 1)
        self.assertEqual(test_board.check_block_liberty(test_board.find_ally(1, 2)), 1)
        self.assertEqual(test_board.check_block_liberty(test_board.find_ally(1, 3)), 1)
        self.assertEqual(test_board.check_block_liberty(test_board.find_ally(1, 4)), 2)


if __name__ == '__main__':
    unittest.main()
