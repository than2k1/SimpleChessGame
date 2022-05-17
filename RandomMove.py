import random

def findRandomMove(validMove):
    return validMove[random.randint(0, len(validMove)-1)]