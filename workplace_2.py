from queue import PriorityQueue


def construct_puzzle(string):
    string = string.replace(" ", "").replace("[", "").replace("]", " ")
    tubes = string.strip().split(" ")
    puzzle = []
    for tube in tubes:
        if tube:
            puzzle.append([int(x) for x in tube.split(",") if x])
        else:
            puzzle.append([])
    return puzzle


def construct_correctness(puzzle):
    max_tube = max(len(tube) for tube in puzzle)
    max_color = 0
    for arr in puzzle:
        for j in arr:
            if j > max_color:
                max_color = j

    if max_color > len(puzzle) * max_tube:
        return False

    counter_list = [0] * max_color
    for arr in puzzle:
        for j in arr:
            counter_list[j - 1] += 1
    for count in counter_list:
        if count != max_tube:
            return False

    return True


class LiquidPuzzle:
    def __init__(self, string):
        self.tubes = construct_puzzle(string)
        if not construct_correctness(self.tubes):
            raise ValueError("Invalid puzzle configuration")
        self.tube_size = max(len(tube) for tube in self.tubes)

    def is_valid_move(self, tube_from, tube_to):
        if not self.tubes[tube_from] or len(self.tubes[tube_to]) >= self.tube_size:
            return False
        if not self.tubes[tube_to] or self.tubes[tube_from][-1] == self.tubes[tube_to][-1]:
            return True
        return False

    def move(self, tube_from, tube_to):
        if self.is_valid_move(tube_from, tube_to):
            new_tubes = [list(tube) for tube in self.tubes]
            new_tubes[tube_to].append(new_tubes[tube_from].pop())
            return LiquidPuzzle.from_puzzle(new_tubes)
        return None

    def get_neighbors(self):
        neighbors = []
        for i in range(len(self.tubes)):
            if not self.tubes[i]:
                continue
            for j in range(len(self.tubes)):
                if i != j and self.is_valid_move(i, j):
                    neighbor = self.move(i, j)
                    if neighbor:
                        neighbors.append(neighbor)
        return neighbors

    @staticmethod
    def from_puzzle(puzzle):
        puzzle_str = ''.join(['[' + ','.join(map(str, tube)) + ']' for tube in puzzle])
        return LiquidPuzzle(puzzle_str)

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


def heuristic(puzzle):
    misplaced_liquids = 0
    mixed_containers = 0
    for tube in puzzle.tubes:
        if len(tube) > 0 and len(set(tube)) > 1:
            mixed_containers += 1
        if len(tube) > 0 and len(set(tube)) == 1 and len(tube) != puzzle.tube_size:
            misplaced_liquids += puzzle.tube_size - len(tube)
    return misplaced_liquids + mixed_containers


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


def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]


def test_a_star():
    initial_state = LiquidPuzzle("[[1,2,3],[3,2,1],[2,3,1],[]]")
    path = a_star(initial_state)
    if path:
        for step in path:
            print(step)
    else:
        print("No solution found.")


def userInterface():
    print("-------------------------------------------------------------------------------------------------------")
    correctInput = False
    puzzle = LiquidPuzzle
    while not correctInput:
        str_in = input("Please enter the Liquid Puzzle: ")
        puzzle = LiquidPuzzle(str_in)
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
    puzzle = LiquidPuzzle("[]")
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


if __name__ == '__main__':
    test_a_star()
