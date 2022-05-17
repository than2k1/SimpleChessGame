# save the information
from turtle import st
import numpy as np
import chess
SIZE = 8
A1 = (7,0)
A8 = (7,7)
H1 = (0,0)
H8 = (0,7)
class Player:
    def __init__(self, isWhite = True):
        self.isWhite = isWhite
        if self.isWhite:
            self.piece = {
                # 'r' : [(7,0),(7,7)],
                # 'n' : [(7,1),(7,6)],
                # 'b' : [(7,2),(7,5)],
                # 'q' : [(7,3)],
                # 'k' : [(7,4)],
                # 'p' : [(6,0),(6,1),(6,2),(6,3),(6,4),(6,5),(6,6),(6,7)]
            }
            
        else:
            self.piece = {
                # 'r' : [(0,0),(0,7)],
                # 'n' : [(0,1),(0,6)],
                # 'b' : [(0,2),(0,5)],
                # 'q' : [(0,3)],
                # 'k' : [(0,4)],
                # 'p' : [(1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7)]
            }
        self.canCastle = (True, True)
        self.enpassant = []#enpassant square (pawn get 2 move ahead)
        self.bitboard = ''
        self.inCheck = False
        self.pins = []
        self.checks = []

    def deletePiece(self, typ, position):
        for i, pos in enumerate(self.piece[typ]):
            if pos == position:
                del self.piece[typ][i]
    
    def addPiece(self, typ, position):
        self.piece[typ].append(position) 

    def updatePosition(self, typ, start, end):
        for i, pos in enumerate(self.piece[typ.lower()]):
            if pos == start:
                self.piece[typ.lower()][i] = end

