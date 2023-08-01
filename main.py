from drawMinesweeper import *
from setup import *

def onAppStart(app):
    app.width = 800
    app.height = 800
    app.message = None
    app.gameOver = False
    app.minesweeper = Minesweeper(9, 9, 10)

def redrawAll(app):
    drawRect(0, 0, 800, 800, fill='green')
    drawLabel('MINESWEEPER', 400, 40, size=40)
    if app.message != None:
        drawLabel(app.message, 400, 90, size=40)
    app.minesweeper.drawGrid()

def onMousePress(app, mouseX, mouseY):
    if not app.gameOver:
        if (app.minesweeper.flagBoxLeft <= mouseX <= app.minesweeper.flagBoxLeft + app.minesweeper.flagBoxWidth
            and 
            app.minesweeper.flagBoxTop <= mouseY <= app.minesweeper.flagBoxTop + app.minesweeper.flagBoxHeight):
            app.minesweeper.clickFlag = True
        app.minesweeper.getCell(mouseX, mouseY)
        
def onStep(app):
    if app.minesweeper.gameOver:
        app.message = "Game Over"
        app.gameOver = True
    if app.minesweeper.checkWin():
        app.message = "Nice job!"
        app.gameOver = True

def onKeyPress(app, key):
    if key == 'r':
        app.width = 800
        app.height = 800
        app.message = None
        app.gameOver = False
        app.minesweeper = Minesweeper(9, 9, 10)

def main():
    runApp()

main()