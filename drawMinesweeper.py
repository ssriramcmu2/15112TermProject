"""
This file implements the gameplay for the Minesweeper game. 
Draws the game board and handles user actions. 
"""
from cmu_graphics import *
import random
from PIL import Image
import copy
from minesweeperAI import *
import time
import os, pathlib

class soundPlay:
    """
    This class plays the sound when called.
    Citations:
    1. Playing sound functionality taken from the Sound Demos
    2. MP3 File(s) for playing sounds taken from these links:
    https://elements.envato.com/explosion-MG2NHPK?
    https://soundspunos.com/nes/421-sounds-from-video-games-8-bit.html#google_vignette
    """
    def __init__(self, relativePath):
        # Convert to absolute path
        self.path = os.path.abspath(relativePath)
        # Get local file URL
        self.url = pathlib.Path(self.path).as_uri()
        self.sound = Sound(self.url)
    def play(self, restart=False):
        # play the sound
        self.sound.play(restart=restart)
    
class Background:
    """
    This class draws the background
    
    Citations: 
    1. Drawing image functionality learned from CMU Graphics Demos
    2. Got the image for the background from this url.
    https://www.vecteezy.com/vector-art/2948764-pixel-background-the-concept-of-games-background
    """
    def __init__(self):
        # open the image and save it in a class variable
        self.background = Image.open('grass.jpeg')
        self.background = CMUImage(self.background)
    
    def draw(self, left, top, width, height):
        # draw the image
        drawImage(self.background,left,top,width=width,height=height)

class Bomb:
    """
    This class initializes the bomb that will be drawn on the board.
    Called when the user clicks on a bomb cell.
    
    Citations: 
    1. Drawing image functionality learned from CMU Graphics Demos
    2. Got the image for the bomb from this url.
    https://www.pngegg.com/en/png-cbukd
    """
    def __init__(self):
        # open the image and save it in a class variable
        self.bomb = Image.open('bomb.png')
        self.bomb = CMUImage(self.bomb)
    
    def draw(self, left, top, width, height):
        # draw the image
        drawImage(self.bomb,left,top,width=width,height=height)
        
class BombGif:
    """
    This class creates an exploding bomb that will be drawn on the board.
    Called as soon as the user clicks on a bomb.
    
    Citations: 
    1. Used the CMU Graphics Demo Folder Provided to Draw GIF's
    2. Got the gif for the bomb from this url.
    https://tenor.com/view/bomb-joypixels-bombing-explode-blast-gif-17542148
    """
    def __init__(self):
        # Load the gif
        myGif = Image.open('bomb.gif')
        self.spriteList = []
        # seek all the frame of the gif and append
        for frame in range(myGif.n_frames):
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//2, myGif.size[1]//2))
            fr = fr.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            fr = CMUImage(fr)
            self.spriteList.append(fr)

        # Fix for broken transparency on frame 0
        self.spriteList.pop(0)
        self.frameIndex = 0
        self.steps = 0
    
    def draw(self, left, top, width, height):
        drawImage(self.spriteList[self.frameIndex],
                left, top, width=width, height=height)
    
    def doStep(self):
        self.steps += 1
        if self.steps % 3 == 0:
            self.frameIndex = (self.frameIndex + 1) % (len(self.spriteList))

