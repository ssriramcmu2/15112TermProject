"""
Main code file to run the game.
"""
from drawMinesweeper import *
import pickle

def onAppStart(app):
    app.width = 800
    app.height = 800
    app.message = "Press r to restart!"
    app.gameOver = False
    app.minesweeper = Minesweeper(9, 9, 10)
    app.backgroundObj = Background()
    app.gameStart = False 
    app.textSize = 60
    app.textChange = 10
    app.AIClicked = False
    app.stepsPerSecond = 2
    app.textShown = True
    app.messageSize = 30
    app.AIGoingRandomMove = False
    app.setMaxShapeCount(5000)
    app.pickleFilename = "checkpoint.pkl"
    
# welcome screen

def welcome_redrawAll(app):
    # draw grass background
    app.backgroundObj.draw(0, 0, app.width, app.height)
    # draw 9 lines vertically
    for i in range(9):
        drawLine(app.width/9 + i * 100, 0, app.width/9 + i * 100, 
                    app.height, lineWidth =3, fill='green')
    # draw 9 lines horizontally
    for i in range(9):
        drawLine(0, app.height/9 + i * 100, app.width, app.height/9 + i * 100,
                lineWidth =3, fill='green')
    # draw the label
    drawLabel("Mine Smarter!", app.width/2, 120, size = 75, font='monospace', 
              fill='green', bold = True)
    # draw a flashing text symbol telling the user to press space
    if app.textShown:
        drawLabel("Press space to begin!", app.width/2 , app.height-200, 
                    size = app.textSize, font='monospace', fill='green', 
                    bold=True)

def welcome_onKeyPress(app, key):
    if key == 'space':
        app.gameStart = True
        setActiveScreen('game')

def welcome_onStep(app):
    # if app.textSize == 60 or app.textSize == 20:
    #     app.textChange *= -1
    # app.textSize = app.textSize + app.textChange
    app.textShown = not app.textShown
    

# gameplay

def game_redrawAll(app):
    # if the AI is about to make a random move, draw confirmation message on 
    # the screen
    if app.AIGoingRandomMove:
        game_drawAIRandomConfirmation(app)
    # otherwise, draw the game board to continue
    else:
        # draw grass background
        app.backgroundObj.draw(0, 0, app.width, app.height)
        drawLabel("Mine Smarter!", app.width/2, 40, size = 60, font='monospace', 
                fill='green', bold = True)
        if app.message != None:
            drawLabel(app.message, app.width/2, 100, size = app.messageSize, 
                      font='monospace', 
                fill='black', bold = True)
        app.minesweeper.drawGrid()

def game_drawAIRandomConfirmation(app):
    """
    This is part of the functionality that tells the user if the AI is going 
    to make a random move
    Draws a confirmation screen
    """
    # draw grass background
    app.backgroundObj.draw(0, 0, app.width, app.height)
    # draw confirmation text
    drawLabel("ALERT", app.width//2, 100, fill='red', size=40, 
              font='monospace', bold = True)
    drawLabel("Heads up! AI is about to make a random move.", 
              app.width//2, app.height//2 - 80, 
              fill='black', size=25, font='monospace', bold = True)
    drawLabel("Press 'y' to continue, 'n' to make your own move", 
              app.width//2, app.height//2 + 80, 
            fill='black', size=25, font='monospace', bold = True)
        

