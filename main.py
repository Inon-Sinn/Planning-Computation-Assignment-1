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


# UI, An auxiliary function
def digits(value):
    return len(str(value))


# This class represent the liquid puzzle
class LiquidPuzzle:
    def __init__(self, string, Moved=False, newTubes=[], colors=0, tube_size=0):
        if Moved:
            self.tubes = newTubes
            self.colors = colors
            self.tube_size = tube_size
        else:
            self.colors = 0
            self.tubes = construct_puzzle(string)
            if not self.construct_correctness():
                raise ValueError("Invalid puzzle configuration")
            self.tube_size = max(len(tube) for tube in self.tubes)

    # Checks if the move is valid only work in the correct direction no reverse action
    def is_valid_move(self, tube_from, tube_to, reverse=False):
        if not self.tubes[tube_from]:
            return False
        if len(self.tubes[tube_to]) >= self.tube_size:
            return False
        if not reverse:
            if not self.tubes[tube_to] or self.tubes[tube_from][0] == self.tubes[tube_to][0]:
                return True
        else:
            if len(self.tubes[tube_from]) > 1 and self.tubes[tube_from][0] == self.tubes[tube_from][1]:
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
    def move(self, tube_from, tube_to, reverse=False):
        if self.is_valid_move(tube_from, tube_to, reverse):
            new_tubes = [list(tube) for tube in self.tubes]
            new_tubes[tube_to].insert(0, new_tubes[tube_from].pop(0))
            return LiquidPuzzle("",True,new_tubes,self.colors,self.tube_size)
        return None

    # Finds all the possible moves for the current liquid puzzle
    def get_neighbors(self):
        top_color = {}
        # top color same counter
        count = 0
        for tube in self.tubes:
            if not tube:
                top_color[count] = 0
            else:
                top = tube[0]
                streak = 1
                for i in range(1, len(tube)):
                    if tube[i] != top:
                        break
                    streak += 1

                top_color[count] = streak
            count += 1

        neighbors = []
        possible_tubes = []
        empty_tube = False
        for i in range(len(self.tubes)):
            if not self.tubes[i] and not empty_tube:
                empty_tube = True
                possible_tubes.append(i)
            elif self.tubes[i]:
                possible_tubes.append(i)

        for i in possible_tubes:
            for j in possible_tubes:
                neighbor = self.move(i, j)
                for k in range(1, top_color[i] + 1):
                    if not neighbor:
                        break
                    if neighbor and i != j and k == top_color[i] and not self.new_eq(neighbor):
                        neighbors.append(neighbor)
                    neighbor = neighbor.move(i, j)

        return neighbors

    # UI, Building a final result using the values given by the, returns Boolean
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

    # UI, Takes a liquidPuzzle and then randomly reverses it, does not return anything
    def reverseBuild(puzzle, count, limit=100):
        cur_limit = limit
        while count > 0 and cur_limit > 0:
            randomFrom = random.randint(0, len(puzzle.tubes) - 1)
            randomTo = random.randint(0, len(puzzle.tubes) - 1)
            if puzzle.is_valid_move(randomFrom, randomTo, reverse=True):
                puzzle = puzzle.move(randomFrom, randomTo, reverse=True)
                count = count - 1
                cur_limit = limit
                print(puzzle)
            else:
                cur_limit = cur_limit - 1
        if cur_limit == 0:
            print("Went over the limit, could be final result")
        return puzzle

    @staticmethod
    # an Auxiliary method for get_neighbors that helps construct a new puzzle
    def from_puzzle(puzzle):
        puzzle_str = '[' + '],['.join([','.join(map(str, tube)) if tube else '' for tube in puzzle]) + ']'
        return LiquidPuzzle(puzzle_str)

    # an Auxiliary method created for A-star to check if we solved the liquid puzzle
    def is_goal(self):
        for tube in self.tubes:
            if len(tube) > 0 and (len(set(tube)) > 1 or len(tube) != self.tube_size):
                return False
        return True

    def new_eq(self, other):
        for tube in self.tubes:
            if tube not in other.tubes:
                return False
        return True

    def __eq__(self, other):
        if isinstance(other, LiquidPuzzle):
            return self.tubes == other.tubes
        return False

    def __hash__(self):
        return hash(tuple(tuple(tube) for tube in self.tubes))

    def __lt__(self, other):
        return str(self.tubes) < str(other.tubes)

    def __str__(self):
        return '[' + ']['.join([','.join(map(str, tube)) if tube else '[]' for tube in self.tubes]) + ']'

    # UI, printing the puzzle for the User Interface
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
    return custom_heuristic(puzzle)


def heuristic_first(puzzle):
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


def heuristic_second(puzzle):
    tubes = puzzle.tubes
    color_count = {}

    result = 0
    # Calculate the number of different colors on another color in a tube
    for tube in tubes:
        for i in range(len(tube) - 1):
            if tube[i] != tube[i + 1]:
                result += 1
        if tube:
            if tube[-1] not in color_count:
                color_count[tube[-1]] = 1
            else:
                color_count[tube[-1]] += 1

    # Check the distribution of the lowest color
    for color, value in color_count.items():
        result += value - 1
    return result


def heuristic_third(puzzle):
    tubes = puzzle.tubes
    tube_size = puzzle.tube_size
    top_color = {}
    bottom_color = {}

    # count the top collection of colors including streaks
    for tube in tubes:
        if tube:
            top = tube[0]  # Top color in the tube
            # Add to dict
            if top not in top_color:
                top_color[top] = 1
            else:
                top_color[top] += 1

            # Check if there is more of the same underneath
            for i in range(1, len(tube)):
                if tube[i] != top:
                    break
                else:
                    top_color[top] += 1
                    # Check if this whole is once solid color i yes remove the count
                    if i == len(tube) - 1:
                        top_color[top] -= len(tube)

    # Get the bottom solid color and the amount
    count = 0
    for tube in tubes:
        if not tube:
            bottom_color[count] = 0
        else:
            bottom = tube[-1]
            streak = 1
            for i in range(len(tube) - 2, -1, -1):
                if tube[i] != bottom:
                    break
                streak += 1

            bottom_color[count] = streak
        count += 1

    # Calculate the value
    result = 0
    # Rule 1 - remove top color
    for color, value in top_color.items():
        result += 2 ** value

    # Rule 2 - completion is king
    for color, value in bottom_color.items():
        result += tube_size - value

    return result


def heuristic_fourth(puzzle):
    """
    Heuristic function for the tube sorting puzzle using Manhattan distance.
    """
    tubes = puzzle.tubes
    tube_size = puzzle.tube_size
    color_goal_positions = {}
    weights = {'empty_weight': 10, 'consolidate_weight': 5, 'overflow_penalty': 2,
               'top_bonus': 1, 'bottom_bonus': 1, 'sequence_reward': 3}

    # Determine the target positions for each color in the goal state
    for idx, tube in enumerate(tubes):
        for pos, color in enumerate(tube):
            if color not in color_goal_positions:
                color_goal_positions[color] = []
            color_goal_positions[color].append((idx, pos))

    total_metric = 0
    for idx, tube in enumerate(tubes):
        current_streak_color = None
        streak_length = 0
        for pos, color in enumerate(tube):
            if color_goal_positions[color]:
                goal_idx, goal_pos = color_goal_positions[color].pop(0)  # Get the first target position for this color
                distance = abs(idx - goal_idx) + abs(pos - goal_pos)  # Calculate a custom distance metric
                total_metric += distance

                # Apply weights
                if pos == len(tube) - 1:
                    total_metric -= weights['top_bonus']
                if pos == 0:
                    total_metric -= weights['bottom_bonus']
                if pos > 0 and tube[pos - 1] == color:
                    total_metric -= weights['consolidate_weight']
                if idx != goal_idx:
                    total_metric += len(color_goal_positions[color]) * weights['overflow_penalty']

                if color == current_streak_color:
                    streak_length += 1
                else:
                    current_streak_color = color
                    streak_length = 1
                total_metric -= weights['sequence_reward'] * (streak_length - 1)

    empty_tubes_count = sum(1 for tube in tubes if not tube)
    total_metric -= empty_tubes_count * weights['empty_weight']

    return total_metric


def custom_heuristic(current_state):
    """
    Heuristic function for the tube sorting puzzle using custom logic.
    """
    tubes = current_state.tubes
    tube_size = current_state.tube_size
    color_goal_positions = {}
    weights = {'empty_tube_penalty': 10, 'color_consistency_bonus': 5, 'extra_color_penalty': 2,
               'top_color_bonus': 1, 'bottom_color_bonus': 1, 'sequence_bonus': 3}

    # Determine the target positions for each color in the goal state
    for idx, tube in enumerate(tubes):
        for pos, color in enumerate(tube):
            if color not in color_goal_positions:
                color_goal_positions[color] = []
            color_goal_positions[color].append((idx, pos))

    total_heuristic = 0
    for idx, tube in enumerate(tubes):
        current_streak_color = None
        streak_length = 0
        for pos, color in enumerate(tube):
            if color_goal_positions[color]:
                goal_idx, goal_pos = color_goal_positions[color].pop(0)  # Get the first target position for this color

                # Apply penalties and bonuses based on positions
                if pos == len(tube) - 1:
                    total_heuristic -= weights['top_color_bonus']
                if pos == 0:
                    total_heuristic -= weights['bottom_color_bonus']
                if pos > 0 and tube[pos - 1] == color:
                    total_heuristic -= weights['color_consistency_bonus']
                if idx != goal_idx:
                    total_heuristic += len(color_goal_positions[color]) * weights['extra_color_penalty']

                # Check for color sequences and apply bonuses
                if color == current_streak_color:
                    streak_length += 1
                else:
                    current_streak_color = color
                    streak_length = 1
                total_heuristic -= weights['sequence_bonus'] * (streak_length - 1)

    empty_tubes_count = sum(1 for tube in tubes if not tube)
    total_heuristic += empty_tubes_count * weights['empty_tube_penalty']

    return total_heuristic

# A star algorithm
def a_star(initial_state):
    open_set = PriorityQueue()
    open_set.put((0, initial_state))
    came_from = {}
    g_score = {initial_state: 0}
    f_score = {initial_state: heuristic(initial_state)}
    closed_set = set()

    count = 0
    while not open_set.empty():
        current = open_set.get()[1]

        if current.is_goal():
            print(f"Total Count: {count}")
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
                if neighbor not in g_score:
                    open_set.put((f_score[neighbor], neighbor))
                else:
                    # Update the priority queue
                    # Remove and reinsert the item to update its priority
                    # This ensures the priority queue maintains the correct order
                    open_set.queue = [(score, item) for score, item in open_set.queue if item != neighbor]
                    open_set.put((f_score[neighbor], neighbor))
        count += 1
    print(f"Total Count: {count}")
    return None

# A star algorithm
def debug_a_star(initial_state,debug):
    open_set = PriorityQueue()
    open_set.put((0, initial_state))
    came_from = {}
    g_score = {initial_state: 0}
    f_score = {initial_state: heuristic(initial_state)}
    closed_set = set()

    saved = initial_state
    count = 0
    while not open_set.empty():
        current = open_set.get()[1]

        if count == 4066 or count == 2118 :
            print("-" * 30)
            print(f"Step {count}: score {f_score[current]} - {current}")
            current.special_print()
            print("-"*30)

        if count == 2118:
            saved = current

        if count >= 2188 and current == saved:
            print(count)

        if count >= 2189:
            for item in open_set.queue:
                if item[1] == saved:
                    print("shit")
            # test2  = 0
            # if any(saved in item for item in open_set.queue):
            #     print(count)

        #debug
        if current in debug:
            print(f"{count}:F Score {f_score[current]}, step number {debug[current]} - {current}")

        if current.is_goal():
            return reconstruct_path(came_from, current)

        # if count >= 2118:
        if count == 4066:
            print(f"Test 1: {saved in closed_set}")
            print(f"Test 2: {current in closed_set}")
            print(f"Test 3")
            print(saved.__hash__() == current.__hash__())

        closed_set.add(current)

        neighbors = current.get_neighbors()
        for neighbor in neighbors:
            if neighbor in closed_set:
                continue

            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor)
                if neighbor not in g_score:
                  open_set.put((f_score[neighbor], neighbor))
                else:
                    open_set.queue = [(score, item) for score, item in open_set.queue if item != neighbor]
                    open_set.put((f_score[neighbor], neighbor))

        count += 1
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


# UI, Solves an liquid puzzle with our algorithm
def solve(initial_state):
    # debug
    # initial_state = LiquidPuzzle("[[], [0, 1, 1], [2, 0, 1], [0, 2, 2]]")
    debug = {}

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

        debug_counter = 0
        for step in path:
            # print(step)
            # step.special_print()
            debug[step] = debug_counter
            debug_counter += 1
    else:
        print("No solution found.")

    return path,debug

def solve_debug(initial_state,debug):
    # debug
    # initial_state = LiquidPuzzle("[[], [0, 1, 1], [2, 0, 1], [0, 2, 2]]")
    # debug = {}

    start_time = time.perf_counter()
    path = debug_a_star(initial_state,debug)
    end_time = time.perf_counter()
    if path:
        runtime = end_time - start_time
        minutes, seconds = divmod(runtime, 60)
        print("-" * 30)
        print(f"Runtime: {int(minutes)} minutes and {seconds:.5f} seconds")
        print("Number of Moves: {}".format(len(path) - 1))
        print("-" * 30)

        debug_counter = 0
        # for step in path:
            # print(step)
            # step.special_print()
            # debug[step] = debug_counter
            # debug_counter += 1
    else:
        print("No solution found.")


# UI, Build a random Liquid Puzzle
def createRandom():
    print("-" * 30)
    puzzle = LiquidPuzzle("[[]]")
    print("Please enter the amount of tubes, size of a tube and amount of colors in the following "
          "format:\nTubes_Amount Tube_Size Color_Amount")

    # while function that runs until the value given are correct for creating a final result
    while True:
        str_in = input("Enter values:")
        str_in = str_in.strip().split(" ")
        tubesAmount, tubeSize, colorAmount = int(str_in[0]), int(str_in[1]), int(str_in[2])
        # tubesAmount, tubeSize, colorAmount = 5,4,4
        if puzzle.buildComplete(tubesAmount, tubeSize, colorAmount):
            print(puzzle.tubes)
            break
        else:
            print("Invalid Input, try Again")

    # Makes a random amount of moves arcading to the user
    print("You can now choose how many reverse moves to make")
    while True:
        print("-" * 30)
        str_in = input("Amount of Random Moves, write 0 to exit: ")
        counter = int(str_in)
        # counter = 1
        if counter == 0:
            break
        puzzle = puzzle.reverseBuild(counter, counter * 100)
        print("\n Result: ")
        puzzle.special_print()


# UI, the User interface
def menu():
    print("-" * 30)
    print("Enter 1 for solving a liquid puzzle and 2 for creating a random one:")
    str_in = input("Input: ")
    value = int(str_in)
    if value == 1:
        correctInput = False
        while not correctInput:
            str_in = input("\nPlease enter the Liquid Puzzle: ")
            try:
                puzzle = LiquidPuzzle(str_in)
                print("\nEnter 1 for automatic and 2 for manual:")
                str_in = input("Input: ")
                value = int(str_in)
                if value == 1:
                    solve(puzzle)
                else:
                    manuel_solving(puzzle)
                break
            except ValueError:
                print("The Input does not stand by the rules of the Game")
    else:
        createRandom()


# UI, runs the manuel ui for solving a liquid puzzle
def manuel_solving(puzzle):
    playing = True
    print("-" * 30)
    print("To move a liquid from one tube to another \nEnter both tube numbers in the following format: 'from' 'to' "
          "example: 1 6")
    puzzle.special_print()
    # puzzle.moveCorrectness(4,5) #debug
    while playing:
        print("-" * 30)
        move = input("Enter the next move, write 0 to exit: ")
        move = move.split(" ")
        if int(move[0]) == 0:
            break
        tubeFrom, tubeTo = int(move[0]), int(move[1])
        # tubeFrom, tubeTo = 2, 1 # debug
        if not puzzle.is_valid_move(tubeFrom - 1, tubeTo - 1):
            print("Invalid Move, try Again")
        else:
            puzzle = puzzle.move(tubeFrom - 1, tubeTo - 1)
            puzzle.special_print()


