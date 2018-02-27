def is_flicker(current, last, two_ago):
    if current.is_note() and last.is_note() and two_ago.is_note():
        return current.pitch() == two_ago.pitch()