#!/usr/bin/env python

from collections import defaultdict
import os
from os.path import isfile, join


from config import Config
from model import Model
from system import System
from util import Util


# TODO: Loop over all model files, and output solutions/traces to solutions directory.
def main(filenames=None, resolutions_filter=None, max_model_count=None):
    if not filenames:
        paths = [join(Util.MODEL_DIR(), p) for p in os.listdir(Util.MODEL_DIR()) if p[0] == 'L']
        filenames = [f for f in paths if isfile(f)]
    resolutions_counter = defaultdict(int)

    model_count = 0
    for filename in filenames:
        with open(filename, 'rb') as ifile:
            data = ifile.read()
            resolution = data[0]
            resolutions_counter[resolution] += 1
            if (not resolutions_filter) or (resolutions_filter and resolution in resolutions_filter):
                m = Model(filename, data)
                s = System(m)

                s.trace = s.find_solution()
                ofilename = join(Util.MY_TRACE_DIR(), 'LA001.nbt')
                s.trace_write(ofilename, s.trace)

                if Config.VERBOSE:
                    print(f'Model #{model_count}', end='')
                m.print()
                model_count += 1
                if max_model_count and model_count >= max_model_count:
                    break

    if Config.VERBOSE:
        for res in sorted(resolutions_counter.keys()):
            print(f'{res:3}: {resolutions_counter[res]}')


# Lightning round resolutions:
#   {20: 18, 30: 23: 40: 15, 50: 4, 60: 17, 70, 7, 80: 19, 85: 2, 90: 6, 100: 25
#   120: 20, 130: 2, 140: 5, 150: 2, 160: 7, 180: 8, 200: 5, 220: 1}
#
if __name__ == '__main__':
    main(filenames=None, resolutions_filter=[20], max_model_count=1)

