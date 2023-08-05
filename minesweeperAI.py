import random

"""   
Citations: (Used these sources to get an idea on how to incorporate AI into the project)
    http://nebula.wsimg.com/8ecbfd87953e91c5b969c020b63bfc5c?AccessKeyId=1AF96B41F86A131EDF19&disposition=0&alloworigin=1
    https://github.com/aditya1702/Machine-Learning-and-Data-Science/blob/master/Minesweeper%20AI%20Bot/Minesweeper.pdf
    https://cs50.harvard.edu/extension/ai/2020/spring/projects/1/minesweeper/
"""

class Knowledge:
    """
    Knowledge statement about a Minesweeper game that consists of a 
    set of board cells and the count of those cells that are mines. 
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __repr__(self):
        return f"{self.cells} = {self.count}"

    def knownMines(self):
        """
        Returns a set of all cells that are known to be mines
        """
        # if the amount of cells in the statement equals the count, then all the cells are mines
        if self.count == 0 or not len(self.cells):
            return None
        if len(self.cells) == self.count:
            return self.cells
        else:
            return None

    def knownSafes(self):
        """
        Returns a set of all cells that are known to be safe
        """
        # if the count is 0, then all the cells are safe.
        if self.count == 0:
            return self.cells
        else:
            return None

    def markMine(self, cell):
        """
        Marks a cell as a mine in a knowledge statement.
        Decrement the count of the cells in the statement that are mines. 
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def markSafe(self, cell):
        """
        Marks a cell as safe in a knowledge statement.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
    """
    This class represents the AI player, which will make smart moves as the game progresses and new Knowledge is attained.
    
    """

    def __init__(self, rows, cols):
        
        # Keep track of which cells have been clicked on
        self.movesMade = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of knowledge statements - AI's knowledge base
        self.knowledge = []
        
        # Set initial rows and cols
        self.rows = rows
        self.cols = cols

    def addKnowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        
        Follows these steps:
            1. Marks the cell as a move that has been made
            2. Marks the cell as safe
            3. Adds new knowledge statements to knowledge base
            4. Marks any cells as safe or mines in knowledge base
            5. Optimizes knowledge by removing subsets.
            6. Marks cells as safes or mines in knowledge base.
        """

        # Step 1: Mark the cell as a move that has been made
        self.movesMade.add(cell)

        # Step 2: Mark the cell as safe
        self.markSafe(cell)

        # Step 3: Add new knowledge statements to knowledge base
        self.appendNewKnowledge(cell, count)

        # Step 4: Mark cells as safe or mines given knowledge base
        self.markCells()

        # Step 5: Optimize the knowledge statements in the Knowledge by removing subsets.
        self.checkForOverlaps()

        # Step 6: Mark cells as safe or mines given new knowledge base
        self.markCells()


    def markMine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for knowledge in self.knowledge:
            knowledge.markMine(cell)

    def markSafe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for knowledge in self.knowledge:
            knowledge.markSafe(cell)

    def markCells(self):
        """
        This method iterates through all the knowledge in knowledge base.
        Marks any cells as mines or safes if they can be identified.
        """
        for knowledge in self.knowledge:
            retrievedSafeCells = knowledge.knownSafes()
            retrievedMineCells = knowledge.knownMines()
            # iterate through copy of the cells so that we don't modify them
            if retrievedSafeCells:
                for safeCell in retrievedSafeCells.copy():
                    if safeCell and safeCell not in self.safes:
                        self.markSafe(safeCell)
                        self.safes.add(tuple(safeCell))
            if retrievedMineCells:
                for mineCell in retrievedMineCells.copy():
                    if mineCell and mineCell not in self.mines:
                        self.markMine(mineCell)
                        self.mines.add(tuple(mineCell))

    def appendNewKnowledge(self, cell, count):
        """
        This method adds new knowledge to knowledge.
        """
        neighbors = []
        # get all the neighbors that are not yet known
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell or (i, j) in self.movesMade or not (0 <= i < self.rows and 0 <= j < self.cols):
                    continue
                if (i, j) in self.safes:
                    continue
                neighbors.append((i, j))
        if not len(neighbors):
            return None
        newKnowledge = Knowledge(neighbors, count)
        self.knowledge.append(newKnowledge)

    def checkForOverlaps(self):
        """
        This method checks for overlapping knowledge statements and optimizes them.
        If there is an overlap, trim the overlapping knowledge statement by removing the overlapping part and reduce the
        mine count.
        """
        # initialize index and max length for while loop
        index = 0 
        knowledge_length = len(self.knowledge)

        while index < knowledge_length:
            # get the current knowledge statement
            currentKnowledge = self.knowledge[index]
            if not len(currentKnowledge.cells):
                index += 1  # Skip empty knowledge statements
                continue
            # loop over the inner statements
            inner_index = 0
            while inner_index < knowledge_length:
                # skip statements that are the same as current.
                if inner_index == index:
                    inner_index += 1
                    continue
                # get the subset statements (check if that is a subset)
                subsetKnowledge = self.knowledge[inner_index]
                isSubset = self.checkSubset(currentKnowledge.cells, subsetKnowledge.cells)
                # if there is a subset, we can remove the overlap and the count
                if isSubset:
                    for cell in currentKnowledge.cells:
                        subsetKnowledge.cells.remove(cell)
                    subsetKnowledge.count -= currentKnowledge.count
                inner_index += 1
            index += 1
            
    def checkSubset(self, inner, outer):
        """
        This function checks if the provided inner set is a subset of the provided outer set
        """
        for elem in inner:
            if elem not in outer:
                return False
        return True

    def makeSafeMove(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                currentMove = (i, j)
                if currentMove not in self.movesMade and currentMove in self.safes:
                    return currentMove
        return None

    def makeRandomMove(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that have not already been chosen, and are not known to be mines.
        """
        currentMove = None
        randomMoveFound = False
        if len(self.mines) == self.rows * self.cols - len(self.movesMade):
            # Game over. All mines identified.
            return None
        while not randomMoveFound:
            currentMove = (random.randrange(self.rows), random.randrange(self.cols))
            if currentMove not in self.movesMade and currentMove not in self.mines:
                randomMoveFound = True
        return currentMove