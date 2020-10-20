import sys
import json
import random
from copy import deepcopy
from read import readInput
from write import writeOutput
import numpy as np

from host import GO

N = 5

WIN_REWARD = 1
DRAW_REWARD = 0.5
LOSS_REWARD = 0

ALPHA = 0.6
GAMMA = 0.8

SWITCH_PROP = 0.05

def main():
    pass

class Board(object):
    def __init__(self, size=5):
        self.size = size
        self.board = np.zeros((size, size))
        self.prev_board = np.zeros((size, size))
        self.piece_type = 1

    def load(self):
        self._load_from_input()
        return self

    def copy(self):
        return deepcopy(self)

    def _load_from_input(self):
        with open('./input.txt') as f:
            lines = f.readlines()

            self.piece_type = int(lines[0])

            self.prev_board = np.array([[int(x) for x in line.rstrip('\n')] for line in lines[1 : self.size + 1]])
            self.board = np.array([[int(x) for x in line.rstrip('\n')] for line in lines[self.size + 1 : 2 * self.size + 1]])

    def is_valid_place(self, i, j, piece_type):
        if (not 0 <= i < self.size) or (not 0 <= j < self.size):
            return False

        if self.board[i][j] != 0:
            return False

        tmp_game = self.copy()

        tmp_game.board[i][j] = piece_type
        if tmp_game.check_liberty(i, j) != 0:
            return True

        dead_pieces = tmp_game._remove_died_pieces(3 - piece_type)
        if tmp_game.check_liberty(i, j) == 0:
            return False

        if dead_pieces and self._is_same_board(self.prev_board, tmp_game.board):
            return False

        return True

    def make_a_move(self, i, j, piece_type):
        if (not 0 <= i < self.size) or (not 0 <= j < self.size) or self.board[i][j] != 0:
            raise Exception

        self.board[i][j] = piece_type
        self._remove_died_pieces(3 - piece_type)

    def _neighbors(self, i, j):
        for direct in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
            new_i, new_j = i + direct[0], j + direct[1]
            if 0 <= new_i < self.size and 0 <= new_j < self.size:
                yield [new_i, new_j]

    def _check_single_liberty(self, i, j):
        liberty = 0
        for neighbor in self._neighbors(i, j):
            if self.board[neighbor[0]][neighbor[1]] == 0:
                liberty += 1
        return liberty

    def check_liberty(self, i, j):
        allies = self.find_ally(i, j)
        liberty = 0
        for ally in allies:
            liberty += self._check_single_liberty(ally[0], ally[1])

        return liberty

    def check_block_liberty(self, pieces):
        rst = 0
        for piece in pieces:
            rst += self._check_single_liberty(piece[0], piece[1])

        return rst

    def find_ally(self, i, j):
        # bfs
        queue = [[i, j]]
        rst = []

        while queue:
            cur = queue.pop(0)
            rst.append(cur)

            for neighbor in self._neighbors(cur[0], cur[1]):
                if self.board[neighbor[0]][neighbor[1]] == self.board[i][j] and [neighbor[0], neighbor[1]] not in queue and [neighbor[0], neighbor[1]] not in rst:
                    queue.append(neighbor)

        return rst

    def _remove_died_pieces(self, piece_type):
        dead_pieces = []
        for i in range(self.size):
            for j in range(self.size):

                if self.board[i][j] == piece_type:
                    block = self.find_ally(i, j)
                    if self.check_block_liberty(block) == 0:
                        self._remove_piece_in_block(block)
                        dead_pieces += block

        return dead_pieces

    def _remove_piece(self, i, j, place_holder=False):
        if place_holder:
            self.board[i][j] = -1
        else:
            self.board[i][j] = 0

    def _remove_piece_in_block(self, pieces, place_holder=False):
        for piece in pieces:
            self._remove_piece(piece[0], piece[1], place_holder)

    def _is_same_board(self, board1, board2):
        if (board1 == board2).all():
            return True
        else:
            return False

    def evaluate_liberty(self):
        rst1, rst2 = 0, 0
        tmp = deepcopy(self)
        for i in range(tmp.size):
            for j in range(tmp.size):
                if tmp.board[i][j] not in [1, 2]:
                    continue

                allys = tmp.find_ally(i, j)
                rst = tmp.check_block_liberty(allys)
                if tmp.board[i][j] == 1:
                    rst1 += rst
                else:
                    rst2 += rst

                tmp._remove_piece_in_block(allys, place_holder=True)

        return [rst1, rst2]

    def evaluate_score(self):
        rst1, rst2 = 0, 0
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 1:
                    rst1 += 1
                elif self.board[i][j] == 2:
                    rst2 += 1

        return [rst1, rst2]

