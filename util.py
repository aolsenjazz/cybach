def key_for_highest_value(item_map):
    high_score = -1000000
    winner = None
    for key in item_map.keys():
        if item_map[key] > high_score:
            winner = key
            high_score = item_map[key]
    return winner