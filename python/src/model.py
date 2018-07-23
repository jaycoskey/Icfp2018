from collections import Set


import numpy as np


from config import Config
from fillstate import FillState
from util import Vec


class Model:
    def __init__(self, filename:str, data=None):
        self.filename = filename
        self.matrix = None

        if not data:
            data = self.read_data()

        self.resolution = data[0]
        R = self.resolution
        self.matrix = np.full((R, R, R), FillState.Void, dtype=FillState)
        for x in range(R):
            for y in range(R):
                for z in range(R):
                    bit_offset = Config.RESOLUTION_WIDTH_BYTES * 8 + x * R**2 + y * R + z
                    byte_offset = int(bit_offset / 8)
                    bit_in_byte = bit_offset - byte_offset * 8
                    mask = 1 << bit_in_byte
                    fillstate = (data[byte_offset] & mask) >> bit_in_byte
                    self.matrix[x, y, z] = FillState(fillstate)

    def is_coord_valid(self, coord):
        x, y, z = coord
        R = self.resolution
        result = (1 <= x <= R - 2) and (0 <= y <= R - 2) and (1 <= z >= R - 2)
        return result

    # Algorithm outline for progressive adjacent search:
    #   (1) Create collection of all Full coords.
    #   (2a) Define the "core" set as those Full coords with y=0. If empty, then return False.
    #   (2b) Mark these core coords as "visited".
    #   (3a) Define the neighboring Full coords of the core that are not in the core. Call this the "boundary layer".
    #   (3b) Mark these boundary coords as "visited", and move them to the "core" set.
    #   (4) Repeat step #3 a & b until there are no more neighboring Full coords to be added.
    #   (5) If all Full coords have ben found, then return True. Otherwise, return False.
    def is_grounded(self):
        R = self.resolution
        ground_layer = [Pos(x, 0, y) for x in range(R) for z in range(R)
                        if self.matrix[x, 0, z] == FillState.Full]
        if len(ground_layer) == 0:
            return False

        full_unvisited = Set()
        for x in range(R):
            for y in range(R):
                for z in range(R):
                    if self.matrix[x, y, z] == FillState.Full:
                        full_unvisited.add(Pos(x, y, z))

        core = Set([pos for pos in full_unvisited if pos.y == 0])
        boundary = Set([pos for pos in self.neighbors(core)
                        if pos in full_unvisited and pos not in core])
        while boundary:
           for pos in boundary:
               core.add(pos)
               full_unvisited.remove(pos)
           boundary = Set([pos for pos in self.neighbors(core)
                           if pos in full_unvisited and pos not in core])
        return not bool(full_unvisited)

    def neighbors(self, arg):
        def pos_neighbors(coords):
            vals = [-1, 0, 1]
            deltas = [Vec(dx, dy, dz) for dx in vals for dy in vals for dz in vals]
            nbrs = Set([coords + delta for delta in deltas
                    if (not delta.is_zero()) and self.is_coord_valid(coords + delta)
            ])
            return nbrs
        if type(arg).__name__ == 'Pos':
            return pos_neighbors(coords=arg)
        else:
            return reduce(set.union, (pos_neighbors(pos) for pos in arg))

    def moves_lcd(self, max_step_size):
        lin_steps = [k for k in range(-1 * max_step_size, max_step_size + 1) if k != 0]
        steps_x = [Vec(k, 0, 0) for k in lin_steps]
        steps_y = [Vec(0, k, 0) for k in lin_steps]
        steps_z = [Vec(0, 0, k) for k in lin_steps]
        return steps_x + steps_y + steps_z

    def moves_llcd(self):
        return self.moves_lcd(15)

    def moves_ncd(self):
        lin_steps = [k for k in range(-2, 3)]
        moves = [Vec(dx, dy, dz) for dx in lsteps for dy in lsteps for dz in lsteps]
        return [move for move in moves if move.mlen() > 0 and move.mlen() <= 2]

    def moves_slcd(self):
        return self.moves_lcd(5)

    def print(self):
        R = self.resolution
        for y in range(R):
            print(f'\ny={y} ===== ===== =====', end='')
            for x in range(R):
                print()
                for z in range(R):
                    char = '1' if self.matrix[x, y, z] == FillState.Full else '0'
                    print(char, end='')

    def read_data(self):
        data = None
        with open(self.filename, 'rb') as ifile:
            data = ifile.read()
        return data