if __name__ == '__main__':
    # 14 - [[], [], [], [], [], [], [], [],[], [], [], [],[], [], [], [],[], [], [], [],[4, 13, 9, 16, 17, 12, 9, 12, 4, 7, 11, 3, 17, 19, 15, 0, 6, 13, 11, 19], [5, 5, 5, 5, 5, 6, 18, 13, 5, 6, 6, 0, 10, 12, 16, 1, 5, 5, 7, 13], [14, 19, 18, 0, 6, 1, 19, 11, 0, 10, 17, 16, 0, 14, 9, 1, 4, 11, 16, 2], [7, 7, 11, 16, 16, 15, 3, 6, 8, 2, 3, 8, 14, 7, 8, 4, 6, 12, 4, 9], [3, 12, 13, 10, 12, 10, 3, 2, 11, 15, 5, 5, 11, 9, 14, 14, 15, 10, 2, 0], [9, 9, 9, 9, 8, 7, 4, 6, 9, 14, 5, 17, 11, 3, 6, 13, 15, 10, 3, 7], [10, 16, 8, 1, 3, 4, 14, 1, 17, 10, 13, 9, 1, 4, 19, 5, 10, 16, 16, 18], [11, 15, 4, 2, 2, 0, 1, 14, 5, 5, 3, 17, 8, 17, 7, 18, 7, 16, 18, 12], [19, 8, 6, 0, 10, 3, 5, 6, 19, 8, 8, 3, 11, 2, 9, 18, 6, 16, 1, 19], [13, 13, 13, 0, 14, 8, 1, 6, 9, 14, 7, 16, 1, 18, 1, 18, 19, 7, 15, 18], [7, 2, 2, 19, 2, 16, 18, 4, 8, 0, 11, 6, 19, 14, 3, 10, 10, 14, 2, 16], [15, 15, 11, 11, 6, 12, 12, 5, 15, 5, 8, 10, 17, 8, 11, 18, 6, 18, 2, 8], [1, 0, 17, 5, 12, 17, 3, 9, 16, 18, 10, 19, 13, 0, 9, 13, 2, 16, 10, 16], [17, 17, 17, 17, 17, 17, 10, 12, 15, 11, 11, 1, 0, 4, 19, 14, 15, 5, 0, 14], [18, 13, 12, 19, 15, 8, 10, 2, 10, 3, 2, 12, 9, 17, 5, 7, 17, 9, 7, 19], [0, 7, 4, 19, 3, 8, 6, 14, 12, 12, 18, 15, 3, 1, 4, 9, 1, 8, 12, 1], [0, 19, 16, 3, 16, 0, 9, 13, 9, 13, 13, 3, 8, 15, 19, 15, 1, 13, 7, 2], [12, 4, 18, 15, 14, 4, 7, 0, 12, 2, 13, 16, 19, 1, 14, 10, 13, 8, 3, 2], [19, 14, 1, 4, 18, 15, 8, 2, 2, 0, 14, 18, 1, 11, 4, 13, 4, 6, 10, 7], [12, 17, 0, 6, 17, 18, 15, 3, 4, 7, 11, 4, 11, 18, 15, 12, 6, 11, 14, 7]]
    # 15 - [[], [], [], [], [], [], [], [], [], [], [10, 14, 5, 48, 23, 16, 3, 23, 16, 2, 20, 24, 22, 20, 8, 8, 18, 19, 23, 1, 7, 22, 39, 40, 1, 22, 7, 20, 2, 37, 13, 24, 26, 38, 17, 22, 22, 29, 23, 46, 36, 5, 21, 3, 34, 1, 5, 3, 7, 12], [11, 5, 26, 35, 29, 15, 40, 27, 10, 14, 18, 38, 23, 4, 44, 25, 48, 35, 38, 10, 30, 27, 15, 19, 30, 28, 41, 21, 42, 41, 1, 5, 19, 36, 47, 25, 3, 36, 35, 48, 27, 43, 45, 42, 28, 27, 44, 8, 40, 0], [9, 39, 2, 32, 41, 24, 43, 9, 18, 29, 25, 35, 18, 34, 2, 37, 24, 37, 23, 10, 15, 37, 17, 34, 11, 16, 32, 33, 39, 31, 31, 0, 1, 3, 13, 42, 21, 46, 23, 30, 5, 39, 35, 46, 0, 7, 28, 14, 10, 49], [31, 12, 2, 4, 7, 30, 30, 30, 4, 31, 41, 7, 45, 45, 9, 43, 47, 30, 31, 20, 7, 15, 29, 23, 9, 49, 8, 11, 21, 21, 1, 14, 17, 21, 38, 10, 2, 43, 48, 48, 30, 25, 8, 14, 27, 5, 6, 20, 17, 48], [7, 27, 37, 45, 5, 31, 7, 44, 9, 48, 28, 24, 18, 46, 42, 18, 15, 30, 44, 49, 26, 49, 9, 36, 21, 8, 3, 11, 23, 0, 25, 10, 10, 3, 28, 24, 26, 45, 20, 20, 13, 37, 25, 32, 48, 6, 4, 13, 6, 15], [15, 15, 15, 43, 10, 5, 27, 7, 46, 9, 3, 4, 31, 13, 44, 23, 28, 15, 27, 44, 14, 38, 6, 28, 15, 34, 37, 14, 43, 40, 2, 12, 8, 34, 3, 49, 6, 44, 12, 17, 35, 47, 25, 24, 30, 21, 39, 24, 26, 41], [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 19, 11, 23, 21, 10, 15, 8, 49, 10, 14, 16, 11, 30, 38, 12, 34, 34, 25, 9, 26, 13, 44, 10, 26, 35, 38, 16, 1, 14, 41, 8, 48, 37, 10, 5, 37, 46], [17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 2, 38, 48, 0, 1, 41, 1, 47, 14, 22, 1, 6, 27, 37, 17, 1, 36, 34, 1, 25, 18, 18, 23, 8, 10, 1, 47, 11, 24, 42, 1, 8, 40, 2, 33, 18, 33], [46, 17, 31, 3, 30, 13, 34, 11, 1, 37, 10, 5, 30, 28, 31, 47, 30, 31, 18, 32, 34, 0, 24, 21, 22, 30, 37, 11, 44, 6, 11, 29, 49, 32, 25, 32, 3, 4, 7, 12, 31, 3, 8, 12, 25, 13, 20, 0, 9, 21], [19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 49, 36, 1, 28, 35, 3, 49, 27, 2, 30, 10, 28, 37, 10, 23, 12, 0, 15, 4, 39, 39, 4, 4, 5, 7, 47, 3, 15, 7, 35, 38, 40, 23, 43, 36, 23], [11, 0, 24, 19, 5, 9, 43, 3, 30, 49, 27, 4, 13, 37, 38, 8, 4, 36, 11, 8, 12, 31, 41, 25, 10, 28, 13, 11, 39, 24, 45, 5, 43, 45, 26, 5, 46, 23, 7, 7, 24, 16, 34, 11, 22, 45, 28, 9, 9, 9], [21, 21, 21, 21, 21, 21, 21, 21, 42, 47, 32, 18, 35, 13, 13, 39, 31, 36, 29, 37, 39, 19, 44, 45, 8, 12, 28, 10, 16, 17, 2, 0, 6, 39, 10, 37, 32, 3, 28, 38, 25, 41, 13, 2, 44, 2, 37, 49, 18, 12], [22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 13, 22, 35, 39, 17, 22, 47, 29, 34, 36, 11, 0, 14, 13, 14, 15, 26, 39, 38, 26, 41, 41, 20, 13, 17, 44, 44, 44, 3, 0, 3, 49, 36, 3, 28, 29, 29, 40, 48, 21], [23, 23, 23, 23, 23, 23, 23, 23, 23, 5, 35, 27, 24, 15, 17, 15, 40, 34, 1, 32, 40, 45, 13, 16, 42, 22, 23, 20, 12, 49, 12, 6, 35, 37, 49, 22, 15, 49, 26, 47, 23, 46, 28, 42, 24, 46, 24, 26, 4, 16], [24, 24, 24, 24, 24, 24, 24, 24, 24, 9, 22, 23, 4, 39, 2, 20, 36, 27, 9, 47, 9, 20, 31, 4, 19, 45, 44, 23, 4, 32, 8, 49, 39, 43, 16, 17, 37, 23, 20, 21, 3, 3, 21, 35, 26, 15, 20, 2, 5, 38], [1, 0, 40, 13, 30, 49, 28, 6, 36, 37, 22, 29, 9, 14, 36, 32, 30, 39, 25, 19, 37, 45, 40, 17, 24, 7, 26, 1, 24, 1, 1, 7, 4, 17, 21, 4, 11, 45, 23, 1, 10, 43, 14, 5, 4, 32, 33, 42, 44, 26], [15, 12, 34, 3, 29, 23, 30, 47, 40, 22, 4, 8, 29, 34, 1, 29, 29, 13, 25, 28, 14, 44, 10, 16, 2, 35, 40, 16, 8, 24, 10, 42, 12, 41, 11, 2, 25, 46, 22, 22, 25, 6, 33, 45, 18, 20, 9, 27, 32, 26], [48, 5, 38, 21, 37, 17, 21, 32, 41, 26, 46, 45, 16, 1, 46, 4, 49, 3, 39, 15, 44, 12, 34, 14, 41, 28, 32, 44, 4, 48, 24, 14, 13, 47, 10, 34, 35, 4, 28, 15, 24, 24, 48, 45, 31, 28, 32, 24, 10, 44], [28, 28, 28, 28, 28, 28, 34, 37, 22, 27, 38, 27, 49, 23, 33, 33, 6, 15, 37, 44, 5, 45, 21, 31, 7, 21, 12, 44, 26, 44, 4, 43, 49, 30, 5, 13, 12, 31, 21, 44, 5, 14, 7, 46, 6, 31, 0, 1, 18, 19], [29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 22, 42, 46, 13, 14, 40, 38, 47, 33, 38, 14, 14, 35, 19, 47, 12, 25, 13, 15, 42, 15, 28, 31, 31, 14, 24, 38, 28, 39, 9, 43, 8, 43, 0, 49, 24, 46, 3, 3, 39], [30, 30, 30, 30, 30, 5, 2, 39, 9, 38, 34, 1, 19, 40, 34, 1, 7, 5, 18, 10, 46, 30, 15, 27, 45, 25, 39, 32, 20, 46, 21, 32, 2, 18, 19, 43, 22, 46, 11, 14, 11, 40, 14, 41, 3, 3, 3, 11, 31, 9], [31, 31, 11, 43, 32, 38, 10, 20, 36, 45, 32, 32, 13, 11, 6, 38, 21, 11, 8, 15, 6, 12, 0, 18, 34, 9, 9, 11, 14, 31, 0, 39, 2, 12, 48, 29, 33, 10, 28, 37, 43, 40, 16, 26, 13, 41, 0, 24, 49, 18], [32, 32, 32, 32, 32, 32, 32, 32, 32, 6, 41, 42, 46, 27, 46, 7, 44, 25, 28, 40, 8, 32, 26, 40, 6, 20, 47, 48, 27, 18, 48, 5, 35, 4, 46, 4, 7, 14, 0, 4, 45, 39, 15, 13, 19, 44, 9, 9, 9, 9], [33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 45, 17, 35, 37, 9, 24, 47, 25, 10, 41, 22, 18, 7, 34, 42, 49, 37, 35, 35, 3, 6, 39, 44, 32, 10, 49, 26], [34, 34, 34, 34, 35, 35, 41, 39, 29, 25, 8, 34, 43, 13, 1, 6, 47, 39, 47, 42, 12, 0, 3, 43, 17, 1, 31, 15, 29, 12, 22, 30, 13, 46, 8, 25, 19, 45, 12, 35, 25, 36, 22, 23, 41, 15, 2, 26, 0, 43], [35, 35, 35, 35, 35, 35, 35, 35, 46, 3, 25, 27, 15, 38, 0, 34, 29, 30, 7, 3, 30, 31, 45, 13, 40, 19, 8, 18, 25, 21, 36, 23, 23, 46, 31, 31, 20, 7, 31, 20, 21, 12, 11, 21, 9, 13, 21, 44, 0, 6], [36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 23, 34, 1, 11, 38, 8, 30, 44, 40, 15, 5, 26, 3, 6, 21, 26, 3, 25, 20, 7, 31, 0, 41, 9, 3, 25, 20, 12, 4, 36, 16, 14, 43, 7, 27, 47, 28, 20], [45, 18, 27, 5, 41, 25, 8, 43, 13, 37, 41, 29, 14, 4, 28, 44, 43, 34, 27, 13, 23, 2, 44, 25, 45, 37, 2, 11, 47, 0, 37, 47, 27, 24, 27, 2, 20, 36, 18, 14, 25, 22, 30, 6, 22, 7, 30, 48, 10, 29], [38, 38, 38, 38, 38, 38, 2, 48, 21, 0, 37, 38, 47, 36, 42, 22, 41, 43, 3, 16, 34, 20, 44, 37, 45, 18, 43, 40, 4, 21, 11, 17, 34, 13, 39, 0, 48, 34, 19, 21, 25, 8, 4, 11, 12, 5, 14, 6, 28, 6], [39, 39, 39, 39, 39, 39, 6, 30, 41, 35, 36, 13, 3, 44, 37, 21, 30, 26, 49, 10, 33, 43, 42, 47, 46, 39, 6, 32, 35, 6, 38, 24, 40, 43, 18, 24, 22, 26, 46, 37, 2, 4, 47, 8, 16, 25, 49, 25, 9, 47], [40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 11, 35, 36, 40, 23, 28, 47, 48, 31, 28, 20, 35, 29, 23, 27, 48, 17, 30, 48, 49, 41, 39, 20, 39, 27, 24, 19, 18, 12, 47, 33, 8, 8, 18, 2, 47], [49, 32, 5, 39, 43, 7, 27, 1, 34, 34, 18, 31, 26, 11, 27, 8, 25, 20, 20, 2, 13, 27, 8, 5, 37, 15, 30, 19, 9, 42, 23, 26, 10, 22, 5, 5, 28, 6, 33, 14, 27, 36, 44, 45, 39, 30, 39, 29, 2, 13], [42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 18, 8, 29, 8, 31, 9, 20, 28, 9, 27, 17, 38, 39, 19, 48, 9, 7, 18, 37, 14, 49, 17, 41, 47, 35, 0, 24, 5], [43, 43, 43, 43, 43, 43, 43, 43, 43, 3, 27, 14, 29, 18, 43, 1, 14, 39, 33, 44, 31, 19, 46, 44, 40, 7, 16, 43, 24, 34, 11, 9, 18, 17, 17, 6, 21, 25, 9, 45, 26, 32, 31, 23, 33, 21, 11, 4, 0, 0], [26, 45, 32, 5, 49, 33, 30, 1, 9, 4, 1, 40, 5, 14, 39, 28, 11, 17, 38, 2, 36, 22, 37, 18, 16, 13, 47, 2, 34, 15, 1, 28, 14, 40, 10, 16, 17, 10, 27, 47, 12, 11, 8, 31, 26, 11, 26, 0, 6, 3], [45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 18, 35, 20, 17, 45, 37, 18, 43, 10, 40, 22, 44, 18, 16, 4, 21, 19, 44, 41, 1, 47, 27, 13, 35, 37, 0, 28, 16, 15, 3, 15, 4, 26, 17, 29, 47, 0, 4, 45], [46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 39, 26, 3, 48, 24, 24, 47, 31, 18, 31, 22, 11, 8, 41, 19, 25, 36, 49, 7, 1, 7, 22, 5, 41, 23, 26, 24, 29, 41, 20, 1, 6, 26, 38, 28, 18, 19], [30, 30, 49, 12, 48, 12, 31, 41, 38, 1, 32, 10, 32, 9, 10, 20, 4, 3, 18, 49, 1, 26, 14, 36, 31, 3, 40, 2, 42, 35, 7, 20, 41, 47, 3, 29, 36, 14, 5, 45, 12, 1, 26, 29, 11, 5, 35, 16, 12, 45], [48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 12, 27, 36, 5, 32, 31, 12, 47, 7, 27, 37, 38, 5, 7, 14, 48, 45, 16, 32, 20, 8, 6, 10, 13, 18, 47, 38, 23, 18, 15, 28, 37, 9, 4, 43, 34, 25, 39], [49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 42, 33, 33, 19, 44, 43, 15, 31, 14, 8, 24, 41, 0, 25, 37, 1, 2, 4, 16, 2, 28, 27, 25, 18, 33, 6, 46, 49, 12, 27, 15, 6, 29, 5, 24, 7, 35, 0, 35], [47, 29, 19, 11, 45, 14, 30, 4, 4, 25, 36, 19, 0, 15, 15, 5, 48, 38, 28, 35, 24, 34, 1, 16, 0, 39, 13, 17, 32, 44, 6, 12, 21, 11, 40, 14, 36, 22, 27, 29, 10, 47, 3, 5, 15, 10, 18, 7, 25, 29], [19, 8, 35, 44, 33, 15, 19, 38, 20, 49, 22, 26, 0, 2, 2, 44, 18, 48, 33, 45, 27, 11, 2, 10, 41, 13, 32, 6, 43, 11, 6, 25, 15, 27, 14, 32, 49, 21, 6, 39, 12, 48, 20, 41, 36, 7, 33, 47, 9, 20], [6, 38, 46, 29, 48, 28, 45, 12, 47, 29, 36, 12, 2, 28, 15, 36, 2, 4, 38, 4, 37, 13, 28, 33, 18, 43, 20, 47, 41, 14, 49, 37, 0, 27, 10, 25, 17, 31, 4, 18, 7, 20, 40, 34, 33, 7, 7, 25, 45, 9], [15, 11, 22, 49, 26, 41, 2, 20, 26, 25, 20, 23, 35, 17, 20, 32, 47, 16, 6, 38, 18, 11, 25, 19, 40, 6, 19, 31, 25, 11, 7, 8, 38, 5, 27, 36, 33, 47, 8, 43, 37, 34, 19, 23, 2, 38, 40, 32, 33, 0], [27, 31, 20, 44, 21, 25, 26, 27, 13, 32, 12, 42, 38, 32, 4, 10, 5, 26, 47, 0, 41, 44, 34, 44, 0, 23, 8, 24, 14, 21, 1, 48, 12, 46, 41, 42, 24, 29, 46, 13, 13, 42, 46, 1, 48, 22, 9, 9, 9, 9], [31, 34, 4, 22, 2, 34, 39, 10, 14, 7, 22, 39, 46, 26, 34, 28, 46, 31, 44, 35, 44, 26, 10, 7, 46, 17, 13, 37, 26, 43, 41, 41, 38, 30, 41, 33, 26, 38, 47, 43, 8, 12, 6, 1, 30, 0, 33, 18, 6, 10], [31, 41, 36, 19, 30, 30, 4, 8, 41, 48, 32, 15, 22, 15, 13, 2, 8, 9, 1, 20, 27, 34, 47, 35, 42, 16, 23, 37, 11, 40, 16, 18, 16, 30, 17, 0, 20, 10, 2, 44, 13, 16, 0, 17, 0, 38, 28, 26, 1, 26], [1, 21, 8, 7, 38, 29, 6, 41, 16, 27, 12, 14, 4, 20, 35, 12, 12, 4, 48, 25, 7, 19, 37, 5, 36, 17, 5, 16, 29, 0, 40, 3, 8, 3, 38, 6, 31, 20, 5, 5, 37, 7, 7, 9, 18, 11, 2, 10, 44, 20], [2, 16, 14, 6, 11, 11, 20, 13, 30, 32, 21, 29, 3, 46, 44, 15, 42, 9, 19, 31, 17, 45, 47, 23, 17, 42, 2, 48, 19, 37, 10, 26, 2, 41, 21, 27, 6, 11, 4, 39, 0, 3, 3, 43, 29, 42, 8, 29, 12, 8], [30, 42, 34, 43, 43, 17, 41, 2, 7, 47, 30, 48, 19, 16, 32, 41, 36, 23, 49, 9, 6, 48, 16, 34, 0, 2, 5, 34, 40, 13, 41, 22, 34, 1, 14, 0, 16, 6, 36, 12, 39, 21, 12, 14, 8, 35, 15, 12, 27, 6]]
    # 16 - [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [11, 20, 28, 8, 27, 33, 48, 7, 3, 47, 30, 9, 18, 8, 29, 48, 38, 25, 31, 9, 35, 19, 6, 39, 4, 46, 1, 43, 26, 26, 44, 25, 11, 5, 4, 43, 43, 37, 10, 5, 9, 7, 20, 25, 8, 41, 2, 40, 45, 10], [32, 28, 1, 16, 23, 48, 22, 28, 16, 35, 29, 5, 37, 9, 47, 23, 8, 37, 1, 11, 30, 41, 6, 48, 39, 17, 8, 15, 7, 34, 20, 27, 24, 28, 37, 42, 24, 25, 14, 44, 3, 36, 44, 17, 36, 14, 19, 20, 42, 38], [46, 5, 47, 17, 7, 41, 45, 11, 42, 23, 2, 1, 28, 24, 7, 24, 9, 40, 12, 14, 9, 17, 33, 37, 17, 37, 42, 15, 7, 43, 0, 45, 16, 37, 23, 13, 15, 6, 15, 12, 23, 32, 12, 25, 18, 5, 36, 37, 32, 17], [21, 37, 1, 12, 44, 14, 3, 25, 40, 2, 2, 33, 23, 28, 47, 23, 33, 23, 12, 18, 46, 17, 44, 18, 10, 44, 11, 36, 49, 32, 18, 36, 49, 2, 43, 35, 30, 0, 25, 11, 47, 43, 37, 26, 1, 34, 13, 43, 32, 21], [11, 46, 20, 3, 47, 18, 30, 29, 49, 36, 35, 15, 14, 10, 30, 4, 16, 49, 14, 46, 43, 38, 49, 14, 43, 35, 5, 32, 34, 49, 17, 44, 38, 38, 7, 14, 28, 26, 11, 11, 15, 28, 39, 39, 24, 14, 7, 4, 10, 32], [13, 42, 18, 24, 20, 49, 49, 28, 21, 48, 2, 18, 7, 15, 25, 44, 24, 45, 0, 14, 16, 24, 36, 26, 45, 16, 45, 5, 3, 21, 48, 40, 3, 20, 8, 43, 26, 39, 40, 3, 14, 19, 40, 33, 12, 40, 38, 3, 49, 21], [6, 31, 32, 6, 20, 19, 10, 10, 19, 4, 31, 38, 3, 44, 35, 47, 26, 5, 21, 40, 18, 26, 37, 3, 34, 12, 39, 36, 44, 1, 40, 33, 2, 27, 19, 48, 47, 9, 45, 18, 29, 34, 1, 37, 12, 45, 34, 39, 19, 19], [42, 4, 41, 27, 21, 42, 44, 7, 34, 36, 23, 33, 7, 10, 0, 48, 33, 9, 35, 8, 23, 6, 47, 3, 29, 33, 31, 22, 48, 20, 14, 12, 25, 43, 20, 45, 0, 21, 40, 21, 16, 33, 28, 0, 15, 2, 33, 42, 27, 30], [31, 0, 18, 1, 45, 38, 47, 7, 38, 19, 5, 42, 6, 21, 24, 33, 38, 5, 5, 17, 41, 31, 16, 2, 29, 13, 48, 46, 41, 17, 11, 36, 43, 49, 12, 35, 29, 27, 7, 0, 22, 17, 24, 2, 40, 29, 15, 26, 42, 37], [29, 29, 29, 29, 29, 29, 3, 42, 13, 3, 28, 32, 20, 40, 17, 33, 44, 4, 30, 17, 34, 43, 31, 16, 4, 6, 34, 26, 9, 49, 28, 28, 41, 34, 28, 23, 23, 20, 44, 21, 12, 43, 32, 19, 1, 16, 40, 32, 6, 44], [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 2, 14, 40, 24, 6, 48, 1, 32, 27, 41, 3, 0, 5, 33, 44, 23, 21, 37, 15, 26, 27, 6, 36, 16, 41, 27, 20, 0, 16, 41, 16, 8, 10, 23, 44, 4, 46, 19], [31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 30, 12, 19, 36, 31, 45, 19, 18, 28, 49, 1, 12, 31, 43, 5, 35, 11, 49, 13, 20, 28, 48, 29, 20, 30, 19, 32, 23, 30, 34, 17, 39, 9, 16, 35, 17, 3, 48, 47, 45], [21, 40, 43, 13, 29, 35, 34, 18, 35, 15, 46, 22, 9, 33, 8, 8, 8, 31, 20, 1, 11, 49, 47, 26, 49, 10, 3, 5, 14, 19, 8, 39, 25, 45, 8, 33, 31, 44, 0, 46, 4, 1, 42, 37, 46, 17, 15, 31, 47, 45], [12, 12, 4, 45, 19, 3, 28, 32, 3, 46, 33, 6, 37, 24, 6, 24, 0, 35, 35, 11, 21, 21, 24, 4, 13, 7, 29, 39, 5, 41, 22, 26, 20, 6, 10, 25, 6, 2, 6, 26, 14, 43, 5, 15, 35, 40, 18, 12, 13, 27], [22, 12, 23, 39, 25, 6, 26, 46, 26, 46, 39, 10, 13, 7, 37, 31, 29, 13, 12, 4, 35, 48, 10, 1, 10, 11, 19, 34, 3, 36, 11, 34, 1, 2, 11, 30, 28, 20, 32, 42, 41, 45, 25, 44, 21, 0, 25, 29, 38, 9], [36, 32, 24, 35, 5, 44, 49, 29, 22, 19, 16, 32, 2, 3, 5, 37, 36, 25, 11, 32, 35, 8, 43, 42, 46, 47, 2, 2, 42, 42, 24, 21, 0, 8, 0, 8, 13, 43, 44, 45, 46, 34, 21, 17, 25, 10, 4, 26, 3, 24], [24, 0, 11, 21, 41, 36, 35, 10, 37, 41, 18, 12, 0, 39, 15, 8, 22, 49, 43, 30, 12, 27, 19, 17, 19, 9, 5, 38, 36, 28, 8, 25, 38, 46, 1, 22, 20, 18, 8, 8, 3, 36, 41, 2, 33, 27, 32, 24, 20, 46], [35, 6, 27, 9, 28, 46, 17, 29, 46, 38, 45, 13, 27, 22, 26, 43, 48, 9, 21, 2, 17, 24, 7, 47, 23, 34, 30, 37, 18, 35, 27, 3, 1, 31, 1, 24, 12, 0, 11, 17, 0, 10, 23, 20, 14, 6, 16, 18, 33, 19], [38, 38, 38, 38, 38, 39, 21, 28, 25, 37, 29, 40, 2, 1, 9, 27, 19, 13, 6, 16, 49, 20, 27, 35, 16, 44, 20, 45, 13, 10, 15, 5, 26, 35, 11, 47, 4, 20, 17, 16, 38, 8, 9, 34, 2, 30, 26, 15, 33, 28], [43, 42, 8, 18, 44, 14, 34, 4, 1, 8, 27, 10, 27, 42, 31, 2, 45, 44, 18, 9, 47, 47, 32, 33, 29, 11, 34, 15, 15, 28, 5, 12, 45, 20, 10, 38, 35, 34, 37, 34, 4, 30, 11, 28, 33, 7, 5, 9, 25, 40], [41, 19, 49, 33, 28, 26, 47, 37, 47, 13, 26, 39, 26, 17, 39, 37, 45, 15, 23, 9, 27, 25, 5, 48, 20, 7, 15, 47, 42, 23, 41, 13, 5, 2, 4, 23, 47, 13, 1, 40, 33, 44, 39, 5, 18, 29, 32, 48, 12, 22], [41, 41, 41, 41, 41, 41, 41, 29, 32, 17, 2, 42, 45, 45, 34, 47, 19, 43, 4, 9, 32, 17, 7, 11, 49, 14, 29, 19, 28, 12, 5, 46, 9, 32, 7, 23, 48, 47, 5, 13, 17, 21, 35, 29, 49, 31, 27, 45, 43, 27], [42, 42, 42, 42, 42, 42, 33, 32, 35, 6, 0, 5, 0, 13, 31, 26, 15, 27, 20, 42, 30, 37, 0, 44, 4, 22, 37, 32, 29, 8, 23, 1, 6, 46, 31, 38, 32, 33, 2, 13, 23, 7, 22, 3, 9, 0, 39, 49, 13, 9], [17, 20, 0, 9, 33, 46, 43, 26, 41, 13, 7, 28, 24, 24, 35, 45, 19, 39, 5, 0, 28, 0, 17, 18, 2, 20, 31, 14, 35, 7, 21, 36, 29, 21, 10, 19, 16, 26, 21, 20, 16, 41, 24, 23, 18, 3, 33, 23, 16, 2], [34, 15, 42, 39, 4, 2, 19, 3, 15, 44, 20, 45, 7, 26, 28, 40, 39, 20, 6, 9, 36, 34, 15, 16, 31, 32, 18, 15, 48, 14, 27, 12, 17, 44, 28, 8, 22, 8, 29, 21, 35, 15, 49, 3, 10, 24, 7, 23, 22, 14], [42, 36, 0, 14, 21, 0, 4, 42, 27, 45, 30, 48, 13, 22, 5, 30, 22, 9, 4, 3, 19, 36, 9, 28, 28, 21, 14, 46, 48, 7, 4, 16, 46, 25, 6, 48, 20, 18, 3, 22, 25, 46, 31, 29, 6, 2, 48, 41, 27, 37], [18, 19, 43, 27, 42, 11, 4, 46, 11, 22, 37, 26, 26, 5, 44, 30, 16, 30, 12, 14, 2, 19, 8, 27, 14, 16, 49, 26, 2, 7, 6, 38, 4, 29, 43, 30, 25, 7, 19, 0, 25, 48, 39, 35, 13, 33, 34, 1, 16, 23], [38, 45, 34, 33, 3, 6, 18, 18, 1, 48, 49, 13, 40, 26, 23, 20, 15, 43, 9, 7, 43, 12, 30, 35, 8, 35, 14, 30, 31, 5, 42, 0, 32, 7, 38, 24, 5, 22, 39, 46, 46, 27, 40, 2, 25, 47, 41, 27, 36, 47], [41, 16, 8, 13, 47, 41, 48, 43, 40, 11, 41, 48, 24, 8, 42, 32, 31, 42, 13, 22, 42, 49, 10, 32, 14, 46, 36, 2, 43, 19, 0, 38, 27, 19, 22, 43, 12, 42, 43, 8, 14, 44, 25, 34, 37, 1, 8, 25, 25, 41], [18, 44, 13, 24, 4, 20, 12, 17, 20, 14, 16, 3, 5, 6, 38, 28, 42, 34, 43, 4, 29, 26, 47, 39, 23, 34, 17, 14, 42, 33, 48, 2, 22, 15, 26, 42, 26, 35, 37, 19, 7, 41, 34, 36, 26, 38, 16, 25, 22, 3], [41, 27, 47, 24, 39, 48, 44, 1, 11, 4, 37, 38, 42, 7, 40, 11, 41, 34, 23, 1, 39, 32, 1, 37, 46, 22, 31, 41, 7, 49, 44, 24, 34, 22, 44, 25, 39, 7, 21, 3, 48, 47, 33, 48, 38, 13, 0, 40, 39, 0], [48, 31, 8, 19, 32, 27, 35, 9, 46, 6, 18, 9, 11, 16, 28, 17, 46, 47, 35, 12, 33, 25, 16, 39, 25, 23, 8, 6, 12, 34, 44, 46, 21, 0, 12, 2, 31, 43, 17, 10, 33, 2, 23, 10, 10, 16, 13, 45, 17, 21], [36, 35, 37, 15, 29, 36, 48, 15, 38, 15, 6, 4, 41, 14, 41, 49, 39, 18, 33, 41, 1, 28, 32, 25, 20, 19, 16, 11, 34, 38, 30, 5, 8, 40, 30, 9, 26, 42, 45, 49, 9, 16, 15, 24, 21, 27, 32, 46, 48, 19], [8, 49, 2, 4, 11, 36, 13, 28, 42, 14, 34, 36, 14, 0, 22, 45, 6, 17, 31, 27, 4, 9, 22, 2, 41, 40, 30, 7, 40, 22, 26, 47, 46, 11, 42, 26, 2, 36, 12, 32, 45, 24, 1, 40, 22, 21, 18, 45, 5, 47], [38, 49, 32, 36, 15, 47, 46, 40, 25, 45, 49, 26, 33, 33, 36, 38, 41, 1, 18, 14, 41, 31, 15, 17, 28, 0, 44, 8, 11, 22, 45, 28, 22, 45, 10, 21, 22, 10, 10, 47, 9, 27, 36, 0, 3, 24, 48, 19, 44, 15], [3, 11, 43, 1, 3, 3, 35, 47, 3, 22, 18, 10, 7, 6, 33, 5, 24, 36, 29, 29, 27, 47, 9, 16, 38, 48, 6, 0, 21, 22, 4, 37, 17, 38, 13, 20, 48, 34, 18, 47, 6, 39, 38, 32, 45, 48, 35, 3, 37, 19], [4, 21, 25, 47, 15, 6, 41, 1, 3, 20, 30, 37, 11, 49, 5, 25, 44, 21, 35, 37, 37, 18, 24, 30, 46, 8, 1, 7, 22, 18, 16, 49, 48, 36, 40, 48, 34, 32, 3, 22, 26, 9, 0, 4, 36, 14, 2, 6, 47, 15], [35, 14, 13, 15, 18, 1, 30, 36, 4, 6, 15, 38, 14, 19, 19, 44, 24, 37, 23, 23, 1, 18, 40, 36, 5, 44, 39, 29, 20, 4, 35, 40, 41, 15, 39, 18, 31, 10, 43, 40, 22, 18, 7, 29, 14, 11, 33, 25, 44, 36], [49, 39, 29, 14, 38, 3, 10, 21, 36, 38, 23, 29, 7, 46, 38, 16, 33, 43, 21, 20, 37, 4, 34, 0, 43, 45, 21, 17, 49, 43, 27, 3, 25, 0, 33, 29, 40, 22, 1, 45, 20, 25, 27, 10, 7, 39, 14, 36, 46, 11], [48, 28, 0, 7, 30, 37, 28, 0, 34, 29, 34, 9, 12, 49, 1, 24, 40, 8, 43, 37, 20, 2, 14, 11, 35, 1, 49, 44, 32, 16, 27, 33, 19, 12, 5, 20, 33, 34, 15, 23, 27, 14, 49, 44, 22, 18, 17, 25, 3, 44], [35, 49, 23, 34, 28, 44, 18, 21, 27, 9, 27, 39, 23, 31, 31, 49, 47, 12, 12, 1, 16, 5, 12, 39, 45, 44, 8, 36, 16, 26, 31, 17, 39, 21, 9, 43, 28, 26, 22, 19, 26, 26, 13, 41, 4, 40, 45, 14, 39, 11], [11, 36, 31, 2, 2, 25, 5, 10, 3, 24, 44, 48, 0, 11, 2, 41, 36, 19, 35, 38, 0, 39, 39, 38, 40, 37, 24, 47, 29, 26, 25, 12, 9, 47, 40, 34, 1, 43, 27, 13, 7, 13, 13, 33, 46, 7, 39, 23, 12, 13], [45, 10, 4, 2, 8, 18, 40, 15, 12, 9, 21, 49, 20, 6, 31, 37, 8, 40, 21, 22, 49, 13, 26, 23, 39, 15, 18, 40, 43, 24, 44, 16, 33, 47, 20, 12, 28, 32, 39, 26, 3, 24, 9, 43, 39, 35, 17, 19, 17, 22], [22, 17, 19, 40, 5, 36, 23, 1, 2, 27, 6, 18, 45, 5, 45, 24, 34, 34, 37, 16, 10, 2, 30, 34, 1, 28, 6, 18, 21, 37, 6, 4, 13, 22, 23, 22, 27, 0, 32, 41, 37, 10, 16, 28, 5, 5, 5, 32, 12, 15], [12, 11, 18, 41, 43, 9, 0, 14, 34, 43, 10, 11, 28, 24, 9, 37, 25, 5, 25, 43, 38, 30, 11, 22, 13, 48, 10, 21, 45, 7, 6, 38, 4, 27, 21, 10, 42, 33, 34, 41, 14, 23, 12, 25, 48, 46, 25, 22, 9, 6], [28, 17, 49, 42, 29, 20, 33, 17, 46, 32, 23, 4, 17, 3, 4, 7, 23, 15, 45, 7, 4, 0, 48, 8, 17, 36, 29, 1, 16, 24, 8, 30, 35, 3, 20, 13, 31, 0, 9, 49, 14, 25, 1, 45, 47, 40, 7, 46, 4, 49], [13, 34, 31, 36, 31, 10, 17, 10, 40, 15, 29, 42, 24, 39, 31, 27, 9, 42, 8, 17, 12, 36, 39, 8, 10, 33, 32, 4, 46, 30, 40, 46, 26, 37, 13, 19, 39, 4, 39, 6, 45, 23, 22, 40, 47, 30, 6, 30, 6, 5], [15, 16, 31, 9, 44, 48, 24, 38, 14, 23, 49, 6, 12, 47, 9, 30, 4, 40, 18, 10, 25, 21, 39, 49, 42, 10, 33, 24, 32, 24, 31, 35, 8, 2, 6, 47, 41, 22, 14, 36, 43, 40, 3, 26, 20, 11, 25, 42, 29, 16], [25, 18, 1, 7, 7, 32, 24, 46, 48, 30, 32, 46, 11, 21, 27, 38, 32, 15, 13, 28, 10, 13, 1, 47, 10, 43, 14, 19, 27, 35, 5, 2, 11, 28, 29, 11, 14, 23, 40, 37, 48, 46, 38, 34, 19, 7, 13, 46, 29, 15], [12, 45, 20, 46, 23, 17, 44, 0, 38, 35, 24, 11, 8, 42, 3, 16, 15, 1, 12, 6, 13, 13, 38, 33, 12, 36, 2, 35, 21, 49, 32, 16, 48, 47, 8, 1, 48, 2, 26, 29, 10, 16, 44, 10, 11, 10, 49, 4, 8, 28]]
    # 17 - [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [29, 11, 49, 38, 41, 36, 38, 39, 15, 33, 45, 34, 18, 9, 5, 34, 2, 22, 37, 2, 5, 1, 13, 15, 47, 46, 4, 10, 0, 31, 24, 21, 49, 13, 18, 34, 10, 40, 10, 17, 28, 47, 15, 31, 32, 9, 20, 41, 11, 33], [49, 27, 44, 18, 42, 31, 29, 13, 14, 39, 20, 48, 18, 31, 7, 26, 36, 19, 1, 42, 23, 17, 18, 49, 16, 8, 31, 23, 44, 1, 41, 31, 12, 39, 11, 20, 18, 19, 6, 31, 13, 8, 19, 39, 36, 20, 20, 48, 41, 20], [17, 29, 31, 17, 37, 10, 41, 17, 17, 1, 41, 28, 37, 36, 47, 36, 15, 10, 28, 4, 16, 28, 4, 38, 5, 33, 33, 10, 43, 3, 42, 21, 22, 3, 26, 22, 0, 48, 17, 46, 23, 41, 29, 36, 9, 21, 13, 12, 45, 8], [24, 47, 19, 49, 11, 37, 35, 45, 22, 47, 48, 15, 42, 38, 36, 31, 0, 22, 7, 47, 21, 30, 1, 38, 12, 45, 18, 3, 47, 8, 30, 13, 7, 46, 2, 23, 17, 22, 14, 19, 14, 45, 46, 44, 31, 6, 26, 46, 5, 1], [21, 40, 44, 10, 48, 10, 35, 25, 27, 20, 20, 27, 23, 28, 29, 38, 3, 25, 5, 4, 6, 42, 43, 30, 23, 21, 3, 11, 24, 42, 4, 38, 39, 3, 48, 44, 18, 14, 47, 1, 7, 2, 10, 47, 48, 36, 35, 6, 40, 20], [46, 14, 31, 32, 43, 19, 13, 28, 34, 7, 1, 27, 33, 26, 15, 42, 6, 30, 12, 40, 42, 34, 33, 20, 14, 34, 16, 18, 45, 28, 33, 28, 43, 2, 31, 25, 49, 28, 30, 30, 44, 19, 41, 30, 9, 47, 43, 18, 38, 30], [38, 37, 23, 17, 26, 13, 39, 32, 30, 30, 15, 49, 19, 18, 46, 28, 6, 31, 44, 30, 7, 2, 20, 18, 10, 36, 39, 12, 48, 28, 26, 32, 9, 34, 34, 1, 40, 38, 28, 22, 33, 22, 27, 15, 14, 36, 2, 21, 8, 12], [44, 24, 28, 32, 18, 29, 2, 37, 34, 5, 35, 9, 19, 36, 35, 37, 26, 4, 29, 32, 9, 46, 28, 30, 12, 26, 38, 30, 33, 32, 12, 25, 47, 14, 29, 23, 38, 9, 4, 31, 44, 6, 6, 38, 23, 48, 27, 3, 41, 1], [38, 19, 16, 44, 45, 11, 17, 27, 23, 48, 24, 4, 43, 2, 0, 1, 18, 0, 34, 21, 40, 11, 39, 20, 5, 40, 38, 29, 28, 37, 15, 22, 8, 42, 15, 32, 35, 40, 32, 4, 9, 15, 21, 19, 15, 6, 30, 2, 25, 27], [42, 48, 7, 19, 35, 45, 23, 19, 9, 14, 34, 16, 11, 22, 9, 18, 34, 48, 8, 35, 43, 1, 0, 25, 13, 46, 12, 45, 0, 24, 43, 4, 43, 22, 21, 3, 9, 44, 35, 8, 17, 14, 36, 7, 9, 45, 16, 24, 24, 39], [48, 21, 42, 8, 6, 44, 12, 6, 8, 26, 46, 23, 7, 42, 24, 25, 45, 48, 44, 44, 31, 43, 2, 9, 7, 44, 21, 20, 8, 23, 30, 10, 24, 35, 46, 19, 45, 39, 17, 13, 43, 2, 5, 26, 1, 28, 38, 6, 6, 41], [10, 4, 0, 42, 16, 32, 24, 32, 35, 35, 2, 37, 23, 12, 37, 21, 16, 6, 43, 42, 17, 48, 23, 47, 9, 37, 11, 18, 6, 11, 25, 36, 49, 33, 11, 28, 49, 16, 13, 10, 26, 42, 10, 43, 39, 47, 11, 7, 0, 1], [23, 7, 32, 27, 2, 15, 19, 11, 25, 33, 49, 9, 19, 29, 35, 46, 18, 21, 28, 41, 13, 41, 15, 2, 48, 5, 38, 22, 11, 11, 25, 30, 15, 49, 9, 1, 11, 6, 3, 20, 14, 39, 2, 30, 49, 45, 41, 32, 2, 44], [18, 3, 3, 35, 21, 21, 18, 29, 1, 30, 45, 31, 38, 29, 15, 44, 38, 9, 8, 15, 12, 45, 43, 28, 28, 37, 17, 7, 40, 15, 2, 31, 3, 1, 31, 11, 14, 21, 23, 5, 15, 44, 12, 10, 16, 28, 43, 37, 16, 35], [35, 27, 45, 48, 39, 37, 1, 4, 40, 20, 29, 10, 13, 14, 8, 21, 31, 8, 25, 7, 25, 27, 47, 44, 30, 3, 41, 1, 49, 7, 22, 15, 3, 48, 21, 14, 33, 6, 26, 12, 46, 42, 35, 35, 0, 4, 9, 16, 19, 26], [21, 20, 10, 42, 15, 18, 7, 36, 43, 18, 29, 26, 36, 42, 4, 18, 1, 28, 21, 24, 32, 32, 3, 6, 41, 49, 35, 5, 31, 13, 37, 49, 21, 5, 15, 19, 45, 7, 16, 16, 5, 18, 35, 36, 42, 13, 40, 23, 10, 44], [19, 34, 7, 39, 24, 3, 20, 43, 37, 0, 41, 46, 44, 13, 25, 41, 5, 45, 34, 40, 48, 23, 5, 41, 33, 19, 4, 35, 18, 34, 38, 17, 9, 3, 19, 42, 6, 28, 19, 24, 49, 7, 42, 19, 0, 10, 14, 48, 10, 0], [33, 31, 32, 22, 4, 35, 47, 1, 9, 16, 36, 24, 28, 15, 36, 10, 15, 48, 5, 20, 15, 10, 18, 16, 35, 37, 29, 25, 19, 8, 11, 20, 31, 27, 31, 19, 45, 10, 18, 6, 48, 0, 26, 21, 44, 43, 47, 16, 14, 44], [26, 4, 40, 34, 47, 17, 43, 17, 3, 23, 14, 35, 21, 3, 23, 8, 15, 49, 4, 19, 26, 16, 11, 20, 20, 5, 24, 5, 25, 18, 30, 40, 45, 19, 28, 9, 4, 43, 32, 29, 32, 27, 34, 42, 27, 1, 26, 29, 0, 17], [49, 48, 11, 37, 0, 38, 24, 22, 20, 44, 42, 42, 14, 23, 46, 18, 24, 12, 22, 19, 16, 37, 32, 36, 40, 24, 34, 19, 22, 0, 48, 28, 34, 23, 38, 37, 31, 48, 6, 18, 43, 27, 17, 4, 46, 32, 8, 16, 25, 28], [3, 7, 1, 17, 41, 28, 2, 29, 31, 25, 47, 48, 4, 8, 20, 34, 45, 37, 27, 15, 43, 17, 35, 15, 9, 49, 4, 24, 37, 30, 15, 15, 37, 22, 32, 26, 26, 6, 13, 4, 19, 0, 16, 39, 40, 48, 7, 42, 41, 47], [36, 16, 8, 48, 29, 3, 4, 34, 33, 46, 13, 16, 18, 1, 8, 9, 6, 36, 6, 20, 26, 41, 32, 7, 5, 45, 8, 0, 20, 29, 47, 38, 17, 34, 41, 25, 9, 46, 24, 32, 9, 15, 9, 44, 21, 6, 2, 25, 16, 35], [2, 33, 5, 8, 27, 40, 47, 21, 49, 7, 36, 18, 17, 3, 25, 15, 43, 22, 36, 27, 6, 38, 11, 29, 12, 1, 30, 17, 27, 24, 49, 28, 2, 29, 21, 34, 17, 47, 8, 28, 29, 14, 23, 16, 42, 46, 4, 27, 38, 12], [21, 31, 44, 26, 36, 5, 13, 24, 32, 34, 17, 32, 1, 38, 30, 14, 12, 13, 22, 44, 42, 36, 39, 3, 49, 24, 32, 12, 21, 35, 26, 2, 1, 12, 46, 48, 20, 41, 49, 1, 21, 0, 12, 35, 49, 38, 5, 37, 1, 13], [36, 38, 18, 5, 43, 34, 22, 4, 17, 16, 41, 29, 12, 2, 41, 22, 45, 34, 45, 13, 12, 43, 39, 42, 30, 43, 29, 26, 26, 38, 40, 49, 14, 21, 47, 41, 32, 32, 40, 14, 43, 19, 11, 27, 1, 20, 3, 44, 25, 44], [48, 39, 27, 17, 38, 19, 28, 11, 1, 49, 25, 24, 36, 12, 24, 46, 3, 36, 36, 4, 44, 8, 32, 36, 35, 34, 7, 40, 49, 44, 47, 48, 37, 37, 12, 21, 13, 48, 7, 47, 24, 2, 10, 25, 48, 7, 15, 8, 30, 2], [31, 27, 6, 26, 31, 33, 41, 39, 2, 4, 20, 41, 28, 33, 40, 33, 12, 31, 42, 48, 5, 32, 16, 11, 30, 27, 1, 37, 16, 12, 18, 16, 36, 40, 28, 16, 29, 40, 30, 40, 10, 40, 9, 9, 17, 22, 37, 37, 5, 36], [27, 43, 42, 0, 16, 31, 35, 38, 27, 27, 47, 34, 2, 40, 31, 39, 37, 25, 11, 30, 25, 39, 35, 6, 33, 40, 0, 36, 39, 29, 25, 45, 15, 30, 17, 0, 13, 41, 4, 33, 21, 7, 29, 20, 24, 20, 14, 29, 39, 43], [38, 26, 34, 49, 2, 0, 3, 23, 41, 34, 23, 15, 32, 26, 11, 7, 37, 27, 28, 21, 5, 39, 48, 17, 14, 40, 27, 0, 38, 13, 22, 37, 49, 20, 19, 45, 36, 37, 11, 5, 36, 4, 8, 29, 13, 21, 29, 24, 18, 13], [44, 0, 27, 18, 16, 11, 23, 25, 14, 6, 33, 35, 0, 14, 32, 29, 20, 31, 28, 26, 39, 49, 24, 1, 11, 3, 0, 42, 33, 20, 11, 34, 24, 12, 0, 18, 16, 44, 2, 9, 46, 38, 1, 25, 25, 2, 20, 23, 16, 15], [9, 45, 47, 32, 40, 48, 37, 14, 42, 26, 35, 25, 6, 43, 18, 35, 28, 29, 5, 13, 2, 5, 19, 14, 24, 45, 43, 47, 27, 7, 32, 23, 32, 20, 41, 32, 41, 13, 49, 4, 24, 35, 30, 31, 1, 39, 41, 33, 34, 35], [14, 4, 33, 42, 49, 4, 26, 6, 35, 27, 43, 33, 22, 49, 41, 41, 6, 39, 30, 16, 13, 31, 23, 13, 22, 28, 11, 10, 6, 20, 16, 6, 30, 21, 15, 43, 6, 39, 16, 10, 23, 26, 13, 30, 35, 34, 47, 46, 42, 31], [36, 40, 11, 29, 14, 3, 7, 2, 33, 35, 38, 31, 40, 33, 5, 23, 9, 43, 42, 12, 19, 1, 33, 24, 1, 30, 21, 10, 30, 32, 31, 49, 20, 47, 5, 18, 13, 28, 49, 12, 16, 7, 21, 27, 5, 4, 33, 14, 4, 44], [27, 45, 31, 11, 32, 0, 17, 9, 34, 47, 45, 39, 31, 44, 32, 2, 36, 12, 29, 23, 3, 34, 35, 14, 28, 15, 8, 7, 41, 39, 12, 2, 13, 26, 7, 38, 26, 42, 38, 30, 40, 43, 20, 29, 17, 39, 4, 7, 14, 22], [46, 1, 21, 35, 12, 14, 14, 3, 37, 32, 0, 5, 24, 18, 43, 17, 30, 27, 26, 45, 8, 11, 40, 9, 14, 32, 41, 40, 1, 40, 30, 17, 39, 25, 29, 12, 9, 8, 10, 42, 25, 47, 20, 12, 16, 33, 30, 48, 12, 7], [38, 36, 46, 23, 25, 18, 5, 9, 0, 33, 21, 26, 34, 34, 6, 37, 2, 24, 26, 14, 45, 2, 15, 35, 42, 0, 6, 48, 10, 1, 36, 11, 5, 11, 26, 33, 11, 48, 8, 45, 30, 5, 19, 14, 45, 26, 29, 26, 45, 26], [32, 13, 29, 31, 36, 39, 40, 9, 33, 5, 49, 46, 25, 8, 9, 19, 33, 4, 5, 8, 44, 16, 47, 46, 32, 31, 36, 47, 10, 15, 14, 27, 8, 22, 15, 18, 3, 12, 43, 36, 27, 22, 18, 32, 0, 40, 8, 13, 4, 46], [20, 7, 17, 22, 6, 43, 47, 42, 5, 29, 32, 29, 1, 5, 5, 36, 37, 28, 43, 5, 40, 46, 49, 27, 17, 20, 23, 9, 5, 37, 25, 38, 34, 10, 15, 25, 22, 35, 15, 11, 19, 11, 22, 47, 9, 33, 44, 0, 47, 44], [10, 45, 26, 19, 35, 6, 12, 39, 35, 37, 15, 3, 22, 37, 44, 48, 32, 45, 0, 23, 29, 31, 28, 46, 49, 18, 34, 42, 18, 37, 3, 27, 41, 34, 19, 2, 24, 40, 6, 23, 34, 8, 25, 10, 25, 22, 2, 0, 2, 43], [26, 25, 5, 15, 35, 7, 43, 27, 26, 27, 22, 47, 47, 48, 47, 5, 44, 40, 20, 13, 36, 8, 43, 13, 9, 19, 24, 41, 49, 12, 2, 25, 28, 49, 17, 42, 44, 17, 27, 19, 31, 3, 13, 14, 34, 40, 20, 20, 30, 10], [3, 14, 14, 8, 25, 26, 3, 48, 25, 10, 7, 12, 19, 26, 29, 46, 3, 23, 11, 39, 46, 49, 28, 40, 44, 32, 46, 28, 46, 9, 8, 49, 5, 34, 36, 9, 21, 17, 42, 29, 41, 12, 1, 44, 24, 40, 11, 40, 23, 34], [41, 33, 11, 21, 9, 46, 19, 21, 1, 14, 20, 43, 12, 4, 10, 22, 49, 42, 13, 10, 7, 44, 1, 45, 4, 47, 0, 27, 24, 45, 23, 28, 19, 1, 46, 17, 46, 3, 45, 41, 3, 0, 2, 22, 25, 8, 10, 46, 30, 2], [5, 38, 4, 47, 31, 18, 17, 4, 35, 7, 19, 10, 27, 21, 7, 3, 10, 46, 24, 2, 5, 30, 17, 27, 3, 21, 32, 37, 9, 23, 49, 27, 37, 45, 7, 11, 7, 2, 11, 45, 31, 39, 41, 18, 18, 45, 48, 37, 23, 8], [13, 33, 31, 4, 38, 22, 37, 30, 48, 34, 1, 23, 6, 49, 18, 39, 17, 10, 2, 26, 14, 45, 8, 7, 31, 13, 34, 20, 13, 8, 33, 13, 11, 44, 4, 13, 12, 12, 39, 22, 39, 33, 36, 11, 38, 0, 13, 49, 17, 6], [3, 24, 36, 7, 30, 17, 49, 0, 8, 46, 8, 33, 39, 44, 37, 9, 48, 2, 37, 10, 36, 43, 24, 31, 31, 43, 29, 22, 41, 8, 36, 15, 4, 3, 24, 14, 11, 42, 33, 13, 29, 4, 33, 34, 12, 14, 10, 14, 6, 49], [9, 4, 28, 7, 22, 19, 8, 30, 3, 0, 6, 6, 45, 39, 9, 22, 37, 43, 21, 0, 10, 41, 29, 8, 12, 46, 46, 7, 26, 40, 1, 37, 47, 23, 13, 47, 16, 16, 19, 23, 47, 39, 30, 15, 44, 48, 0, 43, 34, 4], [3, 15, 16, 37, 33, 39, 46, 3, 20, 3, 35, 43, 39, 40, 28, 42, 15, 20, 11, 38, 39, 6, 41, 16, 0, 47, 12, 41, 34, 23, 23, 47, 38, 0, 46, 42, 48, 38, 18, 42, 48, 20, 24, 11, 9, 22, 9, 33, 42, 32], [47, 14, 47, 25, 4, 33, 31, 17, 27, 22, 24, 10, 26, 0, 47, 17, 16, 19, 8, 5, 38, 45, 14, 46, 41, 25, 32, 40, 49, 0, 41, 25, 1, 8, 23, 30, 35, 15, 22, 39, 20, 3, 21, 25, 27, 29, 38, 39, 1, 30], [5, 25, 22, 16, 7, 46, 46, 13, 24, 28, 44, 12, 0, 6, 19, 49, 0, 10, 39, 40, 22, 11, 21, 2, 38, 43, 22, 12, 18, 42, 46, 16, 25, 43, 6, 16, 23, 4, 45, 2, 38, 6, 24, 33, 40, 45, 35, 40, 38, 44], [27, 12, 45, 13, 22, 48, 45, 16, 33, 7, 44, 10, 36, 21, 24, 6, 29, 8, 33, 39, 28, 2, 26, 1, 34, 23, 7, 22, 21, 27, 33, 14, 48, 25, 42, 29, 3, 24, 10, 46, 46, 16, 17, 30, 3, 17, 28, 39, 41, 10]]
    # 18 - [[], [], [], [], [], [], [], [], [],; [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [88, 6, 6, 33, 66, 0, 0, 0, 17, 4, 38, 49, 41, 36, 9, 9, 16, 38, 37, 7, 19, 21, 21, 22, 22, 22, 58, 23, 60, 74, 40, 25, 1, 2, 27, 29, 20, 66, 92, 36, 17, 64, 17, 35, 61, 72, 74, 10, 30, 36, 8, 44, 37, 48, 5, 39, 39, 39, 21, 90, 42, 42, 89, 37, 45, 74, 51, 64, 43, 93, 50, 54, 96, 76, 68, 41, 69, 86, 2, 12, 9, 45, 15, 68, 46, 16, 2, 75, 47, 47, 47, 21, 68, 21, 87, 48, 48, 13, 42, 90], [51, 51, 51, 51, 51, 51, 51, 51, 51, 51, 51, 51, 51, 51, 51, 51, 51, 20, 2, 10, 18, 72, 84, 98, 41, 9, 78, 89, 0, 72, 14, 60, 92, 75, 74, 57, 19, 77, 32, 0, 3, 4, 4, 66, 7, 86, 28, 21, 53, 65, 13, 75, 15, 37, 54, 72, 17, 17, 6, 18, 19, 19, 22, 22, 25, 36, 29, 55, 30, 49, 8, 45, 83, 23, 28, 33, 24, 34, 34, 35, 35, 11, 2, 36, 22, 37, 48, 45, 42, 47, 78, 74, 64, 55, 40, 44, 4, 56, 2, 45], [52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 31, 29, 36, 44, 94, 11, 77, 75, 71, 74, 11, 10, 19, 59, 73, 9, 23, 44, 7, 94, 38, 80, 78, 12, 37, 47, 65, 94, 5, 47, 62, 21, 51, 99, 71, 85, 32, 89, 65, 37, 40, 81, 0, 4, 54, 0, 9, 9], [53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 36, 61, 31, 38, 50, 32, 66, 98, 59, 72, 74, 24, 71, 7, 41, 75, 63, 65, 96, 2, 95, 54, 60, 77, 81, 56, 31, 55, 15, 3, 19, 37, 69, 78, 76, 2, 66, 70, 97, 80, 78, 64, 9, 28, 46], [54, 54, 54, 54, 54, 54, 54, 44, 66, 74, 38, 5, 87, 47, 85, 32, 10, 9, 79, 12, 5, 81, 67, 65, 58, 38, 68, 98, 21, 26, 51, 47, 28, 69, 95, 36, 80, 0, 83, 20, 27, 71, 6, 64, 95, 48, 47, 79, 11, 21, 79, 83, 78, 19, 69, 84, 7, 72, 22, 73, 24, 65, 55, 69, 58, 28, 31, 27, 11, 17, 49, 17, 21, 22, 36, 84, 12, 57, 13, 13, 14, 15, 10, 66, 17, 18, 18, 38, 22, 22, 23, 14, 27, 93, 83, 34, 11, 55, 30, 30], [55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 23, 34, 50, 71, 78, 18, 86, 93, 38, 53, 61, 96, 87, 76, 93, 96, 74, 30, 31, 65, 88, 28, 85, 47, 57, 87, 49, 1, 91, 99, 83, 72, 18, 2, 66, 88, 76, 51, 96, 55, 15, 75, 48, 83, 74, 65, 68, 29, 34, 51, 49, 42, 29, 99, 14, 80, 71, 72, 85, 73, 41, 15, 28, 64, 51, 67, 0, 42, 58, 12, 60, 28, 24, 32, 66, 39, 76, 42, 74, 56, 82, 87, 83, 1, 3, 27, 0], [56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 71, 31, 37, 4, 40, 0, 90, 58, 11, 10, 70, 57, 5, 24, 27, 63, 62, 75, 29, 1, 4, 4, 4, 7, 9, 26, 14, 26, 66, 66, 17, 17, 72, 19, 23, 24, 25, 27, 41, 71, 11, 50, 29, 29], [57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 92, 28, 94, 36, 48, 36, 6, 16, 63, 4, 75, 18, 22, 75, 87, 32, 94, 44, 12, 12, 84, 62, 17, 12, 59, 49, 94, 7, 34, 48, 41, 64, 12, 50, 97, 1, 95, 59, 14, 30, 23, 37, 13, 13, 13, 14, 14, 14, 58, 20, 22, 61, 23, 23, 23, 44, 34, 26, 83, 2, 11, 81, 29, 25], [41, 10, 65, 17, 23, 9, 98, 36, 33, 92, 65, 51, 12, 95, 78, 2, 11, 86, 6, 86, 63, 75, 79, 84, 20, 36, 48, 76, 23, 81, 82, 72, 36, 32, 32, 96, 0, 1, 87, 48, 49, 11, 61, 51, 93, 44, 68, 99, 23, 31, 78, 55, 32, 4, 43, 97, 70, 78, 99, 70, 34, 28, 31, 23, 77, 62, 35, 11, 41, 85, 12, 62, 87, 89, 54, 38, 5, 63, 54, 25, 96, 5, 59, 95, 62, 19, 87, 8, 34, 32, 62, 73, 58, 6, 38, 77, 89, 3, 4, 87], [59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 59, 8, 32, 36, 30, 10, 60, 35, 32, 59, 92, 26, 58, 87, 17, 1, 99, 91, 48, 40, 81, 53, 30, 88, 7, 60, 63, 39, 84, 64, 54, 87, 72, 4, 58, 61, 72, 75, 4, 2, 24, 80, 23, 65, 3, 80, 96, 21, 82, 27, 83, 75, 36, 1, 4, 4, 31, 93, 9, 9, 50, 49, 45, 13, 14, 78, 6, 57, 15, 83, 17, 52, 18, 57, 29, 30, 39], [60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 9, 50, 7, 49, 84, 74, 40, 76, 2, 0, 28, 21, 93, 28, 91, 63, 74, 26, 6, 86, 60, 53, 99, 59, 28, 63, 95, 82, 3, 75, 70, 74, 68, 8, 77, 74, 20, 94, 16, 72, 49, 74, 2, 23, 45, 97, 0, 50, 65, 9, 11, 40, 36, 77, 13, 14, 14, 16], [61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 61, 94, 98, 55, 41, 73, 80, 84, 47, 4, 39, 15, 30, 8, 9, 1, 25, 70, 5, 95, 48, 83, 4, 16, 53, 86, 46, 42, 63, 94, 58, 1, 49, 56, 1, 59, 41, 94, 81, 54, 46, 81, 80, 10, 96, 31, 83, 19, 85, 37, 58, 18, 72, 6, 78, 64, 1, 24, 87, 48, 12, 98, 11, 83, 41, 95, 82, 48, 98, 1, 1, 3, 92, 90], [86, 66, 48, 94, 0, 1, 66, 34, 74, 5, 6, 23, 60, 58, 86, 14, 15, 16, 0, 17, 17, 18, 18, 49, 7, 13, 39, 8, 96, 6, 3, 9, 33, 33, 86, 34, 35, 35, 37, 37, 90, 39, 39, 39, 12, 83, 40, 72, 41, 81, 71, 39, 42, 42, 63, 8, 98, 65, 78, 44, 91, 25, 45, 45, 45, 45, 45, 45, 13, 82, 46, 46, 46, 46, 21, 85, 79, 36, 97, 89, 38, 47, 47, 47, 73, 48, 48, 48, 48, 48, 48, 48, 99, 42, 31, 91, 67, 88, 1, 33], [63, 68, 27, 73, 2, 38, 2, 43, 32, 93, 77, 11, 97, 73, 36, 66, 97, 89, 61, 5, 63, 87, 74, 13, 98, 57, 33, 87, 27, 19, 67, 18, 24, 74, 54, 60, 84, 8, 72, 25, 51, 54, 74, 32, 96, 81, 71, 46, 55, 73, 21, 63, 99, 25, 75, 64, 35, 74, 88, 57, 71, 57, 42, 36, 27, 71, 84, 5, 7, 58, 48, 63, 85, 17, 54, 63, 8, 71, 84, 57, 73, 71, 45, 19, 62, 32, 57, 0, 0, 57, 58, 9, 66, 97, 13, 14, 15, 16, 16, 17], [64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 93, 67, 52, 35, 7, 7, 81, 20, 71, 64, 12, 51, 79, 49, 84, 79, 31, 95, 78, 50, 83, 62, 30, 55, 8, 0, 77, 87, 23, 22, 51, 96, 48, 7, 11, 26, 50, 43, 35, 57, 92, 83, 7, 77, 60, 99, 26, 19, 14, 85, 79, 68, 39, 26, 95, 78, 65, 45, 81, 89, 8, 57, 8, 38, 51, 30, 88, 1, 63, 13, 31], [10, 68, 42, 16, 99, 48, 62, 4, 42, 74, 1, 1, 1, 1, 76, 35, 42, 97, 30, 9, 36, 35, 62, 70, 2, 55, 89, 38, 38, 17, 14, 19, 92, 22, 22, 24, 15, 32, 26, 83, 33, 33, 34, 46, 25, 79, 35, 39, 37, 39, 97, 28, 68, 55, 38, 87, 8, 41, 87, 43, 43, 43, 43, 43, 9, 20, 33, 44, 44, 44, 12, 41, 76, 45, 45, 68, 80, 46, 46, 9, 79, 59, 21, 94, 47, 7, 71, 33, 50, 45, 86, 50, 94, 48, 48, 0, 77, 25, 48, 86], [66, 66, 66, 66, 66, 66, 66, 66, 66, 86, 89, 51, 7, 71, 12, 12, 21, 73, 74, 97, 31, 23, 67, 69, 2, 86, 7, 86, 65, 32, 49, 12, 40, 94, 11, 87, 3, 70, 76, 76, 21, 46, 9, 86, 95, 36, 13, 69, 15, 15, 31, 16, 18, 55, 19, 19, 19, 24, 24, 25, 5, 62, 67, 64, 74, 84, 29, 29, 30, 22, 98, 96, 23, 34, 20, 76, 28, 35, 35, 35, 43, 26, 37, 37, 38, 8, 49, 41, 39, 41, 94, 40, 40, 41, 41, 43, 43, 43, 5, 83], [67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 19, 58, 25, 18, 26, 92, 36, 74, 22, 10, 45, 36, 77, 69, 75, 79, 81, 9, 54, 76, 83, 38, 43, 84, 79, 96, 76, 51, 24, 89, 76, 42, 1, 39, 60, 32, 93, 30, 48, 73, 55, 60, 18, 62, 68, 95, 31, 62, 11, 37, 2, 7, 6, 3, 3], [68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 95, 62, 8, 11, 50, 72, 65, 44, 5, 78, 34, 84, 85, 75, 49, 52, 75, 34, 12, 3, 24, 38, 8, 24, 36, 30, 71, 58, 11, 77, 68, 7, 2, 59, 41, 1, 70, 48, 5, 86, 31, 86, 32, 88, 5, 60, 61, 29, 70, 11, 79, 74, 79, 24, 64, 51, 83, 4, 24, 64, 90, 10, 51, 84], [69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 69, 55, 38, 55, 36, 50, 0, 72, 6, 8, 84, 83, 66, 67, 19, 57, 80, 20, 25, 71, 75, 52, 40, 81, 77, 59, 21, 68, 17, 85, 51, 7, 93, 57, 24, 75, 33, 65, 85, 32, 61, 96, 75, 97, 22, 50, 21, 0, 1, 1, 42, 21, 29, 75, 9, 63, 14], [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 25, 36, 36, 22, 96, 76, 35, 44, 94, 7, 18, 5, 13, 62, 95, 6, 31, 40, 27, 51, 12, 76, 67, 52, 29, 0, 31, 1, 56, 16, 38, 87, 32, 9, 9, 10, 94, 13, 46, 28, 78], [46, 99, 24, 99, 63, 79, 0, 44, 69, 73, 62, 26, 83, 71, 82, 0, 3, 3, 14, 4, 10, 86, 59, 78, 13, 14, 15, 7, 17, 18, 19, 20, 21, 7, 74, 50, 27, 35, 6, 79, 92, 14, 10, 34, 27, 41, 98, 49, 96, 62, 86, 47, 22, 39, 39, 52, 19, 10, 95, 71, 41, 41, 47, 42, 72, 66, 31, 43, 59, 51, 41, 37, 52, 44, 35, 82, 24, 45, 45, 45, 27, 73, 50, 69, 46, 46, 46, 68, 6, 2, 87, 58, 1, 54, 5, 71, 47, 47, 47, 43], [45, 74, 63, 25, 57, 56, 38, 62, 37, 38, 71, 77, 62, 19, 66, 40, 27, 81, 6, 0, 1, 76, 4, 9, 69, 80, 40, 16, 16, 52, 18, 18, 84, 19, 98, 61, 23, 23, 23, 24, 34, 0, 37, 34, 18, 29, 96, 4, 74, 30, 50, 93, 42, 70, 64, 58, 34, 81, 72, 69, 87, 99, 38, 58, 29, 39, 39, 39, 39, 58, 95, 40, 32, 41, 77, 42, 44, 46, 45, 66, 23, 33, 62, 94, 46, 37, 81, 38, 27, 13, 85, 47, 40, 83, 35, 28, 18, 72, 91, 6], [73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 71, 83, 86, 55, 75, 11, 83, 98, 58, 38, 72, 86, 37, 90, 15, 21, 5, 98, 50, 89, 76, 62, 2, 55, 22, 6, 63, 22, 80, 26, 71, 60, 68, 79, 21, 9, 12, 40, 53, 8, 79, 75, 5, 30, 75, 85, 79], [20, 37, 97, 46, 47, 89, 96, 98, 86, 13, 91, 39, 11, 0, 1, 26, 7, 30, 58, 41, 9, 9, 80, 21, 74, 49, 13, 14, 15, 16, 99, 10, 17, 18, 20, 22, 71, 23, 40, 24, 24, 25, 48, 29, 44, 47, 26, 28, 83, 41, 33, 33, 33, 99, 34, 64, 12, 35, 25, 30, 37, 37, 37, 47, 84, 39, 39, 65, 40, 40, 38, 41, 41, 42, 42, 42, 43, 43, 43, 43, 51, 44, 44, 5, 11, 45, 45, 45, 45, 45, 45, 50, 83, 75, 46, 46, 46, 46, 97, 31], [75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 31, 14, 59, 61, 12, 79, 41, 8, 17, 1, 9, 95, 28, 35, 43, 38, 74, 1, 1, 38, 38, 32, 64, 77, 64, 26, 77, 36, 0, 3, 3, 4, 4, 39, 13, 14, 88, 19, 4, 17, 19, 95, 58, 40, 59, 26, 38, 61, 51, 30, 30, 53, 19, 32, 34, 34, 34, 46, 42, 35, 72, 15, 86, 85, 10, 37, 37, 49, 44, 52, 49, 31, 39, 39, 39, 40, 94, 52, 41, 95, 42, 43, 43, 90, 76, 65, 92, 44], [76, 76, 76, 76, 76, 76, 76, 77, 95, 0, 61, 38, 10, 4, 36, 2, 18, 54, 1, 3, 55, 24, 13, 13, 13, 14, 16, 16, 18, 19, 65, 22, 22, 23, 75, 58, 47, 25, 26, 29, 99, 2, 10, 8, 54, 51, 4, 34, 34, 35, 35, 35, 33, 48, 64, 39, 39, 40, 63, 77, 41, 41, 42, 42, 60, 72, 2, 43, 43, 43, 69, 44, 44, 44, 44, 44, 0, 58, 45, 45, 45, 28, 71, 9, 32, 62, 22, 19, 14, 47, 43, 92, 76, 48, 48, 11, 55, 34, 44, 10], [77, 77, 77, 77, 77, 77, 77, 59, 77, 14, 49, 32, 14, 87, 28, 6, 46, 93, 78, 68, 68, 15, 94, 96, 50, 1, 2, 2, 67, 19, 8, 66, 79, 7, 87, 11, 32, 54, 36, 44, 76, 26, 96, 84, 53, 96, 11, 84, 7, 51, 79, 59, 48, 87, 6, 54, 38, 48, 64, 73, 64, 72, 4, 89, 43, 88, 72, 11, 71, 36, 66, 60, 80, 65, 64, 2, 14, 40, 47, 65, 32, 7, 6, 91, 94, 80, 52, 1, 3, 4, 11, 96, 90, 40, 49, 14, 15, 75, 16, 44], [78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 78, 55, 91, 57, 91, 87, 61, 99, 70, 41, 2, 54, 93, 7, 32, 77, 81, 63, 68, 32, 96, 69, 96, 19, 31, 54, 12, 33, 96, 60, 28, 50, 12, 68, 97, 2, 79, 50, 60, 10, 38, 81, 19, 92, 96, 17, 62, 77, 55, 27, 60, 6, 84, 80, 92, 4, 53, 79, 3, 4, 8, 86, 9, 14, 46, 15, 16], [71, 11, 25, 75, 93, 58, 14, 55, 13, 16, 13, 28, 40, 13, 51, 71, 15, 15, 16, 31, 19, 19, 20, 22, 22, 22, 72, 23, 24, 26, 90, 72, 29, 29, 70, 30, 55, 49, 86, 53, 33, 33, 25, 34, 34, 34, 1, 35, 35, 8, 67, 28, 37, 37, 27, 72, 89, 39, 39, 39, 39, 51, 83, 27, 41, 42, 99, 55, 44, 44, 44, 44, 45, 45, 45, 45, 45, 45, 45, 99, 91, 90, 36, 47, 97, 76, 48, 48, 48, 11, 85, 77, 90, 44, 18, 99, 35, 34, 6, 83], [80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 44, 36, 80, 5, 73, 96, 36, 60, 69, 66, 0, 48, 1, 79, 3, 4, 45, 91, 14, 59, 14, 14, 15, 28, 18, 68, 19, 20, 20, 21, 21, 23, 24, 24, 26, 27, 71, 68, 80, 29, 42, 43, 65, 65, 33, 33, 33, 34, 24, 35, 35, 84, 68, 37, 37, 86, 33, 6], [81, 81, 81, 81, 81, 81, 81, 81, 81, 81, 81, 81, 81, 81, 50, 98, 50, 6, 29, 40, 77, 30, 44, 21, 47, 94, 52, 68, 92, 29, 58, 68, 35, 26, 75, 92, 27, 97, 50, 75, 51, 43, 5, 47, 20, 71, 75, 32, 79, 83, 83, 76, 54, 44, 36, 63, 7, 85, 20, 17, 43, 77, 96, 47, 58, 12, 40, 37, 31, 50, 85, 40, 17, 3, 54, 90, 32, 7, 29, 94, 84, 63, 92, 3, 23, 49, 42, 42, 1, 1, 30, 4, 54, 47, 49, 66, 79, 55, 9, 9], [82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 82, 75, 77, 74, 16, 83, 2, 71, 30, 51, 88, 3, 64, 21, 59, 61, 38, 0, 1, 4, 4, 4, 54, 93, 54, 7, 49, 54, 4, 80, 51, 10, 13, 14, 15, 41, 28, 17, 19, 20, 20, 21, 22, 24, 25, 26, 53, 29, 29, 91], [54, 46, 98, 0, 78, 1, 42, 9, 82, 72, 29, 12, 14, 14, 68, 16, 16, 17, 19, 38, 66, 99, 22, 25, 59, 62, 27, 53, 66, 30, 45, 61, 85, 91, 33, 33, 34, 49, 28, 69, 37, 72, 67, 39, 41, 41, 41, 62, 42, 42, 42, 72, 43, 43, 43, 2, 48, 26, 44, 20, 2, 45, 45, 45, 45, 45, 45, 87, 46, 99, 46, 58, 87, 84, 61, 6, 47, 82, 8, 49, 99, 48, 48, 48, 48, 81, 84, 7, 1, 8, 86, 79, 95, 73, 12, 55, 12, 17, 59, 97], [84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 72, 5, 29, 8, 30, 99, 11, 56, 1, 34, 61, 57, 29, 67, 35, 83, 71, 51, 81, 5, 57, 57, 5, 40, 33, 77, 12, 34, 24, 55, 42, 1, 61, 4, 6, 78, 5, 29, 6, 43, 15, 16, 18, 20, 62, 43, 29, 22, 86, 41, 19, 10, 80, 11, 29, 66, 30, 85, 68, 83, 24, 1, 94, 57, 8, 27], [85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 12, 25, 28, 30, 41, 33, 57, 76, 78, 85, 87, 28, 54, 31, 21, 85, 28, 96, 8, 83, 69, 81, 72, 31, 2, 91, 83, 9, 77, 73, 36, 54, 32, 22, 90, 10, 41, 86, 79, 20, 30, 59, 27, 1, 3, 56, 98, 17, 29, 68, 13, 14, 23, 19, 55, 22, 22, 23, 24, 65, 25, 67, 61, 62], [39, 86, 96, 10, 56, 89, 65, 10, 38, 86, 57, 57, 16, 11, 92, 85, 41, 22, 89, 2, 28, 36, 94, 89, 63, 47, 22, 41, 58, 86, 3, 58, 57, 37, 86, 80, 99, 95, 49, 94, 95, 53, 8, 32, 85, 31, 30, 95, 35, 19, 6, 65, 11, 54, 1, 39, 7, 19, 18, 63, 44, 97, 52, 99, 49, 63, 33, 9, 34, 77, 17, 21, 21, 3, 72, 39, 40, 1, 3, 76, 87, 4, 44, 13, 54, 34, 32, 11, 18, 18, 38, 20, 22, 62, 23, 23, 24, 25, 25, 25], [87, 87, 87, 87, 87, 87, 87, 87, 87, 87, 87, 87, 87, 87, 87, 87, 87, 87, 87, 87, 58, 44, 15, 73, 95, 81, 32, 38, 28, 1, 31, 36, 23, 89, 53, 18, 55, 53, 77, 10, 72, 65, 78, 83, 20, 95, 12, 27, 6, 32, 11, 13, 63, 96, 65, 86, 37, 46, 96, 79, 64, 99, 66, 26, 8, 62, 99, 84, 14, 31, 30, 68, 81, 74, 27, 51, 31, 77, 8, 51, 67, 72, 71, 90, 96, 3, 7, 17, 69, 50, 13, 90, 43, 15, 17, 18, 18, 18, 19, 20], [88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 35, 25, 19, 16, 69, 81, 8, 20, 6, 78, 37, 84, 57, 46, 46, 98, 0, 24, 84, 26, 94, 50, 86, 30, 24, 95, 14, 82, 20, 36, 13, 91, 13, 61, 5, 88, 55, 99, 72, 42, 13, 74, 3, 3, 86], [89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 58, 95, 69, 41, 70, 64, 58, 33, 54, 86, 91, 99, 66, 59, 35, 72, 38, 34, 2, 0, 74, 51, 80, 36, 27, 38, 90, 38, 95, 51, 38, 64, 49, 11, 55, 73, 49, 10, 83, 2, 9, 55, 96, 63, 98, 14, 37, 17, 9, 20, 21, 22, 23, 23, 25, 25, 26, 27, 78, 6, 30], [90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 18, 62, 31, 55, 27, 7, 34, 76, 22, 94, 29, 87, 80, 95, 94, 71, 27, 7, 28, 66, 97, 34, 0, 96, 91, 60, 44, 31, 62, 91, 38, 76, 5, 2, 6, 63, 60, 50, 6, 82, 49, 69, 92, 12, 39, 11, 76, 43, 63, 47, 3, 54, 3, 3, 4, 4, 42, 6, 17, 13], [91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 43, 57, 91, 91, 28, 56, 95, 38, 73, 41, 99, 58, 94, 76, 79, 59, 16, 43, 40, 47, 51, 77, 62, 54, 38, 15, 77, 46, 48, 80, 63, 25, 62, 45, 99, 46, 15, 59, 62, 51, 92, 8, 27, 55, 48, 90], [92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 92, 34, 11, 33, 99, 94, 2, 16, 45, 35, 65, 36, 80, 66, 75, 69, 8, 32, 7, 96, 75, 35, 97, 75, 62, 66, 44, 17, 9, 19, 8, 47, 79, 52, 94, 46, 90, 39, 95, 73, 52, 13, 76, 18, 66, 28, 38, 42, 94, 32, 63, 38, 51, 50, 2, 60, 11, 8, 86, 84, 76, 8, 51, 37, 80, 26, 47, 3, 13], [93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 93, 59, 83, 7, 94, 12, 96, 15, 21, 70, 46, 5, 74, 89, 90, 92, 89, 77, 20, 55, 74, 50, 11, 69, 33, 21, 80, 65, 90, 66, 85, 68, 86, 82, 37, 93, 4, 23, 58, 13, 15, 46, 39, 76, 20, 21, 99, 30, 23, 97, 24, 25, 5, 27, 54, 76, 30], [94, 94, 94, 94, 94, 94, 94, 94, 94, 94, 88, 98, 7, 63, 67, 62, 63, 15, 64, 68, 81, 36, 11, 0, 75, 74, 72, 18, 0, 53, 60, 0, 9, 9, 9, 12, 14, 15, 15, 15, 16, 77, 17, 11, 18, 19, 68, 20, 10, 23, 23, 23, 23, 38, 25, 26, 46, 50, 61, 30, 67, 33, 33, 34, 34, 35, 35, 35, 35, 12, 3, 62, 99, 37, 54, 63, 84, 72, 37, 53, 24, 56, 39, 39, 78, 77, 81, 62, 41, 41, 21, 42, 42, 65, 43, 56, 33, 30, 22, 79], [81, 84, 88, 89, 97, 36, 19, 32, 39, 2, 47, 64, 81, 10, 28, 84, 45, 71, 64, 9, 7, 6, 68, 33, 69, 59, 13, 25, 5, 34, 95, 35, 83, 28, 69, 89, 40, 58, 48, 46, 82, 79, 62, 17, 79, 29, 91, 2, 66, 49, 63, 32, 74, 51, 79, 43, 59, 55, 40, 26, 84, 76, 94, 71, 71, 49, 50, 99, 23, 5, 27, 10, 60, 30, 61, 17, 71, 22, 60, 99, 98, 33, 66, 89, 0, 47, 83, 51, 17, 9, 17, 94, 9, 48, 86, 2, 15, 17, 18, 20], [28, 65, 79, 68, 48, 16, 16, 75, 2, 98, 68, 33, 61, 86, 16, 43, 58, 79, 17, 99, 40, 35, 75, 93, 44, 45, 59, 88, 0, 36, 59, 90, 49, 94, 25, 31, 47, 59, 2, 12, 16, 17, 58, 7, 44, 19, 93, 81, 63, 13, 29, 29, 85, 30, 30, 30, 32, 38, 34, 84, 35, 61, 37, 77, 32, 40, 79, 35, 50, 64, 42, 42, 83, 74, 6, 38, 50, 44, 42, 44, 44, 44, 44, 44, 98, 97, 97, 57, 45, 45, 65, 32, 74, 74, 6, 83, 77, 49, 46, 46], [97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 23, 18, 61, 95, 39, 12, 50, 18, 79, 96, 33, 49, 44, 31, 7, 39, 12, 93, 8, 51, 75, 40, 82, 77, 60, 71, 3, 62, 67, 65, 71, 0, 35, 16, 10, 71, 15, 61, 20, 20, 22, 24, 25, 26, 26, 26, 31, 29, 30, 30, 12, 40, 79, 32, 26, 50, 40, 28, 16, 37, 73, 39, 9, 53, 92, 40, 71, 41, 41, 64, 42, 40, 43, 43, 85, 54, 44], [98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 98, 31, 63, 7, 61, 17, 78, 77, 93, 55, 28, 58, 12, 58, 20, 63, 36, 59, 80, 13, 14, 42, 36, 1, 3, 3, 3, 59, 4, 65, 2, 73, 9, 9, 57, 13, 3, 14, 99, 49, 15, 16, 0, 24, 21, 76, 46, 26, 27, 29, 29, 29, 30, 30, 49, 74, 34, 30, 95, 35, 52, 37, 22, 52, 39, 10, 38, 41, 42, 42, 43], [57, 29, 43, 65, 6, 10, 10, 95, 65, 11, 66, 25, 78, 5, 63, 58, 28, 99, 5, 79, 43, 38, 7, 67, 86, 36, 10, 81, 62, 31, 81, 35, 23, 45, 12, 22, 60, 55, 91, 10, 37, 45, 1, 53, 74, 1, 96, 73, 83, 75, 2, 2, 41, 11, 24, 63, 65, 2, 66, 33, 42, 20, 42, 12, 97, 46, 97, 25, 37, 74, 36, 92, 26, 34, 72, 83, 65, 18, 95, 46, 54, 52, 65, 78, 74, 63, 22, 86, 6, 6, 48, 56, 76, 6, 46, 4, 42, 7, 48, 20], [92, 77, 28, 77, 86, 24, 95, 97, 48, 28, 95, 62, 8, 91, 97, 87, 32, 94, 8, 79, 89, 88, 65, 96, 58, 74, 83, 47, 78, 16, 12, 90, 47, 63, 69, 48, 72, 64, 83, 12, 63, 5, 75, 58, 72, 94, 2, 84, 26, 92, 91, 19, 11, 75, 87, 9, 9, 50, 77, 81, 35, 69, 40, 75, 23, 74, 12, 32, 64, 45, 10, 34, 74, 40, 68, 83, 39, 30, 58, 96, 65, 84, 3, 3, 4, 4, 4, 97, 2, 13, 15, 15, 16, 30, 95, 24, 20, 4, 84, 24], [85, 65, 90, 28, 54, 20, 13, 97, 95, 29, 84, 13, 73, 65, 60, 0, 3, 3, 26, 4, 4, 63, 3, 78, 73, 33, 33, 81, 13, 14, 14, 67, 15, 17, 18, 5, 20, 21, 54, 86, 23, 23, 56, 72, 28, 95, 29, 30, 95, 72, 33, 33, 89, 58, 34, 34, 27, 35, 37, 37, 62, 18, 36, 3, 7, 41, 41, 88, 43, 43, 10, 44, 44, 12, 64, 17, 59, 46, 46, 34, 73, 37, 86, 94, 26, 47, 47, 47, 8, 24, 2, 99, 76, 38, 49, 42, 13, 48, 48, 97], [52, 54, 51, 88, 68, 33, 31, 22, 45, 6, 24, 17, 52, 48, 19, 6, 21, 85, 83, 6, 49, 20, 98, 75, 44, 39, 36, 31, 28, 73, 36, 16, 30, 95, 79, 21, 33, 76, 10, 41, 23, 39, 12, 89, 67, 59, 95, 59, 63, 80, 17, 15, 50, 8, 57, 98, 17, 38, 74, 96, 31, 19, 7, 67, 2, 67, 46, 83, 18, 5, 20, 72, 86, 45, 75, 82, 50, 56, 36, 83, 79, 93, 22, 0, 1, 7, 9, 13, 97, 36, 17, 20, 20, 21, 41, 24, 25, 98, 79, 77], [52, 61, 27, 6, 53, 25, 18, 81, 53, 39, 58, 65, 10, 96, 99, 88, 93, 96, 4, 21, 5, 86, 27, 97, 50, 3, 3, 49, 20, 8, 11, 85, 30, 83, 83, 61, 35, 63, 71, 54, 21, 11, 27, 63, 70, 23, 21, 31, 21, 13, 76, 75, 29, 12, 67, 79, 37, 39, 25, 31, 32, 37, 47, 19, 94, 59, 10, 56, 26, 12, 51, 17, 92, 43, 90, 21, 46, 55, 26, 2, 2, 58, 96, 77, 48, 75, 0, 4, 50, 7, 27, 57, 40, 46, 15, 15, 62, 79, 7, 17], [0, 4, 14, 97, 13, 86, 15, 15, 16, 16, 17, 18, 18, 19, 21, 64, 98, 23, 23, 11, 24, 25, 23, 71, 79, 7, 29, 90, 3, 9, 68, 76, 34, 88, 35, 35, 64, 44, 30, 63, 92, 20, 49, 0, 39, 39, 39, 39, 41, 81, 72, 39, 74, 42, 42, 51, 89, 43, 43, 43, 42, 96, 42, 85, 91, 95, 44, 77, 72, 48, 45, 45, 45, 58, 72, 23, 52, 46, 46, 46, 2, 28, 4, 29, 47, 27, 71, 98, 48, 5, 19, 23, 61, 98, 58, 74, 72, 24, 34, 37], [36, 58, 70, 6, 4, 27, 20, 28, 26, 55, 98, 84, 54, 88, 29, 6, 28, 98, 79, 36, 26, 10, 70, 17, 28, 70, 7, 6, 85, 69, 87, 45, 32, 7, 95, 95, 77, 29, 55, 51, 62, 43, 46, 80, 30, 61, 8, 94, 83, 11, 78, 28, 97, 61, 54, 11, 81, 10, 45, 95, 57, 54, 25, 33, 19, 65, 69, 46, 14, 21, 21, 30, 34, 4, 72, 7, 18, 65, 49, 9, 8, 33, 13, 14, 14, 14, 98, 21, 16, 16, 16, 51, 22, 20, 24, 24, 44, 81, 26, 92], [1, 16, 14, 50, 21, 70, 48, 46, 65, 84, 8, 96, 13, 82, 56, 83, 59, 92, 22, 50, 19, 61, 56, 99, 83, 22, 96, 8, 12, 90, 95, 91, 93, 59, 83, 34, 38, 26, 47, 49, 47, 36, 24, 4, 50, 68, 94, 89, 8, 36, 69, 40, 65, 91, 2, 34, 1, 85, 79, 84, 0, 34, 66, 5, 29, 86, 91, 50, 51, 17, 38, 21, 77, 55, 71, 88, 72, 96, 7, 43, 91, 39, 75, 6, 42, 54, 52, 90, 51, 80, 18, 64, 95, 92, 72, 27, 51, 20, 14, 77], [47, 94, 14, 47, 58, 70, 93, 66, 33, 53, 63, 65, 66, 12, 47, 95, 8, 37, 49, 72, 85, 58, 49, 1, 28, 51, 6, 88, 43, 53, 77, 10, 27, 51, 58, 94, 55, 52, 5, 50, 92, 47, 84, 3, 23, 98, 47, 77, 2, 59, 36, 86, 89, 47, 28, 19, 5, 72, 32, 34, 14, 78, 37, 20, 25, 54, 31, 47, 11, 79, 47, 37, 40, 8, 81, 3, 5, 37, 98, 74, 69, 69, 67, 77, 86, 25, 75, 15, 46, 13, 1, 58, 13, 15, 52, 61, 72, 79, 57, 69], [32, 15, 8, 33, 10, 12, 31, 62, 10, 5, 41, 33, 0, 52, 88, 13, 50, 86, 86, 84, 61, 87, 75, 65, 9, 23, 86, 86, 68, 99, 98, 38, 19, 50, 65, 75, 31, 53, 38, 46, 0, 95, 27, 37, 79, 82, 37, 98, 36, 33, 2, 78, 94, 47, 38, 51, 4, 28, 97, 76, 3, 13, 16, 16, 16, 17, 86, 83, 19, 21, 22, 22, 22, 24, 25, 42, 29, 2, 5, 33, 23, 94, 93, 8, 34, 99, 2, 65, 35, 10, 79, 77, 37, 37, 37, 30, 39, 68, 2, 15], [2, 79, 40, 71, 45, 93, 20, 34, 42, 26, 27, 36, 96, 54, 72, 97, 64, 78, 24, 40, 18, 43, 12, 72, 3, 24, 15, 17, 48, 57, 91, 12, 54, 31, 96, 30, 71, 43, 81, 49, 57, 5, 87, 85, 94, 15, 11, 2, 71, 84, 59, 91, 86, 51, 66, 65, 2, 8, 33, 88, 81, 43, 77, 25, 47, 34, 92, 52, 58, 26, 56, 0, 99, 86, 1, 3, 3, 4, 4, 30, 43, 17, 51, 13, 14, 84, 75, 16, 16, 60, 18, 18, 95, 20, 18, 0, 22, 23, 25, 72], [35, 73, 73, 68, 29, 94, 5, 93, 95, 36, 95, 13, 19, 92, 93, 63, 85, 2, 34, 32, 60, 59, 44, 32, 22, 99, 52, 90, 15, 39, 82, 16, 74, 29, 83, 56, 14, 76, 25, 30, 50, 81, 59, 77, 50, 58, 40, 48, 97, 93, 18, 86, 41, 42, 80, 66, 75, 55, 23, 47, 87, 34, 31, 48, 60, 55, 20, 62, 38, 0, 94, 28, 15, 15, 15, 19, 20, 20, 21, 21, 65, 83, 43, 24, 43, 27, 71, 62, 29, 95, 38, 30, 28, 63, 35, 35, 35, 2, 28, 82], [72, 75, 31, 54, 26, 76, 75, 66, 66, 58, 25, 41, 25, 77, 78, 96, 26, 93, 49, 96, 30, 67, 25, 31, 44, 28, 1, 83, 31, 30, 46, 36, 72, 26, 2, 82, 48, 2, 83, 62, 50, 71, 84, 25, 2, 27, 27, 74, 89, 82, 26, 68, 72, 97, 76, 54, 82, 12, 81, 78, 48, 63, 11, 45, 71, 98, 68, 67, 11, 95, 51, 11, 20, 63, 97, 7, 33, 82, 66, 10, 71, 23, 19, 0, 58, 66, 27, 78, 55, 11, 97, 76, 45, 0, 87, 48, 47, 40, 3, 9], [95, 8, 13, 98, 39, 11, 62, 16, 75, 90, 10, 18, 2, 90, 9, 91, 53, 11, 65, 85, 7, 89, 9, 31, 40, 6, 2, 0, 49, 15, 91, 86, 76, 0, 32, 95, 40, 11, 8, 5, 81, 75, 65, 49, 40, 10, 63, 65, 55, 65, 74, 10, 98, 93, 61, 65, 86, 28, 8, 18, 90, 55, 32, 16, 36, 63, 55, 81, 66, 17, 46, 58, 38, 6, 18, 99, 6, 80, 33, 13, 88, 47, 37, 12, 80, 50, 79, 21, 7, 78, 74, 95, 25, 61, 95, 51, 27, 17, 27, 96], [82, 34, 30, 45, 20, 12, 97, 65, 91, 96, 24, 1, 22, 34, 44, 10, 75, 15, 43, 64, 88, 90, 80, 41, 47, 16, 79, 26, 5, 76, 14, 76, 43, 3, 83, 99, 78, 9, 68, 79, 97, 14, 62, 19, 19, 20, 20, 47, 22, 23, 23, 52, 26, 60, 81, 29, 29, 29, 30, 30, 30, 30, 30, 29, 8, 63, 97, 11, 34, 34, 49, 74, 0, 67, 14, 46, 50, 37, 81, 39, 18, 51, 17, 41, 78, 30, 43, 83, 62, 99, 66, 79, 66, 26, 44, 44, 40, 76, 28, 45], [63, 27, 70, 78, 87, 64, 58, 17, 72, 53, 32, 90, 80, 8, 72, 71, 72, 52, 57, 61, 99, 56, 71, 17, 54, 88, 29, 79, 25, 27, 65, 32, 45, 96, 74, 66, 72, 12, 48, 30, 13, 10, 7, 71, 10, 28, 29, 70, 51, 85, 50, 92, 59, 90, 1, 47, 26, 42, 75, 85, 42, 59, 25, 77, 66, 16, 87, 63, 7, 31, 50, 71, 82, 2, 57, 55, 4, 24, 2, 71, 57, 24, 59, 32, 79, 14, 20, 74, 86, 64, 6, 4, 66, 61, 38, 65, 46, 66, 1, 1], [82, 50, 90, 55, 45, 28, 65, 73, 96, 90, 87, 99, 15, 56, 73, 5, 64, 54, 99, 78, 61, 56, 44, 76, 72, 30, 31, 67, 26, 86, 83, 12, 62, 83, 57, 47, 87, 44, 47, 39, 96, 49, 54, 81, 96, 18, 24, 5, 76, 76, 70, 49, 70, 75, 65, 4, 27, 11, 67, 11, 92, 95, 55, 69, 20, 64, 84, 71, 30, 20, 81, 59, 62, 80, 97, 11, 79, 79, 74, 24, 95, 93, 55, 96, 1, 3, 96, 28, 4, 68, 7, 83, 33, 14, 54, 16, 15, 34, 17, 35], [10, 10, 37, 51, 24, 85, 5, 98, 76, 10, 45, 67, 60, 50, 88, 66, 12, 6, 69, 41, 18, 39, 49, 55, 28, 67, 12, 50, 95, 41, 28, 37, 81, 95, 9, 61, 49, 89, 67, 19, 50, 72, 55, 44, 58, 60, 62, 61, 8, 16, 65, 11, 18, 49, 5, 28, 5, 90, 56, 95, 69, 37, 3, 97, 64, 29, 93, 87, 66, 63, 63, 36, 33, 24, 88, 96, 74, 15, 71, 64, 63, 33, 28, 42, 27, 36, 21, 44, 71, 77, 9, 46, 12, 10, 60, 61, 99, 1, 51, 4], [45, 76, 22, 36, 97, 10, 80, 84, 16, 77, 0, 99, 9, 54, 98, 50, 97, 72, 46, 86, 73, 74, 42, 33, 49, 22, 37, 3, 61, 77, 63, 74, 25, 56, 55, 92, 70, 77, 39, 24, 62, 15, 30, 61, 25, 60, 87, 15, 62, 71, 70, 76, 54, 81, 82, 70, 1, 93, 95, 98, 39, 96, 66, 16, 96, 42, 39, 45, 23, 71, 50, 1, 64, 81, 76, 2, 57, 96, 51, 4, 94, 0, 55, 13, 4, 4, 45, 7, 10, 67, 9, 6, 87, 50, 12, 13, 14, 15, 16, 20], [13, 38, 28, 44, 3, 59, 50, 74, 33, 0, 78, 6, 3, 58, 4, 95, 38, 30, 28, 95, 75, 13, 13, 86, 0, 21, 18, 20, 20, 21, 90, 23, 23, 71, 24, 97, 25, 26, 26, 46, 92, 40, 29, 47, 39, 2, 28, 33, 33, 56, 82, 34, 34, 35, 83, 1, 52, 12, 42, 39, 39, 15, 15, 40, 40, 40, 40, 42, 8, 43, 43, 43, 43, 43, 7, 94, 36, 44, 44, 7, 54, 45, 45, 81, 83, 57, 46, 55, 78, 47, 20, 59, 0, 6, 79, 51, 59, 77, 11, 87], [90, 31, 20, 41, 68, 44, 0, 75, 26, 96, 48, 58, 50, 59, 45, 69, 72, 83, 3, 44, 46, 94, 64, 92, 32, 14, 72, 48, 6, 83, 49, 54, 9, 34, 62, 11, 72, 2, 51, 17, 64, 30, 54, 61, 62, 91, 71, 50, 50, 95, 94, 40, 76, 52, 49, 78, 83, 62, 51, 38, 59, 11, 36, 38, 2, 74, 72, 96, 76, 83, 0, 14, 21, 60, 42, 41, 82, 71, 27, 27, 89, 48, 72, 41, 49, 11, 92, 98, 64, 55, 94, 81, 26, 3, 6, 33, 59, 13, 13, 14], [17, 17, 83, 48, 69, 5, 66, 99, 4, 8, 86, 93, 28, 66, 66, 26, 21, 89, 6, 63, 56, 85, 7, 6, 43, 73, 6, 16, 8, 17, 51, 98, 25, 78, 2, 28, 66, 88, 76, 66, 53, 7, 41, 8, 90, 71, 87, 40, 37, 92, 62, 36, 5, 74, 75, 65, 16, 84, 46, 26, 94, 77, 61, 19, 26, 94, 55, 85, 1, 62, 97, 15, 0, 52, 70, 18, 22, 15, 16, 69, 18, 18, 79, 21, 61, 22, 22, 65, 82, 8, 24, 69, 63, 26, 26, 8, 42, 18, 41, 30], [5, 83, 53, 3, 99, 5, 70, 31, 6, 7, 0, 59, 56, 47, 40, 0, 50, 2, 63, 36, 11, 5, 71, 41, 87, 99, 12, 86, 11, 61, 59, 48, 17, 66, 89, 54, 7, 28, 45, 86, 95, 93, 34, 71, 7, 34, 46, 41, 42, 42, 35, 6, 5, 44, 27, 69, 59, 96, 90, 9, 35, 72, 28, 33, 79, 71, 21, 22, 77, 15, 79, 82, 46, 46, 91, 7, 38, 97, 24, 57, 11, 72, 96, 17, 3, 4, 4, 69, 9, 19, 14, 28, 15, 15, 15, 49, 16, 16, 17, 20], [0, 27, 33, 41, 78, 94, 57, 82, 95, 86, 7, 99, 62, 63, 57, 20, 30, 88, 51, 3, 68, 58, 18, 1, 37, 5, 50, 18, 21, 14, 26, 66, 2, 99, 20, 75, 8, 98, 77, 65, 83, 46, 62, 21, 31, 66, 0, 26, 52, 4, 57, 64, 53, 42, 92, 83, 50, 63, 76, 40, 43, 46, 74, 61, 96, 21, 45, 37, 59, 5, 72, 17, 80, 88, 42, 72, 3, 3, 4, 97, 9, 9, 9, 9, 9, 85, 18, 18, 58, 95, 19, 43, 80, 24, 25, 25, 26, 27, 49, 46], [58, 71, 32, 61, 49, 94, 62, 42, 1, 28, 20, 69, 53, 83, 14, 66, 33, 80, 23, 14, 60, 58, 55, 45, 17, 20, 96, 80, 11, 54, 50, 99, 30, 50, 38, 30, 46, 87, 61, 36, 71, 95, 81, 79, 72, 63, 96, 72, 30, 27, 28, 69, 77, 52, 71, 0, 78, 63, 1, 3, 3, 3, 4, 25, 23, 9, 36, 61, 31, 54, 81, 15, 17, 5, 18, 18, 19, 20, 20, 34, 22, 22, 22, 85, 1, 27, 27, 16, 32, 90, 83, 44, 94, 40, 20, 40, 91, 41, 35, 64], [53, 70, 30, 43, 14, 99, 77, 72, 78, 89, 32, 2, 60, 15, 64, 56, 56, 72, 12, 81, 25, 75, 18, 3, 38, 22, 24, 17, 7, 92, 9, 72, 41, 66, 94, 79, 86, 66, 1, 60, 26, 43, 31, 55, 6, 1, 44, 13, 32, 71, 47, 12, 62, 83, 52, 19, 12, 89, 6, 32, 28, 66, 62, 7, 60, 54, 8, 36, 19, 51, 79, 21, 14, 76, 3, 43, 19, 94, 13, 14, 15, 46, 16, 59, 40, 22, 22, 23, 25, 25, 37, 29, 44, 58, 48, 99, 98, 33, 94, 7], [67, 32, 97, 88, 27, 39, 9, 33, 87, 98, 30, 88, 14, 87, 55, 43, 36, 32, 45, 9, 86, 26, 65, 29, 82, 40, 10, 48, 77, 95, 79, 45, 76, 96, 31, 49, 14, 83, 79, 86, 65, 81, 14, 76, 21, 79, 59, 27, 22, 64, 40, 92, 32, 27, 94, 87, 32, 11, 67, 93, 8, 82, 47, 82, 77, 68, 95, 10, 60, 70, 13, 38, 74, 92, 11, 94, 53, 30, 13, 99, 17, 18, 0, 27, 83, 99, 10, 9, 14, 38, 15, 15, 37, 99, 17, 19, 19, 19, 12, 21], [31, 10, 63, 1, 37, 98, 92, 62, 65, 32, 53, 21, 22, 31, 12, 52, 99, 10, 46, 80, 10, 10, 24, 50, 69, 68, 93, 26, 31, 12, 31, 90, 19, 45, 22, 26, 55, 27, 98, 98, 8, 93, 1, 94, 48, 31, 8, 66, 19, 20, 62, 25, 14, 98, 27, 5, 14, 86, 5, 19, 5, 12, 62, 18, 39, 93, 2, 55, 65, 47, 20, 12, 64, 72, 61, 0, 75, 40, 72, 60, 37, 12, 60, 12, 9, 25, 94, 41, 48, 89, 38, 74, 66, 79, 31, 9, 14, 13, 13, 14], [76, 81, 71, 32, 49, 11, 54, 90, 99, 17, 54, 78, 74, 82, 3, 98, 93, 16, 65, 98, 85, 61, 21, 2, 78, 97, 47, 6, 5, 94, 67, 28, 28, 82, 76, 34, 93, 97, 65, 27, 22, 48, 5, 19, 67, 85, 93, 79, 66, 54, 58, 64, 5, 81, 38, 22, 84, 81, 81, 93, 89, 63, 27, 69, 82, 40, 38, 42, 99, 24, 18, 7, 50, 55, 61, 18, 7, 20, 10, 22, 22, 10, 24, 24, 40, 45, 25, 17, 26, 26, 36, 29, 29, 29, 93, 96, 47, 34, 35, 6], [85, 39, 47, 38, 21, 63, 96, 53, 52, 9, 47, 98, 0, 65, 11, 47, 22, 42, 81, 51, 11, 85, 21, 5, 96, 93, 38, 0, 3, 94, 32, 81, 19, 17, 29, 27, 14, 9, 9, 62, 96, 32, 13, 37, 15, 16, 67, 77, 74, 24, 71, 8, 29, 29, 57, 30, 25, 34, 8, 37, 37, 37, 58, 32, 41, 99, 15, 42, 42, 75, 43, 43, 43, 44, 44, 44, 30, 75, 45, 45, 45, 26, 43, 8, 46, 46, 46, 46, 65, 60, 58, 93, 57, 47, 40, 46, 80, 52, 65, 66], [0, 78, 89, 72, 52, 86, 92, 32, 87, 61, 92, 33, 18, 83, 55, 56, 35, 15, 64, 42, 96, 39, 87, 48, 60, 61, 44, 49, 60, 14, 53, 70, 18, 6, 76, 74, 66, 15, 2, 57, 63, 18, 99, 51, 49, 1, 27, 33, 96, 80, 21, 17, 60, 46, 37, 86, 4, 36, 22, 77, 58, 35, 25, 23, 50, 58, 0, 94, 59, 77, 42, 66, 88, 40, 41, 31, 93, 46, 17, 33, 69, 96, 68, 72, 85, 37, 49, 99, 27, 7, 1, 31, 59, 27, 95, 98, 1, 1, 3, 73], [95, 97, 81, 40, 79, 58, 35, 75, 98, 79, 92, 50, 72, 54, 11, 79, 11, 58, 54, 38, 0, 2, 49, 31, 67, 46, 49, 81, 22, 83, 38, 99, 64, 76, 6, 11, 64, 16, 76, 46, 46, 23, 60, 3, 53, 50, 63, 6, 31, 9, 49, 46, 13, 14, 40, 67, 15, 16, 17, 19, 56, 21, 36, 22, 22, 23, 5, 25, 36, 26, 26, 92, 29, 29, 78, 96, 62, 77, 19, 81, 34, 35, 35, 35, 98, 29, 37, 32, 39, 41, 41, 13, 43, 4, 32, 87, 40, 44, 50, 33], [32, 83, 49, 47, 94, 24, 48, 48, 47, 43, 8, 88, 8, 19, 59, 11, 34, 15, 32, 66, 64, 6, 46, 3, 33, 49, 81, 30, 39, 5, 18, 15, 92, 34, 61, 49, 5, 89, 85, 20, 71, 12, 87, 49, 77, 67, 94, 23, 12, 28, 92, 78, 97, 48, 99, 25, 81, 18, 21, 85, 94, 2, 75, 21, 44, 5, 86, 94, 5, 45, 23, 6, 14, 40, 36, 15, 77, 63, 7, 69, 84, 4, 67, 10, 21, 42, 44, 15, 19, 18, 22, 22, 22, 23, 23, 24, 24, 63, 29, 29], [56, 57, 72, 21, 91, 72, 60, 24, 63, 75, 35, 71, 62, 31, 84, 59, 6, 66, 83, 52, 25, 53, 4, 18, 12, 62, 6, 76, 63, 31, 47, 79, 74, 67, 71, 33, 36, 47, 85, 84, 53, 27, 82, 16, 71, 62, 58, 26, 95, 58, 9, 65, 25, 62, 59, 81, 13, 13, 15, 15, 16, 16, 11, 17, 54, 49, 32, 62, 22, 62, 23, 24, 25, 25, 25, 25, 25, 38, 26, 27, 27, 71, 29, 33, 62, 97, 33, 33, 37, 92, 1, 34, 40, 35, 7, 37, 41, 39, 39, 39], [44, 11, 20, 29, 62, 53, 20, 65, 50, 37, 87, 59, 15, 10, 35, 36, 5, 33, 39, 87, 16, 10, 17, 83, 63, 7, 28, 83, 43, 8, 77, 97, 55, 3, 63, 90, 89, 30, 26, 90, 31, 39, 68, 62, 96, 87, 81, 79, 75, 51, 79, 24, 10, 6, 98, 1, 65, 92, 91, 90, 7, 76, 57, 14, 44, 81, 54, 1, 35, 44, 92, 4, 14, 95, 43, 92, 24, 16, 84, 76, 17, 17, 96, 18, 32, 74, 23, 24, 24, 58, 25, 25, 2, 26, 76, 59, 76, 29, 30, 35], [4, 89, 47, 12, 8, 55, 40, 79, 39, 31, 72, 79, 27, 59, 69, 60, 59, 26, 32, 15, 67, 24, 32, 84, 89, 89, 65, 43, 54, 31, 63, 73, 98, 8, 50, 51, 71, 29, 55, 28, 7, 54, 2, 8, 73, 63, 75, 68, 48, 96, 68, 7, 54, 57, 3, 2, 58, 56, 78, 21, 48, 46, 12, 83, 41, 0, 23, 1, 42, 4, 57, 7, 28, 11, 57, 73, 69, 13, 14, 14, 7, 18, 94, 20, 21, 21, 22, 22, 25, 26, 8, 51, 73, 68, 9, 33, 33, 33, 34, 34], [99, 27, 97, 21, 77, 0, 10, 77, 55, 94, 62, 68, 5, 40, 86, 65, 55, 38, 35, 16, 46, 57, 11, 62, 31, 30, 94, 79, 81, 27, 76, 32, 65, 30, 86, 81, 1, 89, 29, 59, 40, 71, 48, 99, 40, 99, 61, 21, 83, 47, 38, 8, 57, 75, 86, 35, 20, 79, 28, 17, 69, 94, 24, 11, 50, 95, 86, 10, 0, 47, 11, 38, 10, 3, 58, 8, 13, 16, 18, 18, 71, 21, 22, 6, 25, 25, 96, 26, 29, 29, 39, 18, 10, 85, 33, 70, 34, 98, 35, 3], [66, 10, 32, 90, 0, 43, 28, 73, 77, 55, 37, 5, 77, 6, 1, 38, 48, 39, 54, 8, 1, 55, 74, 82, 65, 58, 86, 43, 39, 63, 53, 80, 47, 87, 11, 49, 48, 54, 1, 24, 12, 90, 94, 51, 22, 5, 27, 12, 12, 54, 2, 10, 21, 30, 47, 40, 33, 49, 99, 53, 27, 94, 37, 94, 62, 31, 84, 2, 94, 75, 75, 35, 91, 9, 39, 42, 75, 1, 29, 48, 49, 33, 83, 5, 28, 51, 46, 18, 74, 54, 42, 99, 89, 70, 31, 76, 10, 71, 15, 17], [38, 27, 87, 65, 0, 47, 24, 59, 41, 10, 69, 99, 34, 95, 43, 66, 52, 99, 74, 8, 2, 62, 35, 77, 27, 35, 76, 69, 40, 10, 64, 79, 23, 59, 83, 7, 43, 29, 76, 82, 98, 31, 8, 54, 50, 49, 80, 41, 77, 87, 64, 4, 41, 33, 73, 13, 51, 16, 19, 81, 20, 42, 22, 23, 25, 77, 26, 4, 29, 29, 29, 30, 30, 4, 49, 63, 34, 34, 76, 35, 35, 35, 18, 78, 83, 66, 37, 37, 26, 54, 82, 40, 74, 41, 41, 41, 67, 39, 78, 43], [45, 65, 91, 80, 23, 68, 97, 69, 80, 36, 12, 30, 68, 82, 32, 23, 43, 65, 31, 65, 96, 97, 58, 34, 36, 8, 41, 79, 42, 47, 29, 4, 58, 15, 75, 83, 95, 5, 10, 2, 83, 39, 93, 20, 95, 6, 31, 63, 62, 95, 45, 99, 51, 50, 5, 76, 11, 59, 47, 41, 74, 36, 84, 74, 13, 74, 7, 38, 1, 3, 4, 63, 12, 79, 6, 13, 13, 16, 16, 19, 41, 18, 18, 20, 20, 42, 22, 23, 23, 23, 64, 24, 97, 32, 30, 30, 66, 55, 27, 77], [70, 45, 6, 5, 99, 65, 6, 21, 48, 7, 72, 49, 22, 10, 31, 55, 9, 28, 65, 75, 54, 99, 41, 11, 92, 55, 0, 52, 18, 19, 36, 3, 92, 36, 58, 45, 63, 36, 76, 0, 77, 91, 96, 2, 74, 87, 41, 58, 85, 61, 50, 35, 89, 38, 32, 17, 73, 35, 89, 31, 48, 5, 89, 35, 59, 55, 11, 84, 33, 37, 12, 15, 13, 13, 14, 36, 16, 16, 19, 20, 39, 21, 24, 25, 27, 27, 26, 29, 33, 89, 94, 33, 33, 0, 95, 34, 34, 34, 35, 35], [13, 82, 47, 47, 41, 87, 52, 36, 5, 4, 86, 53, 97, 33, 95, 8, 99, 61, 76, 10, 99, 57, 58, 49, 98, 48, 71, 21, 12, 96, 31, 47, 39, 78, 4, 26, 36, 19, 8, 5, 19, 6, 6, 77, 74, 9, 78, 89, 55, 23, 19, 87, 96, 67, 92, 31, 8, 28, 62, 31, 28, 26, 65, 67, 55, 73, 58, 37, 76, 58, 36, 3, 48, 7, 81, 64, 89, 49, 37, 84, 71, 50, 54, 33, 32, 49, 40, 97, 49, 53, 3, 48, 83, 64, 95, 90, 16, 16, 16, 66], [79, 83, 16, 1, 9, 31, 43, 21, 99, 58, 32, 96, 6, 48, 12, 94, 74, 50, 8, 80, 64, 63, 64, 94, 11, 34, 14, 44, 26, 74, 19, 31, 56, 84, 44, 22, 16, 94, 65, 19, 66, 58, 14, 49, 3, 8, 65, 92, 67, 42, 87, 97, 58, 6, 32, 9, 92, 2, 20, 8, 76, 69, 7, 51, 71, 65, 4, 90, 60, 98, 32, 4, 40, 31, 9, 10, 89, 26, 58, 88, 89, 58, 16, 16, 16, 82, 19, 19, 20, 32, 77, 23, 23, 24, 75, 25, 19, 27, 49, 79], [97, 80, 14, 63, 28, 87, 90, 12, 1, 90, 57, 80, 11, 96, 13, 13, 87, 52, 27, 77, 92, 13, 24, 81, 24, 65, 72, 79, 42, 81, 15, 56, 79, 12, 92, 44, 42, 95, 24, 70, 19, 22, 21, 62, 44, 76, 86, 87, 37, 3, 6, 15, 49, 51, 90, 0, 24, 7, 61, 97, 14, 86, 59, 67, 31, 81, 56, 25, 99, 88, 24, 36, 97, 9, 3, 63, 74, 84, 54, 55, 77, 97, 19, 27, 46, 3, 3, 58, 31, 62, 37, 9, 9, 79, 16, 19, 18, 44, 21, 86], [10, 20, 35, 29, 44, 6, 37, 96, 62, 20, 37, 91, 27, 28, 23, 89, 87, 4, 95, 25, 50, 73, 24, 26, 13, 95, 48, 18, 88, 10, 93, 39, 33, 95, 94, 33, 17, 19, 41, 80, 13, 95, 99, 31, 88, 7, 3, 23, 80, 63, 80, 26, 23, 3, 38, 39, 0, 3, 5, 38, 7, 17, 71, 14, 14, 16, 38, 9, 40, 58, 86, 80, 14, 22, 6, 25, 7, 26, 74, 29, 29, 14, 31, 4, 34, 34, 35, 35, 71, 86, 68, 97, 37, 51, 39, 39, 39, 54, 40, 18], [25, 7, 38, 34, 5, 50, 35, 99, 93, 49, 99, 5, 23, 1, 7, 28, 74, 95, 98, 88, 62, 57, 27, 49, 99, 79, 28, 40, 26, 32, 28, 33, 10, 78, 62, 21, 86, 6, 88, 78, 21, 41, 15, 63, 31, 16, 96, 93, 5, 12, 68, 39, 50, 1, 79, 67, 48, 87, 61, 32, 74, 51, 98, 74, 32, 87, 86, 76, 10, 8, 76, 48, 80, 50, 48, 81, 21, 32, 61, 96, 86, 38, 90, 55, 17, 38, 98, 97, 74, 4, 89, 54, 0, 95, 94, 9, 5, 17, 11, 75], [15, 54, 83, 3, 83, 33, 89, 36, 56, 66, 86, 28, 88, 62, 89, 45, 12, 85, 91, 38, 74, 6, 7, 28, 19, 25, 0, 70, 56, 50, 38, 85, 5, 97, 81, 40, 17, 9, 62, 12, 47, 8, 45, 57, 42, 50, 71, 20, 87, 94, 36, 85, 97, 40, 12, 27, 46, 63, 34, 40, 33, 0, 1, 39, 19, 4, 4, 4, 15, 63, 9, 96, 66, 78, 13, 13, 16, 16, 8, 18, 18, 20, 20, 75, 2, 23, 25, 25, 25, 42, 27, 66, 77, 77, 29, 74, 12, 33, 75, 35], [17, 47, 15, 64, 42, 98, 54, 70, 99, 62, 34, 6, 71, 81, 54, 76, 60, 63, 72, 64, 68, 46, 49, 2, 86, 96, 14, 96, 71, 6, 32, 61, 23, 83, 32, 55, 87, 38, 62, 65, 42, 50, 72, 2, 73, 61, 88, 72, 36, 85, 7, 87, 61, 75, 74, 64, 53, 84, 43, 60, 12, 71, 44, 46, 43, 30, 78, 0, 24, 93, 76, 0, 57, 98, 21, 74, 10, 37, 92, 3, 54, 15, 66, 50, 71, 60, 89, 85, 64, 49, 58, 46, 66, 79, 79, 23, 5, 1, 54, 26], [10, 46, 43, 61, 48, 25, 51, 28, 36, 56, 44, 56, 26, 43, 44, 41, 4, 87, 12, 71, 74, 90, 82, 91, 6, 62, 96, 35, 79, 51, 86, 26, 34, 92, 20, 72, 5, 49, 36, 58, 54, 10, 2, 92, 73, 60, 71, 13, 0, 5, 10, 74, 10, 47, 66, 68, 57, 28, 67, 41, 16, 21, 27, 22, 25, 29, 27, 27, 29, 29, 67, 5, 5, 33, 27, 76, 34, 78, 56, 35, 35, 33, 22, 78, 36, 37, 37, 40, 11, 40, 41, 41, 42, 74, 43, 44, 23, 45, 45, 45], [71, 81, 59, 35, 11, 99, 75, 12, 64, 54, 3, 82, 6, 31, 31, 24, 22, 90, 1, 49, 10, 6, 45, 7, 62, 57, 92, 41, 8, 58, 63, 67, 90, 8, 61, 95, 81, 62, 28, 0, 44, 14, 87, 98, 56, 86, 92, 48, 99, 51, 55, 99, 70, 35, 17, 40, 31, 66, 97, 61, 99, 97, 81, 55, 40, 99, 87, 72, 51, 76, 76, 13, 86, 20, 50, 49, 66, 36, 75, 38, 40, 47, 86, 16, 24, 70, 68, 63, 58, 50, 80, 1, 76, 95, 96, 12, 49, 42, 9, 10], [31, 84, 52, 42, 93, 16, 49, 20, 42, 86, 50, 42, 11, 82, 47, 24, 52, 72, 63, 10, 87, 31, 66, 8, 69, 5, 40, 50, 9, 75, 0, 85, 94, 75, 85, 59, 84, 95, 32, 65, 20, 8, 42, 34, 55, 56, 3, 79, 17, 21, 21, 38, 11, 24, 53, 30, 5, 45, 77, 90, 81, 44, 38, 3, 99, 74, 87, 50, 0, 0, 4, 43, 85, 54, 93, 13, 60, 30, 84, 22, 85, 23, 23, 23, 85, 1, 25, 65, 26, 54, 52, 29, 29, 29, 32, 86, 34, 67, 61, 92]]
    # 19 - [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [33, 10, 61, 84, 32, 13, 50, 50, 68, 70, 37, 99, 30, 7, 2, 64, 69, 91, 2, 13, 1, 11, 12, 11, 46, 28, 35, 47, 14, 15, 22, 4, 0, 62, 53, 95, 27, 38, 20, 3, 17, 92, 70, 29, 49, 57, 80, 26, 48, 58, 36, 66, 71, 5, 49, 95, 89, 0, 4, 4, 28, 8, 9, 9, 1, 12, 34, 14, 75, 66, 72, 37, 49, 9, 26, 71, 68, 77, 65, 48, 51, 43, 61, 46, 46, 65, 52, 3, 14, 8, 52, 94, 66, 56, 57, 57, 58, 58, 59, 2], [82, 57, 40, 97, 70, 96, 16, 79, 35, 84, 29, 99, 28, 1, 87, 87, 26, 52, 24, 49, 75, 85, 32, 25, 91, 51, 56, 96, 50, 55, 83, 1, 87, 30, 44, 38, 72, 27, 3, 7, 82, 25, 67, 44, 80, 27, 97, 13, 3, 94, 38, 2, 27, 64, 52, 18, 70, 5, 2, 81, 3, 65, 89, 15, 31, 75, 9, 91, 99, 67, 98, 26, 0, 1, 4, 5, 5, 36, 12, 94, 70, 17, 16, 16, 16, 62, 39, 93, 73, 30, 84, 47, 51, 50, 41, 1, 75, 81, 52, 52], [65, 53, 91, 39, 81, 43, 22, 28, 69, 61, 87, 63, 75, 38, 75, 83, 21, 76, 19, 13, 6, 37, 8, 94, 47, 49, 35, 21, 27, 64, 89, 38, 98, 73, 67, 33, 98, 2, 38, 54, 33, 42, 88, 38, 92, 27, 99, 75, 0, 4, 4, 4, 58, 85, 31, 56, 24, 93, 68, 65, 22, 25, 74, 44, 59, 98, 90, 51, 39, 40, 41, 41, 81, 46, 62, 39, 52, 67, 45, 56, 30, 53, 47, 63, 67, 51, 66, 66, 66, 1, 93, 27, 69, 1, 29, 71, 74, 43, 78, 47], [14, 14, 14, 42, 49, 70, 39, 39, 65, 59, 52, 91, 42, 3, 93, 76, 29, 30, 87, 94, 2, 0, 31, 9, 12, 61, 15, 16, 69, 58, 72, 98, 76, 84, 27, 94, 61, 34, 35, 41, 41, 43, 94, 6, 46, 88, 50, 47, 19, 98, 86, 86, 52, 53, 87, 57, 57, 10, 95, 60, 60, 60, 47, 39, 62, 14, 82, 0, 68, 67, 25, 72, 75, 17, 99, 17, 7, 49, 78, 79, 28, 81, 81, 82, 82, 34, 6, 59, 93, 84, 30, 85, 61, 70, 92, 90, 90, 75, 34, 3], [83, 67, 49, 25, 19, 5, 44, 83, 34, 76, 42, 56, 6, 16, 18, 38, 43, 38, 59, 49, 83, 28, 91, 36, 66, 62, 48, 92, 70, 83, 37, 93, 21, 26, 70, 83, 53, 5, 14, 15, 51, 26, 28, 76, 83, 70, 11, 18, 28, 33, 27, 35, 99, 72, 46, 0, 95, 62, 25, 62, 54, 29, 55, 56, 6, 57, 59, 65, 18, 13, 30, 41, 66, 90, 68, 68, 42, 69, 71, 74, 75, 78, 78, 73, 80, 3, 82, 98, 83, 83, 36, 92, 2, 37, 60, 85, 85, 77, 73, 16], [86, 0, 89, 23, 1, 4, 58, 19, 7, 54, 9, 73, 5, 40, 15, 15, 16, 17, 21, 81, 24, 47, 33, 35, 35, 41, 78, 45, 45, 46, 46, 46, 47, 34, 77, 23, 52, 53, 54, 55, 55, 49, 57, 57, 1, 61, 91, 60, 25, 87, 98, 66, 66, 21, 10, 68, 69, 54, 70, 71, 37, 74, 31, 98, 76, 76, 49, 78, 81, 82, 19, 83, 20, 34, 53, 81, 9, 85, 85, 85, 89, 87, 40, 58, 81, 40, 94, 3, 90, 90, 90, 90, 90, 61, 64, 93, 7, 53, 96, 58], [28, 70, 60, 16, 26, 20, 41, 55, 13, 20, 25, 8, 92, 1, 2, 11, 24, 2, 61, 34, 49, 7, 9, 9, 3, 11, 16, 37, 26, 66, 37, 95, 64, 21, 44, 23, 44, 83, 69, 33, 35, 75, 39, 83, 43, 45, 91, 56, 61, 49, 51, 54, 62, 38, 59, 9, 60, 86, 31, 10, 86, 5, 66, 69, 69, 3, 94, 74, 74, 74, 28, 76, 77, 77, 77, 65, 78, 80, 80, 80, 26, 68, 20, 84, 28, 32, 39, 69, 90, 90, 70, 95, 95, 95, 97, 77, 4, 96, 96, 96], [11, 13, 57, 12, 48, 77, 8, 28, 35, 99, 98, 32, 54, 11, 21, 0, 20, 4, 4, 70, 24, 9, 25, 89, 12, 65, 89, 8, 96, 16, 17, 91, 60, 86, 88, 76, 54, 47, 29, 39, 35, 41, 50, 45, 45, 52, 46, 31, 42, 51, 56, 57, 13, 86, 28, 63, 63, 18, 36, 34, 50, 34, 72, 48, 69, 64, 77, 89, 41, 78, 79, 80, 98, 82, 23, 84, 25, 42, 89, 68, 90, 90, 90, 46, 50, 26, 80, 51, 49, 84, 42, 95, 95, 17, 14, 75, 96, 8, 52, 60], [7, 10, 42, 65, 71, 38, 96, 60, 11, 30, 34, 21, 26, 73, 37, 55, 28, 64, 30, 22, 31, 63, 58, 56, 87, 25, 58, 91, 21, 38, 13, 16, 18, 84, 24, 71, 70, 29, 72, 40, 46, 24, 5, 91, 8, 57, 11, 11, 99, 14, 84, 25, 25, 16, 15, 2, 10, 68, 27, 39, 75, 91, 93, 33, 83, 32, 43, 8, 75, 20, 61, 38, 93, 54, 54, 54, 54, 23, 55, 55, 56, 47, 56, 74, 61, 27, 62, 49, 51, 66, 30, 19, 34, 22, 28, 12, 72, 72, 80, 74], [46, 69, 31, 26, 42, 29, 48, 87, 86, 31, 33, 83, 67, 65, 78, 57, 34, 24, 61, 90, 50, 93, 19, 97, 42, 72, 64, 99, 35, 31, 0, 26, 81, 94, 46, 7, 16, 27, 43, 46, 22, 52, 57, 27, 10, 35, 97, 40, 43, 45, 37, 34, 79, 47, 7, 82, 51, 52, 29, 42, 55, 57, 59, 60, 62, 61, 23, 50, 59, 74, 96, 75, 75, 77, 80, 51, 78, 82, 82, 83, 84, 38, 50, 85, 69, 93, 9, 90, 36, 45, 26, 5, 94, 45, 96, 6, 87, 61, 57, 46], [68, 36, 13, 48, 79, 84, 13, 35, 65, 21, 6, 99, 51, 59, 2, 45, 79, 96, 37, 13, 70, 99, 79, 11, 71, 18, 94, 86, 94, 27, 42, 11, 70, 37, 50, 90, 75, 90, 75, 79, 95, 49, 7, 6, 99, 99, 84, 50, 61, 25, 68, 30, 78, 88, 32, 3, 50, 4, 26, 17, 8, 48, 15, 86, 62, 21, 95, 83, 20, 35, 59, 40, 47, 41, 29, 43, 46, 71, 53, 57, 54, 55, 10, 59, 60, 23, 99, 61, 24, 26, 7, 63, 47, 99, 76, 68, 62, 12, 4, 72], [18, 28, 59, 59, 77, 63, 91, 75, 73, 17, 50, 15, 47, 31, 10, 93, 10, 38, 19, 44, 72, 96, 30, 67, 20, 38, 30, 86, 86, 49, 57, 26, 25, 61, 60, 96, 42, 77, 36, 49, 72, 86, 55, 78, 27, 6, 62, 18, 24, 36, 11, 47, 49, 13, 2, 93, 88, 57, 96, 26, 49, 19, 3, 82, 49, 63, 38, 91, 41, 74, 26, 69, 72, 66, 18, 55, 13, 12, 54, 39, 8, 0, 0, 23, 5, 5, 9, 44, 11, 50, 79, 49, 17, 86, 39, 54, 89, 50, 31, 40], [80, 36, 28, 20, 81, 32, 93, 67, 34, 35, 61, 58, 84, 14, 62, 96, 28, 38, 38, 24, 80, 22, 36, 25, 40, 77, 81, 67, 77, 41, 63, 11, 60, 28, 50, 4, 69, 21, 58, 12, 0, 49, 75, 17, 81, 5, 31, 24, 91, 16, 19, 85, 86, 24, 73, 47, 33, 42, 39, 91, 41, 41, 45, 90, 27, 92, 51, 51, 53, 53, 54, 30, 56, 56, 57, 93, 4, 72, 71, 69, 69, 97, 45, 3, 9, 76, 6, 26, 79, 26, 82, 82, 82, 82, 86, 32, 51, 5, 14, 28], [63, 44, 61, 85, 63, 58, 1, 3, 73, 82, 38, 30, 96, 13, 14, 15, 30, 19, 87, 98, 71, 53, 27, 65, 29, 29, 32, 58, 67, 43, 9, 45, 46, 10, 66, 93, 33, 93, 52, 53, 53, 53, 17, 54, 55, 9, 59, 60, 85, 98, 63, 68, 97, 24, 69, 95, 40, 80, 78, 71, 71, 95, 76, 22, 11, 23, 62, 62, 80, 12, 73, 84, 94, 34, 85, 3, 76, 50, 98, 37, 90, 90, 90, 20, 30, 95, 96, 96, 21, 3, 3, 97, 97, 97, 97, 97, 97, 97, 97, 97], [55, 24, 92, 95, 7, 31, 50, 58, 38, 12, 0, 92, 12, 78, 47, 82, 62, 12, 50, 37, 82, 81, 43, 57, 87, 12, 77, 2, 4, 83, 5, 5, 26, 60, 8, 15, 38, 19, 1, 50, 67, 91, 2, 35, 61, 15, 39, 41, 41, 41, 41, 43, 45, 45, 51, 36, 93, 53, 54, 54, 54, 57, 57, 48, 30, 94, 83, 35, 25, 66, 14, 68, 5, 1, 69, 69, 12, 20, 93, 88, 72, 1, 40, 74, 74, 74, 62, 75, 76, 77, 95, 79, 1, 88, 4, 61, 44, 65, 66, 85], [52, 40, 52, 83, 18, 20, 31, 2, 34, 65, 74, 98, 82, 33, 23, 28, 70, 36, 11, 7, 96, 8, 15, 15, 31, 95, 82, 19, 21, 56, 91, 93, 32, 37, 40, 40, 41, 43, 84, 45, 45, 48, 88, 53, 53, 55, 55, 30, 65, 6, 58, 61, 3, 28, 67, 95, 83, 64, 3, 68, 69, 25, 71, 71, 72, 72, 87, 81, 70, 15, 78, 79, 24, 17, 17, 82, 83, 59, 86, 52, 84, 40, 9, 26, 28, 30, 90, 90, 90, 91, 10, 44, 20, 20, 25, 95, 87, 96, 96, 57], [35, 35, 44, 90, 77, 14, 14, 48, 28, 24, 19, 23, 8, 89, 73, 70, 86, 77, 48, 34, 11, 18, 62, 35, 93, 31, 3, 37, 38, 63, 6, 25, 39, 80, 53, 96, 50, 73, 4, 34, 24, 38, 36, 8, 10, 18, 5, 78, 89, 94, 23, 76, 3, 60, 94, 70, 53, 30, 6, 14, 16, 17, 66, 21, 22, 67, 8, 29, 32, 19, 28, 4, 46, 84, 8, 52, 54, 33, 71, 56, 57, 41, 69, 4, 8, 33, 18, 66, 68, 12, 71, 71, 24, 74, 74, 88, 76, 76, 78, 92], [50, 28, 77, 28, 42, 53, 49, 91, 24, 14, 2, 4, 26, 58, 9, 9, 70, 12, 93, 99, 17, 33, 95, 35, 59, 27, 92, 68, 33, 35, 5, 36, 94, 26, 39, 41, 41, 43, 45, 46, 46, 51, 54, 54, 57, 59, 85, 98, 6, 63, 3, 44, 46, 68, 8, 13, 71, 72, 72, 76, 11, 42, 75, 91, 82, 82, 83, 83, 59, 70, 14, 59, 3, 90, 90, 24, 55, 33, 40, 94, 99, 89, 0, 28, 80, 62, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 14, 24], [75, 37, 27, 89, 64, 42, 65, 85, 10, 89, 18, 95, 11, 45, 65, 75, 98, 36, 65, 75, 3, 92, 34, 99, 95, 10, 34, 21, 73, 89, 48, 37, 14, 3, 31, 0, 6, 92, 73, 97, 26, 92, 1, 86, 26, 40, 26, 55, 79, 77, 8, 19, 93, 41, 88, 37, 13, 94, 38, 40, 91, 12, 3, 58, 99, 26, 19, 16, 10, 70, 4, 5, 33, 19, 21, 21, 22, 44, 48, 45, 48, 83, 32, 33, 36, 52, 56, 41, 29, 25, 48, 49, 13, 11, 52, 53, 4, 54, 54, 54], [67, 56, 22, 11, 94, 94, 26, 7, 9, 24, 44, 63, 49, 71, 95, 27, 89, 45, 44, 61, 3, 65, 28, 99, 2, 79, 58, 77, 23, 36, 60, 43, 8, 45, 24, 29, 59, 84, 97, 88, 61, 76, 44, 99, 27, 44, 4, 85, 24, 84, 11, 79, 44, 59, 85, 4, 33, 46, 89, 87, 64, 92, 93, 64, 67, 2, 1, 98, 33, 56, 94, 68, 1, 2, 46, 56, 9, 15, 3, 16, 79, 56, 87, 13, 21, 56, 29, 33, 33, 35, 87, 67, 26, 86, 40, 41, 43, 53, 2, 55], [87, 7, 62, 7, 8, 38, 12, 14, 14, 10, 46, 66, 15, 89, 68, 90, 19, 62, 76, 65, 77, 28, 38, 80, 50, 41, 40, 70, 51, 43, 43, 17, 45, 45, 45, 76, 51, 51, 53, 14, 55, 57, 57, 26, 62, 11, 44, 33, 56, 35, 58, 28, 84, 72, 72, 74, 38, 37, 77, 77, 78, 80, 86, 81, 21, 51, 82, 82, 82, 84, 64, 87, 87, 50, 58, 65, 90, 84, 95, 59, 59, 65, 40, 62, 23, 80, 16, 86, 6, 55, 96, 96, 96, 55, 36, 48, 92, 43, 3, 63], [2, 0, 86, 2, 32, 55, 69, 86, 93, 30, 61, 7, 97, 65, 89, 62, 62, 86, 72, 56, 89, 59, 80, 75, 46, 23, 14, 26, 54, 53, 99, 85, 78, 40, 20, 64, 50, 15, 27, 25, 63, 66, 81, 80, 66, 27, 99, 10, 56, 89, 66, 75, 36, 95, 82, 73, 64, 88, 6, 50, 37, 18, 87, 83, 8, 87, 75, 5, 5, 23, 3, 15, 16, 73, 45, 64, 32, 92, 19, 19, 21, 98, 20, 33, 81, 52, 34, 43, 87, 45, 23, 85, 47, 47, 21, 57, 51, 51, 52, 53], [47, 62, 73, 13, 91, 90, 16, 89, 78, 28, 10, 97, 30, 54, 43, 40, 36, 41, 3, 18, 56, 51, 83, 24, 49, 94, 12, 21, 0, 3, 45, 67, 72, 69, 0, 58, 58, 4, 5, 31, 39, 14, 20, 16, 95, 32, 17, 69, 84, 96, 37, 9, 28, 32, 35, 18, 43, 27, 36, 81, 43, 49, 6, 58, 57, 67, 17, 85, 33, 27, 91, 99, 66, 10, 98, 69, 71, 53, 68, 74, 76, 77, 77, 62, 79, 17, 82, 82, 82, 0, 44, 11, 85, 26, 47, 34, 6, 65, 73, 90], [64, 92, 81, 14, 37, 1, 7, 8, 9, 83, 14, 14, 98, 17, 96, 27, 27, 22, 52, 50, 17, 9, 92, 97, 89, 87, 32, 33, 60, 36, 39, 40, 88, 46, 66, 18, 52, 54, 12, 56, 20, 66, 36, 79, 55, 24, 33, 66, 66, 76, 68, 72, 2, 69, 69, 61, 71, 72, 74, 34, 75, 78, 89, 82, 82, 82, 13, 85, 1, 98, 93, 0, 21, 90, 90, 10, 84, 89, 20, 43, 73, 96, 96, 4, 66, 97, 20, 20, 10, 93, 31, 28, 37, 50, 26, 31, 67, 18, 77, 38], [47, 53, 81, 91, 91, 78, 45, 54, 7, 34, 99, 30, 2, 6, 72, 51, 82, 19, 74, 75, 81, 7, 2, 37, 31, 8, 57, 79, 15, 96, 56, 32, 61, 99, 12, 52, 89, 41, 80, 80, 58, 70, 49, 86, 31, 40, 90, 44, 7, 36, 72, 63, 94, 58, 0, 56, 91, 0, 2, 33, 51, 80, 81, 16, 30, 61, 33, 19, 94, 58, 32, 32, 35, 36, 36, 39, 81, 43, 43, 23, 45, 45, 68, 52, 12, 53, 54, 55, 19, 56, 57, 57, 57, 7, 48, 51, 18, 68, 58, 49], [10, 56, 5, 37, 77, 20, 37, 38, 44, 67, 97, 55, 13, 21, 23, 79, 32, 23, 70, 53, 84, 93, 38, 62, 58, 3, 2, 60, 48, 59, 78, 30, 20, 83, 68, 63, 40, 59, 6, 0, 1, 93, 86, 59, 8, 72, 15, 17, 64, 51, 9, 27, 6, 88, 29, 33, 7, 17, 36, 24, 41, 41, 40, 43, 43, 99, 85, 54, 57, 57, 57, 10, 98, 60, 44, 27, 37, 50, 71, 72, 76, 74, 74, 75, 47, 77, 78, 97, 20, 19, 85, 84, 53, 64, 85, 85, 92, 87, 28, 35], [61, 14, 74, 54, 49, 74, 40, 63, 20, 50, 98, 91, 98, 13, 46, 65, 17, 86, 92, 81, 34, 67, 86, 98, 16, 20, 26, 40, 7, 24, 34, 20, 7, 31, 15, 91, 76, 10, 28, 25, 97, 0, 48, 91, 58, 9, 13, 65, 10, 29, 19, 95, 49, 36, 42, 14, 60, 36, 10, 41, 41, 48, 63, 6, 47, 44, 28, 33, 13, 5, 34, 52, 53, 53, 53, 97, 87, 22, 52, 11, 6, 63, 66, 68, 71, 71, 52, 72, 74, 74, 42, 23, 24, 78, 79, 79, 27, 7, 81, 82], [21, 72, 88, 98, 4, 94, 7, 14, 93, 45, 16, 16, 93, 19, 2, 23, 38, 37, 29, 88, 34, 32, 36, 35, 35, 39, 45, 10, 89, 29, 51, 15, 91, 48, 57, 46, 88, 32, 5, 63, 24, 69, 69, 39, 96, 71, 91, 74, 75, 76, 17, 78, 78, 62, 79, 79, 21, 85, 93, 83, 90, 90, 20, 35, 99, 67, 93, 44, 9, 20, 45, 95, 95, 51, 85, 96, 96, 96, 96, 7, 6, 12, 48, 97, 97, 97, 97, 97, 97, 97, 97, 64, 29, 34, 50, 98, 50, 94, 18, 92], [81, 35, 96, 84, 11, 87, 72, 42, 27, 64, 98, 0, 18, 45, 36, 34, 21, 56, 40, 63, 89, 12, 31, 81, 40, 26, 40, 68, 56, 72, 87, 95, 13, 80, 3, 45, 4, 53, 70, 23, 77, 14, 66, 31, 47, 52, 45, 78, 84, 44, 42, 84, 22, 3, 20, 3, 59, 33, 8, 0, 1, 61, 9, 8, 21, 75, 13, 21, 22, 87, 44, 88, 29, 16, 39, 39, 39, 48, 41, 43, 70, 45, 68, 88, 44, 53, 54, 59, 37, 54, 87, 83, 57, 56, 81, 86, 69, 68, 86, 15], [1, 91, 10, 72, 71, 72, 29, 22, 18, 93, 18, 51, 63, 8, 19, 2, 8, 67, 61, 5, 18, 55, 62, 43, 97, 23, 16, 81, 68, 24, 91, 70, 89, 65, 88, 39, 23, 4, 73, 75, 86, 0, 96, 98, 31, 13, 83, 58, 20, 21, 80, 3, 61, 7, 35, 34, 48, 71, 51, 2, 90, 64, 0, 78, 19, 4, 5, 27, 14, 24, 15, 16, 83, 96, 62, 22, 22, 71, 85, 91, 80, 64, 32, 33, 33, 7, 35, 1, 26, 39, 39, 93, 58, 76, 25, 41, 41, 43, 43, 45], [67, 24, 59, 7, 33, 54, 42, 94, 44, 13, 51, 28, 80, 0, 0, 89, 20, 58, 40, 13, 33, 14, 30, 17, 33, 79, 24, 95, 60, 21, 23, 40, 43, 45, 46, 3, 50, 60, 97, 66, 55, 79, 94, 56, 59, 45, 11, 73, 66, 69, 69, 69, 19, 72, 72, 74, 25, 78, 78, 52, 79, 79, 42, 37, 77, 83, 56, 20, 85, 2, 20, 99, 20, 90, 90, 90, 72, 80, 95, 87, 95, 95, 45, 43, 88, 84, 97, 97, 97, 97, 97, 97, 97, 6, 30, 44, 6, 4, 99, 58], [21, 58, 66, 37, 74, 86, 40, 70, 67, 60, 10, 24, 94, 33, 98, 62, 56, 43, 92, 56, 89, 79, 44, 84, 16, 12, 75, 21, 85, 99, 9, 47, 23, 65, 47, 80, 0, 20, 56, 21, 64, 49, 20, 76, 18, 88, 98, 49, 12, 67, 50, 75, 17, 86, 0, 60, 44, 34, 98, 67, 42, 49, 35, 89, 47, 62, 33, 56, 60, 71, 62, 84, 58, 22, 50, 19, 45, 80, 8, 54, 79, 99, 16, 45, 78, 65, 4, 6, 23, 86, 7, 12, 14, 30, 42, 34, 82, 22, 25, 80], [77, 92, 51, 45, 42, 60, 69, 50, 52, 21, 25, 60, 90, 18, 16, 63, 49, 99, 19, 61, 26, 4, 64, 0, 38, 11, 31, 0, 53, 2, 94, 30, 32, 37, 58, 50, 86, 86, 52, 64, 44, 64, 94, 42, 65, 6, 77, 18, 95, 35, 59, 10, 63, 20, 22, 6, 91, 38, 73, 47, 75, 6, 69, 47, 6, 68, 94, 17, 92, 8, 0, 47, 4, 4, 5, 7, 11, 14, 27, 16, 26, 70, 23, 17, 27, 32, 88, 75, 58, 35, 38, 41, 6, 43, 54, 33, 51, 70, 27, 55], [54, 14, 21, 31, 72, 63, 21, 67, 77, 16, 61, 37, 26, 84, 39, 70, 73, 64, 9, 51, 25, 35, 36, 23, 18, 68, 1, 64, 44, 11, 41, 59, 11, 13, 65, 44, 37, 99, 97, 42, 73, 40, 13, 90, 89, 18, 50, 99, 1, 65, 48, 55, 80, 63, 81, 80, 63, 56, 99, 61, 56, 11, 99, 78, 84, 16, 86, 12, 67, 24, 52, 89, 4, 29, 99, 42, 8, 48, 99, 50, 50, 41, 10, 18, 23, 62, 98, 3, 60, 17, 8, 89, 93, 32, 0, 2, 5, 9, 25, 26], [67, 4, 79, 14, 97, 50, 76, 88, 21, 37, 24, 0, 37, 13, 57, 65, 51, 1, 38, 88, 6, 12, 11, 35, 59, 6, 29, 62, 32, 41, 68, 91, 42, 31, 22, 19, 62, 70, 33, 44, 32, 35, 50, 70, 11, 87, 89, 99, 59, 24, 40, 1, 4, 5, 5, 17, 7, 7, 8, 87, 21, 90, 92, 60, 91, 32, 32, 32, 35, 10, 39, 87, 68, 45, 45, 46, 94, 88, 4, 77, 54, 89, 57, 57, 57, 32, 14, 34, 31, 78, 48, 42, 71, 72, 74, 74, 74, 74, 74, 75], [70, 15, 99, 0, 17, 39, 7, 78, 65, 50, 80, 42, 13, 56, 28, 58, 30, 94, 6, 74, 83, 87, 45, 26, 21, 51, 7, 82, 75, 8, 86, 44, 23, 20, 67, 84, 98, 49, 72, 36, 37, 26, 78, 58, 30, 56, 53, 2, 4, 4, 58, 6, 9, 55, 94, 7, 36, 18, 82, 27, 65, 87, 29, 92, 32, 35, 39, 39, 30, 83, 65, 65, 45, 46, 12, 47, 87, 52, 59, 54, 54, 55, 11, 29, 20, 57, 2, 95, 68, 34, 31, 66, 66, 98, 58, 69, 69, 53, 18, 73], [84, 3, 98, 63, 20, 15, 61, 21, 85, 59, 14, 52, 13, 15, 81, 48, 64, 93, 58, 50, 33, 19, 99, 7, 23, 7, 85, 59, 25, 65, 91, 50, 77, 70, 37, 19, 92, 38, 43, 33, 92, 73, 49, 89, 4, 89, 76, 93, 84, 99, 23, 16, 17, 31, 3, 62, 39, 22, 65, 17, 96, 28, 95, 88, 35, 38, 17, 12, 61, 43, 7, 46, 28, 51, 12, 52, 54, 28, 55, 56, 60, 35, 47, 28, 2, 19, 68, 69, 69, 28, 24, 65, 41, 76, 76, 78, 79, 6, 81, 22], [84, 95, 44, 81, 44, 27, 80, 32, 38, 64, 94, 37, 88, 14, 85, 9, 9, 83, 11, 12, 64, 39, 14, 27, 15, 13, 19, 51, 23, 40, 59, 59, 36, 54, 40, 43, 43, 76, 45, 99, 46, 31, 91, 52, 53, 53, 19, 93, 30, 80, 55, 55, 31, 27, 57, 11, 89, 93, 91, 36, 83, 57, 68, 6, 98, 71, 42, 30, 82, 82, 84, 85, 85, 89, 58, 87, 90, 90, 98, 98, 68, 16, 14, 25, 95, 96, 23, 43, 38, 21, 97, 97, 97, 97, 97, 97, 97, 96, 88, 36], [66, 58, 44, 86, 59, 48, 54, 58, 3, 64, 65, 91, 14, 38, 18, 15, 95, 69, 48, 66, 23, 27, 73, 74, 22, 84, 86, 59, 83, 23, 23, 8, 4, 74, 95, 77, 34, 60, 86, 0, 10, 22, 5, 5, 69, 9, 10, 23, 86, 15, 88, 19, 22, 72, 92, 81, 63, 20, 95, 39, 35, 36, 39, 40, 67, 72, 52, 54, 54, 55, 95, 57, 15, 60, 60, 51, 58, 73, 44, 65, 48, 40, 39, 68, 27, 41, 72, 7, 51, 63, 91, 37, 67, 78, 78, 80, 81, 82, 36, 73], [13, 12, 24, 67, 84, 0, 7, 47, 11, 17, 5, 64, 70, 89, 81, 13, 98, 46, 32, 34, 23, 92, 49, 65, 33, 31, 99, 11, 14, 68, 16, 16, 20, 20, 19, 21, 77, 79, 83, 78, 98, 31, 84, 32, 45, 97, 7, 47, 66, 28, 69, 53, 51, 51, 52, 52, 53, 21, 33, 59, 57, 57, 48, 33, 86, 47, 62, 17, 95, 48, 64, 53, 49, 77, 79, 81, 81, 82, 20, 31, 61, 84, 74, 87, 12, 6, 90, 90, 90, 90, 28, 40, 64, 64, 34, 95, 86, 95, 96, 96], [60, 35, 75, 63, 54, 95, 6, 99, 7, 50, 14, 31, 84, 29, 41, 62, 44, 70, 1, 4, 49, 5, 5, 8, 9, 40, 89, 61, 6, 11, 5, 22, 86, 95, 8, 3, 58, 32, 32, 33, 6, 40, 43, 60, 62, 67, 52, 54, 54, 13, 56, 30, 31, 57, 96, 88, 52, 42, 10, 19, 6, 1, 13, 86, 44, 24, 42, 69, 69, 3, 3, 26, 96, 74, 27, 76, 77, 78, 79, 25, 31, 35, 5, 91, 70, 78, 85, 7, 87, 87, 87, 87, 90, 85, 89, 88, 47, 95, 22, 96], [82, 71, 38, 77, 61, 6, 29, 13, 10, 82, 48, 29, 5, 5, 5, 9, 63, 30, 17, 15, 15, 68, 91, 88, 22, 10, 96, 13, 35, 35, 35, 36, 25, 0, 41, 41, 80, 45, 45, 45, 21, 46, 2, 68, 47, 72, 28, 54, 55, 86, 28, 59, 72, 29, 63, 48, 7, 77, 33, 49, 71, 33, 72, 72, 74, 97, 76, 77, 77, 98, 78, 79, 80, 65, 64, 82, 82, 73, 92, 84, 26, 7, 85, 85, 85, 42, 5, 14, 90, 90, 90, 83, 44, 99, 95, 42, 1, 38, 20, 31], [77, 5, 32, 77, 26, 15, 47, 89, 50, 12, 93, 97, 1, 98, 37, 87, 42, 92, 55, 65, 14, 15, 61, 34, 70, 11, 19, 79, 24, 27, 76, 22, 92, 32, 33, 33, 35, 35, 94, 95, 76, 25, 29, 31, 46, 46, 51, 51, 52, 53, 34, 45, 55, 57, 60, 54, 91, 66, 53, 68, 62, 69, 15, 72, 74, 92, 76, 76, 76, 71, 22, 78, 79, 79, 79, 83, 94, 18, 81, 91, 80, 85, 59, 36, 32, 11, 3, 90, 83, 51, 31, 46, 49, 96, 96, 96, 80, 34, 79, 97], [27, 61, 64, 17, 6, 3, 27, 88, 97, 77, 8, 98, 15, 5, 12, 68, 22, 75, 3, 87, 63, 40, 3, 19, 4, 31, 77, 57, 13, 93, 22, 57, 76, 34, 23, 76, 83, 84, 73, 44, 84, 13, 81, 91, 38, 18, 92, 1, 7, 39, 21, 27, 88, 14, 57, 26, 84, 93, 35, 56, 37, 22, 83, 84, 21, 25, 33, 62, 7, 98, 6, 23, 46, 32, 30, 19, 43, 36, 98, 34, 42, 97, 80, 15, 44, 84, 98, 73, 20, 4, 5, 93, 9, 36, 33, 97, 98, 92, 16, 80], [6, 84, 3, 60, 23, 34, 34, 17, 9, 89, 23, 81, 39, 79, 93, 81, 56, 37, 55, 57, 15, 86, 71, 31, 70, 40, 45, 55, 70, 17, 96, 42, 7, 86, 85, 34, 15, 69, 12, 79, 38, 58, 87, 42, 58, 65, 87, 20, 81, 86, 26, 59, 18, 1, 2, 2, 92, 7, 7, 9, 12, 48, 14, 14, 15, 16, 16, 11, 17, 7, 70, 76, 50, 0, 30, 45, 41, 18, 43, 80, 45, 80, 1, 61, 51, 52, 76, 54, 54, 60, 65, 80, 2, 33, 33, 66, 92, 89, 80, 71], [49, 24, 33, 63, 58, 21, 48, 30, 86, 47, 87, 94, 96, 73, 19, 86, 69, 98, 37, 11, 16, 24, 32, 24, 26, 37, 48, 75, 42, 74, 16, 1, 39, 45, 83, 28, 50, 22, 63, 55, 67, 16, 16, 64, 22, 56, 60, 65, 7, 27, 82, 19, 33, 29, 77, 3, 32, 2, 62, 21, 39, 25, 43, 13, 47, 8, 88, 70, 51, 53, 53, 15, 95, 24, 55, 62, 31, 7, 58, 10, 60, 26, 85, 94, 60, 39, 99, 71, 71, 72, 92, 74, 74, 92, 46, 77, 65, 0, 38, 64], [77, 47, 47, 74, 33, 16, 18, 68, 68, 84, 23, 79, 36, 69, 56, 88, 45, 14, 79, 31, 56, 70, 94, 61, 0, 2, 31, 5, 7, 67, 99, 15, 15, 73, 17, 24, 21, 70, 66, 8, 37, 75, 85, 45, 73, 70, 39, 37, 43, 37, 21, 45, 46, 30, 85, 56, 36, 19, 9, 51, 44, 57, 17, 25, 60, 81, 73, 86, 63, 66, 41, 51, 68, 4, 22, 83, 64, 72, 72, 72, 72, 74, 74, 92, 76, 77, 32, 96, 78, 36, 79, 80, 56, 86, 30, 83, 18, 85, 39, 87], [79, 40, 67, 86, 93, 31, 28, 68, 48, 62, 38, 95, 67, 99, 67, 94, 73, 73, 45, 83, 37, 27, 47, 91, 22, 79, 57, 61, 27, 30, 48, 0, 77, 61, 2, 61, 9, 10, 14, 15, 15, 30, 59, 34, 68, 3, 50, 65, 89, 59, 30, 98, 89, 42, 3, 67, 23, 43, 43, 80, 46, 1, 54, 21, 11, 48, 95, 57, 44, 32, 2, 74, 66, 81, 68, 68, 68, 78, 37, 83, 85, 45, 27, 33, 49, 58, 76, 77, 79, 2, 18, 82, 25, 8, 42, 80, 84, 16, 74, 78], [46, 89, 11, 3, 93, 9, 30, 12, 43, 13, 89, 64, 77, 20, 78, 13, 1, 56, 39, 1, 63, 97, 53, 67, 20, 76, 12, 2, 96, 93, 99, 67, 77, 64, 11, 86, 10, 84, 12, 24, 80, 33, 6, 44, 48, 6, 3, 67, 76, 82, 29, 86, 59, 31, 91, 65, 76, 87, 90, 0, 58, 58, 38, 28, 68, 2, 87, 92, 75, 73, 47, 8, 96, 42, 92, 16, 6, 32, 18, 22, 22, 22, 6, 4, 47, 55, 44, 66, 32, 35, 99, 39, 41, 41, 43, 45, 91, 46, 16, 46], [93, 54, 35, 57, 80, 41, 19, 16, 84, 91, 40, 41, 60, 10, 64, 93, 78, 59, 13, 33, 68, 49, 88, 8, 82, 80, 94, 64, 29, 26, 70, 18, 11, 75, 75, 7, 44, 59, 89, 32, 70, 1, 31, 94, 23, 75, 84, 61, 10, 52, 26, 13, 34, 48, 36, 44, 6, 4, 8, 63, 34, 36, 18, 15, 10, 42, 63, 12, 8, 21, 77, 43, 7, 52, 12, 48, 39, 62, 43, 43, 89, 46, 46, 26, 93, 51, 51, 21, 53, 54, 31, 61, 56, 57, 59, 55, 25, 60, 65, 22], [58, 64, 85, 32, 27, 91, 33, 51, 86, 53, 6, 68, 12, 41, 29, 5, 5, 9, 20, 72, 83, 26, 17, 77, 91, 49, 36, 97, 58, 46, 47, 47, 4, 51, 53, 53, 18, 54, 54, 36, 55, 56, 57, 71, 63, 15, 62, 11, 1, 54, 76, 94, 69, 66, 71, 71, 91, 72, 74, 74, 75, 76, 76, 77, 77, 77, 78, 79, 80, 91, 77, 43, 81, 82, 3, 83, 18, 87, 58, 23, 0, 63, 87, 29, 30, 48, 90, 90, 90, 90, 90, 85, 17, 34, 17, 24, 62, 31, 95, 40], [39, 96, 80, 22, 96, 90, 22, 19, 72, 52, 27, 31, 86, 56, 73, 37, 72, 13, 75, 29, 71, 39, 1, 68, 37, 56, 52, 8, 70, 86, 83, 20, 73, 81, 71, 56, 49, 20, 34, 6, 12, 96, 81, 46, 87, 40, 85, 52, 65, 72, 83, 52, 9, 58, 6, 51, 58, 53, 66, 70, 7, 76, 15, 92, 55, 40, 80, 15, 17, 13, 34, 28, 53, 1, 81, 45, 15, 74, 28, 16, 6, 87, 95, 35, 20, 61, 40, 88, 43, 43, 42, 46, 51, 51, 52, 50, 53, 44, 54, 82], [8, 86, 17, 93, 10, 15, 76, 14, 53, 58, 38, 12, 67, 69, 20, 13, 92, 64, 60, 24, 79, 73, 28, 92, 77, 65, 89, 62, 53, 42, 71, 44, 29, 37, 80, 75, 60, 59, 25, 57, 92, 77, 66, 65, 17, 65, 6, 65, 19, 95, 83, 64, 28, 61, 0, 51, 55, 25, 70, 2, 92, 98, 88, 73, 6, 15, 37, 77, 56, 99, 18, 7, 74, 90, 41, 71, 99, 23, 91, 37, 24, 32, 75, 89, 10, 24, 91, 25, 50, 18, 14, 52, 5, 64, 8, 18, 29, 16, 17, 17], [88, 17, 24, 28, 25, 34, 62, 0, 4, 75, 38, 9, 9, 31, 18, 38, 97, 32, 87, 95, 88, 19, 35, 25, 93, 61, 14, 31, 51, 91, 36, 33, 46, 37, 73, 35, 49, 41, 51, 51, 49, 52, 52, 53, 98, 3, 54, 55, 57, 22, 90, 25, 2, 8, 66, 73, 92, 58, 59, 89, 8, 1, 88, 72, 54, 61, 76, 76, 76, 77, 78, 79, 79, 30, 47, 13, 96, 82, 82, 83, 84, 66, 34, 3, 55, 85, 85, 85, 85, 3, 94, 87, 95, 42, 61, 90, 90, 90, 33, 32], [80, 75, 79, 39, 22, 31, 46, 46, 27, 40, 49, 28, 22, 80, 36, 22, 49, 2, 95, 49, 35, 80, 23, 64, 75, 83, 37, 54, 33, 6, 76, 24, 36, 91, 29, 59, 66, 3, 26, 48, 46, 62, 86, 29, 26, 99, 14, 27, 65, 17, 45, 24, 86, 13, 26, 9, 63, 58, 55, 25, 29, 48, 4, 98, 11, 2, 2, 34, 13, 13, 50, 7, 9, 37, 18, 25, 46, 71, 51, 5, 19, 19, 71, 20, 59, 44, 35, 35, 35, 86, 11, 32, 40, 44, 43, 89, 56, 45, 46, 46], [41, 96, 20, 9, 93, 96, 18, 22, 48, 73, 46, 32, 44, 80, 14, 64, 30, 15, 84, 80, 4, 27, 35, 44, 18, 26, 0, 47, 39, 53, 73, 47, 45, 81, 44, 80, 1, 7, 36, 33, 52, 14, 98, 17, 17, 21, 11, 38, 92, 60, 98, 29, 29, 29, 54, 32, 35, 39, 67, 41, 41, 41, 8, 47, 45, 39, 3, 46, 92, 35, 52, 59, 55, 81, 91, 57, 72, 91, 82, 33, 62, 50, 66, 39, 32, 4, 68, 69, 93, 71, 9, 85, 75, 75, 29, 38, 76, 79, 80, 81], [32, 97, 93, 54, 52, 52, 76, 1, 71, 5, 26, 61, 15, 22, 41, 13, 36, 49, 5, 28, 39, 81, 71, 24, 29, 89, 1, 26, 60, 29, 63, 79, 49, 7, 10, 27, 90, 6, 40, 23, 94, 20, 78, 15, 49, 38, 64, 39, 89, 66, 86, 25, 53, 12, 24, 2, 5, 94, 14, 84, 19, 21, 21, 22, 92, 38, 37, 49, 40, 88, 19, 27, 33, 29, 58, 29, 68, 23, 43, 43, 45, 45, 46, 73, 7, 29, 93, 51, 52, 53, 53, 20, 54, 54, 55, 57, 57, 75, 60, 29], [18, 70, 9, 89, 70, 31, 13, 8, 1, 92, 91, 59, 19, 91, 79, 11, 24, 61, 66, 17, 71, 75, 72, 13, 42, 54, 8, 60, 67, 60, 25, 87, 92, 83, 11, 56, 40, 73, 63, 95, 44, 20, 81, 11, 5, 63, 31, 4, 75, 18, 59, 81, 21, 88, 64, 3, 33, 82, 27, 53, 8, 21, 23, 59, 90, 37, 79, 21, 21, 22, 83, 27, 50, 4, 66, 23, 63, 24, 39, 32, 33, 20, 35, 36, 36, 39, 39, 41, 67, 43, 43, 43, 36, 87, 46, 53, 63, 80, 1, 96], [84, 65, 25, 62, 12, 30, 87, 29, 62, 65, 30, 28, 86, 54, 95, 56, 97, 84, 47, 41, 56, 36, 94, 98, 75, 8, 98, 98, 58, 6, 29, 89, 85, 94, 7, 89, 42, 15, 0, 4, 4, 5, 9, 9, 68, 9, 10, 23, 77, 12, 36, 9, 71, 88, 36, 13, 40, 40, 34, 43, 46, 46, 47, 47, 54, 29, 8, 56, 57, 24, 98, 48, 61, 27, 63, 91, 68, 68, 71, 71, 74, 75, 76, 77, 77, 70, 82, 82, 10, 83, 6, 87, 85, 85, 85, 50, 87, 87, 14, 88], [69, 10, 18, 24, 16, 27, 34, 81, 19, 75, 87, 26, 46, 12, 98, 29, 75, 38, 85, 76, 84, 7, 7, 25, 87, 64, 84, 13, 96, 64, 61, 31, 18, 17, 63, 39, 89, 7, 73, 25, 35, 71, 15, 57, 45, 15, 40, 63, 10, 27, 95, 40, 86, 19, 93, 92, 70, 92, 95, 43, 92, 22, 79, 27, 73, 12, 24, 42, 55, 1, 2, 4, 4, 47, 54, 11, 62, 84, 21, 15, 19, 22, 41, 73, 48, 18, 9, 35, 86, 27, 6, 28, 41, 43, 66, 41, 21, 83, 12, 54], [24, 60, 1, 81, 40, 83, 91, 80, 54, 15, 38, 23, 68, 82, 14, 5, 23, 22, 64, 66, 10, 76, 60, 8, 19, 68, 67, 3, 53, 15, 72, 88, 77, 40, 7, 90, 32, 60, 38, 3, 29, 77, 37, 24, 67, 58, 48, 36, 44, 21, 30, 0, 16, 22, 6, 40, 50, 71, 45, 34, 96, 23, 2, 15, 93, 15, 2, 81, 85, 93, 18, 34, 5, 73, 75, 1, 42, 93, 5, 88, 83, 1, 48, 59, 92, 28, 1, 25, 27, 46, 83, 0, 0, 30, 1, 4, 40, 5, 57, 68], [98, 88, 11, 24, 30, 87, 1, 1, 0, 4, 73, 30, 20, 91, 87, 16, 45, 64, 6, 22, 50, 97, 36, 22, 28, 5, 19, 46, 95, 53, 26, 55, 55, 56, 60, 41, 1, 24, 52, 66, 68, 71, 72, 74, 33, 78, 79, 76, 48, 65, 21, 90, 22, 74, 29, 92, 83, 61, 73, 13, 16, 96, 96, 96, 96, 96, 97, 3, 21, 35, 3, 97, 97, 97, 97, 67, 49, 73, 3, 38, 87, 50, 24, 95, 44, 25, 24, 18, 91, 2, 46, 77, 6, 7, 30, 2, 14, 11, 38, 6], [9, 52, 42, 32, 11, 63, 54, 3, 5, 60, 1, 19, 71, 29, 18, 77, 35, 15, 55, 80, 47, 34, 17, 30, 97, 48, 52, 67, 49, 95, 86, 92, 12, 23, 99, 95, 73, 99, 79, 39, 82, 42, 92, 96, 83, 88, 65, 75, 62, 63, 58, 71, 22, 48, 20, 94, 16, 21, 34, 94, 81, 5, 44, 68, 0, 76, 37, 5, 53, 37, 59, 9, 98, 21, 29, 12, 16, 17, 10, 97, 22, 43, 12, 27, 18, 39, 39, 39, 40, 40, 43, 72, 49, 46, 28, 39, 65, 49, 51, 53], [60, 50, 71, 92, 48, 63, 78, 51, 5, 62, 57, 43, 75, 94, 10, 37, 55, 27, 49, 49, 6, 77, 50, 64, 21, 24, 25, 37, 88, 66, 12, 23, 23, 10, 25, 38, 64, 88, 18, 85, 31, 7, 0, 36, 51, 20, 64, 36, 15, 12, 36, 37, 89, 34, 57, 36, 61, 77, 84, 71, 1, 4, 98, 5, 7, 8, 1, 75, 94, 42, 16, 17, 37, 22, 3, 65, 99, 99, 35, 36, 41, 18, 43, 2, 42, 8, 49, 51, 51, 60, 59, 60, 38, 79, 20, 50, 98, 71, 29, 95], [25, 50, 81, 19, 43, 0, 86, 71, 17, 65, 19, 53, 61, 22, 43, 6, 12, 17, 57, 18, 47, 49, 76, 39, 79, 28, 7, 23, 61, 95, 48, 22, 61, 33, 30, 47, 89, 17, 47, 94, 19, 65, 30, 9, 29, 62, 38, 89, 34, 63, 84, 85, 31, 81, 38, 42, 98, 63, 66, 84, 98, 98, 42, 8, 99, 98, 47, 53, 22, 74, 61, 68, 36, 8, 65, 8, 12, 13, 23, 49, 78, 63, 43, 4, 30, 33, 6, 88, 66, 99, 51, 8, 36, 10, 17, 83, 0, 7, 8, 9], [64, 30, 52, 96, 0, 19, 71, 45, 51, 49, 32, 21, 70, 70, 13, 39, 61, 60, 27, 12, 26, 76, 8, 42, 23, 31, 26, 11, 67, 89, 26, 24, 47, 30, 69, 9, 50, 62, 67, 58, 12, 2, 50, 61, 88, 98, 8, 75, 92, 62, 25, 73, 0, 0, 0, 28, 5, 42, 7, 64, 11, 14, 15, 15, 21, 16, 81, 17, 6, 42, 53, 71, 65, 90, 23, 63, 40, 5, 4, 37, 47, 52, 56, 59, 16, 59, 32, 60, 47, 21, 87, 66, 66, 68, 72, 89, 76, 78, 78, 78], [63, 62, 65, 91, 41, 35, 6, 34, 60, 32, 26, 24, 0, 29, 12, 32, 1, 4, 47, 9, 2, 99, 90, 49, 21, 10, 56, 42, 28, 99, 16, 84, 40, 41, 7, 45, 45, 46, 4, 51, 51, 52, 96, 20, 28, 10, 2, 61, 57, 95, 48, 88, 5, 58, 89, 17, 81, 71, 80, 72, 88, 14, 13, 76, 77, 77, 70, 78, 78, 79, 79, 79, 40, 81, 64, 82, 82, 82, 83, 88, 65, 91, 17, 59, 58, 26, 68, 87, 64, 44, 11, 69, 58, 90, 90, 81, 49, 99, 31, 12], [58, 99, 13, 56, 95, 85, 23, 27, 96, 60, 3, 48, 94, 10, 85, 78, 67, 27, 93, 3, 62, 92, 28, 31, 93, 66, 42, 35, 29, 79, 85, 74, 96, 71, 66, 50, 23, 11, 6, 73, 63, 9, 55, 76, 48, 12, 15, 88, 55, 22, 22, 89, 40, 38, 25, 80, 35, 36, 10, 7, 41, 2, 97, 45, 47, 69, 79, 53, 54, 10, 36, 57, 56, 56, 57, 87, 31, 66, 2, 74, 46, 89, 78, 78, 21, 37, 39, 35, 81, 82, 82, 18, 85, 33, 69, 89, 53, 27, 93, 87], [52, 5, 27, 14, 82, 20, 33, 74, 6, 82, 15, 34, 34, 80, 34, 22, 54, 93, 68, 62, 92, 65, 74, 20, 3, 77, 83, 38, 9, 19, 78, 30, 49, 44, 66, 33, 75, 73, 56, 12, 21, 20, 92, 33, 35, 29, 22, 37, 89, 48, 83, 25, 26, 95, 47, 54, 16, 76, 26, 22, 49, 21, 80, 37, 63, 65, 53, 94, 61, 18, 35, 61, 37, 94, 47, 85, 44, 12, 81, 19, 86, 67, 39, 13, 1, 5, 5, 5, 15, 9, 9, 16, 15, 7, 16, 80, 37, 28, 27, 89], [13, 26, 67, 80, 56, 7, 37, 88, 63, 93, 18, 99, 36, 94, 4, 30, 86, 56, 84, 7, 34, 10, 59, 9, 76, 59, 8, 88, 10, 69, 36, 37, 30, 30, 58, 8, 24, 97, 80, 68, 63, 80, 34, 52, 22, 46, 70, 8, 12, 81, 85, 88, 89, 92, 87, 25, 18, 25, 69, 5, 38, 42, 41, 34, 84, 91, 39, 60, 9, 4, 67, 5, 48, 7, 91, 87, 14, 20, 16, 21, 2, 22, 44, 94, 23, 89, 70, 57, 80, 32, 33, 36, 39, 39, 10, 63, 41, 32, 95, 90], [62, 5, 92, 12, 94, 25, 50, 73, 91, 0, 20, 24, 72, 74, 49, 58, 80, 78, 75, 75, 25, 76, 20, 84, 56, 0, 2, 4, 60, 60, 83, 17, 36, 53, 89, 31, 77, 71, 73, 27, 30, 29, 33, 84, 42, 94, 40, 41, 93, 43, 45, 12, 6, 25, 51, 51, 23, 54, 55, 39, 79, 60, 60, 6, 20, 81, 94, 86, 67, 66, 38, 34, 8, 10, 83, 69, 69, 61, 99, 72, 74, 74, 58, 68, 75, 75, 77, 26, 78, 78, 30, 82, 72, 89, 84, 49, 18, 89, 87, 87], [70, 88, 53, 66, 73, 32, 25, 38, 28, 35, 63, 32, 98, 47, 65, 1, 67, 37, 42, 48, 8, 40, 91, 1, 48, 23, 36, 98, 40, 17, 16, 92, 0, 0, 0, 83, 9, 1, 34, 14, 50, 88, 14, 71, 53, 19, 22, 80, 19, 79, 39, 41, 28, 32, 49, 53, 88, 17, 47, 28, 89, 69, 54, 54, 40, 55, 55, 59, 60, 58, 7, 44, 20, 18, 9, 34, 20, 68, 69, 69, 69, 30, 42, 71, 71, 72, 72, 50, 85, 70, 57, 12, 81, 68, 70, 85, 74, 87, 90, 90], [25, 48, 13, 12, 11, 44, 80, 7, 66, 33, 99, 20, 10, 99, 63, 28, 32, 51, 94, 77, 54, 80, 98, 30, 54, 94, 96, 50, 15, 36, 17, 39, 63, 92, 26, 4, 98, 61, 95, 10, 27, 28, 1, 1, 44, 9, 70, 77, 58, 3, 16, 3, 19, 48, 9, 24, 75, 30, 19, 32, 33, 35, 35, 74, 36, 52, 39, 40, 40, 88, 43, 43, 29, 46, 46, 93, 25, 7, 51, 53, 88, 59, 3, 17, 2, 47, 31, 63, 68, 11, 69, 13, 60, 68, 74, 74, 74, 74, 60, 93], [59, 8, 91, 23, 82, 5, 79, 51, 43, 57, 86, 9, 40, 96, 76, 72, 1, 42, 47, 21, 77, 71, 37, 17, 52, 66, 48, 36, 98, 66, 76, 18, 27, 79, 22, 64, 28, 47, 64, 93, 92, 13, 13, 15, 34, 81, 23, 11, 44, 91, 55, 22, 47, 6, 22, 20, 66, 10, 85, 61, 62, 47, 84, 67, 49, 83, 50, 25, 17, 26, 50, 21, 20, 70, 67, 42, 69, 77, 38, 97, 1, 26, 4, 87, 28, 87, 38, 63, 14, 25, 81, 78, 29, 35, 64, 69, 70, 40, 40, 41], [58, 15, 76, 74, 80, 38, 46, 66, 73, 43, 64, 68, 64, 2, 17, 45, 17, 41, 1, 9, 26, 94, 67, 68, 70, 69, 21, 30, 25, 19, 3, 64, 63, 73, 25, 49, 33, 12, 18, 60, 32, 15, 4, 69, 16, 84, 70, 19, 87, 90, 9, 29, 67, 98, 79, 9, 94, 70, 20, 56, 66, 98, 12, 79, 89, 40, 72, 25, 86, 50, 88, 96, 16, 65, 44, 67, 26, 88, 95, 15, 81, 6, 89, 19, 94, 91, 60, 12, 3, 29, 21, 21, 12, 86, 80, 55, 71, 4, 87, 64], [19, 42, 83, 73, 81, 42, 86, 41, 0, 1, 16, 5, 9, 9, 1, 10, 48, 11, 11, 64, 25, 15, 41, 16, 38, 58, 63, 92, 67, 70, 78, 49, 86, 24, 32, 35, 88, 87, 47, 62, 73, 43, 46, 46, 46, 84, 60, 99, 31, 52, 28, 59, 68, 93, 62, 53, 84, 8, 15, 66, 68, 50, 69, 69, 6, 36, 72, 74, 67, 76, 78, 78, 80, 18, 31, 81, 81, 74, 82, 82, 87, 96, 96, 85, 85, 63, 92, 7, 90, 90, 90, 90, 39, 63, 32, 95, 95, 28, 96, 96], [65, 16, 34, 14, 34, 86, 98, 34, 93, 54, 75, 22, 30, 92, 18, 29, 39, 71, 9, 9, 30, 92, 30, 50, 88, 22, 73, 17, 28, 20, 2, 87, 26, 62, 13, 6, 84, 21, 69, 91, 39, 16, 16, 16, 7, 24, 74, 88, 34, 18, 71, 19, 32, 35, 79, 26, 56, 99, 45, 58, 52, 47, 47, 83, 36, 18, 94, 57, 63, 94, 60, 61, 76, 52, 63, 53, 13, 87, 36, 11, 69, 72, 74, 32, 2, 75, 75, 75, 23, 77, 18, 89, 78, 79, 79, 79, 79, 79, 81, 82], [52, 42, 88, 42, 8, 10, 82, 55, 43, 73, 32, 63, 99, 47, 82, 81, 30, 54, 20, 68, 19, 87, 54, 95, 64, 1, 66, 14, 91, 57, 10, 49, 1, 32, 14, 38, 5, 5, 9, 36, 5, 81, 61, 14, 75, 48, 45, 82, 16, 16, 19, 90, 19, 48, 95, 6, 1, 34, 35, 29, 46, 40, 76, 35, 84, 41, 43, 43, 18, 3, 87, 73, 55, 97, 52, 69, 53, 62, 54, 54, 55, 55, 24, 90, 70, 56, 18, 35, 98, 53, 88, 74, 99, 20, 76, 77, 78, 78, 78, 45], [38, 94, 10, 43, 70, 24, 11, 13, 30, 79, 43, 22, 11, 8, 16, 25, 26, 63, 70, 19, 96, 25, 12, 35, 21, 39, 59, 2, 33, 30, 69, 2, 70, 42, 30, 12, 92, 94, 94, 35, 94, 49, 49, 34, 88, 84, 6, 29, 95, 13, 64, 93, 42, 99, 72, 88, 1, 69, 67, 24, 16, 72, 50, 38, 93, 72, 38, 30, 45, 80, 19, 0, 45, 82, 86, 52, 91, 94, 88, 33, 94, 34, 56, 98, 1, 89, 64, 88, 16, 16, 65, 22, 99, 85, 88, 84, 68, 27, 58, 38], [78, 53, 24, 70, 13, 99, 25, 23, 27, 46, 26, 29, 23, 57, 47, 58, 39, 73, 24, 1, 61, 73, 62, 13, 47, 38, 98, 58, 37, 50, 0, 34, 65, 4, 5, 3, 62, 11, 14, 15, 87, 42, 73, 44, 22, 22, 96, 45, 70, 61, 31, 62, 39, 84, 40, 61, 43, 62, 45, 46, 88, 38, 51, 52, 53, 55, 63, 97, 59, 60, 59, 63, 28, 52, 48, 69, 66, 91, 44, 20, 71, 99, 98, 22, 74, 84, 88, 78, 79, 79, 82, 84, 64, 85, 85, 44, 88, 87, 87, 16], [91, 36, 23, 6, 63, 85, 3, 26, 75, 60, 27, 44, 33, 44, 31, 9, 89, 58, 56, 84, 2, 37, 55, 24, 1, 61, 85, 67, 49, 37, 84, 51, 15, 25, 18, 19, 44, 66, 51, 32, 38, 58, 73, 53, 86, 86, 5, 70, 11, 58, 33, 73, 2, 4, 72, 67, 82, 14, 15, 17, 34, 19, 13, 24, 8, 77, 27, 83, 69, 33, 35, 35, 48, 34, 39, 41, 43, 43, 45, 46, 46, 70, 47, 51, 53, 27, 60, 60, 14, 99, 83, 30, 32, 99, 68, 88, 71, 71, 74, 38], [50, 70, 94, 24, 23, 11, 38, 4, 60, 27, 10, 70, 16, 16, 61, 34, 46, 55, 44, 80, 65, 74, 44, 61, 40, 53, 82, 68, 1, 60, 96, 89, 23, 5, 88, 70, 0, 65, 72, 17, 15, 39, 72, 19, 13, 68, 40, 70, 28, 11, 38, 51, 41, 25, 77, 30, 95, 56, 93, 38, 37, 26, 48, 9, 75, 96, 38, 36, 75, 68, 93, 13, 73, 69, 82, 10, 86, 26, 52, 34, 0, 76, 2, 11, 5, 74, 9, 64, 82, 14, 28, 38, 2, 8, 95, 29, 32, 32, 53, 8], [67, 57, 61, 67, 95, 77, 20, 51, 13, 36, 71, 18, 40, 97, 59, 13, 59, 36, 17, 8, 4, 62, 97, 10, 98, 17, 0, 0, 1, 4, 4, 5, 5, 83, 17, 26, 11, 87, 19, 98, 8, 21, 9, 19, 24, 22, 38, 9, 33, 33, 35, 85, 78, 43, 43, 46, 61, 86, 46, 86, 42, 3, 30, 98, 53, 3, 57, 57, 58, 59, 59, 59, 46, 73, 6, 56, 50, 16, 93, 71, 21, 72, 49, 14, 76, 78, 79, 79, 26, 76, 96, 91, 62, 32, 85, 75, 53, 90, 90, 88], [21, 81, 45, 93, 6, 41, 24, 49, 30, 1, 64, 73, 62, 34, 73, 52, 44, 11, 2, 49, 2, 18, 23, 93, 77, 7, 29, 33, 76, 73, 44, 18, 49, 10, 71, 97, 14, 78, 27, 81, 26, 85, 21, 30, 45, 9, 61, 64, 51, 58, 56, 87, 73, 31, 86, 20, 83, 44, 84, 38, 48, 98, 72, 83, 59, 78, 26, 87, 82, 3, 94, 25, 86, 10, 85, 83, 3, 95, 45, 26, 61, 31, 62, 0, 0, 42, 1, 99, 9, 9, 62, 83, 30, 42, 98, 25, 5, 13, 36, 28], [5, 11, 24, 59, 67, 23, 16, 42, 60, 32, 84, 28, 67, 99, 96, 3, 50, 91, 19, 76, 72, 64, 95, 48, 2, 79, 31, 30, 88, 96, 67, 10, 31, 76, 36, 89, 54, 37, 64, 20, 78, 73, 44, 86, 79, 20, 38, 19, 71, 11, 36, 48, 48, 91, 24, 10, 0, 1, 1, 2, 4, 5, 98, 9, 2, 65, 27, 96, 19, 22, 29, 71, 55, 98, 9, 43, 46, 21, 64, 73, 47, 8, 8, 52, 52, 53, 55, 26, 92, 76, 56, 5, 69, 69, 48, 50, 72, 72, 74, 3], [23, 94, 7, 62, 91, 6, 42, 4, 99, 93, 21, 48, 66, 28, 29, 6, 85, 85, 85, 96, 17, 78, 39, 75, 30, 59, 27, 94, 91, 91, 82, 92, 27, 13, 0, 86, 7, 86, 85, 83, 16, 14, 44, 22, 10, 22, 76, 29, 83, 30, 1, 29, 42, 44, 76, 41, 43, 66, 42, 12, 52, 10, 59, 7, 10, 94, 29, 34, 23, 20, 63, 25, 54, 73, 69, 72, 74, 61, 80, 81, 81, 58, 78, 24, 50, 84, 84, 30, 17, 85, 92, 55, 90, 90, 23, 55, 17, 49, 3, 62], [69, 52, 91, 47, 60, 73, 21, 71, 86, 27, 11, 34, 11, 48, 92, 11, 9, 87, 17, 44, 54, 37, 65, 12, 93, 13, 39, 89, 47, 86, 18, 8, 18, 61, 90, 83, 59, 21, 60, 28, 12, 23, 42, 55, 99, 23, 31, 28, 8, 69, 56, 28, 11, 29, 10, 25, 4, 8, 92, 74, 28, 16, 6, 12, 23, 45, 91, 89, 71, 37, 58, 91, 3, 26, 66, 75, 48, 97, 93, 37, 28, 49, 62, 0, 88, 1, 2, 4, 93, 67, 71, 97, 36, 11, 98, 14, 15, 16, 93, 58], [50, 21, 39, 93, 67, 66, 92, 64, 1, 18, 62, 37, 10, 0, 14, 62, 48, 92, 92, 14, 71, 7, 86, 70, 17, 15, 8, 56, 62, 10, 44, 29, 60, 28, 96, 50, 48, 2, 12, 53, 76, 41, 67, 99, 93, 44, 31, 84, 84, 35, 17, 73, 31, 47, 65, 15, 2, 96, 28, 93, 97, 12, 55, 2, 60, 66, 98, 23, 69, 34, 3, 65, 81, 57, 92, 63, 37, 39, 32, 25, 41, 0, 69, 1, 1, 5, 96, 23, 1, 8, 73, 61, 70, 8, 94, 16, 22, 15, 34, 64], [37, 25, 78, 50, 50, 67, 67, 56, 13, 27, 22, 99, 66, 32, 4, 57, 81, 65, 0, 0, 61, 4, 5, 63, 9, 63, 30, 80, 14, 30, 21, 27, 40, 72, 65, 27, 27, 5, 79, 29, 31, 33, 7, 67, 48, 39, 41, 95, 46, 40, 40, 44, 94, 51, 53, 54, 54, 63, 55, 45, 44, 69, 48, 61, 66, 66, 99, 77, 71, 72, 74, 74, 91, 93, 14, 78, 78, 79, 79, 79, 80, 13, 81, 81, 81, 11, 32, 22, 29, 84, 85, 13, 24, 72, 88, 90, 90, 90, 90, 73], [64, 51, 23, 65, 3, 56, 73, 32, 55, 99, 23, 41, 66, 93, 71, 61, 61, 37, 48, 45, 70, 95, 35, 78, 99, 8, 17, 63, 12, 86, 44, 68, 13, 94, 24, 49, 25, 64, 10, 41, 6, 5, 46, 62, 14, 78, 12, 56, 66, 95, 94, 37, 8, 65, 0, 0, 0, 4, 4, 4, 72, 70, 69, 34, 69, 99, 7, 62, 15, 66, 19, 19, 14, 6, 75, 72, 48, 39, 91, 41, 90, 46, 46, 10, 51, 51, 45, 53, 55, 49, 56, 57, 47, 60, 82, 8, 44, 63, 4, 99], [31, 2, 37, 94, 95, 94, 83, 67, 17, 53, 79, 2, 66, 31, 98, 60, 31, 30, 12, 99, 66, 81, 45, 70, 98, 95, 17, 40, 52, 63, 30, 81, 81, 90, 62, 10, 36, 83, 68, 68, 18, 73, 99, 50, 8, 93, 81, 52, 20, 88, 10, 18, 87, 94, 11, 93, 31, 62, 99, 41, 88, 18, 66, 82, 6, 75, 0, 83, 58, 55, 68, 83, 36, 48, 15, 43, 83, 2, 4, 58, 8, 24, 42, 50, 28, 64, 67, 65, 83, 32, 34, 67, 9, 29, 52, 50, 33, 35, 27, 31], [76, 73, 75, 42, 52, 6, 97, 59, 2, 50, 55, 97, 76, 30, 27, 25, 92, 48, 92, 20, 89, 80, 55, 37, 84, 16, 26, 31, 65, 2, 66, 65, 4, 5, 88, 50, 10, 42, 88, 41, 15, 99, 18, 32, 76, 99, 32, 55, 36, 13, 43, 80, 39, 39, 43, 43, 99, 95, 37, 47, 71, 94, 73, 39, 51, 51, 51, 29, 37, 28, 55, 56, 57, 8, 50, 92, 69, 75, 64, 71, 71, 15, 74, 74, 75, 76, 78, 63, 80, 80, 11, 3, 80, 17, 68, 85, 4, 73, 18, 12], [74, 78, 62, 17, 98, 55, 13, 67, 72, 83, 11, 79, 70, 1, 55, 46, 61, 2, 7, 13, 32, 32, 38, 9, 16, 14, 52, 18, 86, 3, 57, 62, 49, 90, 39, 94, 95, 30, 38, 94, 70, 10, 75, 91, 52, 11, 10, 95, 0, 76, 5, 55, 18, 88, 34, 14, 17, 67, 23, 27, 31, 29, 33, 39, 63, 88, 51, 51, 54, 68, 81, 57, 57, 2, 60, 65, 55, 63, 18, 69, 61, 81, 66, 66, 7, 63, 40, 3, 25, 33, 77, 78, 44, 42, 81, 82, 82, 82, 83, 64], [92, 82, 51, 2, 15, 10, 61, 29, 55, 70, 64, 26, 75, 65, 68, 84, 80, 26, 92, 80, 38, 0, 0, 88, 7, 82, 42, 91, 31, 45, 20, 61, 11, 22, 69, 99, 29, 33, 73, 46, 41, 96, 51, 52, 28, 56, 56, 93, 57, 58, 60, 3, 40, 63, 56, 82, 47, 42, 29, 77, 71, 71, 62, 72, 74, 40, 36, 75, 75, 98, 10, 20, 77, 78, 79, 67, 10, 82, 24, 89, 23, 47, 92, 90, 90, 72, 38, 19, 25, 12, 53, 95, 95, 38, 96, 50, 48, 80, 97, 97], [48, 70, 4, 48, 28, 6, 6, 28, 14, 59, 1, 54, 73, 5, 31, 48, 65, 78, 99, 68, 49, 18, 23, 34, 92, 22, 19, 42, 14, 69, 70, 31, 46, 67, 47, 25, 62, 31, 8, 59, 56, 47, 95, 2, 4, 4, 74, 92, 9, 9, 96, 13, 15, 16, 91, 56, 20, 71, 78, 19, 31, 47, 48, 82, 85, 35, 25, 3, 35, 55, 39, 41, 43, 59, 94, 8, 11, 20, 51, 51, 51, 52, 54, 57, 57, 57, 57, 60, 30, 23, 75, 2, 66, 28, 77, 68, 26, 46, 71, 74], [64, 85, 71, 53, 83, 16, 31, 29, 48, 14, 64, 37, 64, 67, 49, 25, 75, 33, 92, 40, 18, 60, 82, 6, 50, 87, 52, 75, 42, 81, 23, 16, 67, 25, 68, 47, 65, 92, 25, 90, 57, 11, 13, 61, 64, 66, 37, 67, 58, 89, 12, 79, 67, 6, 76, 30, 7, 70, 12, 24, 27, 37, 24, 50, 6, 38, 13, 42, 98, 77, 0, 1, 76, 41, 9, 58, 94, 13, 98, 14, 17, 52, 19, 22, 98, 99, 23, 12, 88, 41, 41, 46, 12, 94, 48, 13, 52, 92, 54, 54], [26, 35, 62, 24, 71, 42, 42, 61, 59, 52, 23, 76, 93, 32, 50, 98, 61, 12, 79, 63, 89, 6, 56, 33, 93, 36, 62, 59, 36, 40, 56, 42, 26, 0, 0, 2, 7, 74, 58, 57, 14, 17, 29, 21, 85, 88, 49, 3, 35, 88, 89, 58, 67, 41, 43, 43, 32, 48, 47, 58, 26, 67, 83, 4, 3, 12, 59, 57, 60, 37, 83, 84, 70, 21, 18, 10, 73, 2, 65, 80, 68, 68, 69, 72, 74, 74, 76, 79, 8, 85, 11, 82, 84, 35, 56, 93, 85, 78, 29, 27], [47, 40, 87, 30, 74, 73, 24, 74, 67, 29, 76, 47, 55, 54, 16, 97, 96, 65, 72, 87, 42, 44, 1, 10, 11, 78, 0, 82, 4, 60, 57, 70, 40, 43, 70, 88, 3, 19, 4, 44, 5, 12, 82, 22, 31, 16, 25, 82, 19, 62, 22, 22, 59, 14, 38, 89, 68, 65, 92, 29, 29, 61, 31, 85, 32, 36, 83, 39, 39, 44, 43, 82, 45, 75, 46, 47, 86, 49, 25, 55, 55, 34, 56, 46, 64, 79, 20, 89, 60, 21, 3, 69, 69, 69, 74, 74, 74, 27, 77, 78], [2, 85, 11, 98, 77, 23, 17, 54, 86, 22, 59, 62, 55, 70, 41, 91, 94, 60, 93, 11, 60, 79, 78, 92, 35, 50, 13, 64, 63, 30, 58, 64, 13, 37, 10, 67, 26, 89, 85, 14, 33, 47, 71, 66, 93, 49, 15, 69, 6, 48, 10, 59, 96, 67, 24, 77, 75, 32, 19, 93, 14, 40, 29, 72, 73, 38, 25, 31, 80, 0, 1, 49, 9, 69, 87, 16, 83, 79, 27, 29, 24, 39, 15, 25, 33, 95, 35, 41, 41, 93, 1, 66, 52, 53, 0, 65, 55, 55, 38, 34], [1, 59, 7, 55, 11, 64, 42, 95, 26, 84, 25, 59, 22, 5, 91, 19, 92, 88, 59, 50, 84, 94, 64, 15, 12, 10, 22, 41, 60, 11, 12, 80, 46, 25, 96, 20, 94, 14, 48, 15, 77, 49, 31, 93, 86, 44, 65, 59, 49, 27, 99, 21, 49, 44, 91, 62, 81, 62, 89, 15, 40, 55, 52, 56, 73, 15, 28, 27, 49, 17, 23, 21, 20, 91, 2, 34, 94, 89, 81, 86, 83, 20, 31, 18, 20, 8, 31, 38, 67, 78, 32, 52, 34, 45, 28, 63, 73, 63, 33, 0]]
    # initial_state = LiquidPuzzle("[[], [], [], [], [], [], [], [], [], [], [10, 14, 5, 48, 23, 16, 3, 23, 16, 2, 20, 24, 22, 20, 8, 8, 18, 19, 23, 1, 7, 22, 39, 40, 1, 22, 7, 20, 2, 37, 13, 24, 26, 38, 17, 22, 22, 29, 23, 46, 36, 5, 21, 3, 34, 1, 5, 3, 7, 12], [11, 5, 26, 35, 29, 15, 40, 27, 10, 14, 18, 38, 23, 4, 44, 25, 48, 35, 38, 10, 30, 27, 15, 19, 30, 28, 41, 21, 42, 41, 1, 5, 19, 36, 47, 25, 3, 36, 35, 48, 27, 43, 45, 42, 28, 27, 44, 8, 40, 0], [9, 39, 2, 32, 41, 24, 43, 9, 18, 29, 25, 35, 18, 34, 2, 37, 24, 37, 23, 10, 15, 37, 17, 34, 11, 16, 32, 33, 39, 31, 31, 0, 1, 3, 13, 42, 21, 46, 23, 30, 5, 39, 35, 46, 0, 7, 28, 14, 10, 49], [31, 12, 2, 4, 7, 30, 30, 30, 4, 31, 41, 7, 45, 45, 9, 43, 47, 30, 31, 20, 7, 15, 29, 23, 9, 49, 8, 11, 21, 21, 1, 14, 17, 21, 38, 10, 2, 43, 48, 48, 30, 25, 8, 14, 27, 5, 6, 20, 17, 48], [7, 27, 37, 45, 5, 31, 7, 44, 9, 48, 28, 24, 18, 46, 42, 18, 15, 30, 44, 49, 26, 49, 9, 36, 21, 8, 3, 11, 23, 0, 25, 10, 10, 3, 28, 24, 26, 45, 20, 20, 13, 37, 25, 32, 48, 6, 4, 13, 6, 15], [15, 15, 15, 43, 10, 5, 27, 7, 46, 9, 3, 4, 31, 13, 44, 23, 28, 15, 27, 44, 14, 38, 6, 28, 15, 34, 37, 14, 43, 40, 2, 12, 8, 34, 3, 49, 6, 44, 12, 17, 35, 47, 25, 24, 30, 21, 39, 24, 26, 41], [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 19, 11, 23, 21, 10, 15, 8, 49, 10, 14, 16, 11, 30, 38, 12, 34, 34, 25, 9, 26, 13, 44, 10, 26, 35, 38, 16, 1, 14, 41, 8, 48, 37, 10, 5, 37, 46], [17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 2, 38, 48, 0, 1, 41, 1, 47, 14, 22, 1, 6, 27, 37, 17, 1, 36, 34, 1, 25, 18, 18, 23, 8, 10, 1, 47, 11, 24, 42, 1, 8, 40, 2, 33, 18, 33], [46, 17, 31, 3, 30, 13, 34, 11, 1, 37, 10, 5, 30, 28, 31, 47, 30, 31, 18, 32, 34, 0, 24, 21, 22, 30, 37, 11, 44, 6, 11, 29, 49, 32, 25, 32, 3, 4, 7, 12, 31, 3, 8, 12, 25, 13, 20, 0, 9, 21], [19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 49, 36, 1, 28, 35, 3, 49, 27, 2, 30, 10, 28, 37, 10, 23, 12, 0, 15, 4, 39, 39, 4, 4, 5, 7, 47, 3, 15, 7, 35, 38, 40, 23, 43, 36, 23], [11, 0, 24, 19, 5, 9, 43, 3, 30, 49, 27, 4, 13, 37, 38, 8, 4, 36, 11, 8, 12, 31, 41, 25, 10, 28, 13, 11, 39, 24, 45, 5, 43, 45, 26, 5, 46, 23, 7, 7, 24, 16, 34, 11, 22, 45, 28, 9, 9, 9], [21, 21, 21, 21, 21, 21, 21, 21, 42, 47, 32, 18, 35, 13, 13, 39, 31, 36, 29, 37, 39, 19, 44, 45, 8, 12, 28, 10, 16, 17, 2, 0, 6, 39, 10, 37, 32, 3, 28, 38, 25, 41, 13, 2, 44, 2, 37, 49, 18, 12], [22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 13, 22, 35, 39, 17, 22, 47, 29, 34, 36, 11, 0, 14, 13, 14, 15, 26, 39, 38, 26, 41, 41, 20, 13, 17, 44, 44, 44, 3, 0, 3, 49, 36, 3, 28, 29, 29, 40, 48, 21], [23, 23, 23, 23, 23, 23, 23, 23, 23, 5, 35, 27, 24, 15, 17, 15, 40, 34, 1, 32, 40, 45, 13, 16, 42, 22, 23, 20, 12, 49, 12, 6, 35, 37, 49, 22, 15, 49, 26, 47, 23, 46, 28, 42, 24, 46, 24, 26, 4, 16], [24, 24, 24, 24, 24, 24, 24, 24, 24, 9, 22, 23, 4, 39, 2, 20, 36, 27, 9, 47, 9, 20, 31, 4, 19, 45, 44, 23, 4, 32, 8, 49, 39, 43, 16, 17, 37, 23, 20, 21, 3, 3, 21, 35, 26, 15, 20, 2, 5, 38], [1, 0, 40, 13, 30, 49, 28, 6, 36, 37, 22, 29, 9, 14, 36, 32, 30, 39, 25, 19, 37, 45, 40, 17, 24, 7, 26, 1, 24, 1, 1, 7, 4, 17, 21, 4, 11, 45, 23, 1, 10, 43, 14, 5, 4, 32, 33, 42, 44, 26], [15, 12, 34, 3, 29, 23, 30, 47, 40, 22, 4, 8, 29, 34, 1, 29, 29, 13, 25, 28, 14, 44, 10, 16, 2, 35, 40, 16, 8, 24, 10, 42, 12, 41, 11, 2, 25, 46, 22, 22, 25, 6, 33, 45, 18, 20, 9, 27, 32, 26], [48, 5, 38, 21, 37, 17, 21, 32, 41, 26, 46, 45, 16, 1, 46, 4, 49, 3, 39, 15, 44, 12, 34, 14, 41, 28, 32, 44, 4, 48, 24, 14, 13, 47, 10, 34, 35, 4, 28, 15, 24, 24, 48, 45, 31, 28, 32, 24, 10, 44], [28, 28, 28, 28, 28, 28, 34, 37, 22, 27, 38, 27, 49, 23, 33, 33, 6, 15, 37, 44, 5, 45, 21, 31, 7, 21, 12, 44, 26, 44, 4, 43, 49, 30, 5, 13, 12, 31, 21, 44, 5, 14, 7, 46, 6, 31, 0, 1, 18, 19], [29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 22, 42, 46, 13, 14, 40, 38, 47, 33, 38, 14, 14, 35, 19, 47, 12, 25, 13, 15, 42, 15, 28, 31, 31, 14, 24, 38, 28, 39, 9, 43, 8, 43, 0, 49, 24, 46, 3, 3, 39], [30, 30, 30, 30, 30, 5, 2, 39, 9, 38, 34, 1, 19, 40, 34, 1, 7, 5, 18, 10, 46, 30, 15, 27, 45, 25, 39, 32, 20, 46, 21, 32, 2, 18, 19, 43, 22, 46, 11, 14, 11, 40, 14, 41, 3, 3, 3, 11, 31, 9], [31, 31, 11, 43, 32, 38, 10, 20, 36, 45, 32, 32, 13, 11, 6, 38, 21, 11, 8, 15, 6, 12, 0, 18, 34, 9, 9, 11, 14, 31, 0, 39, 2, 12, 48, 29, 33, 10, 28, 37, 43, 40, 16, 26, 13, 41, 0, 24, 49, 18], [32, 32, 32, 32, 32, 32, 32, 32, 32, 6, 41, 42, 46, 27, 46, 7, 44, 25, 28, 40, 8, 32, 26, 40, 6, 20, 47, 48, 27, 18, 48, 5, 35, 4, 46, 4, 7, 14, 0, 4, 45, 39, 15, 13, 19, 44, 9, 9, 9, 9], [33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 45, 17, 35, 37, 9, 24, 47, 25, 10, 41, 22, 18, 7, 34, 42, 49, 37, 35, 35, 3, 6, 39, 44, 32, 10, 49, 26], [34, 34, 34, 34, 35, 35, 41, 39, 29, 25, 8, 34, 43, 13, 1, 6, 47, 39, 47, 42, 12, 0, 3, 43, 17, 1, 31, 15, 29, 12, 22, 30, 13, 46, 8, 25, 19, 45, 12, 35, 25, 36, 22, 23, 41, 15, 2, 26, 0, 43], [35, 35, 35, 35, 35, 35, 35, 35, 46, 3, 25, 27, 15, 38, 0, 34, 29, 30, 7, 3, 30, 31, 45, 13, 40, 19, 8, 18, 25, 21, 36, 23, 23, 46, 31, 31, 20, 7, 31, 20, 21, 12, 11, 21, 9, 13, 21, 44, 0, 6], [36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 23, 34, 1, 11, 38, 8, 30, 44, 40, 15, 5, 26, 3, 6, 21, 26, 3, 25, 20, 7, 31, 0, 41, 9, 3, 25, 20, 12, 4, 36, 16, 14, 43, 7, 27, 47, 28, 20], [45, 18, 27, 5, 41, 25, 8, 43, 13, 37, 41, 29, 14, 4, 28, 44, 43, 34, 27, 13, 23, 2, 44, 25, 45, 37, 2, 11, 47, 0, 37, 47, 27, 24, 27, 2, 20, 36, 18, 14, 25, 22, 30, 6, 22, 7, 30, 48, 10, 29], [38, 38, 38, 38, 38, 38, 2, 48, 21, 0, 37, 38, 47, 36, 42, 22, 41, 43, 3, 16, 34, 20, 44, 37, 45, 18, 43, 40, 4, 21, 11, 17, 34, 13, 39, 0, 48, 34, 19, 21, 25, 8, 4, 11, 12, 5, 14, 6, 28, 6], [39, 39, 39, 39, 39, 39, 6, 30, 41, 35, 36, 13, 3, 44, 37, 21, 30, 26, 49, 10, 33, 43, 42, 47, 46, 39, 6, 32, 35, 6, 38, 24, 40, 43, 18, 24, 22, 26, 46, 37, 2, 4, 47, 8, 16, 25, 49, 25, 9, 47], [40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 11, 35, 36, 40, 23, 28, 47, 48, 31, 28, 20, 35, 29, 23, 27, 48, 17, 30, 48, 49, 41, 39, 20, 39, 27, 24, 19, 18, 12, 47, 33, 8, 8, 18, 2, 47], [49, 32, 5, 39, 43, 7, 27, 1, 34, 34, 18, 31, 26, 11, 27, 8, 25, 20, 20, 2, 13, 27, 8, 5, 37, 15, 30, 19, 9, 42, 23, 26, 10, 22, 5, 5, 28, 6, 33, 14, 27, 36, 44, 45, 39, 30, 39, 29, 2, 13], [42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 42, 18, 8, 29, 8, 31, 9, 20, 28, 9, 27, 17, 38, 39, 19, 48, 9, 7, 18, 37, 14, 49, 17, 41, 47, 35, 0, 24, 5], [43, 43, 43, 43, 43, 43, 43, 43, 43, 3, 27, 14, 29, 18, 43, 1, 14, 39, 33, 44, 31, 19, 46, 44, 40, 7, 16, 43, 24, 34, 11, 9, 18, 17, 17, 6, 21, 25, 9, 45, 26, 32, 31, 23, 33, 21, 11, 4, 0, 0], [26, 45, 32, 5, 49, 33, 30, 1, 9, 4, 1, 40, 5, 14, 39, 28, 11, 17, 38, 2, 36, 22, 37, 18, 16, 13, 47, 2, 34, 15, 1, 28, 14, 40, 10, 16, 17, 10, 27, 47, 12, 11, 8, 31, 26, 11, 26, 0, 6, 3], [45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 18, 35, 20, 17, 45, 37, 18, 43, 10, 40, 22, 44, 18, 16, 4, 21, 19, 44, 41, 1, 47, 27, 13, 35, 37, 0, 28, 16, 15, 3, 15, 4, 26, 17, 29, 47, 0, 4, 45], [46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 39, 26, 3, 48, 24, 24, 47, 31, 18, 31, 22, 11, 8, 41, 19, 25, 36, 49, 7, 1, 7, 22, 5, 41, 23, 26, 24, 29, 41, 20, 1, 6, 26, 38, 28, 18, 19], [30, 30, 49, 12, 48, 12, 31, 41, 38, 1, 32, 10, 32, 9, 10, 20, 4, 3, 18, 49, 1, 26, 14, 36, 31, 3, 40, 2, 42, 35, 7, 20, 41, 47, 3, 29, 36, 14, 5, 45, 12, 1, 26, 29, 11, 5, 35, 16, 12, 45], [48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 12, 27, 36, 5, 32, 31, 12, 47, 7, 27, 37, 38, 5, 7, 14, 48, 45, 16, 32, 20, 8, 6, 10, 13, 18, 47, 38, 23, 18, 15, 28, 37, 9, 4, 43, 34, 25, 39], [49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 42, 33, 33, 19, 44, 43, 15, 31, 14, 8, 24, 41, 0, 25, 37, 1, 2, 4, 16, 2, 28, 27, 25, 18, 33, 6, 46, 49, 12, 27, 15, 6, 29, 5, 24, 7, 35, 0, 35], [47, 29, 19, 11, 45, 14, 30, 4, 4, 25, 36, 19, 0, 15, 15, 5, 48, 38, 28, 35, 24, 34, 1, 16, 0, 39, 13, 17, 32, 44, 6, 12, 21, 11, 40, 14, 36, 22, 27, 29, 10, 47, 3, 5, 15, 10, 18, 7, 25, 29], [19, 8, 35, 44, 33, 15, 19, 38, 20, 49, 22, 26, 0, 2, 2, 44, 18, 48, 33, 45, 27, 11, 2, 10, 41, 13, 32, 6, 43, 11, 6, 25, 15, 27, 14, 32, 49, 21, 6, 39, 12, 48, 20, 41, 36, 7, 33, 47, 9, 20], [6, 38, 46, 29, 48, 28, 45, 12, 47, 29, 36, 12, 2, 28, 15, 36, 2, 4, 38, 4, 37, 13, 28, 33, 18, 43, 20, 47, 41, 14, 49, 37, 0, 27, 10, 25, 17, 31, 4, 18, 7, 20, 40, 34, 33, 7, 7, 25, 45, 9], [15, 11, 22, 49, 26, 41, 2, 20, 26, 25, 20, 23, 35, 17, 20, 32, 47, 16, 6, 38, 18, 11, 25, 19, 40, 6, 19, 31, 25, 11, 7, 8, 38, 5, 27, 36, 33, 47, 8, 43, 37, 34, 19, 23, 2, 38, 40, 32, 33, 0], [27, 31, 20, 44, 21, 25, 26, 27, 13, 32, 12, 42, 38, 32, 4, 10, 5, 26, 47, 0, 41, 44, 34, 44, 0, 23, 8, 24, 14, 21, 1, 48, 12, 46, 41, 42, 24, 29, 46, 13, 13, 42, 46, 1, 48, 22, 9, 9, 9, 9], [31, 34, 4, 22, 2, 34, 39, 10, 14, 7, 22, 39, 46, 26, 34, 28, 46, 31, 44, 35, 44, 26, 10, 7, 46, 17, 13, 37, 26, 43, 41, 41, 38, 30, 41, 33, 26, 38, 47, 43, 8, 12, 6, 1, 30, 0, 33, 18, 6, 10], [31, 41, 36, 19, 30, 30, 4, 8, 41, 48, 32, 15, 22, 15, 13, 2, 8, 9, 1, 20, 27, 34, 47, 35, 42, 16, 23, 37, 11, 40, 16, 18, 16, 30, 17, 0, 20, 10, 2, 44, 13, 16, 0, 17, 0, 38, 28, 26, 1, 26], [1, 21, 8, 7, 38, 29, 6, 41, 16, 27, 12, 14, 4, 20, 35, 12, 12, 4, 48, 25, 7, 19, 37, 5, 36, 17, 5, 16, 29, 0, 40, 3, 8, 3, 38, 6, 31, 20, 5, 5, 37, 7, 7, 9, 18, 11, 2, 10, 44, 20], [2, 16, 14, 6, 11, 11, 20, 13, 30, 32, 21, 29, 3, 46, 44, 15, 42, 9, 19, 31, 17, 45, 47, 23, 17, 42, 2, 48, 19, 37, 10, 26, 2, 41, 21, 27, 6, 11, 4, 39, 0, 3, 3, 43, 29, 42, 8, 29, 12, 8], [30, 42, 34, 43, 43, 17, 41, 2, 7, 47, 30, 48, 19, 16, 32, 41, 36, 23, 49, 9, 6, 48, 16, 34, 0, 2, 5, 34, 40, 13, 41, 22, 34, 1, 14, 0, 16, 6, 36, 12, 39, 21, 12, 14, 8, 35, 15, 12, 27, 6]]")
    # result = solve(initial_state)
    # arr = initial_state.get_neighbors()
    # solve_debug(initial_state,result[1])
    menu()
