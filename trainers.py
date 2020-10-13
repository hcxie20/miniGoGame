import sys

from host import judge, GO
from read import readInput, readOutput
from write import writeOutput, writeNextInput
from my_player3 import BasePlayer
from random_player import RandomPlayer


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
            print("output.txt not found or invalid format")
            return(3-piece_type)

        if action == "MOVE":
            if not go.place_chess(x, y, piece_type):
                print('Game end.')
                print('The winner is {}'.format('X' if 3 - piece_type == 1 else 'O'))
                return(3 - piece_type)

            go.died_pieces = go.remove_died_pieces(3 - piece_type)

        if verbose:
            go.visualize_board()
            print()

        if go.game_end(piece_type, action):
            result = go.judge_winner()
            if verbose:
                print('Game end.')
                if result == 0:
                    print('The game is a tie.')
                else:
                    print('The winner is {}'.format('X' if result == 1 else 'O'))
            return(result)

        piece_type = 2 if piece_type == 1 else 1

        if action == "PASS":
            go.previous_board = go.board
        writeNextInput(piece_type, go.previous_board, go.board)

        return(0)

class TRandomPlayer(RandomPlayer):
    def train(self, result):
        pass

    def play_one_step(self):
        N = 5
        piece_type, previous_board, board = readInput(N)
        go = GO(N)
        go.set_board(piece_type, previous_board, board)
        action = self.get_input(go, piece_type)
        writeOutput(action)
    pass
