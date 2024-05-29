from queue import PriorityQueue
import ast


def construct_puzzle(string):
    try:
        puzzle = ast.literal_eval(string)
    except Exception as e:
        return []
    return puzzle


def construct_correctness(puzzle):
    color_count = {}
    max_tube = max(len(tube) for tube in puzzle) if puzzle else 0

    # Count occurrences of each color
    for tube in puzzle:
        for color in tube:
            if color in color_count:
                color_count[color] += 1
            else:
                color_count[color] = 1

    # Check if each color has the correct amount in the puzzle
    for color, count in color_count.items():
        if count > max_tube * len(puzzle):
            return False

    return True


class LiquidPuzzle:
    def __init__(self, string):
        self.tubes = construct_puzzle(string)
        if not construct_correctness(self.tubes):
            raise ValueError("Invalid puzzle configuration")
        self.tube_size = max(len(tube) for tube in self.tubes)

    def is_valid_move(self, tube_from, tube_to):
        if not self.tubes[tube_from]:
            return False
        if len(self.tubes[tube_to]) >= self.tube_size:
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
            for j in range(len(self.tubes)):
                if i != j and self.is_valid_move(i, j):
                    neighbor = self.move(i, j)
                    if neighbor:
                        neighbors.append(neighbor)
        return neighbors

    @staticmethod
    def from_puzzle(puzzle):
        puzzle_str = '[' + '],['.join([','.join(map(str, tube)) if tube else '' for tube in puzzle]) + ']'
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


def test_a_star():
    # initial_state = LiquidPuzzle(
    #     "[[], [], [], [], [], [4, 4, 4, 2, 6, 18, 9, 3, 18, 1, 5, 0, 6, 13, 18, 9, 14, 13, 2, 3], [5, 5, 5, 5, 5, 6, "
    #     "4, 17, 16, 9, 5, 5, 6, 17, 14, 12, 16, 3, 11, 0], [14, 16, 10, 0, 6, 19, 12, 10, 1, 7, 14, 14, 2, 4, 6, 4, "
    #     "3, 3, 1, 1], [7, 7, 7, 7, 7, 7, 11, 13, 19, 2, 18, 17, 3, 2, 1, 16, 0, 1, 5, 4], [8, 8, 8, 8, 8, 8, 8, 8, 7, "
    #     "1, 11, 19, 9, 14, 9, 17, 1, 1, 1, 14], [16, 8, 12, 15, 13, 2, 2, 8, 7, 2, 15, 19, 1, 6, 2, 2, 4, 6, 1, 12], "
    #     "[10, 10, 10, 10, 10, 10, 10, 10, 12, 3, 15, 19, 4, 1, 16, 14, 11, 16, 18, 0], [5, 13, 10, 11, 9, 12, 5, 10, "
    #     "0, 3, 8, 3, 3, 10, 3, 17, 18, 14, 17, 15], [12, 12, 12, 6, 19, 19, 2, 4, 4, 13, 2, 3, 10, 15, 0, 4, 17, 9, "
    #     "15, 16], [13, 13, 13, 13, 13, 13, 13, 4, 11, 19, 6, 11, 9, 16, 11, 7, 0, 0, 17, 1], [14, 14, 14, 14, 14, 14, "
    #     "14, 7, 18, 7, 17, 19, 17, 19, 11, 13, 7, 8, 0, 19], [15, 15, 3, 0, 4, 8, 2, 18, 12, 11, 19, 0, 0, 7, 10, 15, "
    #     "18, 17, 5, 0], [16, 16, 16, 14, 10, 5, 8, 2, 15, 3, 12, 18, 4, 18, 11, 6, 5, 6, 15, 17], [13, 1, 3, 10, 16, "
    #     "8, 9, 17, 7, 8, 5, 11, 9, 9, 15, 12, 5, 7, 19, 0], [18, 18, 18, 17, 12, 3, 11, 6, 2, 19, 18, 1, 15, 9, 14, "
    #     "12, 4, 15, 5, 7], [17, 10, 19, 18, 2, 12, 6, 17, 19, 2, 13, 8, 9, 5, 4, 11, 12, 18, 13, 11], [3, 9, 16, 16, "
    #     "12, 3, 6, 16, 8, 17, 11, 1, 18, 0, 0, 17, 7, 18, 19, 15], [10, 14, 6, 8, 12, 13, 11, 7, 3, 9, 10, 15, 15, 0, "
    #     "15, 19, 12, 9, 4, 4], [5, 16, 2, 18, 1, 17, 6, 14, 16, 16, 6, 6, 0, 16, 4, 9, 15, 17, 0, 13], [3, 19, 7, 11, "
    #     "13, 15, 11, 1, 9, 2, 2, 6, 9, 11, 8, 5, 12, 19, 9, 1]]")
    initial_state = LiquidPuzzle("[[], [0, 1, 1], [2, 0, 1], [0, 2, 2]]")
    path = a_star(initial_state)
    if path:
        for step in path:
            print(step)
    else:
        print("No solution found.")


if __name__ == '__main__':
    test_a_star()
    # test_ida_star()
