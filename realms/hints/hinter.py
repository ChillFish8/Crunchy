import random

HINTS = [
    'You can increase your characters power by leveling them up.',
    'Your character can loose power and other stats if they run out of Food.',
    'Treats increase the chances of gaining bonus hearts.',
]


def get_hint():
    return random.choice(HINTS)