def game_onMousePress(app, mouseX, mouseY):
    # check if the mouse click is in any target zone
    # set the appropriate variable to True (referenced in OnStep)
    if not app.gameOver:
        
        if (app.minesweeper.saveLeft <= mouseX <=
            app.minesweeper.saveLeft + app.minesweeper.saveWidth
            and 
            app.minesweeper.saveTop <= mouseY <= 
            app.minesweeper.saveTop + app.minesweeper.AIBoxHeight):
            # Save the minesweeper state with the checkpoint file using pickle
            with open(app.pickleFilename, 'wb') as file:
                pickle.dump(app.minesweeper, file)
            app.message = "Game saved."


        elif (app.minesweeper.loadLeft <= mouseX <=
            app.minesweeper.loadLeft + app.minesweeper.saveWidth
            and 
            app.minesweeper.loadTop <= mouseY <= 
            app.minesweeper.loadTop + app.minesweeper.AIBoxHeight):
            # Load the minesweeper state back from the saved file using pickle
            with open(app.pickleFilename, 'rb') as file:
                app.minesweeper = pickle.load(file)
            app.message = "Game loaded."
    
        elif (app.minesweeper.flagBoxLeft <= mouseX <=
            app.minesweeper.flagBoxLeft + app.minesweeper.flagBoxWidth
            and 
            app.minesweeper.flagBoxTop <= mouseY <= 
            app.minesweeper.flagBoxTop + app.minesweeper.flagBoxHeight):
            # we are clicking on a flag, so set the cursor in the game 
            # to be a flag cursor
            app.minesweeper.clickFlag = True
            
        elif (app.minesweeper.AIBoxLeft <= mouseX <= 
            app.minesweeper.AIBoxLeft + app.minesweeper.AIBoxWidth
            and 
            app.minesweeper.AIBoxTop <= mouseY <= 
            app.minesweeper.AIBoxTop + app.minesweeper.AIBoxHeight):
            # user is trying to make an AI move. 
            # start wth trying to make a safe move
            move = game_makeAISafeMove(app)
            if move == None:
                # if the move is none, that means the AI could not make a 
                # safe move (doesn't know enough information)
                # the AI has to make a random move, but the user should be 
                # alerted that the AI is going to make a random move.
                # indicate that we are going to make a random move
                app.AIGoingRandomMove = True
            else:
                # get the cell
                app.minesweeper.getAICell(move)
        
        else:
            # get the cell given by the click (if exists)
            app.minesweeper.getCell(mouseX, mouseY)
            app.message = 'Press r to restart the game.'
        
def game_onStep(app):
    # checks the game conditions every step
    # increase the steps per second to make the game faster
    app.stepsPerSecond = 1000
    if app.minesweeper.gameOver:
        app.minesweeper.bombGif.doStep()
        app.message = "Game Over! Press 'r' to restart."
        app.gameOver = True
    if app.minesweeper.checkWin() and app.minesweeper.firstCell != None:
        # if the user won, stop all gameplay.
        app.message = "You won! Press 'r' to restart."
        app.gameOver = True

def game_makeAISafeMove(app):
    # if the game is trying to make an AI safe move, call it
    # get the cell given by the AI's safe move.
    AIcell = app.minesweeper.AI.makeSafeMove()
    return AIcell

def game_makeAIRandomMove(app):
    # make random move only returns a valid random move (that is, not a 
    # random move where the AI knows a mine is there.)
    AIcell = app.minesweeper.AI.makeRandomMove()
    return AIcell
        
def game_onKeyPress(app, key):
    # restart the game if the user presses r
    if key == 'r':
        app.width = 800
        app.height = 800
        app.message = "Press r to restart the game."
        app.gameOver = False
        app.minesweeper = Minesweeper(9, 9, 10)
    # user confirms that they want to make a random move
    if key == 'y' and app.AIGoingRandomMove:
        # make random move only returns a valid random move (that is, 
        # not a random move where the AI knows a mine is there.)
        move = game_makeAIRandomMove(app)
        if move == None:
            # if the move is still none, that means that the game has 
            # been won (alll the cells that are available are the AI's 
            # known mines)
            # stop gameplay
            # check using the board if the game has been won
            if app.minesweeper.checkWin():
                # if the user won, stop all gameplay.
                app.message = "Nice job! Press 'r' to restart."
                app.gameOver = True
        else:
            # otherwise, get the random move
            app.minesweeper.getAICell(move)
        # stop the move
        app.AIGoingRandomMove = False
    elif key == 'n' and app.AIGoingRandomMove:
        # don't let the AI make a random move
        app.AIGoingRandomMove = False

def main():
    runAppWithScreens(initialScreen='welcome')

main()