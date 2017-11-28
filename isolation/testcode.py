from gamestate import *

print('Creating empty board:')
g = GameState()

print('Getting legals moves for player 1:')
p1_empty_moves = g.get_legal_moves()
print('Legals moves for player1: {}'.format(len(p1_empty_moves or [])))

print('Applying (0,0) move for player 1:')
g1 = g.forecast_move((0,0))

print('Get legals moves for player 2:')
p2_moves = g1.get_legal_moves()
print('Legal moves for player2: {}'.format(len(p2_moves or [])))

if (0, 0) in set(p2_moves):
    print('Fail!')
else:
    print('Looks good!')

print('Calling min_value on empty board:')
g_new = GameState()
v = min_value(g_new)

if v == 1:
    print('returned expected score')
else:
    print('Wrong!')

best_moves = set([(0,0), (2,0), (0,1)])
rootNode = GameState()
minimax_move = minimax(rootNode)

print('Best move choices: {}'.format(best_moves))
print('Chosen moves:{}'.format(minimax_move))
if minimax_move in best_moves:
    print("That's one of the best move choices. Looks like your minimax-decision function worked!")
else:
    print("Uh oh...looks like there may be a problem.")
