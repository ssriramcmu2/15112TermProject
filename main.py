"""
Main code file to run the game.
"""
from drawMinesweeper import *
import pickle

def onAppStart(app):
    app.maxAIMoves = None
    app.mode = 'Unlimited AI'
    restartApp(app)

def restartApp(app):
    app.width = 800
    app.height = 800
    app.message = "Press r to restart the game."
    app.gameOver = False
    # define minesweeper object
    app.minesweeper = Minesweeper(9, 9, 10)
    app.backgroundObj = Background()
    # text params
    app.textSize = 60
    app.textChange = 10
    app.AIClicked = False
    app.stepsPerSecond = 2
    app.textShown = True
    app.messageSize = 30
    app.AIGoingRandomMove = False
    app.setMaxShapeCount(5000)
    app.pickleFilename = "checkpoint.pkl"
    app.steps = 0
    # scores list
    scoreFile = open("highScores.txt", "r")
    scoreData = scoreFile.read()
    app.scores = scoreData.splitlines()
    # convert the scores from strings to integers
    for scoreIndex in range(len(app.scores)):
        app.scores[scoreIndex] = int(app.scores[scoreIndex])
    scoreFile.close()
    app.scoreWritten = False
    # coords for difficulty boxes
    app.unlimitedLeft = 75
    app.limitedLeft = 300
    app.noLeft = 525
    app.AIClicks = 0
    # back button coords
    app.backCoord = 20

# helper functions

def drawBackButton(app):
    drawRect(app.backCoord, app.backCoord, 75, 75, fill='yellow', 
             border='black')
    drawLabel("Back", app.backCoord + 75//2, 
              app.backCoord + 75//2, font='fantasy', fill='black', 
              size=20, bold=True)
    
# welcome screen

def welcome_redrawAll(app):
    # draw grass background
    app.backgroundObj.draw(0, 0, app.width, app.height)
    # draw 9 lines vertically
    for i in range(9):
        drawLine(app.width/9 + i * 100, 0, app.width/9 + i * 100, 
                    app.height, lineWidth =1, fill='green')
    # draw 9 lines horizontally
    for i in range(9):
        drawLine(0, app.height/9 + i * 100, app.width, app.height/9 + i * 100,
                lineWidth =1, fill='green')
    # draw the label
    drawLabel("Mine Smarter!", app.width/2, 120, size = 100, font='fantasy', 
              fill='red', bold = True)
    # draw a flashing text symbol telling the user to press space
    if app.textShown:
        drawLabel("Press space to begin!", app.width//2 , app.height-200, 
                    size = app.textSize, font='fantasy', fill='black', 
                    bold=True)
    drawLabel(f"Mode = {app.mode}", app.width/2, 240, size=35, 
              font='fantasy', fill='black', bold=True)
    # draw the difficulty boxes
    welcome_drawUnlimitedBox(app)
    welcome_drawLimitedBox(app)
    welcome_drawNoAIBox(app)

