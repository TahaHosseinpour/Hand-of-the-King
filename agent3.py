import random
import math
import logging
from copy import deepcopy

# python main.py --player1 agent3 --player2 random_agent
# python main_tester_new.py --player1 agent3 --player2 random_agent

COMPANION_NOISE_RANGE = 1
LOCATION_NOISE_RANGE = 10
REPETITIONS_AT_EACH_TEMPERATURE = 5

#---------(Prerequisite Functions)------------------------------------------------------------------------------------------------------------------------------

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

def make_move(cards, move, player):
    varys_location = find_varys(cards)
    varys_row, varys_col = varys_location // 6, varys_location % 6
    move_row, move_col = move // 6, move % 6
    selected_card = find_card(cards, move)

    if selected_card.get_name() == 'Varys':
        return cards, player

    removing_cards = []

    for i in range(len(cards)):
        if cards[i].get_name() == 'Varys':
            varys_index = i
            continue

        # If the card is between Varys and the selected card and has the same house as the selected card
        if varys_row == move_row and varys_col < move_col:
            if cards[i].get_location() // 6 == varys_row and varys_col < cards[i].get_location() % 6 < move_col and \
                    cards[i].get_house() == selected_card.get_house():
                removing_cards.append(cards[i])

                # Add the card to the player's cards
                player.add_card(cards[i])

        elif varys_row == move_row and varys_col > move_col:
            if cards[i].get_location() // 6 == varys_row and move_col < cards[i].get_location() % 6 < varys_col and \
                    cards[i].get_house() == selected_card.get_house():
                removing_cards.append(cards[i])

                # Add the card to the player's cards
                player.add_card(cards[i])

        elif varys_col == move_col and varys_row < move_row:
            if cards[i].get_location() % 6 == varys_col and varys_row < cards[i].get_location() // 6 < move_row and \
                    cards[i].get_house() == selected_card.get_house():
                removing_cards.append(cards[i])

                # Add the card to the player's cards
                player.add_card(cards[i])

        elif varys_col == move_col and varys_row > move_row:
            if cards[i].get_location() % 6 == varys_col and move_row < cards[i].get_location() // 6 < varys_row and \
                    cards[i].get_house() == selected_card.get_house():
                removing_cards.append(cards[i])

                # Add the card to the player's cards
                player.add_card(cards[i])

    # Add the selected card to the player's cards

    player.add_card(selected_card)

    # Set the location of Varys
    cards[varys_index].set_location(move)

    # Remove the cards
    for card in removing_cards:
        cards.remove(card)

    # Remove the selected card
    cards.remove(selected_card)

    # Return the selected card's house
    return cards, player

def find_card(cards, location):
    '''
    This function finds the card at the location.

    Parameters:
        cards (list): list of Card objects
        location (int): location of the card

    Returns:
        card (Card): card at the location
    '''

    for card in cards:
        if card.get_location() == location:
            return card

def set_banners(player1, player2, last_house, last_turn):
    '''
    This function sets the banners for the players.

    Parameters:
        player1 (Player): player 1
        player2 (Player): player 2
        last_house (str): house of the last chosen card
        last_turn (int): last turn of the player
    '''

    # Get the cards of the players
    player1_cards = player1.get_cards()
    player2_cards = player2.get_cards()

    # Get the banners of the players
    player1_banners = player1.get_banners()
    player2_banners = player2.get_banners()

    for house in player1_cards.keys():
        # Flag to keep track of the selected player
        selected_player = None

        # The player with the more cards of a house gets the banner
        if len(player1_cards[house]) > len(player2_cards[house]):
            # Give the banner to player 1
            selected_player = 1

        elif len(player2_cards[house]) > len(player1_cards[house]):
            # Give the banner to player 2
            selected_player = 2

        # If the number of cards is the same, the player who chose the last card of that house gets the banner
        else:
            if last_house == house:
                if last_turn == 1:
                    # Give the banner to player 1
                    selected_player = 1

                else:
                    # Give the banner to player 2
                    selected_player = 2

            else: # If the last card was not of the same house
                if player1_banners[house] > player2_banners[house]: # If player 1 has more banners of the house
                    selected_player = 1
                
                elif player2_banners[house] > player1_banners[house]: # If player 2 has more banners of the house
                    selected_player = 2

        # If player 1 should get the banner
        if selected_player == 1:
            # Give the banner to player 1
            player1.get_house_banner(house)
            player2.remove_house_banner(house)

        elif selected_player == 2:
            # Give the banner to player 2
            player1.remove_house_banner(house)
            player2.get_house_banner(house)

