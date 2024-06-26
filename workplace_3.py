import random


class liquidPuzzle:
    correctInput = False
    colors = 0
    tubes = 0
    tubeSize = 0

    def __init__(self, string):
        self.puzzle = self.constructPuzzle(string)
        self.correctInput = self.constructCorrectness()
        if self.correctInput:
            self.tubes = len(self.getPuzzle())

    # test if the puzzle is Standing by the game rules, returns Boolean
    def constructCorrectness(self):
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
        if maxColor > len(puzzle) * maxTube:
            return False
        # Check if each color has the correct amount in the puzzle
        counterList = [0] * maxColor
        for arr in puzzle:
            for j in arr:
                counterList[j - 1] = counterList[j - 1] + 1
        for i in counterList:
            if i != maxTube:
                return False

        self.setColors(maxColor)
        self.setTubeSize(maxTube)
        return True

    # Constructs the puzzle given be the user and returns it
    # Currently only works on correct input, returns puzzle
    def constructPuzzle(self, string):
        # Remove all whitespaces in the string for easier processing
        string = string.replace(" ", "")
        # just some auxiliary variables
        puzzle = []
        Skip, tempFirst, AddToTemp = False, 0, True
        # We shall now go over all internal lists
        for i in range(1, len(string) - 1):
            # This skip a turn if found an empty internal array
            if Skip:
                Skip = False
                continue
            # check if it is an empty array
            if string[i] == '[' and string[i + 1] == ']':
                puzzle.append([])
                Skip = True
            # Check if it is the beginning of full array
            elif string[i] == '[' and string[i + 1] != ']':
                AddToTemp = True
                tempFirst = i + 1
                continue
            # Check if we are in between two internal arrays
            elif string[i] == ',' and not AddToTemp:
                continue
            # Check if we are in the middle of an internal array
            elif string[i] != ']' and AddToTemp:
                continue
            # if we finished an internal array we add it to the puzzle as new list
            else:
                AddToTemp = False
                # cut out the internal array and turn it into an a list of integers
                cut_str = string[tempFirst:i]
                cut_str = cut_str.split(",")
                for j in range(len(cut_str)):
                    cut_str[j] = int(cut_str[j])
                # Add it to the final product
                puzzle.append(cut_str)
        return puzzle

    # Given a move from the user we first have to check it it is a possible move, this work foe value from 0 to tubes-1
    # for ease of use later in the heuristic, returns Boolean
    def moveCorrectness(self, tubeFrom, tubeTo, reverse=False):

        # Check the input
        if tubeFrom >= self.getTubes() or tubeTo >= self.getTubes():
            return False
        if tubeFrom < 0 or tubeTo < 0:
            return False
        if tubeFrom == tubeTo:
            return False

        # check that we can actually move
        puzzle = self.getPuzzle()

        # Check if the target Tube is full
        if len(puzzle[tubeTo]) == self.tubeSize:
            return False

        # Check From tube is not empty
        if len(puzzle[tubeFrom]) == 0:
            return False

        # Check if the uppermost color in the target tube is the same as the color we want to move
        if len(puzzle[tubeTo]) != 0 and not reverse:
            tubeToColor = puzzle[tubeTo][0]
            tubeFromColor = puzzle[tubeFrom][0]
            if tubeToColor != tubeFromColor:
                return False

        # When we do a reverse move we can not move a color which has a different color below
        if reverse and len(puzzle[tubeFrom]) > 1:
            colorToMove = puzzle[tubeFrom][0]
            colorBelow = puzzle[tubeFrom][1]
            if colorToMove != colorBelow:
                return False
        return True

    # Move the value from the one tube to the target tube, return True if it worked and false otherwise, returns Boolean
    def move(self, tubeFrom, tubeTo, reverse=False):
        if not self.moveCorrectness(tubeFrom, tubeTo, reverse):
            return False
        puzzle = self.getPuzzle()
        moveValue = puzzle[tubeFrom].pop(0)
        puzzle[tubeTo].insert(0, moveValue)
        return True

    # Building a final result using the values given by the, returns Boolean
    def buildComplete(self, tNum, tSize, colorNum):
        if colorNum >= tNum:
            return False
        if tNum < 0 or tSize < 0 or colorNum < 0:
            return False
        self.setTubes(tNum)
        self.setTubeSize(tSize)
        self.setColors(colorNum)
        self.setCorrectness(True)
        puzzle = []
        for i in range(tNum):
            puzzle.append([])
        for i in range(colorNum):
            for j in range(tSize):
                puzzle[i].append(i + 1)
        self.setPuzzle(puzzle)
        return True

    # Takes a liquidPuzzle and then randomly reverses it, does not return anything
    def reverseBuild(self, count, limit=100):
        curlimit = limit
        while count > 0 and curlimit > 0:
            randomFrom = random.randint(0, self.getTubes() - 1)
            randomTo = random.randint(0, self.getTubes() - 1)
            if self.move(randomFrom, randomTo, reverse=True):
                count = count - 1
                curlimit = limit
                print(self)
            else:
                curlimit = curlimit - 1
        if curlimit == 0:
            print("Went over the limit, could be final result")

    # setting functions
    def setTubes(self, tubes):
        self.tubes = tubes

    def setColors(self, Color):
        self.colors = Color

    def setTubeSize(self, size):
        self.tubeSize = size

    def setPuzzle(self, puzzle):
        self.puzzle = puzzle

    def setCorrectness(self, bool):
        self.correctInput = bool

    # getter functions
    def getTubes(self):
        return self.tubes

    def getColors(self):
        return self.colors

    def getTubeSize(self):
        return self.tubeSize

    def getPuzzle(self):
        return self.puzzle

    def getCorrectness(self):
        return self.correctInput

    # printing the puzzle for the User Interface
    def __str__(self):
        result = ""
        puzzle = self.getPuzzle()
        for i in range(self.getTubeSize()):
            row = ""
            for j in range(self.getTubes()):
                cell = ""
                leftToFill = self.tubeSize - len(puzzle[j])
                if len(puzzle[j]) != 0 and i >= leftToFill:
                    value = puzzle[j][i - leftToFill]
                    cell = " |" + str(value) + " " * (self.digits(self.colors) - self.digits(value)) + "|"
                else:
                    cell = " |" + " " * self.digits(self.colors) + "|"
                row = row + cell
            result = result + "\n" + row

        row = ""
        for i in range(self.getTubes()):
            cell = " " * 2 + str(i + 1) + " " * (self.digits(self.colors) - self.digits(i + 1)) + " "
            row += cell
        return result + "\n" + row

    def digits(self, value):
        return len(str(value))


