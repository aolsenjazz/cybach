def key_for_highest_value(item_map):
    return max(item_map.iterkeys(), key=(lambda key: item_map[key]))