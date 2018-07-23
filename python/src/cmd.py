from abc import ABC, abstractmethod


from fillstate import FillState
from util import Util, Vec


class Cmd(ABC):
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def bytes_repr(self):
        pass

    @abstractmethod
    def execute(self):
        pass


class CmdFill(Cmd):
    def __init__(self, system, nd):
        self.system = system
        self.nd = nd

    def __str__(self):
        return f'Fill {self.nd}'

    def bytes_repr(self):
        return bytes([Util.encode_nd(self.nd) & 3])

    def execute(self):
        bot = self.system.current_bot()
        pos_fill = self.system.current_bot().pos + self.nd
        Util.nano_assert_is_valid(pos_fill)

        if self.system.matrix[pos_fill] == FillState.Void:
            self.system.matrix[pos_fill] = FillState.Full
            self.system.energy_used += Config.COST_FILL_VOID
        else:  # FillState.Full
            self.system.energy_used += Config.COST_FILL_FULL


class CmdFission(Cmd):
    def __init__(self, system, nd, m):
        self.system = system
        self.nd = nd  # nd = near coordinate difference
        self.m = m  # Count of bids given to the first child

    def __str__(self):
        return f'Fission {self.nd} | {self.m}'

    def bytes_repr(self):
        b1 = (Util.encode_nd(self.nd) << 5) & 5
        b2 = m
        return bytes([b1, b2])

    def execute(self):
        bot = self.system.current_bot()
        Util.nano_assert(len(bot.seeds) > 0)

        n = len(bid.seeds)
        seeds = self.system.current_bot().seeds.copy()
        # TODO
        bot_new.bid = seeds[0]
        bot_new.seeds = seeds[2: m + 1]
        bot_new.pos = bot.pos + nd

        bot.seeds = seeds[m + 1: n]

        self.system.bots = self.system.bots + [bot_new]
        self.system.energy_used += 24


class CmdFlip(Cmd):
    def __init__(self, system):
        self.system = system

    def __str__(self):
        return 'Flip'

    def bytes_repr(self):
        return bytes([0b1111_1101])

    def execute(self):
        bot = self.system.current_bot()
        self.harmonics = self.harmonics.next()


class CmdFusionP(Cmd):
    def __init__(self, system, nd):
        self.system = system
        self.nd = nd

    def __str__(self):
        return f'FusionP {self.nd}'

    def bytes_repr(self):
        return bytes([(self.nd << 3) & 7])

    def execute(self):  # TODO
        bot = self.system.current_bot()
        bot_s = [b for b in self.system.bots if bot.pos + self.nd == b.pos]
        # TODO: Assert that bot_s's Cmd is CmdFusionS, and that its CmdFusionS's matches.
        bot.seeds = bot.seeds + [bot_s.bid] + bot_s.seeds
        self.system.bots = [b for b in self.system.bots if b != bot_s]
        self.system.energy_used -= Config.COST_FUSION


class CmdFusionS(Cmd):
    def __init__(self, system, nd):
        self.system = system
        self.nd = nd

    def __str__(self):
        return f'FusionS {self.nd}'

    def bytes_repr(self):
        return bytes([(self.nd << 3) & 6])

    def execute(self):
        # bot = self.system.current_bot()
        pass  # See CmdFusionP.execute()


class CmdGFill(Cmd):
    def __init__(self, system, nd, fd):
        self.system = system
        self.nd = nd
        self.fd = fd

    def __str__(self):
        return f'GFill {self.nd} {self.fd}'

    def bytes_repr(self):
        b1 = (self.nd << 5) & 0b001
        b2 = Util.encode_fd(self.fd.x)
        b3 = Util.encode_fd(self.fd.y)
        b4 = Util.encode_fd(self.fd.z)
        return bytes([b1, b2, b3, b4])

    def execute(self):
        bot = self.system.current_bot()
        pass  # TODO


class CmdGVoid(Cmd):
    def __init__(self, system, nd, fd):
        self.system = system
        self.nd = nd
        self.fd = fd

    def __str__(self):
        return f'GVoid {self.nd} {self.fd}'

    def bytes_repr(self):
        return bytes([self.nd << 5])

    def execute(self):
        bot = self.system.current_bot()
        pass  # TODO


class CmdHalt(Cmd):
    def __init__(self, system):
        self.system = system

    def __str__(self):
        return 'Halt'

    def bytes_repr(self):
        return bytes([0b1111_1111])

    def execute(self):
        # bot = self.system.current_bot()
        pass


# There are 90 long linear coordinate differences
class CmdLMove(Cmd):
    def __init__(self, system, sld1: Vec, sld2: Vec):
        self.system = system
        self.sld1 = sld1
        self.sld2 = sld2

    def __str__(self):
        return 'LMove {self.sld1} {self.sld2}'

    def bytes_repr(self):
        a1, i1 = Util.encode_sld(self.sld1)
        a2, i2 = Util.encode_sld(self.sld2)
        b1 = (a2 << 6) & (a1 << 4) & 6
        b2 = (i2 << 4) & (i1 << 4)
        return bytes([b1, b2])

    def execute(self):
        bot = self.system.current_bot()
        pos0 = self.pos
        pos1 = self.pos + sldp1
        pos2 = pos1 + sld2
        Util.nano_assert_region(pos0, pos1, lambda p: p.is_empty())
        Util.nano_assert_region(pos1, pos2, lambda p: p.is_empty())
        bot.pos = pos2
        self.system.energy_used += 2 * (sld1.mlen() + 2 + sld2.mlen())


# There are 30 short linear coordinate differences
class CmdSMove(Cmd):
    def __init__(self, system, lld):
        self.system = system
        self.lld = lld

    def __str__(self):
        return f'SMove {self.lld}'

    def bytes_repr(self):
        a, i = Util.encode_lld(self.lld)
        b1 = (a << 4) & 7
        b2 = i
        return bytes([b1, b2])

    def execute(self):
        bot = self.system.current_bot()
        bot.pos = bot.pos + self.lld
        self.system.energy_used += 2 * self.lld.mlen()


class CmdVoid(Cmd):
    def __init__(self, system, nd):
        self.system = system
        self.nd = nd

    def __str__(self):
        return f'Void {self.nd}'

    def bytes_repr(self):
        b = (Util.encode_ncd(self.nd) << 3) & 0b010
        return bytes([b])

    def execute(self):
        s = self.system
        bot = s.current_bot()
        pos_new = bot.pos + self.nd
        m = s.matrix
        if m[pos_new] == FillState.Full:
           m[pos_new] = FillState.Void
           s.energy -= 12
        else: # m[pos] == Void
            s.energy += 3


# No system state change
class CmdWait(Cmd):
    def __init__(self, system):
        self.system = system

    def __str__(self):
        return 'Wait'

    def bytes_repr(self):
        return bytes([0b1111_1110])

    def execute(self):
        bot = self.system.current_bot()
        pass  # TODO

