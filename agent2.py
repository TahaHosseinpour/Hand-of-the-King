import random
import math
import logging

# python main.py --player1 agent2 --player2 random_agent

COMPANION_NOISE_RANGE = 1
LOCATION_NOISE_RANGE = 3

def pad_or_truncate(some_list, target_len):
    # to make lists fit the size we want (extend list with -1)
    return some_list[:target_len] + [-1]*(target_len - len(some_list))

def find_varys(cards):
    '''
    This function finds the location of Varys on the board.

    Parameters:
        cards (list): list of Card objects

    Returns:
        varys_location (int): location of Varys
    '''

    varys = [card for card in cards if card.get_name() == 'Varys']

    varys_location = varys[0].get_location()

    return varys_location

def get_valid_moves(cards):
    '''
    This function gets the possible moves for the player.

    Parameters:
        cards (list): list of Card objects

    Returns:
        moves (list): list of possible moves
    '''

    # Get the location of Varys
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

def get_valid_ramsay(cards):
    '''
    This function gets the possible moves for Ramsay.

    Parameters:
        cards (list): list of Card objects
    
    Returns:
        moves (list): list of possible moves
    '''

    moves=[]

    for card in cards:
        moves.append(card.get_location())
    
    return moves

def get_valid_jon_sandor_jaqan(cards):
    '''
    This function gets the possible moves for Jon Snow, Sandor Clegane, and Jaqen H'ghar.

    Parameters:
        cards (list): list of Card objects
    
    Returns:
        moves (list): list of possible moves
    '''

    moves=[]

    for card in cards:
        if card.get_name() != 'Varys':
            moves.append(card.get_location())
    
    return moves

def evaluate_state(cards, player1, player2):
    """
    Evaluates the board state and returns a heuristic score.
    """
    # Assuming 'collected_cards' is an attribute in Player
    return random.randint(0, 10)

def generate_neighbor_normal(cards, current_move):
    """
    Generates a neighboring move for simulated annealing when choose_companion==false
    """
    valid_moves = get_valid_moves(cards)
    if valid_moves:
        return random.choice(valid_moves)
    return current_move

def change_or_generate_location( cards, current_move, valid_moves, move, index):

    # current_move has parameter index => random change it
    if len(current_move) >= index+1:
        
        # for card in cards:
        #     print(card.get_location(), end=' ')
        # print(valid_moves)
        # print(current_move, index)

        is_varis = False
        for card in cards:
            if card.get_location() == current_move[index]:
                if card.get_name() == 'Varys':
                    is_varis = True
                    break  

        if is_varis:
            location_index = random.randrange(0, len(valid_moves))
        else:
            location_index = valid_moves.index(current_move[index])

        random_noise = random.randint( -LOCATION_NOISE_RANGE, LOCATION_NOISE_RANGE )
        new_location_index = max(0, min(location_index + random_noise, len(valid_moves)-1))
        move.append(valid_moves[new_location_index])

    # current_move doesn't have parameter index => random generate it
    else:
        if len(valid_moves) >= 1:
            move.append(random.choice(valid_moves))
                
        else:
            # If not enough moves, just use what's available
            move.append(valid_moves)

    return pad_or_truncate(move, index+1)

def change_or_generate_companion( current_companion, companion_cards, move, index):
    
    # current_companion has parameter index => random change it
    if len(current_companion) >= index+1:
                
        companion_index = list(companion_cards.keys()).index(current_companion[index])
        random_noise = random.randint(-COMPANION_NOISE_RANGE, COMPANION_NOISE_RANGE)
        new_companion_index = max(0, min(companion_index + random_noise, len(companion_cards)-1))
        new_companion = list(companion_cards.keys())[new_companion_index]
        move.append(new_companion)

    # current_companion doesn't have parameter index => random generate it
    else:
        if len(companion_cards) > 0:
            move.append(random.choice(list(companion_cards.keys())))
                
        else:
            # If there aren't enough companion cards, append none
            move.append(None)

    return pad_or_truncate(move, index+1)