def evaluate_state(player1, player2):
    """
    Evaluates the board state and returns a heuristic score.
    """

    player1_banners = player1.get_banners()
    player2_banners = player2.get_banners()

    player1_score = sum(player1_banners.values())
    player2_score = sum(player2_banners.values())

    if player1_score != player2_score:
        return (player1_score - player2_score) * 10
    else:
        if player1_banners['Stark'] > player2_banners['Stark']:
            return player1_banners['Stark'] - player2_banners['Stark']
        
        elif player2_banners['Stark'] > player1_banners['Stark']:
            return player1_banners['Stark'] - player2_banners['Stark']
        
        elif player1_banners['Greyjoy'] > player2_banners['Greyjoy']:
            return player1_banners['Greyjoy'] - player2_banners['Greyjoy']
        
        elif player2_banners['Greyjoy'] > player1_banners['Greyjoy']:
            return player1_banners['Greyjoy'] - player2_banners['Greyjoy']
        
        elif player1_banners['Lannister'] > player2_banners['Lannister']:
            return player1_banners['Lannister'] - player2_banners['Lannister']
        
        elif player2_banners['Lannister'] > player1_banners['Lannister']:
            return player1_banners['Lannister'] - player2_banners['Lannister']
        
        elif player1_banners['Targaryen'] > player2_banners['Targaryen']:
            return player1_banners['Targaryen'] - player2_banners['Targaryen']
        
        elif player2_banners['Targaryen'] > player1_banners['Targaryen']:
            return player1_banners['Targaryen'] - player2_banners['Targaryen']
        
        elif player1_banners['Baratheon'] > player2_banners['Baratheon']:
            return player1_banners['Baratheon'] - player2_banners['Baratheon']
        
        elif player2_banners['Baratheon'] > player1_banners['Baratheon']:
            return player1_banners['Baratheon'] - player2_banners['Baratheon']
        
        elif player1_banners['Tyrell'] > player2_banners['Tyrell']:
            return player1_banners['Tyrell'] - player2_banners['Tyrell']
        
        elif player2_banners['Tyrell'] > player1_banners['Tyrell']:
            return player1_banners['Tyrell'] - player2_banners['Tyrell']
        
        elif player1_banners['Tully'] > player2_banners['Tully']:
            return player1_banners['Tully'] - player2_banners['Tully']
        
        elif player2_banners['Tully'] > player1_banners['Tully']:
            return player1_banners['Tully'] - player2_banners['Tully']

    return player1_score - player2_score

#---------(Normal Game Functions)------------------------------------------------------------------------------------------------------------------------------

def generate_random_move_and_simulate(cards, player1, player2, depth):
    """
    Generates a random move for simulated annealing when choose_companion==false
    """
    new_cards = deepcopy(cards)
    new_player1 = deepcopy(player1)
    new_player2 = deepcopy(player2)
    neighbor = []

    for i in range(depth):

        valid_moves = get_valid_moves(new_cards)

        # end of the game
        if len(valid_moves) == 0:
            break

        random_move = random.choice(valid_moves)
        neighbor.append(random_move)

        for card in new_cards:
            if card.get_location() == random_move:
                last_house = card.get_house()
        
        if i%2 == 0:
            new_cards, new_player1 = make_move(new_cards, random_move, new_player1)
            set_banners(new_player1, new_player2, last_house, 1)

        elif i%2 == 1:
            new_cards, new_player2 = make_move(new_cards, random_move, new_player2)
            set_banners(new_player1, new_player2, last_house, 2)

    return neighbor, new_cards, new_player1, new_player2

