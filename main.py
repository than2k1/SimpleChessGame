# draw the UI

import pygame as pg
from ChessEngine import *
import RandomMove

DIMENSION = 8
SIZE = 512
WINDOW_SIZE = 800
IMAGES = {}
SQ_SIZE = SIZE / DIMENSION
FPS = 24


def load_images():
    pieces = ["bp", "bR", "bN", "bB", "bQ", "bK", "wp", "wR", "wN", "wB", "wQ", "wK"]
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("images/{name}.png".format(name=piece)), (SQ_SIZE, SQ_SIZE))

def main():
    pg.init()
    screen = pg.display.set_mode((SIZE, SIZE))
    clock = pg.time.Clock()
    screen.fill(pg.Color("black"))
    gs = ChessEngine()
    load_images()
    moveMade = False
    validMove = gs.getValidMove()
    selected = () # the selected square
    playerClick = [] #keep 2 positions of first and second selected square
    running = True
    gameOver = False
    player1 = False #if human play white
    player2 = False #if human play black
    while running:
        humanTurn = (gs.whiteToMove and player1) or (not gs.whiteToMove and player2)

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            if e.type == pg.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    x, y = pg.mouse.get_pos()
                    col = int(x // SQ_SIZE)
                    row = int(y // SQ_SIZE)
                    if selected == (row, col):  # click the same square twice
                        selected = ()
                        playerClick = []
                    else :
                        selected = (row, col)
                        # print(selected)
                        playerClick.append(selected)
                    if len(playerClick) == 2: # click 2 times
                        start = playerClick[0]
                        end = playerClick[1]
                        
                        print(start, end)
                        move = Move(start, end, gs.board)
                        # print(validMove)
                        for i in range(len(validMove)):
                            if move == validMove[i]:
                        
                                gs.makeMove(validMove[i])
                                # print(move.getChessNotation())

                                selected = ()
                                playerClick = []
                                moveMade = True
                        if not moveMade:
                            selected = ()
                            playerClick = []
            
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_BACKSPACE:
                    print("backspace pressed")
                    gs.undoMove()
                    moveMade = True
                    selected = ()
                    playerClick = []

        #AI here
        if not gameOver and not humanTurn:
            AIMove = RandomMove.findRandomMove(validMove)
            gs.makeMove(AIMove)
            moveMade = True

        if moveMade:
            validMove = gs.getValidMove()
            if len(validMove) == 0:
                gameOver = True
            moveMade = False
        



        draw_game(screen, gs, validMove, selected)
        clock.tick(FPS)
        pg.display.flip()


def highlight_square(screen, gs, validMove, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): 
            s = pg.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(pg.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(pg.Color('yellow'))
            for move in validMove:
                if move.start == (r,c):
                    screen.blit(s, (move.end[1]*SQ_SIZE, move.end[0]*SQ_SIZE))

def draw_game(screen, gs, validMove, selected):
    draw_board(screen)
    highlight_square(screen, gs, validMove, selected)
    draw_pieces(screen, gs.board)

def draw_board(screen):
    for i in range(0, DIMENSION):
        for j in range(0, DIMENSION):
            
            color = pg.Color("white") if (i+j)%2 == 0 else pg.Color("gray")
            pg.draw.rect(screen, color, pg.Rect(j*SQ_SIZE, i*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    for row in range(0, DIMENSION):
        for col in range(0, DIMENSION):
            if board[row, col] != "__":
                screen.blit(IMAGES[board[row, col]], (col*SQ_SIZE, row*SQ_SIZE))
    

if __name__ == "__main__":
    main()