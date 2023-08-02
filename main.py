from drawMinesweeper import *
from setup import *

def onAppStart(app):
    app.width = 800
    app.height = 800
    app.message = None
    app.gameOver = False
    app.minesweeper = Minesweeper(9, 9, 10)
    app.AIClicked = False
    
# welcome screen

def welcome_redrawAll(app):
    drawLabel("Mine Smarter!", app.width/2, app.height/2, size = 24)

def welcome_onKeyPress(app, key):
    if key == 'space':
        setActiveScreen('game')

# gameplay

def game_redrawAll(app):
    drawRect(0, 0, 800, 800, fill='green')
    drawLabel('MINESWEEPER', 400, 40, size=40)
    if app.message != None:
        drawLabel(app.message, 400, 90, size=40)
    app.minesweeper.drawGrid()

def game_onMousePress(app, mouseX, mouseY):
    if not app.gameOver:
        if (app.minesweeper.flagBoxLeft <= mouseX <= app.minesweeper.flagBoxLeft + app.minesweeper.flagBoxWidth
            and 
            app.minesweeper.flagBoxTop <= mouseY <= app.minesweeper.flagBoxTop + app.minesweeper.flagBoxHeight):
            app.minesweeper.clickFlag = True
        if (app.minesweeper.AIBoxLeft <= mouseX <= app.minesweeper.AIBoxLeft + app.minesweeper.AIBoxWidth
            and 
            app.minesweeper.AIBoxTop <= mouseY <= app.minesweeper.AIBoxTop + app.minesweeper.AIBoxHeight):
            app.AIClicked = True
        app.minesweeper.getCell(mouseX, mouseY)
        
def game_onStep(app):
    if app.minesweeper.gameOver:
        app.message = "Game Over"
        app.gameOver = True
    if app.minesweeper.checkWin():
        app.message = "Nice job!"
        app.gameOver = True
    if app.AIClicked:
        AIcell = app.minesweeper.AI.make_safe_move()
        if AIcell == None:
            AIcell = app.minesweeper.AI.make_random_move()
            if AIcell == None:
                app.message = "Nice job!"
                app.gameOver = True
        if AIcell != None: 
            app.minesweeper.getAICell(AIcell[0], AIcell[1])
        app.AIClicked = False

def game_onKeyPress(app, key):
    if key == 'r' and app.gameOver:
        app.width = 800
        app.height = 800
        app.message = None
        app.gameOver = False
        app.minesweeper = Minesweeper(9, 9, 10)

def main():
    runAppWithScreens(initialScreen='welcome')

main()