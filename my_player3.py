import random
import sys
import json
from read import readInput
from write import writeOutput
import numpy as np

from host import GO

N = 5

WIN_REWARD = 1
DRAW_REWARD = 0.5
LOSS_REWARD = 0

ALPHA = 0.7
GAMMA = 0.9


# def default(self, obj):
#     if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
#         np.int16, np.int32, np.int64, np.uint8,
#         np.uint16,np.uint32, np.uint64)):
#         return int(obj)
#     elif isinstance(obj, (np.float_, np.float16, np.float32,
#         np.float64)):
#         return float(obj)
#     elif isinstance(obj, (np.ndarray,)): # add this line
#         return obj.tolist() # add this line
#     return json.JSONEncoder.default(self, obj)

class BasePlayer(object):
    def __init__(self):
        self.type = 'base'

    def get_input(self, go, piece_type):
        raise NotImplementedError

    def train(self):
        pass

    def _load_training(self):
        raise NotImplementedError

    def _update_training(self):
        raise NotImplementedError

    def play_one_step(self):
        piece_type, previous_board, board = readInput(N)
        go = GO(N)
        go.set_board(piece_type, previous_board, board)
        action = self.get_input(go, piece_type)
        writeOutput(action)


class QLearningPlayer(BasePlayer):
    def __init__(self):
        self.type = 'qlearning'

        self.alpha = ALPHA
        self.gamma = GAMMA

        self.q_values = self._load_training()
        self.state_history = []

    def get_input(self, go, piece_type):
        encoded_board = self._encode_board(go.board, piece_type)

        current_q_values = self._get_current_q_value(encoded_board)

        i, j = self._select_best_move(go, current_q_values, piece_type)

        self.state_history.append([encoded_board, [i, j]])

        if i == float('-inf'):
            return "PASS"

        return i, j

    def _select_best_move(self, go, q_values, piece_type):
        count = 0
        while count < len(q_values) ** 2:
            i, j = self._select_best_q(q_values)

            if go.valid_place_check(i, j, piece_type, test_check=True):
                return (i, j) if q_values[i][j] >= 0 else (float('-inf'), float('-inf'))

            q_values[i][j] = -10
            count += 1

        return (float('-inf'), float('-inf'))

    def _select_best_q(self, q_values):
        row, col = 0, 0
        mx = float('-inf')

        for i in range(len(q_values)):
            for j in range(len(q_values)):
                if q_values[i][j] > mx:
                    mx = q_values[i][j]
                    row, col = i, j

        return row, col

    def train(self, result):
        '''
        '''
        if result.lower() == 'draw':
            reward = DRAW_REWARD
        elif result.lower() == 'win':
            reward = WIN_REWARD
        else:
            reward = LOSS_REWARD

        self.state_history.reverse()
        max_q_value = -1
        for unit in self.state_history:
            board, move = unit

            q = self._get_current_q_value(board)
            if move[0] != float('-inf'):
                if max_q_value < 0:
                    q[move[0]][move[1]] = reward
                else:
                    q[move[0]][move[1]] = q[move[0]][move[1]] * (1 - self.alpha) + self.alpha * self.gamma * max_q_value
            max_q_value = np.max(q)
        self.state_history = []
        # update training results
        self._update_training()

    def _encode_board(self, board, piece_type):
        # board_units = [str(board[i][j]) for i in range(len(board)) for j in range(len(board))]
        # print('wtf')
        return ''.join([str(board[i][j]) for i in range(len(board)) for j in range(len(board))])

    def _get_current_q_value(self, encoded_board):
        if encoded_board in self.q_values:
            return self.q_values[encoded_board]

        new_q_values = [[0 for _ in range(N)] for _ in range(N)]
        self.q_values[encoded_board] = new_q_values
        return new_q_values

    def _load_training(self):
        try:
            f = open('./qv.txt', 'r')
        except FileNotFoundError:
            f = open('./qv.txt', 'w')
            f.write(json.dumps({}))
            f.close()
            f = open('./qv.txt', 'r')

        content = f.read()
        f.close()
        return json.loads(content)

    def _update_training(self):
        with open('./qv.txt', 'w') as f:
            f.write(json.dumps(self.q_values))


class RandomPlayer():
    def __init__(self):
        self.type = 'random'

    def get_input(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check = True):
                    possible_placements.append((i,j))

        if not possible_placements:
            return "PASS"
        else:
            return random.choice(possible_placements)

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = QLearningPlayer()
    # player = RandomPlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)