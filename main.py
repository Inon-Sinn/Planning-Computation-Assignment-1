class liquidPuzzle:
    correctInput = False

    def __init__(self, str):
        self.puzzle = self.constructPuzzle(str)
        self.correctInput = self.testCorrectness()

    # test if the puzzle is Standing by the game rules
    def testCorrectness(self):
        puzzle = self.getPuzzle()

        # Find the length of the biggest tube and the  highest color
        maxTube = 0
        maxColor = 0
        for arr in puzzle:
            length = len(arr)
            if maxTube < length:
                maxTube = length
            for j in arr:
                if j > maxColor:
                    maxColor = j

        # Check Tubes are of the max size or 0
        for i in puzzle:
            length = len(i)
            if length != maxTube and length != 0:
                return False

        # Check the amount of colors in the puzzle is correct
        # a small test so we don't waste space and runtime
        if maxColor > len(puzzle)*maxTube:
            return False
        # Check if each color has the correct amount in the puzzle
        counterList = [0]*maxColor
        for arr in puzzle:
            for j in arr:
                counterList[j-1] = counterList[j-1] + 1
        for i in counterList:
            if i != maxTube:
                return False
        return True

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