def generate_neighbor_companion(cards, companion_cards, current_companion):
    """
    Generates a neighboring companion for simulated annealing when choose_companion==true
    """
    if len(current_companion) <= 0:
        logging.exception("invalid current_companion")
        return None
    
    # get current selected companion and change it randomly.
    companion_index = list(companion_cards.keys()).index(current_companion[0])
    random_noise = random.randint(-COMPANION_NOISE_RANGE, COMPANION_NOISE_RANGE)
    new_companion_index = max(0, min(companion_index + random_noise, len(companion_cards)-1))
    new_companion = list(companion_cards.keys())[new_companion_index]

    move = [new_companion]
    choices = companion_cards[new_companion]['Choice']

    # Gendry, Melisandre => [companion_card]
    # choices == 0

    # Jon, Sandor => [companion_card, location]
    if choices == 1:

        valid_moves = get_valid_jon_sandor_jaqan(cards)
        move = change_or_generate_location( cards, current_companion, valid_moves, move, 1)

    # Ramsay => [companion_card, location, location]
    elif choices == 2:

        valid_moves = get_valid_ramsay(cards)
        move = change_or_generate_location( cards, current_companion, valid_moves, move, 1)
        move = change_or_generate_location( cards, current_companion, valid_moves, move, 2)
                      
    # Jaqen => [companion_card, location, location, companion_card]
    elif choices == 3:

        valid_moves = get_valid_jon_sandor_jaqan(cards)
        move = change_or_generate_location( cards, current_companion, valid_moves, move, 1)
        move = change_or_generate_location( cards, current_companion, valid_moves, move, 2)
        move = change_or_generate_companion( current_companion, companion_cards, move, 3)
        
    return move
        
def simulated_annealing_normal(cards, player1, player2):
    """
    Simulated annealing algorithm to find the optimal move when choose_companion==false
    """
    current_move = random.choice(get_valid_moves(cards))
    current_score = evaluate_state(cards, player1, player2)
    temperature = 100
    cooling_rate = 0.99

    while temperature > 1:
        neighbor = generate_neighbor_normal(cards, current_move)
        new_score = evaluate_state(cards, player1, player2)
        if new_score > current_score or math.exp(-abs(new_score - current_score) / temperature) > random.random():
            current_move = neighbor
            current_score = new_score
        temperature *= cooling_rate

    return current_move

def generate_random_companion(cards, companion_cards):
    """
    Generates a random move for simulated annealing when choose_companion==true
    """
    
    # get a random companion.
    new_companion = random.choice(list(companion_cards.keys()))
    move = [new_companion]
    choices = companion_cards[new_companion]['Choice']

    # Gendry, Melisandre => [companion_card]
    # choices == 0

    # Jon, Sandor => [companion_card, location]
    if choices == 1:
        move.append(random.choice(get_valid_jon_sandor_jaqan(cards)))
        move = pad_or_truncate(move, 2)

    # Ramsay => [companion_card, location, location]
    elif choices == 2:
        valid_moves = get_valid_ramsay(cards)

        if len(valid_moves) >= 2:
            move.extend(random.sample(valid_moves, 2))
                
        else:
            move.extend(valid_moves)  # If not enough moves, just use what's available

        move = pad_or_truncate(move, 3)
                      
    # Jaqen => [companion_card, location, location, companion_card]
    elif choices == 3:
        valid_moves = get_valid_jon_sandor_jaqan(cards)

        if len(valid_moves) >= 2 and len(companion_cards) > 0:
            move.extend(random.sample(valid_moves, 2))
            move.append(random.choice(list(companion_cards.keys())))
                
        else:
            # If there aren't enough moves or companion cards, just return what's possible
            move.extend(valid_moves)
            move.append(random.choice(list(companion_cards.keys())) if companion_cards else None)

        move = pad_or_truncate(move, 4)
        
    return move

def simulated_annealing_companion(cards, player1, player2, companion_cards):
    """
    Simulated annealing algorithm to find the optimal move when choose_companion==true
    """

    current_companion = generate_random_companion(cards, companion_cards)
    print(current_companion)
    current_score = evaluate_state(cards, player1, player2)
    temperature = 100
    cooling_rate = 0.99

    while temperature > 1:
        neighbor = generate_neighbor_companion(cards, companion_cards, current_companion)
        print(neighbor)
        new_score = evaluate_state(cards, player1, player2)
        if new_score > current_score or math.exp(-abs(new_score - current_score) / temperature) > random.random():
            current_companion = neighbor
            current_score = new_score
        temperature *= cooling_rate

    return current_companion

def get_move(cards, player1, player2, companion_cards, choose_companion):
    """
    Main function to return the move for the agent.
    """
    if choose_companion:
        if companion_cards:
            return simulated_annealing_companion(cards, player1, player2, companion_cards)
        else:
            return []
    else:
        return simulated_annealing_normal(cards, player1, player2)
