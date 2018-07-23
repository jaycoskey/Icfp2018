from os.path import join


from cmd import *
from config import Config
from competitionphase import CompetitionPhase
from harmonics import Harmonics
from nanobot import Nanobot
from util import NanoException, Pos, Util


class System:
    def __init__(self, model):
        self.bots = []
        self.competition_phase = CompetitionPhase.Full
        self.energy_used = 0
        self.harmonics = Harmonics.Low
        self.matrix = None
        self.model = model
        self.trace = []  # List of commands

        pos = Pos(0, 0, 0)
        seeds = list(range(1, 41))
        bot = Nanobot(pos, seeds)
        self.bots.append(bot)

    def assert_ready_to_halt(self):
        Util.nano_assert(self.is_ready_to_halt())

    # TODO: Find actual solution trace.
    # TODO: Break model into clusters (e.g., w/ k-means) and send distinct nanobots to them.
    # TODO: Optimize branching into clusters
    # TODO: Within each cluster, optimize path.
    def find_solution(self):
        ifilename = join(Util.ICFP_TRACE_DIR(), 'LA001.nbt')
        trace = self.trace_read(ifilename)
        return trace

    def is_ready_to_halt(self):
        return self.pos.is_origin() and len(self.bots) == 1 and self.harmonics == Harmonics.Low

    def is_solution(self):
        result = (self.harmonics == Harmonics.Low
                  and len(self.bots) == 0
                  # and self.trace
                  and self.matrix.matches(self.model)
                  )
        return result

    # TODO: Complete definition. Groundedness is one trait, but there are others.
    def is_well_formed(self):
        return False

    # TODO: Address issue: Trace (.nbt) files read & written back to disk aren't identical to the original.
    #                      Related: Why do the default trace files all begin with 0x34?
    def trace_read(self, ifilename):
        Util.nano_assert(ifilename.endswith('.nbt'), f'Unrecognized trace filename extension: {ifilename}')
        cmds = []
        with open(ifilename, 'rb') as ifile:
            data = ifile.read()
            byte_count = 0
            cmd_count = 0
            while byte_count < len(data):
                print(Util.log_chars(cmd_count), end='')
                b = data[byte_count]
                b13 = b & 0b0000_0111
                is_b48_full = (b & 0b1111_1000) == 0b1111_1000

                bsel14 = lambda b: (b & 0b0000_1111)
                bsel15 = lambda b: (b & 0b0001_1111)
                bsel48 = lambda b: (b & 0b1111_1000) >> 3
                bsel56 = lambda b: (b & 0b0011_0000) >> 4
                bsel58 = lambda b: (b & 0b1111_0000) >> 4
                bsel78 = lambda b: (b & 0b1100_0000) >> 6

                cmd = None
                if b13 == 0b000:  # GVOID
                    nd = Util.decode_nd(bsel48(b))
                    fdx = data[byte_count + 1]
                    fdy = data[byte_count + 2]
                    fdz = data[byte_count + 3]
                    fd = Util.decode_fd(fdx, fdy, fdz)
                    cmd = CmdGVoid(system=self, nd=nd, fd=fd)
                elif b13 == 0b001:  # GFILL
                    nd = Util.decode_nd(bsel48(b))
                    fdx = data[byte_count + 1]
                    fdy = data[byte_count + 2]
                    fdz = data[byte_count + 3]
                    fd = Util.decode_fd(fdx, fdy, fdz)
                    cmd = CmdGFill(system=self, nd=nd, fd=fd)
                elif b13 == 0b011:  # VOID
                    nd = Util.decode_nd(bsel48(b))
                    cmd = CmdVoid(system=self, nd=nd)
                elif b13 == 0b011:  # FILL
                    nd = Util.decode_nd(bsel48(b))
                    return CmdFill(system=self, nd=nd)
                elif b13 == 0b100:  # SMOVE or LMOVE
                    if b & 0b0000_1111 == 0b0000_0100:
                        lld_a = bsel56(b)
                        lld_i = bsel15(b)
                        lld = Util.decode_lld(lld_a, lld_i)
                        cmd = CmdSMove(system=self, lld=lld)
                    elif b & 0b0000_1111 == 0b0000_1100:
                        sld1_a = bsel56(b)
                        sld2_a = bsel78(b)

                        bnext = data[byte_count + 1]
                        sld1_i = bsel14(bnext)
                        sld2_i = bsel58(bnext)

                        sld1 = Util.decode_sld(sld1_a, sld1_i)
                        sld2 = Util.decode_sld(sld2_a, sld2_i)
                        cmd = CmdLMove(system=self, sld1=sld1, sdl2=sld2)
                    else:
                        raise NanoException(f'Unregonized trace bit sequence staring with "100": {bin(b)}')
                elif b13 == 0b101:  # FLIP or FISSION
                    if is_b48_full:
                        cmd = CmdFlip(system=self)
                    else:
                        nd = Util.decode_nd(bsel48(b))
                        m = data[byte_count + 1]
                        cmd = CmdFission(system=self, nd=nd, m=m)
                elif b13 == 0b110:  # WAIT or FUSIONS
                    if is_b48_full:
                        cmd = CmdWait(system=self)
                    else:
                        nd = Util.decode_nd(bsel48(b))
                        cmd = CmdFusionS(system=self, nd=nd)
                elif b13 == 0b111:  # HALT or FUSIONP
                    if is_b48_full:
                        cmd = CmdHalt(system=self)
                    else:
                        nd = Util.decode(bsel48(b))
                        cmd = CmdFusionP(system=self, nd=nd)
                else:
                    raise NanoException(f'Unregonized trace bit sequence: {bin(b)}')
                cmds.append(cmd)
                byte_count += Util.byte_count(type(cmd).__name__)
                cmd_count += 1
            print()
        return cmds

    def trace_repr(self, cmds):
        cmd_strs = list(map(lambda c: f'{str(c):20s}', cmds))
        chunk_strs = [' => '.join(chunk) for chunk in Util.chunks(5, cmd_strs)]
        return '\n'.join(chunk_strs)

    def trace_write(self, ofilename, cmds):
        if Config.VERBOSE:
            print(self.trace_repr(cmds))
        data = bytes([b for cmd in self.trace for b in cmd.bytes_repr()])
        with open(ofilename, 'wb') as ofile:
            ofile.write(data)

