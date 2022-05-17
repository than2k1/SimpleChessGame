# draw the UI

import pygame as pg
from ChessEngine import *

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
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            if e.type == pg.MOUSEBUTTONDOWN:
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
                    if move in validMove:
                        gs.makeMove(move)
                        # print(move.getChessNotation())

                        selected = ()
                        playerClick = []
                        moveMade = True
                    else:
                        selected = ()
                        playerClick = []
            
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_BACKSPACE:
                    print("backspace pressed")
                    gs.undoMove()
                    moveMade = True
                    selected = ()
                    playerClick = []

        if moveMade:
            validMove = gs.getValidMove()
            moveMade = False


        draw_game(screen, gs)
        clock.tick(FPS)
        pg.display.flip()


def draw_game(screen, gs):
    draw_board(screen)

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