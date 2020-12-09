#!/usr/bin/python3
#
# AN EXAMPLE USE CASE OF IMDCC
#
# This script copies the fixed atoms of the simulation box
# to a 3x3 grid and places the normal atoms into the middle cell.
#
# atom type 0 -> normal atom
# atom type 1 -> fixed atoms
#

import sys, os, argparse
from contextlib import ExitStack

import imd_cookie_cutter as imdcc


class ExpandProcessor(imdcc.Processor):
    """
    imdcc.Processor that copies and moves fixed atoms and adjusts the index
    """
    def __init__(self, box, shift, infile, outfile, nprocs=0, keep=False):
        super().__init__(infile, outfile, nprocs)
        self.box = box
        self.shift = shift # x, y, index
        self.keep = keep # keep normal atoms

    def process(self, data):
        data["number"] += self.shift.components[2]
        data["x"] += self.box.components[0]*self.shift.components[0]
        data["y"] += self.box.components[1]*self.shift.components[1]
        
        return data["type"] == 1 or self.keep


def main(args):
    rows, columns = 3, 3
    box = imdcc.Vector3D(0, 0, 0)
    atoms = 0

    # open files
    with ExitStack() as stack:
        try: # open input file
            infile = stack.enter_context(open(args.input, "r"))
        except FileNotFoundError:
            print(
                "Could not find input file '{}'".format(args.input),
                file=sys.stderr)
            sys.exit(1)

        outfile = stack.enter_context(open(args.output + ".tmp", "w")) # use a temporary file

        # count atoms an get box size
        for line in infile:
            if not line.startswith("#"):
                atoms += 1
            if line.startswith("#X"):
                box.components[0] = imdcc.estimate_type(line.strip().split()[1])
            if line.startswith("#Y"):
                box.components[1] = imdcc.estimate_type(line.strip().split()[2])
            if line.startswith("#Z"):
                box.components[2] = imdcc.estimate_type(line.strip().split()[3])
        print("{} atoms found".format(atoms))

        # copy, move a reindex atom configuration to new cells
        xrange, yrange = range(columns), range(rows)
        for x in xrange:
            for y in yrange:
                index_shift = (x*rows+y)*atoms # cell_number*number_of_atoms
                copy_normal = (
                    x == xrange[len(xrange)//2]
                    and y == yrange[len(yrange)//2]
                    ) # copy normal atoms or just fixed ones
                print("\nCopying cell {} of {}. Copy sphere? {}".format(
                    index_shift//atoms + 1, columns*rows, copy_normal))

                # actual shifting via new processor
                tmp_infile = stack.enter_context(open(args.input, "r"))
                processor = ExpandProcessor(
                    box, imdcc.Vector3D(x,y,index_shift), tmp_infile, outfile,
                    args.nprocs, keep=copy_normal)
                processor(verbose=args.verbose) # aka processor.execute(*args)

    with ExitStack() as stack:
        print("\nCleaning up temporary file")
        # this time open temporary file as input and real output
        infile = stack.enter_context(open(args.output + ".tmp", "r"))
        outfile = stack.enter_context(open(args.output, "w"))

        # get file length needed for progress bar
        file_length = 0
        with open(infile.name, "r") as f:
            for i in f:
                file_length += 1

        pbar = imdcc.ProgressBar(100, file_length)

        skip_comment = False
        for line in infile:
            pbar.increase()

            # if first header end (line with an "#E") skip all other comment
            # lines since these are just copies of the original header
            if skip_comment and line.startswith("#"):
                continue
            if line.startswith("#E"):
                skip_comment = True

            # modify first ehader to have new box size dimensions
            if line.startswith("#X"):
                line = "#X {:.16e} 0.0000000000000000e+00 0.0000000000000000e+00\n".format(
                    box.components[0]*columns)
            if line.startswith("#Y"):
                line = "#Y 0.0000000000000000e+00 {:.16e} 0.0000000000000000e+00\n".format(
                    box.components[1]*rows)
            if line.startswith("#Z"):
                line = "#Z 0.0000000000000000e+00 0.0000000000000000e+00 {:.16e}\n".format(
                    box.components[2]*2) # just give a bit of headroom
            outfile.write(line)

    # self explanatory
    if not args.debug:
        print("\nRemoving temporary file")
        os.remove(args.output + ".tmp")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a checkpoint file from IMD.")
    parser.add_argument("-n", "--nprocs", default=0, type=int, metavar="",
        help="Number of processes. Ignore this parameter if you don't want parallelization.")
    parser.add_argument("-i", "--input", type=str, metavar="", help="Input file path")
    parser.add_argument("-o", "--output", type=str, metavar="", help="Output file path")
    parser.add_argument("-v", "--verbose", action="store_true",
        help="Show status in form of progress bar and other visual goodies.")
    parser.add_argument("-d", "--debug", action="store_true",
        help="Keeps the temporary file created in the process for debugging purposes.")
    parser.add_argument('--version', action='version', version='1.0')

    main(parser.parse_args())
