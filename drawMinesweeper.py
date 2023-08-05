from cmu_graphics import *
import random
from PIL import Image
import copy
from minesweeperAI import *

class Bomb:
    """
    This class initializes the bomb that will be drawn on the board.
    Called when the user clicks on a bomb cell.
    
    Citations: Got the image for the bomb from this url.
    https://www.pngegg.com/en/png-cbukd
    """
    def __init__(self):
        # open the image and save it in a class variable
        self.bomb = Image.open('bomb.png')
        self.bomb = CMUImage(self.bomb)
    
    def draw(self, left, top, width, height):
        # draw the image
        drawImage(self.bomb,left,top,width=width,height=height)

class Flag:
    """
    This class initializes the flag that will be drawn on the board.
    Called when the user clicks on a cell with the flag cursor active.
    
    Citations: Got the image for the flag from this url.
    https://www.iconfinder.com/icons/3024770/flag_flags_marker_nation_icon
    """
    def __init__(self):
        # open the image and save it in a class variable
        self.flag = Image.open('flag.png')
        self.flag = CMUImage(self.flag)
    def draw(self, left, top, width, height):
        # draw the image
        drawImage(self.flag,left,top,width=width,height=height)
        

class Minesweeper:
    """
    This class allows for the gameplay of the Minesweeper game.
    Draws the board and appropriate buttons, and handles gameplay.
    
    Citations: Drawing a 2D Grid was taken from chapter 5, section 3.2 in CS Academy
    """
    def __init__(self, rows, cols, mines):
        # board constants
        self.rows = rows
        self.cols = cols
        self.numberOfMines = mines
        # grid dimensions
        self.boardLeft = 150
        self.boardTop = 150
        self.boardWidth = 500
        self.boardHeight = 500
        self.cellBorderWidth = 2
        # initialize a 2D list for the grid that will be used
        self.grid = [([False] * self.cols) for row in range(self.rows)]
        # get a set of all the cells in the grid
        self.cells = set()
        for row in range(len(self.grid)):
            for col in range(len(self.grid)):
                self.cells.add((row, col))
        # initialize a set of the mines, and cells that have been clicked
        self.mines = set()
        self.clickedCells = set()
        # assign the mines to the mine set
        self.assignMines()
        # initialize the bomb 
        self.bomb = Bomb()
        # game over bool
        self.gameOver = False
        # flag coords
        self.flagBoxLeft = self.boardLeft + (self.boardWidth//2 + 20)
        self.flagBoxTop = 700
        self.flagBoxWidth = self.boardWidth//2
        self.flagBoxHeight = 75
        self.flag = Flag()
        # AI Coords
        self.AIBoxWidth = self.boardWidth//2
        self.AIBoxHeight = 75
        self.AIBoxLeft = self.boardLeft
        self.AIBoxTop = 700
        # AI Class initialized
        self.AI = MinesweeperAI(self.rows, self.cols)
        self.clickFlag = False
        self.flagCells = set()
        # print(self.mines)
        # print("----------------------")
        # for row in self.grid:
        #     print(row)
    
    def assignMines(self):
        """
        This function randomly assigns the designated number of mines on the grid.
        Stores them in the self.mines set.
        """
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
    
    def getNeighboringMineCount(self, cell):
        """
        This function gets the number of neighboring cells that are mines.
        Takes in a current cell in tuple (row, col) as an argument.
        """
        # iterate through all the cell's neighbors
        # check if there is a mine in one of the cells
        mineCount = 0
        deltaValues = [-1, 0, 1]
        for drow in deltaValues:
            for dcol in deltaValues:
                examinedRow = cell[0] + drow
                examinedCol = cell[1] + dcol
                if (0 <= examinedRow < self.rows) and (0 <= examinedCol < self.cols):
                    if self.grid[examinedRow][examinedCol]:
                        # increment mine count by 1
                        mineCount += 1
        return mineCount
    
    def drawGrid(self):
        """
        This function draws the grid.
        """
        # draw the board and the border
        self.drawBoard()
        self.drawBoardBorder()
        # draw button for flagging
        self.drawFlagButton()
        # draw button for AI 
        self.drawAIButton()
    
    def drawAIButton(self):
        """
        Part of the drawing functionality, draws the box that will make an AI Move.
        """
        # draw the box
        drawRect(self.AIBoxLeft, self.AIBoxTop, self.AIBoxWidth, self.AIBoxHeight, fill='green')
        # draw a label
        drawLabel("Click to make an AI Move!", self.AIBoxLeft + self.AIBoxWidth//2, 
                    self.AIBoxTop + self.AIBoxHeight//2, fill='white', 
                    size = 15, font='monospace', bold=True)
        
    def drawFlagButton(self):
        """
        Part of the drawing functionality, draws the box that will allow flagging of cells.
        """
        # draw the box
        drawRect(self.flagBoxLeft, self.flagBoxTop, self.flagBoxWidth, 
                self.flagBoxHeight, fill='orange')
        # draw a label
        drawLabel("Click to set flag cursor", self.flagBoxLeft + self.flagBoxWidth//2, 
                    self.flagBoxTop + self.flagBoxHeight//2, fill='white', 
                    size = 15, font='monospace', bold=True)
        
    def drawBoard(self):
        """
        This function draws the board and each individual cell, keeping in
        track any conditions each cell may be under (a potential bomb, flag, or normal count).
        """
        # iterate through the length of the board
        for row in range(self.rows):
            for col in range(self.cols):
                # debug feature to show all the mines
                # color = None
                # if (row, col) in self.mines:
                #     color = 'red'
                # # draw the cell 
                # self.drawCell(row, col, color)
                cell = (row, col)
                # draw the cell
                self.drawCell(cell)
                # draw the flag on the selected cell
                if cell in self.clickedCells and cell in self.flagCells:
                    self.drawFlag(cell)
                # draw a bomb if a mine is clicked without the flag setting
                elif cell in self.clickedCells and self.grid[row][col]:
                    self.drawBomb(cell)
                    self.gameOver = True
                # otherwise, get the count and draw the count of nearest mines
                elif cell in self.clickedCells and not self.grid[row][col]:
                    count = self.getNeighboringMineCount(cell)
                    # if the count is 0, floodfill the other neighbors that are 0
                    if count == 0:
                        self.drawFloodFill(cell)
                    else:   
                        self.drawCount(count, cell)
                        
    def drawFloodFill(self, cell, visited=None):
        """
        This function is called when a specific cell is clicked, and has a count of 0.
        Recursively checks all neighbors to see if any of them have a count of 0. 
        'clears' all the cells by drawing them as white, to make the game easier.
        Takes in a specific cell given by (row, col) as input.
        """
        # define a visited set
        if visited == None:
            visited = set()
        # break once you are back at a cell you already visited
        if cell in visited:
            return 
        # add the cell to the AI's knowledge
        self.getAICell(cell)
        # add the cell to the visited set
        visited.add(cell)
        # first, draw the current cell as white
        self.drawCell(cell, 'white')
        # get all the neighboring cells
        neighbors = self.getNeighboringCells(cell)
        # iterate through all neighbors
        for neighbor in neighbors:
            # recursively call if the neighbor is 0
            if self.getNeighboringMineCount(neighbor) == 0:
                self.drawFloodFill(neighbor, visited) 
            else:
                self.clickedCells.add(neighbor)
                self.getAICell(neighbor)
            
    def getNeighboringCells(self, cell):
        """
        Helper function that returns a list of all the neighbors of a cell.
        Takes in a specific given by (row, col) as input.
        """
        # iterate through all the cell's neighbors
        # add to list if valid cell
        neighbors = []
        deltaValues = [-1, 0, 1]
        for drow in deltaValues:
            for dcol in deltaValues:
                examinedRow = cell[0] + drow
                examinedCol = cell[1] + dcol
                if (0 <= examinedRow < self.rows) and (0 <= examinedCol < self.cols):
                        neighbors.append((examinedRow, examinedCol))
        return neighbors
        
    def drawBomb(self, cell):
        """
        This function draws the bomb when called.
        Takes in a specific cell given by (row, col) to draw the bomb on.
        """
        # get dimensions
        cellLeft, cellTop = self.getCellLeftTop(cell)
        cellWidth, cellHeight = self.getCellSize()
        self.bomb.draw(cellLeft, cellTop, cellWidth, cellHeight)
        
    def drawFlag(self, cell):
        """
        This function draws the flag when called. 
        Takes in a specific cell given by (row, col) to draw the flag on.
        """
        # get dimensions
        cellLeft, cellTop = self.getCellLeftTop(cell)
        cellWidth, cellHeight = self.getCellSize()
        self.flag.draw(cellLeft, cellTop, cellWidth, cellWidth)
        
    def drawBoardBorder(self):
        """
        This function draws the board border (part of drawing grid)
        """
        # draw board border with double thickness
        drawRect(self.boardLeft, self.boardTop, self.boardWidth, self.boardHeight,
           fill=None, border='white',
           borderWidth=2*self.cellBorderWidth)
    
    def drawCell(self, cell, fillColor=None):
        """
        This function draws a cell, given by row, col.
        Takes in optional parameter fillColor if specified.
        """
        # draw the cell with specified fill color
        cellLeft, cellTop = self.getCellLeftTop(cell)
        cellWidth, cellHeight = self.getCellSize()
        drawRect(cellLeft, cellTop, cellWidth, cellHeight,
                fill=fillColor, border='white',
                borderWidth=self.cellBorderWidth)
    
    def drawCount(self, count, cell):
        """
        This function draws the count of the neighboring mines on a particular cell, 
        given by (row, col).
        
        Takes in the count, row, and col of the cell as input.
        """
        # draw the counter in the center of the cell
        cellLeft, cellTop = self.getCellLeftTop(cell)
        cellWidth, cellHeight = self.getCellSize()
        drawLabel(count,
                  cellLeft + cellWidth//2,
                  cellTop + cellHeight//2,
                  size=20, fill='white')
        
    def getCellLeftTop(self, cell):
        """
        This helper function (used to draw the cell), gets the cell's left and top coords.
        """
        # get the cell's left, top position
        cellWidth, cellHeight = self.getCellSize()
        cellLeft = self.boardLeft + cell[1] * cellWidth
        cellTop = self.boardTop + cell[0] * cellHeight
        return (cellLeft, cellTop)

    def getCellSize(self):
        """
        This helper function (used to draw the cell), gets the cell's size.
        """
        # get the cell's size
        cellWidth = self.boardWidth / self.cols
        cellHeight = self.boardHeight / self.rows
        return (cellWidth, cellHeight)

    def getCell(self, mouseX, mouseY):
        """
        This function is called by main when a mouse click is pressed.
        Takes in a mouseX, mouseY coordinate as input and does the following:
            1) Gets the count of the neighboring cells that are mines
            2) Adds to the AI's knowledge if the cell is safe.
            3) Adds to the clicked cells set.
            4) If the cell is a flag, then add to the flagCells set
        """
        # get the cell given by a set of mouseX , mouseY) coordinates
        for row in range(self.rows):
            for col in range(self.cols):
                cell = (row, col)
                cellLeft, cellTop = self.getCellLeftTop(cell)
                cellWidth, cellHeight = self.getCellSize()
                # check if the mouse was clicked on the cell
                if ((cellLeft <= mouseX <= cellLeft + cellWidth) and 
                        (cellTop <= mouseY <= cellTop + cellHeight)):
                    count = self.getNeighboringMineCount(cell)
                    # add the cell to the AI's knowledge if it is a safe cell'
                    if (row, col) not in self.mines:
                        self.AI.addKnowledge(cell, count)
                    self.clickedCells.add(cell)
                    # if we are clicking a flag
                    if self.clickFlag:
                        self.flagCells.add(cell)
                        self.clickFlag = False
                        
    def getAICell(self, cell):
        """
        This function is called by main when the AI is trying to make a move.
        Takes in a row, col as input, and adds to the AI's knowledge based on the count of that cell.
        Adds to clicked cells
        """
        # find the cell
        for rowIndex in range(self.rows):
            for colIndex in range(self.cols):
                row, col = cell[0], cell[1]
                # if this is the cell
                if row == rowIndex and colIndex == col:
                    # get the count of the cell
                    count = self.getNeighboringMineCount(cell)
                    # add to the AI's knowledge
                    self.AI.addKnowledge((row, col), count)
                    # add to clicked cells
                    self.clickedCells.add((row, col))
                    break
    
    def checkWin(self):
        """
        This function is called by main to check if we have won the game
        Game is won either when the user has flagged all the mines OR if the user clicks on all the safe cells
        OR if the AI knows all the mines.
        """
        # return True if the win condition is satisfied
        if (self.cells - self.clickedCells == self.mines or 
            self.flagCells == self.mines):
            return True
        return False