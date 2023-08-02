from cmu_graphics import *
import random
from PIL import Image
import copy
from minesweeperAI import *

class Bomb:
    def __init__(self):
        self.bomb = Image.open('bomb.png')
        self.bomb = CMUImage(self.bomb)
    
    def draw(self, left, top, width, height):
        drawImage(self.bomb,left,top,width=width,height=height)

class Flag:
    def __init__(self):
        self.flag = Image.open('flag.png')
        self.flag = CMUImage(self.flag)
    def draw(self, left, top, width, height):
        drawImage(self.flag,left,top,width=width,height=height)
        

class Minesweeper:
    # Drawing 2D Grid taken from chapter 5, section 3.2 in CS Academy
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.numberOfMines = mines
        self.boardLeft = 150
        self.boardTop = 150
        self.boardWidth = 500
        self.boardHeight = 500
        self.cellBorderWidth = 2
        self.grid = [([False] * self.cols) for row in range(self.rows)]
        self.cells = set()
        for row in range(len(self.grid)):
            for col in range(len(self.grid)):
                self.cells.add((row, col))
        self.mines = set()
        self.clickedCells = set()
        self.assignMines()
        self.bomb = Bomb()
        self.gameOver = False
        # flag coords
        self.flagBoxLeft = self.boardTop + self.boardWidth
        self.flagBoxTop = 700
        self.flagBoxWidth = 125
        self.flagBoxHeight = 50
        self.flag = Flag()
        # AI Coords
        self.AIBoxLeft = 400
        self.AIBoxTop = 700
        self.AIBoxWidth = 150
        self.AIBoxHeight = 50
        self.AI = MinesweeperAI(9, 9)
        self.clickFlag = False
        self.flagCells = set()
        print(self.mines)
        # print("----------------------")
        # for row in self.grid:
        #     print(row)
    
    def assignMines(self):
        # randomly place 10 mines on the grid
        for _ in range(self.numberOfMines):
            mineRow = random.randrange(self.rows)
            mineCol = random.randrange(self.cols)
            # check if the randomly generated mine is not in the mine set
            if (mineRow, mineCol) not in self.mines:
                self.mines.add((mineRow, mineCol))
                self.grid[mineRow][mineCol] = True
        # if there are any mines missing, add until there are 10 mines
        while len(self.mines) != self.numberOfMines:
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
        # draw button for flagging
        self.drawFlagButton()
        # draw button for AI 
        self.drawAIButton()
    
    def drawAIButton(self):
        # draw the box
        drawRect(self.AIBoxLeft, self.AIBoxTop, self.AIBoxWidth, self.AIBoxHeight, fill='red')
        # draw a label
        drawLabel("Click to make an AI Move!", self.AIBoxLeft + self.AIBoxWidth//2, 
                    self.AIBoxTop + self.AIBoxHeight//2, fill='white')
        
    def drawFlagButton(self):
        # draw the box
        drawRect(self.flagBoxLeft, self.flagBoxTop, self.flagBoxWidth, self.flagBoxHeight, fill='blue')
        # draw a label
        drawLabel("Click to set flag cursor", self.flagBoxLeft + self.flagBoxWidth//2, 
                    self.flagBoxTop + self.flagBoxHeight//2, fill='white')
        
    def drawBoard(self):
        # iterate through the length of the board
        for row in range(self.rows):
            for col in range(self.cols):
                # debug feature to show all the mines
                # color = None
                # if (row, col) in self.mines:
                #     color = 'red'
                # # draw the cell 
                # self.drawCell(row, col, color)
                
                # draw the cell
                self.drawCell(row, col)
                # draw the flag on the selected cell
                if (row, col) in self.clickedCells and (row, col) in self.flagCells:
                    self.drawFlag(row, col)
                # draw a bomb if a mine is clicked without the flag setting
                elif (row, col) in self.clickedCells and self.grid[row][col]:
                    self.drawBomb(row, col)
                    self.gameOver = True
                # otherwise, get the count and draw the count of nearest mines
                elif (row, col) in self.clickedCells and not self.grid[row][col]:
                    count = self.getNeighboringMineCount(row, col)
                    if count == 0:
                        self.drawFloodFill(row, col)
                    else:
                        self.drawCount(count, row, col)
    
    def drawFloodFill(self, row, col, visited=None):
        # define a visited set
        if visited == None:
            visited = set()
        # break once you are back at a cell you already visited
        if (row, col) in visited:
            return 
        # add the cell to the AI's knowledge
        self.getAICell(row, col)
        # add the cell to the visited set
        visited.add((row, col))
        # first, draw the current cell as grey
        self.drawCell(row, col, 'black')
        # get all the neighboring cells
        neighbors = self.getNeighboringCells(row, col)
        # iterate through all neighbors
        for neighbor in neighbors:
            neighborRow, neighborCol = neighbor
            # recursively call if the neighbor is 0
            if self.getNeighboringMineCount(neighborRow, neighborCol) == 0:
                self.drawFloodFill(neighborRow, neighborCol, visited)        
        
    def getNeighboringCells(self, row, col):
        # iterate through all the cell's neighbors
        # add to set if valid cell
        neighbors = []
        deltaValues = [-1, 0, 1]
        for drow in deltaValues:
            for dcol in deltaValues:
                examinedRow = row + drow
                examinedCol = col + dcol
                if (0 <= examinedRow < self.rows) and (0 <= examinedCol < self.cols):
                        neighbors.append((examinedRow, examinedCol))
        return neighbors
        
    def drawBomb(self, row, col):
        # get dimensions
        cellLeft, cellTop = self.getCellLeftTop(row, col)
        cellWidth, cellHeight = self.getCellSize()
        self.bomb.draw(cellLeft, cellTop, cellWidth, cellWidth)
        
    def drawFlag(self, row, col):
        # get dimensions
        cellLeft, cellTop = self.getCellLeftTop(row, col)
        cellWidth, cellHeight = self.getCellSize()
        self.flag.draw(cellLeft, cellTop, cellWidth, cellWidth)
        
    def drawBoardBorder(self):
        # draw board border with double thickness
        drawRect(self.boardLeft, self.boardTop, self.boardWidth, self.boardHeight,
           fill=None, border='black',
           borderWidth=2*self.cellBorderWidth)
    
    def drawCell(self, row, col, fillColor=None):
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
                # check if the mouse was clicked on the cell
                if ((cellLeft <= mouseX <= cellLeft + cellWidth) and 
                        (cellTop <= mouseY <= cellTop + cellHeight)):
                    self.clickedCells.add((row, col))
                    # if we are clicking a flag
                    if self.clickFlag:
                        self.flagCells.add((row, col))
                        self.clickFlag = False
                        
    def getAICell(self, row, col):
        for rowIndex in range(self.rows):
            for colIndex in range(self.cols):
                if row == rowIndex and colIndex == col:
                    count = self.getNeighboringMineCount(row, col)
                    self.AI.add_knowledge((row, col), count)
                    self.clickedCells.add((row, col))
                    break
    
    def checkWin(self):
        if (self.cells - self.clickedCells == self.mines or 
            self.flagCells == self.mines):
            return True
        return False