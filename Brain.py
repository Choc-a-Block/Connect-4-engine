import random

import GUI
import Neuralnetwork as nnn
import math
from itertools import chain
import pickle
import Montecarlosearch as mcs
import dill


def softmax(nums):
    return [math.exp(num) / sum([math.exp(num) for num in nums]) for num in nums]

def train():
    global network
    epochs = 1000 #int(input("How many epochs"))
    evals = 10 #int(input("How many evals per move"))
    alpha = 0.01#float(input("What do you want alpha to be"))
    loss = 0.99#float(input("What do you want loss to be"))
    gameboard = GUI.board()
    network = nnn.network([nnn.layer(nnn.leakyrelu, nnn.leakyreluder, 7*6, 7*6*5), nnn.noise(0.001), nnn.layer(nnn.leakyrelu, nnn.leakyreluder, 7*6*5, 7*6*5), nnn.noise(0.001), nnn.layer(nnn.leakyrelu, nnn.leakyreluder, 7*6*5, 7*6*5), nnn.layer(nnn.sigmoid, nnn.sigmoidder, 7*6*5, 1)], alpha, loss)
    player = 2
    treem = mcs.tree(1, 1, evalposition)
    for epoch in range(epochs):
        gameboard.reset()
        updatestotal = []
        print(epoch)
        result = 0
        isdraw = False
        while not (gameboard.check_four_in_a_row() or isdraw):
            if player == 1:
                player = 2
            else:
                player = 1
            for i in range(evals):
                print(i)
                treem.searchnext()
            eval = treem.getevals()
            percentages = softmax(eval)
            cumper = [sum(percentages[i+1:]) if i != 6 else 0 for i in range(7)]
            print(cumper)
            choice = random.random()
            chosen = False
            for i in range(7):
                if choice >= cumper[i]:
                    if(gameboard.addcounter(i, player)):
                        treem, updates = mcs.cuttree(treem, i)
                        if len(updatestotal) == 0:
                            updatestotal = updates
                        else:
                            for t in range(len(updatestotal[1])):
                                updatestotal[1][t] += updates[1][t]
                            for t in range(len(updatestotal[0])):
                                for s in range(len(updatestotal[0][t])):
                                    updatestotal[0][t][s] += updates[0][t][s]
                        chosen = True
                        break
            if chosen == False:
                isdraw = True
                result = 0
            board = gameboard.getboard()
            for row in board:
                print(row)
        if not isdraw:
            if player == 1:
                result = 1
            else:
                result = -1
        network.updatelayers(updatestotal, result)
        with open("network.bin", "wb") as f:
            dill.dump(network, f)




def evalposition(moves):
    global network
    gameboard = GUI.board()
    player = 1
    for move in moves:
        gameboard.addcounter(move, player)
        if player == 1:
            player = 2
        else:
            player = 1
    board = gameboard.getboard()
    #for row in board:
    #    print(row)
    board = list(chain.from_iterable(board))
    eval = network.run(board)[0]
    #print(eval)
    #print("\n\n")
    network.backprop([1])
    vals = network.getupdatevals()
    isend = gameboard.check_four_in_a_row()
    return eval, vals, isend


train()