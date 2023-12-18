import re
import json

pattern = r"PokerStars Hand #(\d+): Hold'em No Limit \(50/100\) - (.+)\n"
player_pattern = r'Seat (\d+): (\S+) \((\d+) in chips\)'
small_blind_pattern = r'(\S+): posts small blind (\d+)\n'
big_blind_pattern = r'(\S+): posts big blind (\d+)\n'
turn_pattern = r' \*\*\*(.*?)\*\*\* '
hand_pattern = r'Dealt to (\S+) \[(\S+) (\S+)\]'
p_pattern = r'(\S+): (.*?)\n'
winner_pattern = r'(\S+) collected'
board_pattern = r'Board \[(.*?)\]'
uncalled_bet_pattern = r'Uncalled bet \((\d+)\) returned to (\S+)\n'
# button_pattern = r'Seat #(\d+)'


def single_parse_data(game_data: str) -> dict:
    gameid, timestamp = re.findall(pattern, game_data)[0]

    # button = re.findall(button_pattern, data)[0]

    # Extract player names, their seats and chips
    player_matches = re.findall(player_pattern, game_data)
    num_players = len(player_matches)
    players = [{
        'seat': int(match[0]),
        'player_name': match[1],
        'start_money': float(match[2])
    } for match in player_matches]
    cur_pot = 0
    after_money = {match[1]: float(match[2]) for match in player_matches}
    
    # Extract blind info
    small_blind, small_blind_value = re.findall(small_blind_pattern, game_data)[0]
    big_blind, big_blind_value = re.findall(big_blind_pattern, game_data)[0]
    cur_pot += float(small_blind_value) + float(big_blind_value)
    after_money[big_blind] -= float(big_blind_value)
    after_money[small_blind] -= float(small_blind_value)
    
    # Extract all turn
    turns = re.findall(turn_pattern, game_data, flags=re.DOTALL)
    
    # Extract the hand of players
    hand_matches = re.findall(hand_pattern, turns[0])
    for i in range(num_players):
        players[i]['player_hand'] = [hand_matches[i][1], hand_matches[i][2]]
    
    # Extract actions
    actions = dict()
    num_cards_on_board = (0, 3, 4, 5)
    # action_denote: {
    #     'all-in': 1,
    #     'checks': 2,
    #     'calls': 3,
    #     'raises': 4,
    #     'folds': 5,
    #     'out of game': -1
    # }
    simple_action = {
        'checks': 2,
        'folds': 5
    }
    raise_variations = ['bets', 'raises']
    
    # Stores the move in a list
    for turn in range(4):
        cur_call_players = {match[1]: 0 for match in player_matches}
        if turn == 0:
            cur_call = float(big_blind_value)
            cur_call_players[small_blind] += float(small_blind_value)
            cur_call_players[big_blind] += float(big_blind_value)
        else:
            cur_call = 0

        try:
            turns[turn]
        except IndexError:
            actions[num_cards_on_board[turn]] = None
            continue

        temp_lst = []
        p_match = re.findall(p_pattern, turns[turn])
        for p_action in p_match:
            cur_action = p_action[1].split()
            if 'all-in' == cur_action[-1]:
                temp_lst.append([p_action[0], [1, 0]])
                if cur_action[0] != 'calls':
                    cur_call += float(cur_action[1])
                delta_money = cur_call - cur_call_players[p_action[0]]
                cur_call_players[p_action[0]] = cur_call
                cur_pot += delta_money
                after_money[p_action[0]] -= delta_money
            else:
                if cur_action[0] in simple_action:
                    temp_lst.append([p_action[0], [simple_action[cur_action[0]], 0]])
                elif cur_action[0] in raise_variations:
                    temp_lst.append([p_action[0], [4, float(cur_action[1])]])
                    cur_call += float(cur_action[1])
                    delta_money = cur_call - cur_call_players[p_action[0]]
                    cur_call_players[p_action[0]] = cur_call
                    cur_pot += delta_money
                    after_money[p_action[0]] -= delta_money
                elif cur_action[0] == 'calls':
                    temp_lst.append([p_action[0], [3, 0]])
                    delta_money = cur_call - cur_call_players[p_action[0]]
                    cur_call_players[p_action[0]] = cur_call
                    cur_pot += delta_money
                    after_money[p_action[0]] -= delta_money

        actions[num_cards_on_board[turn]] = temp_lst

    # Extract win money, and winner(s)
    uncalled_bet_match = re.search(uncalled_bet_pattern, game_data)
    if uncalled_bet_match:
        uncalled_bet = float(uncalled_bet_match.group(1))
        return_bet_to = uncalled_bet_match.group(2)
        after_money[return_bet_to] += uncalled_bet
        cur_pot -= uncalled_bet

    winners = re.findall(winner_pattern, turns[-1])
    for winner in winners:
        after_money[winner] += cur_pot / len(winners)
    
    for k, v in after_money.items():
        for i in range(num_players):
            if k == players[i]['player_name']:
                players[i]['after_money'] = v
                break
    
    for i in range(num_players):
        players[i]['delta_money'] = players[i]['after_money'] - players[i]['start_money']

    # Extract cards on board
    board_match = re.search(board_pattern, game_data)
    if board_match:
        board = board_match.group(1).split()
    else:
        board = []


    parsed_data = {
        'gameid': int(gameid),
        # 'timestamp': timestamp,
        'players': players,
        'small_blind': small_blind,
        'small_blind_value': float(small_blind_value),
        'big_blind': big_blind,
        'big_blind_value': float(big_blind_value),
        'actions': actions,
        'winners': winners,
        'board': board
    }

    return parsed_data


def parse_data(data: str) -> list:
    splited_data = data.split(sep='\n\n')
    result = []
    for d in splited_data:
        result.append(single_parse_data(d.strip()))
    return result

def main():
    with open('poker_ai/datasets/pluribus.txt', 'r') as f:
        data = f.read().strip()
    parsed_data = parse_data(data)

    with open('poker_ai/datasets/parsed_data.json', 'w') as f2:
        json.dump(parsed_data, f2, indent=4)
    print('Done')
    return parsed_data

if __name__=="__main__":
    main()
