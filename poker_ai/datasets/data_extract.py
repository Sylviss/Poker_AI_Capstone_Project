import re
# import json

pattern = r"PokerStars Hand #(\d+): Hold'em No Limit \(50/100\) - (.+)\n"
player_pattern = r'Seat (\d+): (\S+) \((\d+) in chips\)'
small_blind_pattern = r'(\S+): posts small blind (\d+)\n'
big_blind_pattern = r'(\S+): posts big blind (\d+)\n'
turn_pattern = r' \*\*\*(.*?)\*\*\* '
hand_pattern = r'Dealt to (\S+) \[(\S+) (\S+)\]'
p_pattern = r'(\S+): (.*?)\n'
winner_pattern = r'(\S+) collected'
board_pattern = r'Board \[(.*?)\]'
# button_pattern = r'Seat #(\d+)'


def single_parse_data(game_data: str) -> dict:
    gameid, timestamp = re.findall(pattern, game_data)[0]

    # I don't even know what's 'button'
    # button = re.findall(button_pattern, data)[0]

    # Extract player names, their seats and chips
    player_matches = re.findall(player_pattern, game_data)
    num_players = len(player_matches)
    players = [{
        'seat': int(match[0]),
        'player_name': match[1],
        'start_money': int(match[2])
    } for match in player_matches]
    # players_name = [match[1] for match in player_matches]
    
    # Extract blind info
    small_blind, small_blind_value = re.findall(small_blind_pattern, game_data)[0]
    big_blind, big_blind_value = re.findall(big_blind_pattern, game_data)[0]
    
    # Extract all turn
    turns = re.findall(turn_pattern, game_data, flags=re.DOTALL)
    
    # Extract the hand of players
    hand_matches = re.findall(hand_pattern, turns[0])
    for i in range(num_players):
        players[i]['player_hand'] = [hand_matches[i][1], hand_matches[i][2]]
    
    # Extract actions
    actions = dict()
    num_cards_on_board = (0, 3, 4, 5)
    # action_denote = {
    #     'all-in': 1,
    #     'checks': 2,
    #     'calls': 3,
    #     'raises': 4,
    #     'folds': 5
    # }
    # out of game: -1
    simple_action = {
        'checks': 2,
        'calls': 3,
        'folds': 5
    }
    raise_variations = ['bets', 'raises']
    # old code below
    # for turn in range(4):
    #     try:
    #         turns[turn]
    #     except IndexError:
    #         actions[num_cards_on_board[turn]] = None
    #         continue

    #     temp_lst = []
    #     for p in players_name:
    #         p_pattern = p + r': (.*?)\n'
    #         p_match = re.findall(p_pattern, turns[turn])
    #         if p_match:
    #             if len(p_match) == 1:
    #                 cur_action = p_match[0]
    #                 for k, v in action_denote.items():
    #                     if 'all-in' in cur_action:
    #                         temp_lst.append([p, [[1, 0]]])
    #                         break
    #                     elif cur_action.startswith(k) and v in (2, 3, 5):
    #                         temp_lst.append([p, [[v, 0]]])
    #                         break
    #                     elif 'bets' in cur_action or 'raises' in cur_action:
    #                         a = re.findall(r'(\S+) (\d+)', cur_action)[0]
    #                         temp_lst.append([p, [4, [int(a[1])]]])
    #                         break
    #             else:
    #                 # cases when player took more than 1 action in game
    #                 # haven't implemented because of confusions
    #                 pass
    #         else:
    #             temp_lst.append([p, [[-1, 0]]])

    #     actions[num_cards_on_board[turn]] = temp_lst

    # new code: just stores all the moves in a list
    for turn in range(4):
        try:
            turns[turn]
        except IndexError:
            actions[num_cards_on_board[turn]] = None
            continue

        temp_lst = []
        # p_pattern = r'(\S+): (\S+) (\d+) and is (\S+).*?\n'
        # p_pattern_2 = r'(\S+): (\S+) (\d+).*?\n'
        # p_pattern = f'({p_pattern})|({p_pattern_2})|({p_pattern_3})'
        p_match = re.findall(p_pattern, turns[turn])
        for p_action in p_match:
            if 'all-in' in p_action[1]:
                temp_lst.append([p_action[0], [1, 0]])
            else:
                cur_action = p_action[1].split()
                if cur_action[0] in simple_action:
                    temp_lst.append([p_action[0], [simple_action[cur_action[0]], 0]])
                elif cur_action[0] in raise_variations:
                    temp_lst.append([p_action[0], [4, int(cur_action[1])]])

        actions[num_cards_on_board[turn]] = temp_lst

    # Extract win money, and winner(s)
    winners = re.findall(winner_pattern, turns[-1])
    win_money = int(re.search(r'Total pot (\d+)', game_data).group(1))

    # Extract cards on beard
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

    # For checking
    print(*parsed_data, sep='\n\n')

    return parsed_data

if __name__=="__main__":
    main()