# A function that just is the interface the user will interact with
def userInterface():
    print("-------------------------------------------------------------------------------------------------------")
    correctInput = False
    puzzle = liquidPuzzle
    while not correctInput:
        str_in = input("Please enter the Liquid Puzzle: ")
        puzzle = liquidPuzzle(str_in)
        # debug = "[[], [1, 4, 3, 1], [1, 4, 3, 4], [2, 2, 4, 3], [1, 2, 3, 2]]"
        # puzzle = liquidPuzzle(debug)
        if not puzzle.getCorrectness():
            print("The Input does not stand by the rules of the Game")
        else:
            correctInput = True
    print(puzzle)
    playing = True
    print("To move a liquid from one tube to another \nEnter both tube numbers in the following format: 'from' 'to' "
          "example: 1 6")
    # puzzle.moveCorrectness(4,5) #debug
    while playing:
        print("-------------------------------------------------------------------------------------------------------")
        move = input("Enter the next move: ")
        move = move.split(" ")
        tubeFrom, tubeTo = int(move[0]), int(move[1])
        # tubeFrom, tubeTo = 2, 1 # debug

        # we take one down as it works for the player, can be changed
        print(puzzle.moveCorrectness(tubeFrom - 1, tubeTo - 1))
        if not puzzle.move(tubeFrom - 1, tubeTo - 1):
            print("Invalid Move, try Again")
        else:
            print(puzzle)


# Build a random Liquid Puzzle
def createRandom():
    print("-------------------------------------------------------------------------------------------------------")
    puzzle = liquidPuzzle("[]")
    correctInput = False
    print("Please enter the amount of tubes, size of a tube and amount of colors in the following "
          "format:\nTubes_Amount Tube_Size Color_Amount")

    # while function that runs until the value given are correct for creating a final result
    while not correctInput:
        str_in = input("Enter values:")
        str_in = str_in.split(" ")
        tubesAmount, tubeSize, colorAmount = int(str_in[0]), int(str_in[1]), int(str_in[2])
        # tubesAmount, tubeSize, colorAmount = 4,0,4
        if puzzle.buildComplete(tubesAmount, tubeSize, colorAmount):
            correctInput = True
            print(puzzle)
        else:
            print("Invalid Input, try Again")

    # Makes a random amount of moves arcading to the user
    print("You can now choose how many reverse moves to make")
    while True:
        print("-------------------------------------------------------------------------------------------------------")
        str_in = input("Amount of Random Moves: ")
        counter = int(str_in)
        puzzle.reverseBuild(counter, counter * 5)
        print("\n Result: {}".format(puzzle.getPuzzle()))


def menu():
    print("-----------------------------------------------------------------------------------------------------------")
    print("Enter 1 for creating a random liquid puzzle and 2 manually solving one:")
    str_in = input("Enter: ")
    value = int(str_in)
    if value == 1:
        createRandom()
    else:
        userInterface()


# Just the main function, if you don't know this we have other problems
if __name__ == '__main__':
    menu()
    # createRandom()
    # userInterface()
    example = [[], [1, 4, 3, 1], [1, 4, 3, 4], [2, 2, 4, 3], [1, 2, 3, 2]]