def generate_neighbor_move_and_simulate(cards, player1, player2, current_move, current_possibility):
    """
    Generates a neighboring move for simulated annealing when choose_companion==false
    """
    new_cards = deepcopy(cards)
    new_player1 = deepcopy(player1)
    new_player2 = deepcopy(player2)
    neighbor = []
    
    for i in range(len(current_move)):

        valid_moves = get_valid_moves(new_cards)

        # end of the game
        if len(valid_moves) == 0:
            break

        new_move = 0
        if current_move[i] in valid_moves:

            if random.random() < current_possibility[i]:
                move_index = valid_moves.index(current_move[i])
                random_noise = random.randint( -LOCATION_NOISE_RANGE, LOCATION_NOISE_RANGE )
                new_move_index = max(0, min(move_index + random_noise, len(valid_moves)-1))
                new_move = valid_moves[new_move_index]

            else:
                new_move = current_move[i]

        else:
            new_move = random.choice(valid_moves)
        
        neighbor.append(new_move)

        for card in new_cards:
            if card.get_location() == new_move:
                last_house = card.get_house()

        if i%2 == 0:
            new_cards, new_player1 = make_move(new_cards, new_move, new_player1)
            set_banners(new_player1, new_player2, last_house, 1)

        elif i%2 == 1:
            new_cards, new_player2 = make_move(new_cards, new_move, new_player2)
            set_banners(new_player1, new_player2, last_house, 2)

    return neighbor, new_cards, new_player1, new_player2

def simulated_annealing_normal(cards, player1, player2, depth):
    """
    Simulated annealing algorithm to find the optimal move when choose_companion==false
    """
    possibility_min = 0.5
    current_possibility = [(possibility_min+i*(0.4/(depth-1))) for i in range(depth)] if depth > 1 else [0.9]
    temperature = 100
    cooling_rate = 0.99

    # current_move = [random.choice(range(36)) for _ in range(depth)]
    # simulated_cards, simulated_player1, simulated_player2 = simulate_move(cards, current_move, player1, player2)
    # current_score = evaluate_state(simulated_player1, simulated_player2)

    current_move, simulated_cards, simulated_player1, simulated_player2 = generate_random_move_and_simulate(cards, player1, player2, depth)
    current_score = evaluate_state(simulated_player1, simulated_player2)

    # print("current_move = ",current_move, current_score, current_move[0] in get_valid_moves(cards))

    while temperature > 1:
        for _ in range(REPETITIONS_AT_EACH_TEMPERATURE):
            
            # neighbor = generate_neighbor_move(current_move, current_possibility)
            # new_simulated_cards, new_simulated_player1, new_simulated_player2 = simulate_move(cards, neighbor, player1, player2)
            
            # # invalid move (couldn't simulate)
            # if new_simulated_cards == None:
            #     continue

            neighbor, new_simulated_cards, new_simulated_player1, new_simulated_player2 = generate_neighbor_move_and_simulate(cards, player1, player2, current_move, current_possibility)
            new_score = evaluate_state(new_simulated_player1, new_simulated_player2)

            # print("at temperature = ",temperature, " neighbor = ",neighbor, new_score, neighbor[0] in get_valid_moves(cards))

            if new_score > current_score or math.exp(-abs(new_score - current_score) / temperature) > random.random():
                current_move = neighbor
                current_score = new_score

        temperature *= cooling_rate

        # reducing the likelihood of applying noise over time (exploration to exploitation)
        possibility_min = 0.1 + 0.4 * (temperature/100)
        current_possibility = [(possibility_min+i*(0.4/(depth-1))) for i in range(depth)] if depth > 1 else [0.9]

    # print("best = ",current_move, current_score)
    return current_move

#---------(Game Functions with Companion Cards)------------------------------------------------------------------------------------------------------------------------------

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

def change_or_generate_location( cards, current_move, valid_moves, move, index):

    # current_move has parameter index => random change it
    if len(current_move) >= index+1:

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

def simulated_annealing_companion(cards, player1, player2, companion_cards):
    """
    Simulated annealing algorithm to find the optimal move when choose_companion==true
    """

    current_companion = generate_random_companion(cards, companion_cards)
    current_score = evaluate_state(player1, player2)
    temperature = 100
    cooling_rate = 0.99

    while temperature > 1:
        neighbor = generate_neighbor_companion(cards, companion_cards, current_companion)
        new_score = evaluate_state(player1, player2)
        if new_score > current_score or math.exp(-abs(new_score - current_score) / temperature) > random.random():
            current_companion = neighbor
            current_score = new_score
        temperature *= cooling_rate

    return current_companion

#---------(Main Function)------------------------------------------------------------------------------------------------------------------------------

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
        return simulated_annealing_normal(cards, player1, player2, depth=5)[0]
