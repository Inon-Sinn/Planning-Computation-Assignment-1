from queue import PriorityQueue
import ast
import time
import random


# this function exists to construct a puzzle given a string
def construct_puzzle(string):
    try:
        puzzle = ast.literal_eval(string)
    except Exception as e:
        return []
    return puzzle


# An auxiliary function
def digits(value):
    return len(str(value))


# This class represent the liquid puzzle
class LiquidPuzzle:
    def __init__(self, string):
        self.colors = 0
        self.tubes = construct_puzzle(string)
        if not self.construct_correctness():
            raise ValueError("Invalid puzzle configuration")
        self.tube_size = max(len(tube) for tube in self.tubes)

    # Checks if the move is valid only work in the correct direction no reverse action
    def is_valid_move(self, tube_from, tube_to,reverse=False):
        if not self.tubes[tube_from]:
            return False
        if len(self.tubes[tube_to]) >= self.tube_size:
            return False
        if not self.tubes[tube_to] or self.tubes[tube_from][0] == self.tubes[tube_to][0]:
            return True
        return False

    # Checks if the given puzzle is even a correct input
    def construct_correctness(self):
        color_count = {}
        max_tube = max(len(tube) for tube in self.tubes) if self.tubes else 0

        # Count occurrences of each color
        for tube in self.tubes:
            for color in tube:
                if color in color_count:
                    color_count[color] += 1
                else:
                    color_count[color] = 1

        # Check if each color has the correct amount in the puzzle
        for color, count in color_count.items():
            if count > max_tube * len(self.tubes):
                return False
        self.colors = len(color_count)
        return True

    # Makes a move if the move is valid else return None, but if it is correct is builds a new liquid puzzle
    def move(self, tube_from, tube_to,reverse=False):
        if self.is_valid_move(tube_from, tube_to, reverse):
            new_tubes = [list(tube) for tube in self.tubes]
            new_tubes[tube_to].insert(0, new_tubes[tube_from].pop(0))
            return LiquidPuzzle.from_puzzle(new_tubes)
        return None

    # Finds all the possible moves for the current liquid puzzle
    def get_neighbors(self):
        neighbors = []
        for i in range(len(self.tubes)):
            for j in range(len(self.tubes)):
                if i != j and self.is_valid_move(i, j):
                    neighbor = self.move(i, j)
                    if neighbor:
                        neighbors.append(neighbor)
        return neighbors

    # Building a final result using the values given by the, returns Boolean
    def buildComplete(self, tNum, tSize, colorNum):
        if colorNum >= tNum:
            return False
        if tNum < 0 or tSize < 0 or colorNum < 0:
            return False
        self.tube_size = tSize
        self.colors = colorNum
        puzzle = []
        for i in range(tNum):
            puzzle.append([])
        for i in range(colorNum):
            for j in range(tSize):
                puzzle[i].append(i + 1)
        self.tubes = puzzle
        return True

    # Takes a liquidPuzzle and then randomly reverses it, does not return anything
    def reverseBuild(self, count, limit=100):
        cur_limit = limit
        while count > 0 and cur_limit > 0:
            randomFrom = random.randint(0, len(self.tubes) - 1)
            randomTo = random.randint(0, len(self.tubes) - 1)
            if self.move(randomFrom, randomTo, reverse=True):
                count = count - 1
                cur_limit = limit
                print(self)
            else:
                cur_limit = cur_limit - 1
        if cur_limit == 0:
            print("Went over the limit, could be final result")

    @staticmethod
    # an axilliary method for get_neighbors that helps construct a new puzzle
    def from_puzzle(puzzle):
        puzzle_str = '[' + '],['.join([','.join(map(str, tube)) if tube else '' for tube in puzzle]) + ']'
        return LiquidPuzzle(puzzle_str)

    # an Auxilliary method created for A-star to check if we solved the liquid puzzle
    def is_goal(self):
        for tube in self.tubes:
            if len(tube) > 0 and (len(set(tube)) > 1 or len(tube) != self.tube_size):
                return False
        return True

    def __eq__(self, other):
        return self.tubes == other.tubes

    def __hash__(self):
        return hash(tuple(tuple(tube) for tube in self.tubes))

    def __lt__(self, other):
        return str(self.tubes) < str(other.tubes)

    def __str__(self):
        return '[' + ']['.join([','.join(map(str, tube)) if tube else '[]' for tube in self.tubes]) + ']'

    # printing the puzzle for the User Interface
    def special_print(self):
        result = ""
        puzzle = self.tubes
        for i in range(self.tube_size):
            row = ""
            for j in range(len(self.tubes)):
                cell = ""
                leftToFill = self.tube_size - len(puzzle[j])
                if len(puzzle[j]) != 0 and i >= leftToFill:
                    value = puzzle[j][i - leftToFill]
                    cell = " |" + str(value) + " " * (digits(self.colors) - digits(value)) + "|"
                else:
                    cell = " |" + " " * digits(self.colors) + "|"
                row = row + cell
            result = result + "\n" + row

        row = ""
        for i in range(len(self.tubes)):
            cell = " " * 2 + str(i + 1) + " " * (digits(self.colors) - digits(i + 1)) + " "
            row += cell
        print(result + "\n" + row)


