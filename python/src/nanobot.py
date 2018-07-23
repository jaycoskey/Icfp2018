# The Lightning round's initial nanobot has 1 + 19 seeds
# The Full round's initial nanobot has 1 + 39 seeds
class Nanobot:
    def __init__(self, init_pos, seeds=None):
        self.bid = seeds[0]
        self.is_active = True
        self.pos = init_pos
        self.seeds = seeds[1:]