class BasePlayer(object):
    def __init__(self):
        self.type = 'base'
        self.board = Board(5)

    def play_one_step(self):
        self.board = Board(5).load()
        action = self.get_input()
        self._write_out_put(action)

    def _write_out_put(self, result):
        res = ""
        if result == "PASS":
            res = "PASS"
        else:
            res += str(result[0]) + ',' + str(result[1])

        with open('output.txt', 'w') as f:
            f.write(res)

    def get_input(self):
        raise NotImplementedError

    def _location_score(self, i, j):
        if self.board.size == 5:
            ls = [1, 2, 1, 2, 1]
            return (ls[i] + ls[j]) / 2

        return 0

    def _evaluate_location(self, game_board=None):
        if not game_board:
            game_board = self.board

        rst1, rst2 = 0, 0
        for i in range(game_board.size):
            for j in range(game_board.size):
                if game_board.board[i][j] == 1:
                    rst1 += self._location_score(i, j)
                else:
                    rst2 += self._location_score(i, j)

        return [rst1, rst2]

    def _evaluate_liberty(self, game_board=None):
        '''
        return liberty for 1 and 2
        '''
        if not game_board:
            game_board = self.board

        return game_board.evaluate_liberty()

    def _evaluate_score(self, game_board=None):
        if not game_board:
            game_board = self.board

        return game_board.evaluate_score()

    def evaluate(self, game_board):
        scores = self._evaluate_score(game_board)
        liberties = self._evaluate_liberty(game_board)
        locations = 2 * self._evaluate_location(game_board)

        return scores[0] + liberties[0] + locations[0] - scores[1] - liberties[1] - locations[1]

    def _find_valid_places(self, board, piece_type):
        rst = []
        for i in range(board.size):
            for j in range(board.size):
                if board.is_valid_place(i, j, piece_type):
                    rst.append([i, j])

        return rst

class ABPruningPlayer(BasePlayer):
    def __init__(self, search_depth=2, branch_factor=20):
        super(ABPruningPlayer, self).__init__()
        self.type = 'ab pruning'
        self.search_depth = search_depth
        self.branch_factor = branch_factor

    def get_input(self):
        action = self.ab_search(self.board, self.board.piece_type)
        if not action:
            return 'PASS'

        else:
            return action

    def find_places(self, board, piece_type):
        places = self._find_valid_places(board, piece_type)
        np.random.shuffle(places)
        if len(places) > self.branch_factor:
            places = places[:self.branch_factor]

        return places

    def ab_search(self, board: Board, piece_type):
        return self.max_value(board, piece_type, float('-inf'), float('inf'), self.search_depth)[1]

    def max_value(self, board, piece_type, a, b, k):
        if k == 0:
            return self.evaluate(board), None if piece_type == 1 else -self.evaluate(board), None

        places = self.find_places(board, piece_type)
        value = float('-inf')
        action = None

        for place in places:
            tmp_board = board.copy()
            tmp_board.make_a_move(place[0], place[1], piece_type)

            old_value = value
            value = max(value, self.min_value(tmp_board, 3 - piece_type, a, b, k - 1))
            if value != old_value:
                action = place

            if value >= b:
                return value, action

            a = max(a, value)

        return value, action

    def min_value(self, board, piece_type, a, b, k):
        if k == 0:
            return self.evaluate(board) if piece_type == 1 else -self.evaluate(board)

        places = self.find_places(board, piece_type)
        value = float('inf')

        for place in places:
            tmp_board = board.copy()
            tmp_board.make_a_move(place[0], place[1], piece_type)

            value = min(value, self.max_value(tmp_board, 3 - piece_type, a, b, k - 1)[0])

            if value <= a:
                return value

            b = min(b, value)

        return value

class BaseLearningPlayer(BasePlayer):
    def train(self, result, update=True):
        pass

    def _load_training(self):
        pass

    def _update_training(self):
        pass

class QLearningPlayer(BaseLearningPlayer):
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
                if q_values[i][j] > mx or (q_values[i][j] == mx and random.random() <= SWITCH_PROP):
                    mx = q_values[i][j]
                    row, col = i, j

        return row, col

    def train(self, result, update=True):
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
        if update:
            self._update_training()

    def _encode_board(self, board, piece_type):
        if piece_type == 2:
            # exchange 1, 2
            for i in range(len(board)):
                for j in range(len(board)):
                    if board[i][j] != 0:
                        board[i][j] = 3 - board[i][j]
        gradient = np.array(np.gradient(board), dtype=np.int32).flatten()
        return int(''.join(str(i + 2) for i in gradient))

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
    player = ABPruningPlayer()
    player.play_one_step()
