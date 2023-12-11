import re
import json

def parse_data(game_data: str) -> dict:
    pattern = r"PokerStars Hand #(\d+): Hold'em No Limit \(50/100\) - (.+)\n"
    gameid, timestamp = re.findall(pattern, game_data)[0]

    # I don't even know what's 'button'
    # button_pattern = r'Seat #(\d+)'
    # button = re.findall(button_pattern, data)[0]

    # Extract player names, their seats and chips
    player_pattern = r'Seat (\d+): (\S+) \((\d+) in chips\)'
    player_matches = re.findall(player_pattern, data)
    num_players = len(player_matches)
    players = [{
        'seat': int(match[0]),
        'player_name': match[1],
        'start_money': int(match[2])
    } for match in player_matches]
    players_name = [match[1] for match in player_matches]
    
    # Extract blind info
    small_blind, small_blind_value = re.findall(
        r'(\S+): posts small blind (\d+)\n', game_data)[0]
    big_blind, big_blind_value = re.findall(
        r'(\S+): posts big blind (\d+)\n', game_data)[0]
    
    # Extract all turn
    turn_pattern = r' \*\*\*(.*?)\*\*\* '
    turns = re.findall(turn_pattern, game_data, flags=re.DOTALL)
    
    # Extract the hand of players
    hand_pattern = r'Dealt to (\S+) \[(\S+) (\S+)\]'
    hand_matches = re.findall(hand_pattern, turns[0])
    for i in range(num_players):
        players[i]['player_hand'] = [hand_matches[i][1], hand_matches[i][2]]
    
    # Extract actions
    actions = dict()
    num_cards_on_board = (0, 3, 4, 5)
    action_denote = {
        'all-in': 1,
        'checks': 2,
        'calls': 3,
        'raises': 4,
        'folds': 5
    }
    # out of game: -1
    for turn in range(4):
        try:
            turns[turn]
        except IndexError:
            actions[num_cards_on_board[turn]] = None
            continue

        temp_lst = []
        for p in players_name:
            p_pattern = p + r': (.*?)\n'
            p_match = re.findall(p_pattern, turns[turn])
            if p_match:
                if len(p_match) == 1:
                    cur_action = p_match[0]
                    for k, v in action_denote.items():
                        if 'all-in' in cur_action:
                            temp_lst.append([p, [[1, 0]]])
                            break
                        elif cur_action.startswith(k) and v in (2, 3, 5):
                            temp_lst.append([p, [[v, 0]]])
                            break
                        elif 'bets' in cur_action or 'raises' in cur_action:
                            a = re.findall(r'(\S+) (\d+)', cur_action)[0]
                            temp_lst.append([p, [4, [int(a[1])]]])
                            break
                else:
                    # cases when player took more than 1 action in game
                    # haven't implemented because of confusions
                    pass
            else:
                temp_lst.append([p, [[-1, 0]]])

        actions[num_cards_on_board[turn]] = temp_lst
    
    # Extract win money, and winner(s)
    winner_pattern = r'(\S+) collected'
    winners = re.findall(winner_pattern, turns[-1])
    win_money = int(re.search(r'Total pot (\d+)', game_data).group(1))

    # Extract cards on beard
    board_pattern = r'Board \[(.*?)\]'
    board_match = re.search(board_pattern, game_data)
    if board_match:
        board = board_match.group(1).split()
    else:
        board = []


    parsed_data = {
        'gameid': int(gameid),
        'timestamp': timestamp,
        'players': players,
        'small_blind': small_blind,
        'small_blind_value': int(small_blind_value),
        'big_blind': big_blind,
        'big_blind_value': int(big_blind_value),
        'actions': actions,
        'win_money': win_money,
        'winners': winners,
        'board': board
    }

    return parsed_data


with open('poker_ai/datasets/small_dataset.txt', 'r') as f:
    data = f.read().strip()
parsed_data = parse_data(data)

# For checking, or just use vscode's debugger
print(json.dumps(parsed_data, indent=4))