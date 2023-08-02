import random

class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    This class gets created only when a new cell opens up on the board upon a click.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        Returns None if there are no known mines.
        """
        if self.count == 0 or not len(self.cells):
            return None
        if len(self.cells) == self.count:
            return self.cells
        else:
            return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        Returns None if there are no known safes.
        """
        if self.count == 0:
            return self.cells
        else:
            return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        :arg: cell
        updates self.cells and self.count
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        :arg: cell
        updates self.cells and self.count
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
    
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge

        :arg: cell - tuple (i, j), count - int
        updates self.mines, self.safes, self.moves_made, and self.knowledge
        """

        # Step 1: Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # Step 2: Mark the cell as safe
        self.mark_safe(cell)

        # Step 3: The function should add a new sentence to the AI’s knowledge base,
        # based on the value of cell and count, to indicate that count of the cell’s neighbors are mines.
        # Be sure to only include cells whose state is still undetermined in the sentence.
        self.append_new_sentence_to_knowledge(cell, count)

        # Step 4: Mark cells as safe or mines given knowledge base
        self.mark_cells()

        # Step 5 : Optimize the sentences in the Knowledge by removing subsets.
        self.check_for_overlapping_sentence_and_optimize_them()

        # Step 6: Mark cells as safe or mines given new knowledge base
        self.mark_cells()

        # for sentence in self.knowledge:
        #     if len(sentence.cells):
        #         print(f'sentence = {sentence}')
        #
        # print(f'List of safe moves = {self.safes}')
        # print(f'List of mines = {self.mines}')

    def mark_cells(self):
        """
        This method iterates through all the sentences in knowledge base.
        Marks any cells as mines or safes if they can be identified.
        Returns None.
        """
        for sentence in self.knowledge:
            retrieved_safe_cells = sentence.known_safes()
            retrieved_mine_cells = sentence.known_mines()
            if retrieved_safe_cells:
                for safe_cell in list(retrieved_safe_cells):
                    if safe_cell and safe_cell not in self.safes:
                        self.mark_safe(safe_cell)
                        self.safes.add(tuple(safe_cell))
            if retrieved_mine_cells:
                for mine_cell in list(retrieved_mine_cells):
                    if mine_cell and mine_cell not in self.mines:
                        self.mark_mine(mine_cell)
                        self.mines.add(tuple(mine_cell))

    def append_new_sentence_to_knowledge(self, cell, count):
        """
        This method adds new sentences to knowledge
        :arg: cell (row, column)
        :arg: count Int
        return None
        """
        neighbors = []
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell or (i, j) in self.moves_made or not (0 <= i < self.height and 0 <= j < self.width):
                    continue
                if (i, j) in self.safes:
                    continue
                neighbors.append((i, j))
        if not len(neighbors):
            return None
        new_sentence = Sentence(neighbors, count)
        self.knowledge.append(new_sentence)

    def check_for_overlapping_sentence_and_optimize_them(self):
        """
        This method checks for overlapping sentences and optimizes them.
        If there is an overlap, trim the overlapping sentence by removing the overlapping part and reduce the
        mine count.
        Returns None
        """
        for current_sentence_index, current_sentence in enumerate(self.knowledge):
            # print(f'current_sentence={current_sentence}, current_sentence_index={current_sentence_index}')
            if not len(current_sentence.cells):
                continue
            for current_index in range(len(self.knowledge)):
                if current_index == current_sentence_index or not len(self.knowledge[current_index].cells):
                    continue
                looping_sentence = self.knowledge[current_index]
                # print(f'looping_sentence={looping_sentence}')
                is_subset = current_sentence.cells.issubset(looping_sentence.cells)
                if is_subset:
                    # print(f'Found {current_sentence} is subset of {looping_sentence}')
                    for cell in current_sentence.cells:
                        looping_sentence.cells.remove(cell)
                    looping_sentence.count -= current_sentence.count

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        for i in range(self.height):
            for j in range(self.width):
                current_move = (i, j)
                if current_move not in self.moves_made and \
                        current_move in self.safes:
                    # print(f'returning a safe move = {current_move}')
                    return current_move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        current_move = None
        random_move_found = False
        if len(self.mines) == self.height * self.width - len(self.moves_made):
            # Game over. All mines identified.
            return None
        while not random_move_found:
            current_move = (random.randrange(self.height), random.randrange(self.width))
            if current_move not in self.moves_made and \
                    current_move not in self.mines:
                # print(f'returning a random move = {current_move}')
                random_move_found = True
        return current_move
