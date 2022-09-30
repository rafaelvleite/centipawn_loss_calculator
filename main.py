# -*- coding: utf-8 -*-

from stockfish import Stockfish
import chess.pgn
from datetime import datetime
import matplotlib.pyplot as plt


start = datetime.now()

stockfish = Stockfish(path="/usr/local/Cellar/stockfish/15/bin/stockfish", 
                      depth=22, parameters={"Threads": 4, "Hash": 32768})

stockfish.get_parameters()

pgn = open("Li, Ben_vs_Niemann, Hans Moke_2021.07.22.pgn")
game = chess.pgn.read_game(pgn)
game.headers["Event"]
game.headers["Date"]
game.headers["White"]
game.headers["Black"]

white_centipawn_loss_list = []
black_centipawn_loss_list = []
evaluations = []

evaluation = stockfish.get_evaluation()
evaluations.append(evaluation['value'])

for move in game.mainline_moves():
    stockfish.make_moves_from_current_position([move])
    evaluation = stockfish.get_evaluation()
    if evaluation['type'] == 'cp':
        evaluations.append(evaluation['value'])
    else:
        evaluations.append(None)
    print(move, evaluation)

evaluationsAdjusted = evaluations.copy()

for i,e in enumerate(evaluationsAdjusted[:-1], 1):
    if evaluationsAdjusted[i] is None:
        evaluationsAdjusted[i] = evaluationsAdjusted[i-1]

#evaluationsAdjusted = [x for x in evaluationsAdjusted if x!= None]
evaluationsAdjusted = [x - evaluations[0] for x in evaluationsAdjusted] 

evaluationsAdjusted = [max(min(x, 1000), -1000) for x in evaluationsAdjusted]

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
        
    


plt.plot([x/100 for x in evaluationsAdjusted if x != None], color='magenta', marker='o',mfc='pink' ) #plot the data
plt.xticks(range(0,len(evaluationsAdjusted)+1, 1)) #set the tick frequency on x-axis

plt.ylabel('Evaluation') #set the label for y axis
plt.xlabel('Half Move') #set the label for x-axis
plt.title("Plotting the evaluations") #set the title of the graph
plt.show() #display the graph



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











