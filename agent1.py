import random
import math

def find_varys(cards):
    """
    Finds the location of Varys on the board.
    """
    varys = [card for card in cards if card.get_name() == 'Varys']
    return varys[0].get_location()

def get_valid_moves(cards):
    """
    Gets all valid moves for Varys based on the board state.
    """
    varys_location = find_varys(cards)
    varys_row, varys_col = varys_location // 6, varys_location % 6
    moves = []
    for card in cards:
        if card.get_name() == 'Varys':
            continue
        row, col = card.get_location() // 6, card.get_location() % 6
        if row == varys_row or col == varys_col:
            moves.append(card.get_location())
    return moves

def evaluate_state(cards, player1, player2):
    """
    Evaluates the board state and returns a heuristic score.
    """
    # Assuming 'collected_cards' is an attribute in Player
    return len(player1.collected_cards) - len(player2.collected_cards)

def generate_neighbor(cards, current_move):
    """
    Generates a neighboring move for simulated annealing.
    """
    valid_moves = get_valid_moves(cards)
    if valid_moves:
        return random.choice(valid_moves)
    return current_move

def simulated_annealing(cards, player1, player2, companion_cards, choose_companion):
    """
    Simulated annealing algorithm to find the optimal move.
    """
    current_move = random.choice(get_valid_moves(cards))
    current_score = evaluate_state(cards, player1, player2)
    temperature = 100
    cooling_rate = 0.99

    while temperature > 1:
        neighbor = generate_neighbor(cards, current_move)
        new_score = evaluate_state(cards, player1, player2)
        if new_score > current_score or math.exp((new_score - current_score) / temperature) > random.random():
            current_move = neighbor
            current_score = new_score
        temperature *= cooling_rate

    return current_move

def get_move(cards, player1, player2, companion_cards, choose_companion):
    """
    Main function to return the move for the agent.
    """
    if choose_companion:
        if companion_cards:
            selected_companion = random.choice(list(companion_cards.keys()))
            move = [selected_companion]
            choices = companion_cards[selected_companion]['Choice']

            if choices == 1:
                move.append(random.choice(get_valid_moves(cards)))
            elif choices == 2:
                valid_moves = get_valid_moves(cards)
                if len(valid_moves) >= 2:
                    move.extend(random.sample(valid_moves, 2))
                else:
                    move.extend(valid_moves)
            elif choices == 3:
                valid_moves = get_valid_moves(cards)
                if len(valid_moves) >= 2 and len(companion_cards) > 0:
                    move.extend(random.sample(valid_moves, 2))
                    move.append(random.choice(list(companion_cards.keys())))
                else:
                    move.extend(valid_moves)
                    move.append(random.choice(list(companion_cards.keys())) if companion_cards else None)

            return move
        else:
            return []
    else:
        return simulated_annealing(cards, player1, player2, companion_cards, choose_companion)