def welcome_drawUnlimitedBox(app):
    """
    This function draws a box for selecting unlimited AI moves
    """
    drawRect(app.unlimitedLeft, app.height//2 - 100, 175, 150, fill='green', 
             border='black')
    drawLabel("Unlimited AI Moves", app.unlimitedLeft + 175//2, 
              (app.height//2-100)+150//2, font='fantasy', fill='black', 
              size=18, bold=True)

def welcome_drawLimitedBox(app):
    """
    This function draws a box for selecting limited AI moves
    """
    drawRect(app.limitedLeft, app.height//2 - 100, 175, 150, fill='orange', 
             border='black')
    drawLabel("10 AI Moves", app.limitedLeft + 175//2, 
              (app.height//2-100)+150//2, font='fantasy', fill='black', 
              size=20, bold=True)

def welcome_drawNoAIBox(app):
    """
    This function draws a box for selecting no AI moves
    """
    drawRect(app.noLeft, app.height//2 - 100, 175, 150, fill='red', 
             border='black')
    drawLabel("No AI Moves", app.noLeft + 175//2, 
              (app.height//2-100)+150//2, font='fantasy', fill='black',
              size=20, bold=True)

def welcome_onMousePress(app, mouseX, mouseY):
    # determine max amount of AI Moves
    if (app.unlimitedLeft <= mouseX <=
            app.unlimitedLeft + 150
            and 
            app.height//2 - 100 <= mouseY <= 
            app.height//2 - 100 + 150):
        app.maxAIMoves = None
        app.mode = 'Unlimited AI'
        
    elif (app.limitedLeft <= mouseX <=
            app.limitedLeft + 150
            and 
            app.height//2 - 100 <= mouseY <= 
            app.height//2 - 100 + 150):
        app.maxAIMoves = 10
        app.mode = 'Limited AI'
        
    elif (app.noLeft <= mouseX <=
            app.noLeft + 150
            and 
            app.height//2 - 100 <= mouseY <= 
            app.height//2 - 100 + 150):
        app.maxAIMoves = 0
        app.mode = 'No AI'
    

def welcome_onKeyPress(app, key):
    if key == 'space':
        restartApp(app)
        app.minesweeper.maxAIMoves = app.maxAIMoves
        app.minesweeper.mode = app.mode
        setActiveScreen('game')
        
        

def welcome_onStep(app):
    app.stepsPerSecond = 2
    # toggle text
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
        drawLabel("Mine Smarter!", app.width/2, 40, size = 70, font='fantasy', 
                fill='red', bold = True)
        if app.message != None:
            drawLabel(app.message, app.width/2, 90, size = app.messageSize, 
                      font='fantasy', 
                fill='black', bold = True)
        app.minesweeper.drawGrid()
        drawLabel(f"Time: {app.minesweeper.getScore()} sec.", app.width/2, 
                  125, size=app.messageSize, font='fantasy', fill='black', 
                  bold = True)
        game_drawHighScores(app)
        drawBackButton(app)
        game_drawMaxAIBox(app)

def game_drawMaxAIBox(app):
    """
    This function draws in the top right corner the max AI moves
    """
    maxMoves = None
    if isinstance(app.minesweeper.maxAIMoves, int):
        maxMoves = str(app.minesweeper.maxAIMoves - app.AIClicks)
    # draw rect
    drawRect(app.width-170, 40, 160, 100, fill='white', border='black')
    # draw the number of moves left
    drawLabel(f"AI Moves Left: {maxMoves}", (app.width-170) + 160//2, 
              40 + 100//2, fill='black', font='fantasy', size=17, bold=True)

def game_drawHighScores(app):
    """
    This function prints the top 10 scores of the game
    """
    drawLabel("Times:", 70, 150, 
              size=40, font='fantasy',
              fill='black', bold=True)
    # draw the top 5 count from app.scores
    count = 0
    for scoreIndex in range(len(app.scores)):
        score = sorted(app.scores)[scoreIndex]
        # can't have a score that's 0
        if score == 0:
            continue
        drawLabel(str(score) + " sec.", 70, 150 + 50 * (scoreIndex), 
                  size = 40, fill = 'black', font='fantasy', bold=True)
        count += 1
        if count >= 10:
            break
    

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
              font='fantasy', bold = True)
    drawLabel("Heads up! AI is about to make a random move.", 
              app.width//2, app.height//2 - 80, 
              fill='black', size=25, font='fantasy', bold = True)
    drawLabel("Press 'y' to continue, 'n' to make your own move", 
              app.width//2, app.height//2 + 80, 
            fill='black', size=25, font='fantasy', bold = True)
        

def game_onMousePress(app, mouseX, mouseY):
    """
    Citations: 
    1. Storing class objects with pickle: 
    https://docs.python.org/3/library/pickle.html
    """
    # go back if the back button was clicked
    if (app.backCoord <= mouseX <= app.backCoord + 75
        and 
        app.backCoord <= mouseY <= app.backCoord + 75):
        setActiveScreen('welcome')
        
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
                # sound files can't be saved, so temporarily set to None
                app.minesweeper.bombSound = None
                app.minesweeper.beepSound = None       
                pickle.dump(app.minesweeper, file)
                # set them back
                app.minesweeper.bombSound = soundPlay('explosion.mp3')
                app.minesweeper.beepSound = soundPlay('score.mp3')
            app.message = "Game saved."


        elif (app.minesweeper.loadLeft <= mouseX <=
            app.minesweeper.loadLeft + app.minesweeper.saveWidth
            and 
            app.minesweeper.loadTop <= mouseY <= 
            app.minesweeper.loadTop + app.minesweeper.AIBoxHeight):
            # Load the minesweeper state back from the saved file using pickle
            with open(app.pickleFilename, 'rb') as file:
                app.minesweeper = pickle.load(file)
                # reset the sound files back to original
                app.minesweeper.bombSound = soundPlay('explosion.mp3')
                app.minesweeper.beepSound = soundPlay('score.mp3')
            app.message = "Game loaded."
    
        elif (app.minesweeper.flagBoxLeft <= mouseX <=
            app.minesweeper.flagBoxLeft + app.minesweeper.flagBoxWidth
            and 
            app.minesweeper.flagBoxTop <= mouseY <= 
            app.minesweeper.flagBoxTop + app.minesweeper.flagBoxHeight):
            # we are clicking on a flag, so set the cursor in the game 
            # to be a flag cursor
            app.minesweeper.clickFlag = not app.minesweeper.clickFlag 
            if app.minesweeper.clickFlag:
                app.message = 'Flag Cursor ACTIVE'
            else:
                app.message = 'Press r to restart the game.'
            
            
        elif (app.minesweeper.AIBoxLeft <= mouseX <= 
            app.minesweeper.AIBoxLeft + app.minesweeper.AIBoxWidth
            and 
            app.minesweeper.AIBoxTop <= mouseY <= 
            app.minesweeper.AIBoxTop + app.minesweeper.AIBoxHeight):
            # user is trying to make an AI move. 
            if (app.minesweeper.maxAIMoves == None 
                or app.AIClicks < app.minesweeper.maxAIMoves):
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
                app.AIClicks += 1
            else:
                app.message = 'Reached max AI Moves!'
        
        else:
            # get the cell given by the click (if exists)
            app.minesweeper.getCell(mouseX, mouseY)
            app.message = 'Press r to restart the game.'
        
def game_onStep(app):
    # checks the game conditions every step
    # increase the steps per second to make the game faster
    app.stepsPerSecond = 1000
    if app.minesweeper.firstCell != None:
        app.steps += 1
        if app.steps % 40 == 0:
            app.minesweeper.stepScore()
    if app.minesweeper.gameOver:
        app.minesweeper.bombGif.doStep()
        app.message = "Game Over! Press 'r' to restart."
        app.gameOver = True
    if app.minesweeper.checkWin() and app.minesweeper.firstCell != None:
        # if the user won, stop all gameplay.
        app.message = "You won! Press 'r' to restart."
        # add scores to the score list and save
        # only add scores for modes other than unlimited AI
        if not app.scoreWritten and app.minesweeper.maxAIMoves != None:
            app.scores.append(app.minesweeper.timer)
            with open('highScores.txt','w') as file:
                for score in app.scores:
                    file.write((str(score) + '\n'))
            app.scoreWritten = True
            file.close()
        app.minesweeper.gameOver = True
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
        restartApp(app)
        app.minesweeper.maxAIMoves = app.maxAIMoves
        app.minesweeper.mode = app.mode
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