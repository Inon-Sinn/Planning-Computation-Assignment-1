class liquidPuzzle:

    correctInput = False

    def __init__(self, str):
        self.puzzle = self.constructPuzzle(str)
        self.testCorrectness()

    # test if the puzzle is Standing by the game rules
    def testCorrectness(self):
        self.correctInput = True

    # Constructs the puzzle given be the user and returns it
    def constructPuzzle(self, str):
        return []

    # setting functions
    def setTubes(self, tubes):
        self.tubes = tubes

    def setColor(self, Color):
        self.color = Color

    # getter functions
    def getTubes(self):
        return self.tubes

    def getColor(self):
        return self.color

    def getPuzzle(self):
        return self.puzzle

    def getCorrectness(self):
        return self.correctInput

# A function that just is the interface the user will interact with
def userInterface():
    correctInput = False
    while not correctInput:
        str_in = input("Please enter the Liquid Puzzle: ")
        puzzle = liquidPuzzle(str_in)
        if not puzzle.getCorrectness():
            print("The Input does not stand by the rules of the Game")
        else:
            correctInput = True


# Just the main function, if you dont know this we have other problems
if __name__ == '__main__':
    userInterface()