class Flag:
    """
    This class initializes the flag that will be drawn on the board.
    Called when the user clicks on a cell with the flag cursor active.
    
    Citations: 
    1. Drawing image functionality learned from CMU Graphics Demos
    2. Got the image for the flag from this url.
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
    
    Citations: 
    1. Drawing a 2D Grid was taken from chapter 5, section 3.2 in CS Academy
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
        self.floodedCells = set()
        self.clearedCells = set()
        # initialize the bomb 
        self.bomb = Bomb()
        self.bombGif = BombGif()
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
        # first list coords
        self.firstCell = None
        self.initialSafes = set()
        self.firstFlood = False
        # save coords
        self.saveLeft = 15
        self.saveTop = 700
        self.loadLeft = self.boardLeft + self.boardWidth + 40
        self.loadTop = 700
        self.saveWidth = 100
        # sound
        self.bombSound = soundPlay('explosion.mp3')
        self.beepSound = soundPlay('score.mp3')
        self.soundPlay = True
        # score
        self.timer = 0
        # max AI moves
        self.maxAIMoves = None
        self.mode = None
    
    def stepScore(self):
        """
        This function is called by main. 
        Increments the score
        """
        if not self.gameOver:
            self.timer += 1
    
    def getScore(self):
        """
        This function return the final score
        """
        return self.timer
        
    def setBoard(self):
        """
        This function generates a board with mines, given the first cell was 
        clicked.
        """
        # get the neighbors of the first safe cell
        neighbors = self.getNeighboringCells(self.firstCell)
        # add the initial cell and all its neighbors to a initial safe set
        self.initialSafes.add(self.firstCell)
        for neighbor in neighbors:
            self.initialSafes.add(neighbor)
        # randomly assign mines outside of the safe cells.
        self.assignMines()
        # indicate that we want to draw a floodfill from the first click
        self.drawFloodFill(self.firstCell)
    
    def assignMines(self):
        """
        This function randomly assigns the designated number of mines on the 
        grid.
        Stores them in the self.mines set.
        """     
        # randomly place 10 mines on the grid
        while len(self.mines) != self.numberOfMines:
            # add mine row and col
            mineRow = random.randrange(self.rows)
            mineCol = random.randrange(self.cols)
            # add to mine set and set value to True
            if ((mineRow, mineCol) not in self.mines and 
                (mineRow, mineCol) not in self.initialSafes):
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
        for examinedRow in range(cell[0] - 1, cell[0] + 2):
            for examinedCol in range(cell[1] - 1, cell[1] + 2):
                if ((0 <= examinedRow < self.rows) and 
                    (0 <= examinedCol < self.cols)):
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
        self.drawSaveButton()
        self.drawLoadButton()
    
    def drawAIButton(self):
        """
        Part of the drawing functionality, draws the box that will make 
        an AI Move.
        """
        # draw the box
        drawRect(self.AIBoxLeft, self.AIBoxTop, self.AIBoxWidth, 
                 self.AIBoxHeight, fill='green')
        # draw a label
        drawLabel("Click to make an AI Move!", 
                  self.AIBoxLeft + self.AIBoxWidth//2, 
                    self.AIBoxTop + self.AIBoxHeight//2, fill='white', 
                    size = 20, font='fantasy', bold=True)
        
    
    def drawSaveButton(self):
        """
        Part of the drawing functionality, draws the box that will save 
        an AI Move.
        """
        # draw the box
        drawRect(self.saveLeft, self.saveTop, self.saveWidth, self.AIBoxHeight, fill='white')
        # # draw a label
        drawLabel("Save", 15 + 100//2, 700 + self.AIBoxHeight//2, fill='black', 
                     size = 25, font='fantasy', bold=True)
    
    def drawLoadButton(self):
        """
        Part of the drawing functionality, draws the box that will Load 
        an AI Move.
        """
        # draw the box
        drawRect(self.loadLeft, self.loadTop, self.saveWidth, 
                 self.AIBoxHeight, fill='white')
        # # draw a label
        drawLabel("Load", 
                  self.loadLeft + self.saveWidth//2, 
                    self.loadTop + self.AIBoxHeight//2, fill='black', 
                    size = 25, font='fantasy', bold=True)
           
    def drawFlagButton(self):
        """
        Part of the drawing functionality, draws the box that will allow 
        flagging of cells.
        """
        # draw the box
        drawRect(self.flagBoxLeft, self.flagBoxTop, self.flagBoxWidth, 
                self.flagBoxHeight, fill='orange')
        # draw a label
        drawLabel("Click to set flag cursor", 
                  self.flagBoxLeft + self.flagBoxWidth//2, 
                    self.flagBoxTop + self.flagBoxHeight//2, fill='black', 
                    size = 20, font='fantasy', bold=True)
        
    def drawBoard(self):
        """
        This function draws the board and each individual cell, keeping in
        track any conditions each cell may be under 
        (a potential bomb, flag, or normal count).
        """
        # iterate through the length of the board
        for row in range(self.rows):
            for col in range(self.cols):
                cell = (row, col)
                # draw the cell in corresponding color
                if cell in self.floodedCells:
                    self.drawCell(cell, 'lightGreen')
                else:
                    self.drawCell(cell)
                # draw the flag on the selected cell
                if cell in self.flagCells and cell not in self.clearedCells:
                    self.drawFlag(cell)
                # draw a bomb if a mine is clicked without the flag setting
                elif (cell in self.clickedCells and self.grid[row][col] and
                      cell not in self.flagCells):
                    self.gameOver = True
                    self.drawBombGif(cell)
                    self.drawAllBombs()
                    if self.soundPlay:
                        self.bombSound.play()
                        self.soundPlay = False
                    # self.drawBomb(cell)
                # otherwise, get the count and draw the count of nearest mines
                elif cell in self.clearedCells and not self.grid[row][col]:
                    count = self.getNeighboringMineCount(cell)
                    # if the count is 0, floodfill the other neighbors 
                    # that are 0
                    if count == 0:
                        self.drawFloodFill(cell)
                    else:   
                        self.drawCount(count, cell)
    
    def drawAllBombs(self):
        """
        This function draws all the bombs in red if a mine is clicked
        """
        for mine in self.mines:
            # if the game is over, draw all the mines
            # change cell color to red
            if mine not in self.clickedCells:
                self.drawCell(mine, 'red')
                self.drawBomb(mine)
                        
    def drawFloodFill(self, cell):
        """
        This function is called when a specific cell is clicked, 
        and has a count of 0.
        Recursively checks all neighbors to see if any of them have a 
        count of 0. 
        'clears' all the cells by drawing them as grey, to make the game 
        easier.
        Takes in a specific cell given by (row, col) as input.
        """
        # if the cell is in the flooded set, return without doing anything.
        if cell in self.floodedCells:
            return
        # add the cell to the AI's knowledge
        self.getAICell(cell)
        # if the cell is 0, add to clicked and break
        if self.getNeighboringMineCount(cell) != 0:
            self.clickedCells.add(cell)
            return
        # add the cell to the flooded set
        self.floodedCells.add(cell)
        # add cell to cleared
        self.clearedCells.add(cell)
        # get all the neighboring cells
        neighbors = self.getNeighboringCells(cell)
        # iterate through all neighbors
        for neighbor in neighbors:
            # recursively call on all the neighbors
            self.drawFloodFill(neighbor)
            
    def getNeighboringCells(self, cell):
        """
        Helper function that returns a list of all the neighbors of a cell.
        Takes in a specific given by (row, col) as input.
        """
        # iterate through all the cell's neighbors
        # add to list if valid cell
        neighbors = []
        # iterate through all possible combinations of drow and col
        for examinedRow in range(cell[0] - 1, cell[0] + 2):
            for examinedCol in range(cell[1] - 1, cell[1] + 2):
                # check if the neighbor is a valid neighbor and append to list
                if ((0 <= examinedRow < self.rows) 
                    and (0 <= examinedCol < self.cols)):
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
    
    def drawBombGif(self, cell):
        """
        This function draws the bomb gif when called.
        Takes in a specific cell given by (row, col) to draw the bomb on.
        """
        # get dimensions
        cellLeft, cellTop = self.getCellLeftTop(cell)
        cellWidth, cellHeight = self.getCellSize()
        self.bombGif.draw(cellLeft, cellTop, cellWidth, cellHeight)
    
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
        drawRect(self.boardLeft, self.boardTop, self.boardWidth, 
                 self.boardHeight,
           fill=None, border ='black',
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
                fill=fillColor, border='black',
                borderWidth=self.cellBorderWidth)
    
    def drawCount(self, count, cell):
        """
        This function draws the count of the neighboring mines on a 
        particular cell, given by (row, col).
        
        Takes in the count, row, and col of the cell as input.
        """
        # draw the counter in the center of the cell
        cellLeft, cellTop = self.getCellLeftTop(cell)
        cellWidth, cellHeight = self.getCellSize()
        drawLabel(count,
                  cellLeft + cellWidth//2,
                  cellTop + cellHeight//2,
                  size=20, fill='white', bold=True)
        
    def getCellLeftTop(self, cell):
        """
        This helper function (used to draw the cell), gets the cell's left and 
        top coords.
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
                    # check if the click was the first click
                    if self.firstCell == None:
                        self.firstCell = cell
                        # add to the AI's knowledge
                        self.AI.addKnowledge((row, col), 0)
                        # add to clicked and cleared cells
                        self.clickedCells.add((row, col))
                        self.clearedCells.add((row, col))
                        self.setBoard()
                        self.beepSound.play(restart=True)
                    else:
                        count = self.getNeighboringMineCount(cell)
                        # add the cell to the AI's knowledge if it is a 
                        # safe cell'
                        if (row, col) not in self.mines:
                            self.AI.addKnowledge(cell, count)
                        self.clickedCells.add(cell)
                        if cell not in self.mines and not self.clickFlag:
                            self.beepSound.play(restart=True)
                        # remove a flag from the cell if it is clicked
                        if self.clickFlag and cell in self.flagCells:
                            self.flagCells.remove(cell)
                            self.clickedCells.remove(cell)
                            self.clickFlag = False
                        # if we are clicking a flag
                        elif self.clickFlag and cell not in self.clearedCells:
                            self.flagCells.add(cell)
                            self.clickFlag = False
                        elif cell in self.flagCells and not self.clickFlag:
                            continue
                        else:
                            self.clearedCells.add((row, col))
                        
    def getAICell(self, cell):
        """
        This function is called by main when the AI is trying to make a move.
        Takes in a row, col as input, and adds to the AI's knowledge based on 
        the count of that cell.
        Adds to clicked cells.
        """
        # find the cell
        for rowIndex in range(self.rows):
            for colIndex in range(self.cols):
                row, col = cell[0], cell[1]
                # if this is the cell
                if row == rowIndex and colIndex == col:
                    if cell not in self.mines and not self.clickFlag:
                        self.beepSound.play(restart=True)
                    # check if the click was the first click
                    if self.firstCell == None:
                        self.firstCell = cell
                        # add to the AI's knowledge
                        self.AI.addKnowledge((row, col), 0)
                        # add to clicked and cleared cells
                        self.clickedCells.add((row, col))
                        self.clearedCells.add((row, col))
                        self.setBoard()
                    else:
                        # get the count of the cell
                        count = self.getNeighboringMineCount(cell)
                        # add to the AI's knowledge
                        self.AI.addKnowledge((row, col), count)
                        # add to clicked and cleared cells
                        self.clickedCells.add((row, col))
                        self.clearedCells.add((row, col))
                    break
    
    def checkWin(self):
        """
        This function is called by main to check if we have won the game
        Game is won if the user clicks on all the safe cells.
        """
        # return True if the win condition is satisfied
        if self.cells - self.clickedCells == set() and not self.gameOver:
            return True
        return False