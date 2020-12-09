#!/usr/bin/python3
#
# AN EXAMPLE USE CASE OF IMDCC
#
# A ball of atoms of type 0 on a ground plane of atoms of type 1
# In the simulation atoms of type 1 will be seen as fixed atoms
#
# atom type 0 -> normal atom
# atom type 1 -> fixed atoms
#

import sys, argparse
from contextlib import ExitStack

import imd_cookie_cutter as imdcc


class BallOnFixedGroundProcessor(imdcc.Processor):
    """
    imdcc.Processor that removes atoms outside of a sphere or ground
    and changes the atom types of the ground atoms to 1 (fixed)
    """
    def __init__(self, infile, outfile, nprocs=0):
        # setup
        super().__init__(infile, outfile, nprocs)
        offset, height, radius = 10, 50, 200
        
        # ball on fixed ground
        ground = imdcc.BoxSelector(
            imdcc.Vector3D(-offset,-offset,-offset),
            imdcc.Vector3D(500, 500, height+offset)
        )
        sphere = imdcc.SphereSelector(
            imdcc.Vector3D(241.925, 241.925, height+radius),
            radius
        )
        
        self.keep = {ground, sphere}
        self.fixed = {ground}

    def process(self, data):
        pos = imdcc.Vector3D(data["x"], data["y"], data["z"])
        
        # atom type changers
        if any({f.contains(pos) for f in self.fixed}):
            data["type"] = 1 # atom type 1 is a fixed atom
        
        # cookie cutters
        return any({k.contains(pos) for k in self.keep})


def main(args):
    with ExitStack() as stack:
        try: # open input file
            infile = stack.enter_context(open(args.input, "r"))
        except FileNotFoundError:
            print(
                "Could not find input file '{}'".format(args.input),
                file=sys.stderr
                )
            sys.exit(1)
        
        outfile = stack.enter_context(open(args.output, "w"))
        
        processor = BallOnFixedGroundProcessor(infile, outfile, args.nprocs)
        processor(verbose=args.verbose) # aka processor.execute(*args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a checkpoint file from IMD.")
    parser.add_argument("-n", "--nprocs", default=0, type=int, metavar="", help="Number of processes. Ignore this parameter if you don't want parallelization.")
    parser.add_argument("-i", "--input", type=str, metavar="", help="Input file path")
    parser.add_argument("-o", "--output", type=str, metavar="", help="Output file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show status in form of progress bar and other visual goodies.")
    parser.add_argument('--version', action='version', version='1.0')
    args = parser.parse_args()
    
    #print(args)
    main(args)
