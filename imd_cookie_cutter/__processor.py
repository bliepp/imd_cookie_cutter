#!/usr/bin/python3
#
#
#

import concurrent.futures
import abc
import imd_cookie_cutter.__helper as helper
from imd_cookie_cutter.__typecaster import estimate_type

class Processor(abc.ABC):
    
    def __init__(self, infile, outfile, nprocs=0, verbose=True):
        self.__in = infile
        self.__out = outfile
        self.__cols = None
        self.__nprocs = int(nprocs)
        self.__verbose = verbose
        
        file_length = 0
        for i in open(self.__in.name, "r"):
            file_length += 1
        self.__pbar = helper.ProgressBar(100, file_length)
    
    @abc.abstractmethod
    def process(self, data):
        pass

    def __call__(self, nprocs=None, verbose=False):
        self.execute(nprocs, verbose)

    def execute(self, nprocs=None, verbose=False):
        executor = self.__exec_step
        if verbose:
            print("Starting cookie cutting")
            executor = self.__exec_step_verbose

        if nprocs != None:
            self.__nprocs = int(nprocs)

        if self.__nprocs > 1:
            executor = concurrent.futures.ProcessPoolExecutor(self.__nprocs)
            futures = [
                executor.submit(executor, line) for line in self.__in
            ]
            concurrent.futures.wait(futures)
        else:
            for line in self.__in:
                status = executor(line)
                if status == helper.Break:
                    break
                # nee need to check for helper.Continue,
                # since the loop is finished anyway.

        if verbose: print("\nCookie cutting finished. Yummie!")

    def __exec_step_verbose(self, line):
        result = self.__exec_step(line)
        self.__pbar.increase()
        return result

    def __exec_step(self, line):
        # just copy comments
        if line.startswith("#"):
            self.__out.write(line)
            if line.startswith("#C"):
                self.__cols = line[3:].strip().split()
            return helper.Continue
        # check if line has to be copied
        # deprecated, since process isnt an argument anymore
        #if not process: # if process is False, None, etc.
        #    return helper.Continue
        #if callable(process): # if process is function, functor, etc.
        #    data = self.__read_data(line)
        #    if not data:
        #        return helper.Continue
        #    if not process(data):
        #        return helper.Continue
        data = self.__read_data(line)
        if not data:
            return helper.Continue
        if not self.process(data):
            return helper.Continue

        line = " ".join(
                str(i) for i in helper.order_dict(data, self.__cols)
            ) + "\n"
        self.__out.write(line)
        return helper.Success

    def __read_data(self, line):
        data = line.strip().split()
        data = [estimate_type(i) for i in data]
        if len(self.__cols) == len(data):
            return dict(zip(self.__cols, data))
        else: return None # no incomplete lines eg. caused by walltimes
