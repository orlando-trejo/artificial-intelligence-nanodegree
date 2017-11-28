from copy import deepcopy

xlim, ylim = 3, 2

class GameState:

    def __init__(self):
        self._board = [[0] * ylim for _ in range(xlim)]
        self._board[-1][-1] = 1
        self._parity = 0
        self._players_locations = [None, None]

    def forecast_move(self, move):

        if move not in self.get_legal_moves():
            raise RunTimeError('Move is not valid.')

        newboard = deepcopy(self)
        newboard._board[move[0]][move[1]] = 1
        newboard._players_locations[self._parity] = move
        newboard._parity ^= 1
        return newboard

    def get_legal_moves(self):

        loc = self._players_locations[self._parity]
        if not loc:
            return self.get_blank_spaces()

        moves = []
        rays = [(1,0), (1,1), (0,1), (-1,1), (0,-1),
                (-1,-1), (0,-1), (1,-1)]

        for dx, dy in rays:
            _x, _y = loc
            while 0 <= _x + dx < xlim and 0 <= _y + dy < ylim:
                _x, _y = _x + dx, _y + dy
                if self._board[_x][_y]:
                    break
                moves.append((_x, _y))

        return moves

    def get_blank_spaces(self):
        spaces = [(x,y) for x in range(xlim) for y in range(ylim)
                    if self._board[x][y] == 0]

        return spaces

def terminal_state(gameState):
    return not bool(gameState.get_legal_moves())

def min_value(gameState):
    if terminal_state(gameState):
        return +1

    v = float('inf')

    for move in gameState.get_legal_moves():
        v = min(v, max_value(gameState.forecast_move(move)))

    return v

def max_value(gameState):
    if terminal_state(gameState):
        return -1

    v = float('-inf')

    for move in gameState.get_legal_moves():
        v = max(v, min_value(gameState.forecast_move(move)))

    return v

def minimax(gameState):
    best_score = float('-inf')
    best_move = [None, None]

    for move in gameState.get_legal_moves():
        v = min_value(gameState.forecast_move(move))
        if v > best_score:
            best_score = v
            best_move = move

    return best_move