# The heuristic function
def heuristic(puzzle):
    tubes = puzzle.tubes
    tube_size = puzzle.tube_size

    # Calculate the number of non-homogeneous tubes
    mixed_tubes = sum(1 for tube in tubes if len(set(tube)) > 1)

    # Calculate the number of tubes that need to be emptied or consolidated
    empty_moves = 0
    for tube in tubes:
        if len(tube) == 0:
            continue
        colors = set(tube)
        if len(colors) > 1:
            empty_moves += len(tube)
        else:
            if len(tube) < tube_size:
                empty_moves += (tube_size - len(tube))

    return mixed_tubes + empty_moves


# A star algorithm
def a_star(initial_state):
    open_set = PriorityQueue()
    open_set.put((0, initial_state))
    came_from = {}
    g_score = {initial_state: 0}
    f_score = {initial_state: heuristic(initial_state)}
    closed_set = set()

    while not open_set.empty():
        current = open_set.get()[1]

        if current.is_goal():
            return reconstruct_path(came_from, current)

        closed_set.add(current)

        for neighbor in current.get_neighbors():
            if neighbor in closed_set:
                continue

            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor)
                open_set.put((f_score[neighbor], neighbor))

    return None


# Reconstructs the path found with A star
def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]


# The Algorithm for IDA-star
def ida_star(initial_state):
    def search(node, g, bound):
        f = g + heuristic(node)
        if f > bound:
            return f, None
        if node.is_goal():
            return True, [node]
        min_bound = float('inf')
        for neighbor in node.get_neighbors():
            if neighbor in visited:
                continue
            visited.add(neighbor)
            temp_bound, path = search(neighbor, g + 1, bound)
            if temp_bound is True:
                return True, [node] + path
            if temp_bound < min_bound:
                min_bound = temp_bound
            visited.remove(neighbor)
        return min_bound, None

    bound = heuristic(initial_state)
    visited = {initial_state}
    while True:
        temp_bound, path = search(initial_state, 0, bound)
        if temp_bound is True:
            return path
        if temp_bound == float('inf'):
            return None
        bound = temp_bound


# An auxiliary function used mainly for UI
def test_ida_star():
    initial_state = LiquidPuzzle(
        "[[], [], [0, 4, 1, 4, 5, 0], [5, 2, 5, 2, 1, 5], [3, 1, 3, 3, 4, 0], [2, 4, 1, 0, 3, 0], [0, 3, 4, 2, 2, 1], "
        "[2, 5, 1, 5, 4, 3]]")
    print("start")
    path = ida_star(initial_state)
    if path:
        for step in path:
            print(step)
    else:
        print("No solution found.")
    print()


# An auxiliary function used mainly for UI
def test_a_star():
    initial_state = LiquidPuzzle("[[], [0, 1, 1], [2, 0, 1], [0, 2, 2]]")
    path = a_star(initial_state)
    if path:
        for step in path:
            print(step)
    else:
        print("No solution found.")


def solve(initial_state):
    # debug
    # initial_state = LiquidPuzzle("[[], [0, 1, 1], [2, 0, 1], [0, 2, 2]]")

    start_time = time.perf_counter()
    path = a_star(initial_state)
    end_time = time.perf_counter()
    if path:
        runtime = end_time - start_time
        minutes, seconds = divmod(runtime, 60)
        print("-" * 30)
        print(f"Runtime: {int(minutes)} minutes and {seconds:.5f} seconds")
        print("Number of Moves: {}".format(len(path) - 1))
        print("-" * 30)
        for step in path:
            step.special_print()
    else:
        print("No solution found.")


# Build a random Liquid Puzzle
def createRandom():
    print("-------------------------------------------------------------------------------------------------------")
    puzzle = LiquidPuzzle("[[]]")
    print("Please enter the amount of tubes, size of a tube and amount of colors in the following "
          "format:\nTubes_Amount Tube_Size Color_Amount")

    # while function that runs until the value given are correct for creating a final result
    while True:
        str_in = input("Enter values:")
        str_in = str_in.split(" ")
        tubesAmount, tubeSize, colorAmount = int(str_in[0]), int(str_in[1]), int(str_in[2])
        # tubesAmount, tubeSize, colorAmount = 5,4,4
        if puzzle.buildComplete(tubesAmount, tubeSize, colorAmount):
            print(puzzle.tubes)
            break
        else:
            print("Invalid Input, try Again")

    # Makes a random amount of moves arcading to the user
    # print("You can now choose how many reverse moves to make")
    # while True:
    #     print("-------------------------------------------------------------------------------------------------------")
    #     str_in = input("Amount of Random Moves: ")
    #     counter = int(str_in)
    #     puzzle.reverseBuild(counter, counter * 5)
    #     print("\n Result: ")
    #     puzzle.special_print()


def menu():
    print("-----------------------------------------------------------------------------------------------------------")
    print("Enter 1 for solving a liquid puzzle and 2 for creating a random one:")
    str_in = input("Input: ")
    value = int(str_in)
    if value == 1:
        correctInput = False
        while not correctInput:
            str_in = input("\nPlease enter the Liquid Puzzle: ")
            try:
                puzzle = LiquidPuzzle(str_in)
                solve(puzzle)
                break
            except ValueError:
                print("The Input does not stand by the rules of the Game")
    else:
        createRandom()


if __name__ == '__main__':
    # UI()
    menu()
    # createRandom()
    # initial_state = LiquidPuzzle("[[], [0, 1, 1], [2, 0, 1], [0, 2, 2]]")
    # print("hi")