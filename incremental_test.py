import json
import sys
from datetime import datetime
import os
from shutil import copy
import functools

# globals - is this a good idea? For now, don't see why I would need
# more than 1 place to put my outputs. 
# could choose to put this back into the checkpoint defintion
# can do the thing where if checkpoint is called w/o args, it goes here
# and if it is specified, then it goes there.
# https://realpython.com/primer-on-python-decorators/#both-please-but-never-mind-the-bread
assert_dir = ''
output_dir = ''
# def compare_if_exists
# https://www.codementor.io/@sheena/advanced-use-python-decorators-class-function-du107nxsv
# https://realpython.com/primer-on-python-decorators/#decorating-classes


class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.num_calls = 0

    def __call__(self, *args, **kwargs):
        self.num_calls += 1
        print(f"Call {self.num_calls} of {self.func.__name__!r}")
        return self.func(*args, **kwargs)

# https://www.artima.com/weblogs/viewpost.jsp?thread=240845#decorator-functions-with-decorator-arguments

class Checkpoint:

    def __init__(self, f):
        functools.update_wrapper(self, f)
        self.assert_dir = ''
        self.log_dir = ''
        self.output_file = ''
        self.func = f
        # print("Inside __init__()")
        print(self.assert_dir)
        print(self.log_dir)
        print(f)

    def __get__(self, instance, owner):
        # print("Inside __get__()")

        from functools import partial
        # breakpoint()
        return partial(self.__call__, instance)
        
    def __call__(self, *args, **kwargs):

        global assert_dir
        global output_dir
        self.assert_dir = assert_dir
        self.log_dir = output_dir
    
       # Getting the argument names of the
        # called function
        argnames = self.func.__code__.co_varnames[:self.func.__code__.co_argcount]
        
        # Getting the Function name of the
        # called function
        self.output_file = self.func.__name__ + ".json"
            
        print(self.output_file, "(", end = "")
        # argnames = 'boop'
        # printing the function arguments
        print(', '.join( '% s = % r' % entry
            for entry in zip(argnames, args[:len(argnames)])), end = ", ")
        
        # Printing the variable length Arguments
        print("args =", list(args[len(argnames):]), end = ", ")
        # breakpoint()
        # Printing the variable length keyword
        # arguments
        print("kwargs =", kwargs, end = "")
        print(")")
        # self.writeJsonToFile(self.assert_dir, self.log_dir, self.output_file, args[1:], 'args')
        # self.writeJsonToFile(self.assert_dir, self.log_dir, self.output_file, kwargs, 'kwargs')

        data = self.func(*args, **kwargs)
        # breakpoint()
        print(data)
        # self.writeJsonToFile(self.assert_dir, self.log_dir, self.output_file, data, 'results')
        x = {'args': args[1:], 'kwargs' : kwargs, 'results' : data}
        self.writeJsonToFile(self.assert_dir, self.log_dir, self.output_file, x, self.func.__name__)

        return data

    def writeJsonToFile(self, assert_dir, log_dir, output_file, data, name):
        print('testdata: ' + str(data)) 
        if assert_dir == '':
            print('nothing to compare against')
        else:
            try:
                with open(assert_dir + '/' + output_file) as testf:
                    comp_data = json.load(testf)
                    print('savedata: ' +  str(comp_data))
                    if(comp_data == data):
                        print('pass')
                    else:
                        assert comp_data == data , "ERROR: Checkpoint " + os.path.splitext(output_file)[0] + " not the same"
            except:
                print('comparison file doesn''t exist. consider updating assert log')
        with open(log_dir + '/' + output_file, 'a+') as f:
            f.write(json.dumps({name: data}))                   

        return
    
class Worker:
    def __init__(self, startPoint):
        # test recording arguments
        self.startPoint = startPoint

        # test recording class member
        self.classData = []

        #test this as a class member that changes when another member function is called
        self.classMember = 1

    # @Checkpoint
    def step2_doWorkNextStep(self):
        print("Doing step 2")

        self.classData = [i * 2 for i in self.classData]
        return self.classData

    @Checkpoint
    def step3_Arguments(self, offset):
       # breakpoint()
        print("Doing step 3")
        print("offset: " + str(offset))
        self.classData = [i + offset for i in self.classData]
        return [self.classData, 'complication']

    def incrementClassMember(self):
        self.classMember = self.classMember + 1
    
    # @Checkpoint
    # todo - test this in a loop
    def step4_ClassMemberChange(self):
       # breakpoint()
        print("Doing step 4")

        self.incrementClassMember()
        self.classData = [i + self.classMember for i in self.classData]
        return self.classData

    # # @Checkpoint
    def step5_LoopingClassMember(self, count):
       # breakpoint()
        print("Doing step 5")

        for j in range(count):
            print("iter" + str(j))
            self.incrementClassMember()
            self.classData = [i + self.classMember for i in self.classData]

        return self.classData

    # @Checkpoint
    def step1_DoWorkNoArgs(self):
        print("Doing step 1")

        for x in range(self.startPoint):
            self.classData.append(x)
        return self.classData




def readconfig(configfile):

    with open(configfile) as f:
        data = json.load(f)
    return data

# make output dir and copy in config file/all other run inputs
def makeOutputDir(curdir, testcase):
    today = datetime.now()

    unique_log_dir = curdir + '/' + testcase + "_" + today.strftime('%Y%m%d') + "_" + today.strftime('%H%M%S')
    os.mkdir(unique_log_dir)

    # return full path so (hopefully) less can go wrong
    return os.path.abspath(unique_log_dir)
    
def copyToLog(log, file):
    copy(file, log)

if __name__ == "__main__":
    
    # read config - running this scenario
    config = readconfig(sys.argv[1])

    # global assert_dir 
    assert_dir = ''
    # read comparison dir, if provided and exists
    print(len(sys.argv))
    if len(sys.argv) > 2:
        assert_dir = sys.argv[2]    

    # todo - configurable
    top_level_output_dir = 'logs'
    if not os.path.exists(top_level_output_dir):
        os.mkdir(top_level_output_dir)
    # mkdir output file
    # global output_dir 
    output_dir = makeOutputDir(top_level_output_dir, config['testcase'])
    print("All outputs going to: " + output_dir)

    # write command line arguments to the log
    with open(output_dir + '/args.txt', 'w+') as f:
        # print(sys.argv[0:])
        f.write(' '.join(sys.argv[0:]))

    # move config.json to log
    copy(sys.argv[1], output_dir)

    worker = Worker(config['input_arg'])
    # do work
    a = worker.step1_DoWorkNoArgs()
    b = worker.step2_doWorkNextStep()
    c = worker.step3_Arguments(10)
    d = worker.step4_ClassMemberChange()
    # 5 loops - TODO
    e = worker.step5_LoopingClassMember(5)

# todo - multiple iterations of function - could just check at the end? 
# todo - map 
# autoformat the json
# fix syntax - write all out at once
# handle loops/every X times saving - write name reasonably