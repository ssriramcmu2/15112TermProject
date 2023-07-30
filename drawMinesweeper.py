from cmu_graphics import *
import random
from PIL import Image
import copy

class Bomb:
    def __init__(self):
        myGif = Image.open('minebomb.gif')
        self.spriteList = []
        for frame in range(myGif.n_frames):  #For every frame index...
            #Seek to the frame, convert it, add it to our sprite list
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//2, myGif.size[1]//2))
            fr = fr.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            fr = CMUImage(fr)
            self.spriteList.append(fr)

        ##Fix for broken transparency on frame 0
        self.spriteList.pop(0)
        
        self.spriteCounter = 0
    
    def draw(self, x, y):
        #Draw current kirb sprite
        drawImage(self.spriteList[self.spriteCounter],
                  x, y, align = 'center')
        # self.spriteCounter += 1 
        # self.spriteCounter = self.spriteCounter % len(self.spriteList)
    

class Minesweeper:
    # Drawing 2D Grid taken from chapter 5, section 3.2 in CS Academy
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = rows
        self.boardLeft = 150
        self.boardTop = 150
        self.boardWidth = 500
        self.boardHeight = 500
        self.cellBorderWidth = 2
        self.grid = [([False] * self.cols) for row in range(self.rows)]
        self.mines = set()
        self.clickedCells = set()
        self.assignMines()
        self.bomb = Bomb()
        self.gameOver = False
        print(self.mines)
    
    def assignMines(self):
        # randomly place 10 mines on the grid
        for _ in range(10):
            mineRow = random.randrange(self.rows)
            mineCol = random.randrange(self.cols)
            # check if the randomly generated mine is not in the mine set
            if (mineRow, mineCol) not in self.mines:
                self.mines.add((mineRow, mineCol))
                self.grid[mineRow][mineCol] = True
        # if there are any mines missing, add until there are 10 mines
        while len(self.mines) != 10:
            mineRow = random.randrange(self.rows)
            mineCol = random.randrange(self.cols)
            if (mineRow, mineCol) not in self.mines:
                self.mines.add((mineRow, mineCol))
                self.grid[mineRow][mineCol] = True
    
    def getNeighboringMineCount(self, row, col):
        # iterate through all the cell's neighbors
        # check if there is a mine in one of the cells
        mineCount = 0
        deltaValues = [-1, 0, 1]
        for drow in deltaValues:
            for dcol in deltaValues:
                examinedRow = row + drow
                examinedCol = col + dcol
                if (0 <= examinedRow < self.rows) and (0 <= examinedCol < self.cols):
                    if self.grid[examinedRow][examinedCol]:
                        # increment mine count by 1
                        mineCount += 1
        return mineCount
    
    def drawGrid(self):
        # draw the board and the border
        self.drawBoard()
        self.drawBoardBorder()
    
    def drawBoard(self):
        # iterate through the length of the board
        for row in range(self.rows):
            for col in range(self.cols):
                # draw the cell 
                self.drawCell(row, col, None)
                # draw a bomb if a mine is clicked
                if (row, col) in self.clickedCells and self.grid[row][col]:
                    self.drawBomb(row, col)
                    self.gameOver = True
                # otherwise, get the count and draw the count of nearest mines
                elif (row, col) in self.clickedCells and not self.grid[row][col]:
                    count = self.getNeighboringMineCount(row, col)
                    self.drawCount(count, row, col)
    
    def drawBomb(self, row, col):
        # get dimensions
        cellLeft, cellTop = self.getCellLeftTop(row, col)
        cellWidth, cellHeight = self.getCellSize()
        x = cellLeft + cellWidth//2
        y = cellTop + cellHeight//2
        self.bomb.draw(x, y)
        
    def drawBoardBorder(self):
        # draw board border with double thickness
        drawRect(self.boardLeft, self.boardTop, self.boardWidth, self.boardHeight,
           fill=None, border='black',
           borderWidth=2*self.cellBorderWidth)
    
    def drawCell(self, row, col, fillColor):
        # draw the cell with specified fill color
        cellLeft, cellTop = self.getCellLeftTop(row, col)
        cellWidth, cellHeight = self.getCellSize()
        drawRect(cellLeft, cellTop, cellWidth, cellHeight,
                fill=fillColor, border='black',
                borderWidth=self.cellBorderWidth)
    
    def drawCount(self, count, row, col):
        # draw the counter in the center of the cell
        cellLeft, cellTop = self.getCellLeftTop(row, col)
        cellWidth, cellHeight = self.getCellSize()
        drawLabel(count,
                  cellLeft + cellWidth//2,
                  cellTop + cellHeight//2,
                  size=20)
        
    def getCellLeftTop(self, row, col):
        # get the cell's left, top position
        cellWidth, cellHeight = self.getCellSize()
        cellLeft = self.boardLeft + col * cellWidth
        cellTop = self.boardTop + row * cellHeight
        return (cellLeft, cellTop)

    def getCellSize(self):
        # get the cell's size
        cellWidth = self.boardWidth / self.cols
        cellHeight = self.boardHeight / self.rows
        return (cellWidth, cellHeight)

    def getCell(self, mouseX, mouseY):
        # get the cell given by a set of mouseX , mouseY) coordinates
        for row in range(self.rows):
            for col in range(self.cols):
                cellLeft, cellTop = self.getCellLeftTop(row, col)
                cellWidth, cellHeight = self.getCellSize()
                if ((cellLeft <= mouseX <= cellLeft + cellWidth) and 
                        (cellTop <= mouseY <= cellTop + cellHeight)):
                    self.clickedCells.add((row, col))