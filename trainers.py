import sys
import random

from host import judge, GO
from read import readInput, readOutput
from write import writeOutput, writeNextInput
from my_player3 import BasePlayer
from random_player import RandomPlayer

def cond_print(verbose, value):
    if verbose:
        print(value)


class THost():
    def judge(self, n_move, verbose):
        N = 5

        piece_type, previous_board, board = readInput(N)
        go = GO(N)
        go.verbose = verbose
        go.set_board(piece_type, previous_board, board)
        go.n_move = n_move
        try:
            action, x, y = readOutput()
        except:
            cond_print(verbose, "output.txt not found or invalid format")
            return(3-piece_type)

        if action == "MOVE":
            if not go.place_chess(x, y, piece_type):
                cond_print(verbose, 'Game end.')
                cond_print(verbose, 'The winner is {}'.format('X' if 3 - piece_type == 1 else 'O'))
                return(3 - piece_type)

            go.died_pieces = go.remove_died_pieces(3 - piece_type)

        if go.game_end(piece_type, action):
            result = go.judge_winner()
            if verbose:
                cond_print(verbose, 'Game end.')
                if result == 0:
                    cond_print(verbose, 'The game is a tie.')
                else:
                    cond_print(verbose, 'The winner is {}'.format('X' if result == 1 else 'O'))
            return(result)

        piece_type = 2 if piece_type == 1 else 1

        if action == "PASS":
            go.previous_board = go.board
        writeNextInput(piece_type, go.previous_board, go.board)

        return(0)

class TRandomPlayer(BasePlayer):
    def play_one_step(self):
        N = 5
        piece_type, previous_board, board = readInput(N)
        go = GO(N)
        go.set_board(piece_type, previous_board, board)
        action = self.get_input(go, piece_type)
        writeOutput(action)

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
    pass
