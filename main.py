# -*- coding: utf-8 -*-
import chess
import chess.engine
import chess.pgn
from datetime import datetime

def evaluate_game(board, engine, limit):
   info = engine.analyse(board, limit)
   print(info['depth'])
   return info['score'].white().score(mate_score=10000)

start = datetime.now()

engine = chess.engine.SimpleEngine.popen_uci('/usr/local/Cellar/stockfish/15/bin/stockfish')

movetimesec = 2
depth = 22
limit=chess.engine.Limit(time=movetimesec, depth=depth)

pgn = open("Li, Ben_vs_Niemann, Hans Moke_2021.07.22.pgn")
pgn = open("Pantzar, Milton_vs_Niemann, Hans Moke_2022.01.08.pgn")
game = chess.pgn.read_game(pgn)
game.headers["Event"]
game.headers["Date"]
game.headers["White"]
game.headers["Black"]

board = game.board()

evaluations = []

evaluation = engine.analyse(board, limit=limit)['score'].white().score()
evaluations.append(evaluation)

for move in game.mainline_moves():
    print(board)
    board.push(move)
    positionEvaluation = evaluate_game(board, engine, limit)
    evaluations.append(positionEvaluation)
        
print(evaluations)

evaluationsAdjusted = evaluations.copy()
#evaluationsAdjusted = [x - evaluations[0] for x in evaluationsAdjusted] 
evaluationsAdjusted = [max(min(x, 1000), -1000) for x in evaluationsAdjusted]

white_centipawn_loss_list = []
black_centipawn_loss_list = []

index = 0
for singleEvaluation in evaluationsAdjusted:
    if index > 0:
        previous_state_evaluation = evaluationsAdjusted[index - 1]
        current_state_evaluation = evaluationsAdjusted[index]    
        if index % 2 != 0:
            white_centipawn_loss_list.append(previous_state_evaluation - current_state_evaluation)
        else:
            black_centipawn_loss_list.append(current_state_evaluation - previous_state_evaluation)
    index += 1
        

white_average_centipawn_loss = round(sum(white_centipawn_loss_list) / len(white_centipawn_loss_list))
black_average_centipawn_loss = round(sum(black_centipawn_loss_list) / len(black_centipawn_loss_list))

print("White average centipawn loss: {}".format(white_average_centipawn_loss))
print("Black average centipawn loss: {}".format(black_average_centipawn_loss))



#####################
print("Done! Job complete!")
#####################
#####################
finish = datetime.now()
print('Demorou mas foi! O job todo demorou: {}'.format(finish - start))
#####################
#####################

