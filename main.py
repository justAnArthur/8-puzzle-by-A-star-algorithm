import math
import time
from copy import deepcopy

statistics = {'nodes': 0}
directions = {(0, 1): 'right', (0, -1): 'left', (1, 0): 'down', (-1, 0): 'up'}

goal_state = None
routes = None
heuristic_method = None
sizes = None


def find_position(state, target):
    """
    Find the position of a target element in a given state.

    :param state: A 2D array representing the state.
    :param target: The element to find in the state.
    :return: A tuple representing the position of the target element in the form (row, column).
    """

    for i in range(sizes[0]):
        for j in range(sizes[1]):
            if state[i][j] == target:
                return i, j


def getAvailableRoutes(state, prev_move):
    """
    :param state: The current state of the puzzle
    :param prev_move: The previous move made in the puzzle
    :return: A list of available moves

    This method takes the current state of the puzzle and the previous move made, and returns a list of available
    moves. Each move is represented by a list containing the direction of the move and the resulting state of the
    puzzle after making the move.

    The method first finds the position of the empty space (represented by 0) in the current state. It then iterates
    over the possible directions to move in and checks if the move is valid: - If the previous move is provided and
    the current move is the reverse of the previous move, it is not considered as a valid move. - It calculates the
    new position after making the move. - It checks if the new position is within the boundaries of the puzzle. - If
    the move is valid, it creates a new state by swapping the empty space with the neighboring tile and adds the move
    to the list of available moves.

    Finally, the method returns the list of available moves.

    Note: The method relies on an external function `find_position` and requires the `directions` and `sizes`
    variables to be defined and accessible by the method.
    """

    x, y = find_position(state, 0)

    moves = []
    # directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for dx, dy in directions.keys():
        if prev_move is not None and dx == prev_move[0] * -1 and dy == prev_move[1] * -1:
            continue

        nx, ny = x + dx, y + dy

        if 0 <= nx < sizes[0] and 0 <= ny < sizes[1]:
            new_state = deepcopy(state)
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            moves.append([[dx, dy], new_state])

    return moves


def getHeuristicScore(state):
    """
    Calculate the heuristic score for a given state.

    :param state: The current state of the puzzle.
    :return: The heuristic score for the state.
    """

    score = 0  # 0 is goal (filtered by min)

    match heuristic_method:
        case 1:
            for i, row in enumerate(state):
                for j, element in enumerate(row):
                    if state[i][j] != goal_state[i][j]:
                        score += 1

        case 2:
            for i, row in enumerate(state):
                for j, element in enumerate(row):
                    x, y = find_position(goal_state, element)
                    score += abs(i - x)
                    score += abs(j - y)

    return score


# Handle user inputs
print("Enter a state sizes, like m n, or ENTER if default: ")
_sizes = input().split()
if len(_sizes) > 0:
    assert _sizes[0].isdigit() and int(_sizes[0]) > 0 and _sizes[1].isdigit() and int(_sizes[1]) > 0 \
        , "Values must be digits and more than 0"
    sizes = [int(_sizes[0]), int(_sizes[1])]
else:
    sizes = [3, 3]

print(f"Enter a initial state of the puzzle 1-{sizes[0] * sizes[1] - 1}, and 0 as an empty one: ")
_initial_state = input().split()
assert len(_initial_state) == sizes[0] * sizes[1] \
    , f"You must provide exactly {sizes[0] * sizes[1]} characters."
assert set(_initial_state) == set([str(i) for i in range(sizes[0] * sizes[1])]) \
    , "Must be a range of values."
routes = [{'state':
               [[0 if x == 'A' else int(x) for x in _initial_state[i * sizes[1]:(i + 1) * sizes[1]]] for i in
                range(sizes[0])]
           }]

print(f"Enter a goal state of the puzzle 1-{sizes[0] * sizes[1] - 1}, and 0 as an empty one, or ENTER if default: ")
_goal_state = input().split()
if len(_goal_state) > 1:
    assert len(_goal_state) == sizes[0] * sizes[1] \
        , f"You must provide exactly {sizes[0] * sizes[1]} characters."
    assert set(_goal_state) == set([str(i) for i in range(sizes[0] * sizes[1])]) \
        , "Tou must provide the characters 1-8 a."
    goal_state = [[0 if x == 'A' else int(x) for x in _initial_state[i * sizes[1]:(i + 1) * sizes[1]]] for i in
                  range(sizes[0])]
else:
    goal_state = [[0] * sizes[1] for _ in range(sizes[0])]
    num = 1

    for i in range(sizes[0]):
        for j in range(sizes[1]):
            if num == sizes[0] * sizes[1]:
                goal_state[i][j] = 0
            else:
                goal_state[i][j] = num
                num += 1

print("Select method for calculating a Heuristic score: ")
_heuristic_method = input()
assert _heuristic_method.isdigit() \
    , "Must be number."
assert int(_heuristic_method) in range(1, 3) \
    , "Must be from 1 or 2."
heuristic_method = int(_heuristic_method)

timer = time.perf_counter()

while True:
    if statistics['nodes'] >= math.factorial(sizes[0] * sizes[1]):
        print('')
        print('There\'s no solutions')
        break

    # Find the nodes with the best heuristics score
    best = min(routes, key=lambda route: route.get('heuristic_score', 0))
    best_index = routes.index(best)

    # Print actual information
    print(
        f"Nodes: {statistics['nodes']} | "
        f"Depth: {len(best.get('path', []))} | "
        f"Score: {best.get('heuristic_score')} | "
        f"Time: {round(abs(timer - time.perf_counter()), 4)} sec",
        end="\r", flush=True,
    )

    # If 0 - goal state
    if best.get('heuristic_score') == 0:
        print('')
        print(' '.join(map(lambda move: directions.get(tuple(move)), best.get('path'))))
        break

    # Remove a checked one
    del routes[best_index]

    if len(best.get('path', [])) >= 31:
        continue

    # Map moves
    moves = map(
        lambda move: {
            'path': best.get('path', [])[:] + [move[0]],
            'heuristic_score': getHeuristicScore(move[1]),
            'state': move[1],
        },
        getAvailableRoutes(best['state'], best['path'][-1] if len(best.get('path', [])) > 0 else None)
    )

    # Remove the reversal move
    if best.get('path') is not None:
        moves = filter(
            lambda move: move['path'] != best['path'][-1],
            moves
        )

    # And a new "children" by move from this best node
    routes.extend(moves)

    statistics['nodes'] += 1
