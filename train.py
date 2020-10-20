import os
import shutil
import time
import host
from my_player3 import QLearningPlayer, ABPruningPlayer
from trainers import THost, TRandomPlayer

host = THost()
qlearner = ABPruningPlayer()
# qlearner = QLearningPlayer()
opponent = TRandomPlayer()

PRINT = False
TRAIN = True

NUM_GAMES = 1000

def cond_print(val):
    if PRINT:
        print(val)

def pre_clean_up():
    cond_print('Clean Up..')
    if os.path.exists('input.txt'):
        os.remove('input.txt')

    if os.path.exists('output.txt'):
        os.remove('output.txt')

    shutil.copy('./init/input.txt', './input.txt')
    cond_print ('Start Playing')

def _clean_output():
    if os.path.exists('output.txt'):
        os.remove('output.txt')

def play(player1, player2):
    pre_clean_up()

    moves = 0

    while True:
        _clean_output()

        cond_print('Black makes move...')
        player1.play_one_step()
        moves += 1

        rst = host.judge(moves, PRINT)

        if rst != 0:
            break

        _clean_output()

        cond_print('White makes move...')
        player2.play_one_step()

        rst = host.judge(moves, PRINT)

        if rst != 0:
            break

    pre_clean_up()
    return rst

def play_round(round_num, player1, player2):
    cond_print('Round {0}'.format(round_num))
    winner = play(player1, player2)

    if winner == 0:
        result = 'draw'
    elif winner == 1:
        result = 'win'
    else:
        result = 'loss'
    # player1.train(result, False)

    if winner == 0:
        result = 'draw'
    elif winner == 2:
        result = 'win'
    else:
        result = 'loss'
    # player2.train(result, False)

    if winner == 2:
        cond_print('Player 2 {0} Win'.format(player2.type))
        return 2
    elif winner == 0:
        cond_print('Tie')
        return 0
    else:
        cond_print('Player 1 {0} Win'.format(player1.type))
        return 1

def main(opponent=TRandomPlayer()):
    start = time.time()

    play_time = NUM_GAMES
    player1 = opponent
    player2 = qlearner
    black_win_time = 0
    white_win_time = 0
    black_tie_time = 0
    white_tie_time = 0

    for round in range(0, play_time, 2):

        percent = round / play_time
        if percent * 100 % 10 == 0:
            print('{0}%'.format(percent * 100))

        rst = play_round(round + 1, player1, player2)
        if rst == 2:
            white_win_time += 1
        elif rst == 0:
            white_tie_time += 1

        rst = play_round(round + 2, player2, player1)
        if rst == 1:
            black_win_time += 1
        elif rst == 0:
            black_tie_time += 1

    print('===== summary =====')
    print('You play as Black | Win: {0} | Lose: {1} | Tie: {2}'.format(black_win_time, play_time // 2 - black_win_time - black_tie_time, black_tie_time))
    print('You play as white | Win: {0} | Lose: {1} | Tie: {2}'.format(white_win_time, play_time // 2 - white_win_time - white_tie_time, white_tie_time))

    end = time.time()

    print('Time Taken: {0} seconds'.format(end - start))

    # for player in [player1, player2]:
    #     player._update_training()

if __name__ == '__main__':
    main()
    pass
