class liquidPuzzle:
    correctInput = False

    def __init__(self, str):
        self.puzzle = self.constructPuzzle(str)
        self.testCorrectness()

    # test if the puzzle is Standing by the game rules
    def testCorrectness(self):
        self.correctInput = True

    # Constructs the puzzle given be the user and returns it
    # Currently only works on correct input
    def constructPuzzle(self, str):
        # Remove all whitespaces in the string for easier processing
        str = str.replace(" ", "")
        # just some auxiliary variables
        puzzle = []
        Skip, tempFirst, AddToTemp = False, 0, True
        # We shall now go over all internal lists
        for i in range(1, len(str) - 1):
            # This skip a turn if found an empty internal array
            if Skip:
                Skip = False
                continue
            # check if it is an empty array
            if str[i] == '[' and str[i + 1] == ']':
                puzzle.append([])
                Skip = True
            # Check if it is the beginning of full array
            elif str[i] == '[' and str[i + 1] != ']':
                AddToTemp = True
                tempFirst = i+1
                continue
            # Check if we are in between two internal arrays
            elif str[i] == ',' and not AddToTemp:
                continue
            # Check if we are in the middle of an internal array
            elif str[i] != ']' and AddToTemp:
                continue
            # if we finished an internal array we add it to the puzzle as new list
            else:
                AddToTemp = False
                # cut out the internal array and turn it into an a list of integers
                cut_str = str[tempFirst:i]
                cut_str = cut_str.split(",")
                for j in range(len(cut_str)):
                    cut_str[j] = int(cut_str[j])
                # Add it to the final product
                puzzle.append(cut_str)
        return puzzle

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
    print(puzzle.getPuzzle())


# Just the main function, if you don't know this we have other problems
if __name__ == '__main__':
    userInterface()
    example = [[], [1, 4, 3, 1], [1, 4, 3, 4], [2, 2, 4, 3], [1, 2, 3, 2]]
