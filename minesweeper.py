import itertools
import random
import copy

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
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
        """
        # if the amount of remaining cell(s) in the sentence equal to the count of mine(s), confidently return all cells as mines
        if len(self.cells) == self.count:
            return self.cells
        # else return an empty set
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # if the remaining cells in the sentence correspond to a mine count of 0, confidently return all cells as safes
        if self.count == 0:
            return self.cells
        # else return an empty set
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # if cell(mine) exists in the sentence, remove it from the sentence and reduce the mine count by 1
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # if cell(safe) exists in the sentence, simply remove it from the sentence
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
        """
        # mark the cell as a move that has been made
        self.moves_made.add(cell)

        # mark the cell as safe
        self.mark_safe(cell)

        # add the new sentence with the corresponding cell's neighbors 
        # that are not yet determined with the cell's mine count to the AI's knowledge base
        allNeighbors, mineCount = self.return_neighbors(cell)
        unknownNeighbors = allNeighbors - self.mines - self.safes
        if unknownNeighbors != set():
            newSentence = Sentence(unknownNeighbors, count - mineCount)
            # if the sentence is not repeated
            if newSentence not in self.knowledge:
                self.knowledge.append(newSentence)

        # mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        for sentence in self.knowledge:
            # if the returning set containing the known mines is not empty
            mines = copy.deepcopy(sentence.known_mines())
            if mines != set() and mines not in self.mines:
                for mine in mines:
                    self.mark_mine(mine)
            # if the returning set containing the known safes is not empty
            safes = copy.deepcopy(sentence.known_safes())
            if safes != set() and safes not in self.safes:
                for safe in safes:
                    self.mark_safe(safe)

        # add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        for sentence in self.knowledge:
            # if there is remaining unknown cells in the sentence
            if len(sentence.cells) != 0:
                for sentence2 in self.knowledge:
                    # ignore the same sentence
                    if sentence == sentence2:
                        continue
                    # if there is remaining unknown cells in the sentence
                    if len(sentence2.cells) != 0:
                        # if sentence1 is the subset of sentence2
                        if sentence.cells.issubset(sentence2.cells):
                            deducedCells = sentence2.cells - sentence.cells - self.moves_made
                            deducedCount = sentence2.count - sentence.count
                            reducedSentence = Sentence(deducedCells, deducedCount)
                            if reducedSentence not in self.knowledge:
                                self.knowledge.append(reducedSentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        remainingChoice = set()
        for i in range(0, self.height):
            for j in range(0, self.width):
                remainingChoice.add((i, j))
        # eliminate moves already made and moves that are known to be mines-encountering
        remainingChoice = remainingChoice - self.moves_made - self.mines
        # if the set is not an empty set
        if remainingChoice != set():
            # return a random choice of the set
            return random.sample(remainingChoice, 1).pop()
        else:
            return None

    # return the neighbors of cell
    def return_neighbors(self, cell):
        i, j = cell
        mineCount = 0
        # intialize returning set
        neighbors = set()
        # loop through each row and column
        for y in range(i-1, i+2):
            for x in range(j-1, j+2):
                # if the cell exists within bound and that it is not the home cell
                if y >= 0 and y < self.height and x >= 0 and x < self.width and (y, x) != (i, j):
                    # then add the cell to neighbors
                    neighbors.add((y, x))
                    # check if it is known to be mine and if it is increment the mine count
                    if (y, x) in self.mines:
                        mineCount += 1
        return neighbors, mineCount