class ChessEngine:

    directions = {
        "R":  [(0,1), (0,-1), (-1,0), (1,0)],
        "B": [(1, 1), (-1, -1), (1, -1), (-1, 1)],
        "Q": [(0,1), (0,-1), (-1,0), (1,0), (1, 1), (-1, -1), (1, -1), (-1, 1)],
        "N": [(2,1), (-2, -1), (1, 2), (-1, -2), (-2, 1), (2, -1), (1, -2), (-1, 2)],
        "K":  [(0,1), (0,-1), (-1,0), (1,0), (1, 1), (-1, -1), (1, -1), (-1, 1)],
        "BPC": [(1,1),(1,-1)], #black pawn capture
        "WPC": [(-1,1),(-1,-1)]#white pawn capture
    }

    def __init__(self):
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ])
        self.log = []
        self.whiteToMove = True
        # board = chess.Board()
        self.black = Player(False)
        self.white = Player(True)
        for r in range(SIZE):
            for c in range(SIZE):
                color, p = self.board[r][c][0], self.board[r][c][1].lower()
                if  color == 'w': 
                    if p in self.white.piece.keys():
                        self.white.piece[p].append((r,c))
                    else:
                        self.white.piece[p] = [(r,c)]
                elif color == 'b':
                    if p in self.black.piece.keys():
                        self.black.piece[p].append((r,c))
                    else:
                        self.black.piece[p] = [(r,c)]

    def makeMove(self, move):
        #take piece from start position to end position
        player = self.white if self.whiteToMove else self.black
        if move.capturedPiece != "__":
            opponent = self.black if self.whiteToMove else self.white
            captured = move.capturedPiece[1].lower()
            opponent.deletePiece(captured, move.end)
        moved = move.movedPiece[1].lower()
        player.updatePosition(moved, move.start, move.end)
        self.board[move.end[0], move.end[1]] = move.movedPiece
        self.board[move.start[0], move.start[1]] = "__"
        self.log.append(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if len(self.log) == 0:
            return
        lastMove = self.log.pop()
        opponent = self.black if self.whiteToMove else self.white
        if lastMove.capturedPiece != "__":
            player = self.white if self.whiteToMove else self.black
            captured = lastMove.capturedPiece[1].lower()
            player.addPiece(captured, lastMove.end)
        moved = lastMove.movedPiece[1].lower()
        opponent.updatePosition(moved, lastMove.end, lastMove.start)
        self.board[lastMove.start[0], lastMove.start[1]] = lastMove.movedPiece
        self.board[lastMove.end[0], lastMove.end[1]] = lastMove.capturedPiece
        self.whiteToMove = not self.whiteToMove

    def getAllMove(self):
        player = self.white if self.whiteToMove else self.black
        moveList = []
        for typ, position in player.piece.items():
                if typ == "p":
                    for row, col in position:
                        moveList += self.getPawnMove(row, col)
                if typ == "r":
                    for row, col in position:
                        moveList += self.getMultiMove(row, col)
                if typ == "b":
                    for row, col in position:
                        moveList += self.getMultiMove(row, col)
                if typ == "q":
                    for row, col in position:
                        moveList += self.getMultiMove(row, col)
                if typ == "k":
                    for row, col in position:
                        moveList += self.getKingMoves(row, col)
                    #castle move!
                if typ == "n":
                    for row, col in position:
                        moveList += self.getKnightMove(row, col)
                    

        return moveList

    def getValidMove(self):
        moves = []
        player = self.white if self.whiteToMove else self.black
        player.inCheck, player.pins, player.checks = self.checkPinAndCheck()
        print(player.inCheck, player.pins, player.checks)
        king = player.piece['k'][0]
        if player.inCheck:
            moves = self.getAllMove()
            if len(player.checks) == 1:
                #check = (row, col, dir0, dir1) 
                checkingRow, checkingCol = player.checks[-1][0], player.checks[-1][1]
                piece = self.board[checkingRow][checkingCol]
                validSquare = []
                checkDirRow, checkDirCol = player.checks[-1][2], player.checks[-1][3]
                if piece[1].lower() == 'n': #the knight
                    validSquare.append((checkingRow, checkingCol))
                else:
                    for i in range(1,SIZE):
                        square = (king[0] + checkDirRow*i, king[1] + checkDirCol*i)
                        validSquare.append(square)
                        if square[0] == checkingRow and square[1] == checkingCol:
                            break
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].movedPiece[1].lower() != 'k':
                        if not moves[i].end in validSquare:
                            moves.remove(moves[i])
                    else:
                        moves.remove(moves[i])
                moves += self.getKingMoves(king[0], king[1])
            elif len(player.checks) >1:
                #double check
                moves = self.getKingMoves(king[0], king[1])
        else:
            moves = self.getAllMove()
        # for move in moves:
        #     print(move.start, move.end)
        print("_______________")
        if len(moves) == 0:
            if player.inCheck == True:
                print("checkmate")
            else:
                print("draw")
        return moves

    def getKingMoves(self, r, c):
        moveList = []
        player = self.white if self.whiteToMove else self.black
        allyColor = self.board[r][c][0]
        direction = self.directions["K"]
        for dir in direction:
            row = r + dir[0]
            col = c + dir[1]
            if 0 <= row < SIZE and 0 <= col < SIZE and self.board[row][col][0] != allyColor:
                player.updatePosition("K", (r,c), (row, col))
                inCheck, _ , _ = self.checkPinAndCheck()
                if not inCheck:
                    moveList.append(Move((r,c), (row,col), self.board))
                player.updatePosition("K", (row,col), (r,c))
        return moveList



    def getPawnMove(self, r, c ):
        #promotion and enpassant move !!
        isPined = False
        pinDir = ()
        player = self.white if self.whiteToMove else self.black
        for i in range(len(player.pins)-1, -1, -1):
            if player.pins[i][0] == r and player.pins[i][1] == c:
                isPined = True
                pinDir = (player.pins[i][2], player.pins[i][3])
                player.pins.remove(player.pins[i])
                break
        moveList = []
        if self.whiteToMove:
            if (r-1>=0):
                if self.board[r-1][c] == "__": #the front is empty
                    if not isPined or pinDir == (-1,0):
                        moveList.append(Move((r,c), (r-1, c), self.board))
                        if self.board[r-2][c] == "__" and r == 6:
                            moveList.append(Move((r,c), (r-2, c), self.board))
        else:
            if (r+1<SIZE):
                if not isPined or pinDir == (1,0):
                    if self.board[r+1][c] == "__": #the front is empty
                        moveList.append(Move((r,c), (r+1, c), self.board))
                        if self.board[r+2][c] == "__" and r == 1:
                            moveList.append(Move((r,c), (r+2, c), self.board))
        #capture move
        if self.whiteToMove:
            if (c-1 >= 0):
                if not isPined or pinDir == (-1,-1):
                    if self.board[r-1][c-1][0] ==  "b": 
                        moveList.append(Move((r,c), (r-1, c-1), self.board))
            if (c+1<SIZE) :
                if not isPined or pinDir == (-1,1):
                    if self.board[r-1][c+1][0] == "b": 
                        moveList.append(Move((r,c), (r-1, c+1), self.board))
        
        else:
            if (c-1 >= 0):
                if not isPined or pinDir == (1,-1):
                    if self.board[r+1][c-1][0] ==  "w": 
                        moveList.append(Move((r,c), (r+1, c-1), self.board))
            if (c+1<SIZE) :
                if not isPined or pinDir == (1,1):
                    if self.board[r+1][c+1][0] == "w": 
                        moveList.append(Move((r,c), (r+1, c+1), self.board))
        return moveList

    def getMultiMove(self, r, c):
        moveList = []
        piece = self.board[r][c][1]
        playerColor = "w" if self.whiteToMove else "b"
        opponentColor = "b" if self.whiteToMove else "w"
        isPined = False
        pinDir = ()
        player = self.white if self.whiteToMove else self.black
        for i in range(len(player.pins)-1, -1, -1):
            if player.pins[i][0] == r and player.pins[i][1] == c:
                isPined = True
                pinDir = (player.pins[i][2], player.pins[i][3])
                player.pins.remove(player.pins[i])
                break
        if isPined:
            direction = [pinDir,(-pinDir[0], -pinDir[1])]
            print("______________")
            print(direction)
            print("______________")
        else:
            direction = self.directions[piece.upper()]
        
        for dir in (direction):
            i = 1
            while SIZE > r + i*dir[0] >=0  and SIZE > c+i*dir[1] >=0 and self.board[r + i*dir[0]][c+i*dir[1]][0] != playerColor:
                moveList.append(Move((r,c), (r + i*dir[0], c+i*dir[1]), self.board))
                if self.board[r + i*dir[0]][c+i*dir[1]][0] == opponentColor:
                    break
                i += 1
                
        return moveList     

    def getKnightMove(self, r, c):
        moveList = []
        piece = self.board[r][c][1]
        playerColor = "w" if self.whiteToMove else "b"
        opponent = "b" if self.whiteToMove else "w"
        isPined = False
        pinDir = ()
        player = self.white if self.whiteToMove else self.black
        for i in range(len(player.pins)-1, -1, -1):
            if player.pins[i][0] == r and player.pins[i][1] == c:
                isPined = True
                pinDir = (player.pins[i][2], player.pins[i][3])
                player.pins.remove(player.pins[i])
                break
        if isPined:
            return []    
        direction = self.directions[piece.upper()]
        for dir in direction:
            if r + dir[0] >=0 and r + dir[0] < SIZE and c+dir[1] >=0 and c+dir[1] < SIZE and self.board[r + dir[0]][c+dir[1]][0] != playerColor:
                moveList.append(Move((r,c), (r + dir[0], c+dir[1]), self.board))
        return moveList
    
    def checkPinAndCheck(self):
        #=> inCheck, pin, checks
        inCheck = False
        pins = []
        checks = []
        allyColor = 'w' if self.whiteToMove else 'b'
        oppColor = 'b' if self.whiteToMove else 'w'
        direction = self.directions['Q'] #get diagonal and straight direction for slider piece
        player = self.white if self.whiteToMove else self.black
        startRow, startCol = player.piece['k'][0][0], player.piece['k'][0][1] #row and col of king
        for dir in direction:
            possiblePin = ()
            for i in range(1,SIZE):
                row = startRow + i*dir[0]
                col = startCol + i*dir[1]
                if 0 <= row < SIZE and 0 <= col < SIZE:
                    piece = self.board[row][col]
                    if piece[0] == allyColor:
                        if possiblePin == ():
                            possiblePin = (row, col, dir[0], dir[1])
                        else:
                            break
                    elif piece[0] == oppColor:
                        typ = piece[1].upper()
                        if typ in ["P", "K"]:
                            if i == 1:
                                #pawn and king can move only 1 step
                                if typ == "P":
                                    checkDir = self.directions["BPC"] if self.whiteToMove else self.directions["WPC"]
                                    if (-dir[0],-dir[1]) in checkDir: 
                                        inCheck = True
                                        checks.append((row, col, dir[0], dir[1]))
                                        break
                                else:
                                    checkDir = self.directions["K"]
                                    if dir in checkDir:
                                        inCheck = True
                                        checks.append((row, col, dir[0], dir[1]))
                                        break
                            else:
                                break
                        else:
                            checkDir = self.directions[typ.upper()]
                            if (dir[0],dir[1]) in checkDir:
                                if possiblePin == ():
                                    #in check direction with no shield => check
                                    inCheck = True
                                    checks.append((row, col, dir[0], dir[1]))
                                    break
                                else:
                                    pins.append(possiblePin)
                                    break
                            else:
                                break
        #check for opponent knight
        opponent = self.black if self.whiteToMove else self.white
        knight = opponent.piece['n']
        for n in knight:
            for dir in self.directions['N']:
                row = n[0] + dir[0]
                col = n[1] + dir[1]
                if (row, col) == (startRow, startCol):
                    inCheck = True
                    checks.append((n[0],n[1],dir[0],dir[1]))
                    break
        return inCheck, pins, checks
                
                        
                    



    
    
class Move:
    # the chess notation and the matrix structure is diff, so we need to transform from
    # from the notation to row, col in matrix and vice versa
    RankToRow = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    RowToRank = {v: k for k, v in RankToRow.items()}
    FileToCol = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    ColToFile = {v:k for k,v in FileToCol.items()}


    def __init__(self, first, second, board, flag = None):
        self.start = first
        self.end = second
        self.movedPiece = board[self.start[0], self.start[1]]
        self.capturedPiece = board[self.end[0], self.end[1]]
        self.moveID = self.start[0] * 1000 + self.start[1]*100 + self.end[0] * 10 + self.end[1]
        self.flag = flag
    def getChessNotation(self):
        return (self.movedPiece[1] if self.movedPiece[1] != "p" and self.movedPiece != "__"  else "")+ self.getRankFile(self.start[0], self.start[1]) + " " + self.getRankFile(self.end[0], self.end[1])

    def getRankFile(self, row, col):
        return self.ColToFile[col] + self.RowToRank[row]

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Move):
            raise TypeError("Type err")
        return self.moveID == __o.moveID