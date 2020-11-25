#!/usr/bin/python3
#
#
#

import concurrent.futures
import abc
import imd_cookie_cutter.__helper as helper
from imd_cookie_cutter.__typecaster import estimate_type


class Processor(abc.ABC): 
    def __init__(self, infile, outfile, nprocs=0):
        self.__in = infile
        self.__out = outfile
        self.__cols = None
        self.__nprocs = int(nprocs)

        self.use_columns = True
        
        file_length = 0
        with open(self.__in.name, "r") as f:
            for i in f:
                file_length += 1
        self.__pbar = helper.ProgressBar(100, file_length)
    
    @abc.abstractmethod
    def process(self, data):
        pass
    
    @property
    def columns(self):
        return self.__cols

    @columns.setter
    def columns(self, other):
        if isinstance(other, (list, tuple)):
            self.__cols = list(other)
        else:
            print("Setting attribute 'columns' failed. Argument is not an iterable.")
    
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
            if line.startswith("#C") and not self.columns:
                self.columns = line[3:].strip().split()
            return helper.Continue
        # check if columns exist. these are mandatory
        if not self.columns and self.use_columns:
            print("No keys set for data columns")
            return helper.Break
        # check if line has to be copied
        data = self.__read_data(line)
        if not data:
            return helper.Continue
        if not self.process(data):
            return helper.Continue

        orderfunc = lambda iterator, *args: iterator # dont order, return itself
        if isinstance(data, dict):
            orderfunc = helper.order_dict

        line = " ".join(
                str(i) for i in orderfunc(data, self.columns)
            ) + "\n"
        self.__out.write(line)
        return helper.Success

    def __read_data(self, line):
        data = line.strip().split()
        data = [estimate_type(i) for i in data]
        if len(self.columns) == len(data):
            return dict(zip(self.columns, data))
        else: return None # no incomplete lines eg. caused by walltimes
