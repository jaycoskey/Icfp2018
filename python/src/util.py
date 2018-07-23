import os
from os.path import join


class NanoException(Exception):
    pass


class Pos:
    def __init__(self, x, y, z):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

    def __add__(self, vec):
        vec_type = type(vec).__name__
        Util.nano_assert(vec_type == 'Vec', 'Type mismatch in Pos addition')
        return Pos(self.x + vec.x, self.y + vec.y, self.z + vec.z)

    def __iadd__(self, vec):
        vec_type = type(vec).__name__
        Util.nano_assert(vec_type == 'Vec', 'Type mismatch in Pos incremental addition')
        self.x += vec.x
        self.y += vec.y
        self.z += vec.z

    def __sub__(self, pos):
        pos_type = type(pos).__name__
        Util.nano_assert(pos_type == 'Pos', 'Type mismatch in Pos subtraction')
        return Vec(self.x - pos.x, self.y - pos.y, self.z - pos.z)

    def is_origin(self):
        return self.x == 0 and self.y == 0 and self.z == 0


class Util:
    @staticmethod
    def ICFP_TRACE_DIR():
        if '_ICFP_TRACE_DIR' not in dir(Util):
            Util._ICFP_TRACE_DIR = join(os.environ['PROJECT_DIR'], '../dfltTracesL')
        return Util._ICFP_TRACE_DIR

    @staticmethod
    def MODEL_DIR():
        if '_MODEL_DIR' not in dir(Util):
            Util._MODEL_DIR = join(os.environ['PROJECT_DIR'], '../problemsL')
        return Util._MODEL_DIR

    @staticmethod
    def MY_TRACE_DIR():
        if '_MY_TRACE_DIR' not in dir(Util):
            Util._MY_TRACE_DIR = join(os.environ['PROJECT_DIR'], '../my_solutions')
        return Util._MY_TRACE_DIR

    @staticmethod
    def byte_count(clsname):
        count = None
        if clsname == 'CmdHalt':
            count = 1
        elif clsname == 'CmdFill':
            count = 1
        elif clsname == 'CmdFission':
            count = 2
        elif clsname == 'CmdFlip':
            count = 1
        elif clsname == 'CmdFusionP':
            count = 1
        elif clsname == 'CmdFusionS':
            count = 1
        elif clsname == 'CmdGFill':
            count = 4
        elif clsname == 'CmdGVoid':
            count = 1
        elif clsname == 'CmdLMove':
            count = 2
        elif clsname == 'CmdSMove':
            count = 2
        elif clsname == 'CmdVoid':
            count = 1
        elif clsname == 'CmdWait':
            count = 1
        else:
            raise Util.NanoException('Unrecognized command type')
        return count

    @staticmethod
    def chunks(size, items):
        for k in range(0, len(items), size):
            yield items[k:k+size]

    @staticmethod
    def decode_fd(x, y, z):
        return (x - 30, y - 30, z - 30)

    @staticmethod
    def decode_lld(a, i):
        dx = 0
        dy = 0
        dz = 0
        if a == 1:    # dx != 0
            dx = i - 15
        elif a == 2:  # dy != 0
            dy = i - 15
        elif a == 3:  # dz != 0
            dz = i - 15
        else:
            raise Util.NanoException('decode_sld: Invalid value of a')
        return Vec(dx, dy, dz)

    @staticmethod
    def decode_nd(b5):
        z_enc = b5 % 3
        b5 = (b5 - z_enc) / 3
        y_enc = b5 % 3
        b5 = (b5 - y_enc) / 3
        x_enc = b5 % 3

        dz = z_enc - 1
        dy = y_enc - 1
        dx = x_enc - 1
        return Vec(dx, dy, dz)

    @staticmethod
    def decode_sld(a, i):
        dx = 0
        dy = 0
        dz = 0
        if a == 1:    # dx != 0
            dx = i - 5
        elif a == 2:  # dy != 0
            dy = i - 5
        elif a == 3:  # dz != 0
            dz = i - 5
        else:
            raise Util.NanoException('decode_sld: Invalid value of a')
        return Vec(dx, dy, dz)

    @staticmethod
    def encode_fd(delta):
        return delta + Vec(30, 30, 30)

    # Long linear coordinate difference
    @staticmethod
    def encode_lld(delta):
        if delta.x != 0:
            a = 1
            i = delta.x + 15
        elif delta.y != 0:
            a = 2
            i = delta.y + 15
        elif delta.z != 0:
            a = 3
            i = delta.z + 15
        else:
            raise Util.NanoException('Long linear coordinate difference violation')
        return a, i

    # Near coordinate difference
    @staticmethod
    def encode_ncd(delta):
        result = (delta.x + 1) * 9 + (delta.y + 1) * 3 + (delta.z + 1)
        return result

    # Short linear coordinate difference
    @staticmethod
    def encode_sld(delta):
        if delta.x != 0:
            a = 1
            i = delta.x + 5
        elif delta.y != 0:
            a = 2
            i = delta.y + 5
        elif delta.z != 0:
            a = 3
            i = delta.z + 5
        else:
            raise Util.NanoException('Short linear coordinate difference violation')
        return a, i

    @staticmethod
    def log_chars(n):
        if n % 1_000_000 == 0:
            return 'M\n'
        if n % 500_000 == 0:
            return 'D\n'
        if n % 100_000 == 0:
            banner = '=' * 20
            return f'C\n{banner}{n}{banner}\n'
        if n % 50_000 == 0:
            return 'L\n'
        if n % 10_000 == 0:
            return 'X\n'
        if n % 5_000 == 0:
            return 'V\n'

        if n % 1000 == 0:
            return 'm\n'
        elif n % 500 == 0:
            return 'd\n'
        elif n % 100 == 0:
            return 'c\n'
        elif n % 50 == 0:
            return 'l'
        elif n % 10 == 0:
            return 'x'
        elif n % 5 == 0:
            return 'v'
        else:
            return '.'

    @staticmethod
    def nano_assert(cond, msg):
        if not cond:
            raise NanoException(msg)

    @staticmethod
    def nano_assert_coord(coord, pred, msg):
        if not pred(coord):
            raise NanoException(msg)

    @staticmethod
    def nano_assert_region(c1, c2, pred, msg):
        for coord in region(c1, c2):
            Util.nano_assert(coord, pred, msg)

    @staticmethod
    def region(c1, c2):
        xmin = min(c1.x, c2.x)
        xmax = max(c1.x, c2.x)

        ymin = min(c1.y, c2.y)
        ymax = max(c1.y, c2.y)

        zmin = min(c1.z, c2.z)
        zmax = max(c1.z, c2.z)

        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                for z in range(zmin, zmax + 1):
                    yield (x, y, z)


class Vec:
    def __init__(self, x, y, z):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

    def __add__(self, vec):
        vec_type = type(vec).__name__
        Util.nano_assert(vec_type == 'Vec', 'Type mismatch in Vec addition')
        return Vec(self.x + vec.x, self.y + vec.y, self.z + vec.z)

    def __iadd__(self, vec):
        self.x += vec.x
        self.y += vec.y
        self.z += vec.z

    def __str__(self):
        result = f'<{self.x}, {self.y}, {self.z}>'
        return result

    def __sub__(self, vec):
        vec_type = type(vec).__name__
        Util.nano_assert(vec_type == 'Vec', 'Type mismatch in Vec subtraction')
        return Vec(self.x - vec.x, self.y - vec.y, self.z - vec.z)

    def clen(self):
        return max(abs(self.x), abs(self.y), abs(self.z))

    def is_zero(self):
        return self.x == 0 and self.y == 0 and self.z == 0

    def mlen(self):
        return abs(self.x) + abs(self.y) + abs(self.z)

