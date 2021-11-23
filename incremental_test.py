import json
import sys
from datetime import datetime
import os
from shutil import copy
# from decorator
import functools

# globals
assert_dir = ''
output_dir = ''
# def compare_if_exists

def counter(func, arg1):
    print(arg1)
    def _counter(f):
       # breakpoint()
        _counter.calls += 1
        print("In deco: " + str(_counter.calls))
        def wrapper(self, *args, **kwargs):
            print("DECO " + getattr(self, func))
            return f(self, *args, **kwargs)
        return wrapper
    _counter.calls = 0
    return _counter

# import functools

# def decorator(func):
#     @functools.wraps(func)
#     def wrapper_decorator(*args, **kwargs):
#         # Do something before
#         value = func(*args, **kwargs)
#         # Do something after
#         return value
#     return wrapper_decorator

# def counter2(arg1):
#     print(arg1)
#     def _counter(f):
#             def wrapper(self, *args, **kwargs):
#             return f(self, *args, **kwargs)
#         return wrapper
#     return _counter

# https://www.artima.com/weblogs/viewpost.jsp?thread=240845#decorator-functions-with-decorator-arguments

class Checkpoint:

    def __init__(self, f):
        functools.update_wrapper(self, f)
        self.assert_dir = ''
        self.log_dir = ''
        self.output_file = ''
        self.func = f
        print("Inside __init__()")
        print(self.assert_dir)
        print(self.log_dir)
        print(f)

    def __get__(self, instance, owner):
        print("Inside __get__()")

        from functools import partial
        # breakpoint()
        return partial(self.__call__, instance)
        
    def __call__(self, *args, **kwargs):

        #@functools.wraps(func)
        print("Inside __call__()")
        global assert_dir
        global output_dir
        self.assert_dir = assert_dir
        self.log_dir = output_dir
        print(self.assert_dir)
        print(self.log_dir)
        print("Inside __call__2()")

       # Getting the argument names of the
        # called function
        # breakpoint()
        argnames = self.func.__code__.co_varnames[:self.func.__code__.co_argcount]
        
        # Getting the Function name of the
        # called function
        self.output_file = self.func.__name__ + ".json"

        # def wrapped_f(*args):
        #     print("Inside wrapped_f()")
        #     print "Decorator arguments:", self.arg1, self.arg2, self.arg3
        #     f(*args)
        #     print "After f(*args)"
        # return wrapped_f

        # def inner_func(*args, **kwargs):
            
        print(self.output_file, "(", end = "")
        argnames = 'boop'
        # printing the function arguments
        print(', '.join( '% s = % r' % entry
            for entry in zip(argnames, args[:len(argnames)])), end = ", ")
        
        # Printing the variable length Arguments
        print("args =", list(args[len(argnames):]), end = ", ")
        
        # Printing the variable length keyword
        # arguments
        print("kwargs =", kwargs, end = "")
        print(")")
        data = self.func(*args, **kwargs)
        # breakpoint()
        print(data)
        self.testCheckpoint(self.assert_dir, self.log_dir, self.output_file, data)
        print(data)
            # return data
        # return inner_func

    def testCheckpoint(self, assert_dir, log_dir, output_file, data):
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
        with open(log_dir + '/' + output_file, 'w+') as f:
            f.write(json.dumps(data))                   

        return
    

# def inout():
#     def decorator(fun):
#         print(message1)
#         @function_details
#         def wrapper(*args, **kwargs):
#             return fun(*args, **kwargs)
#         print(message2)
#         return wrapper
#     return decorator

# def decodecorator(message1, message2):
#     def decorator(fun):
#         print(message1)
#         @function_details
#         def wrapper(*args, **kwargs):
#             return fun(*args, **kwargs)
#         print(message2)
#         return wrapper
#     return decorator
#def decorator_factory(argument):
#    def decorator(function):
#        def wrapper(*args, **kwargs):
#            funny_stuff()
#            something_with_argument(argument)
#            result = function(*args, **kwargs)
#            more_funny_stuff()
#            return result
#        return wrapper
#    return decorator
    
# if the checkpoint exists in 
# def testCheckpoint(func):


class Worker:
    def __init__(self, startPoint):
        # test recording arguments
        self.startPoint = startPoint

        # test recording class member
        self.classData = []

        #test this as a class member that changes when another member function is called
        self.classMember = 1

    @Checkpoint
    def step2_doWorkNextStep(self):
        print("Doing step 2")

        self.classData = [i * 2 for i in self.classData]
        return self.classData

    @Checkpoint
    # @decodecorator('zzzzzzzzzzzzzz', 'xxxxxxxxxxx')
    def step3_Arguments(self, offset):
       # breakpoint()
        print("Doing step 3")
        print("offset: " + str(offset))
        self.classData = [i + offset for i in self.classData]
        return [self.classData, 'complication']

    def incrementClassMember(self):
        self.classMember = self.classMember + 1
    
    #@call_counter()
    @Checkpoint
    # todo - test this in a loop
    def step4_ClassMemberChange(self):
       # breakpoint()
        print("Doing step 4")

        self.incrementClassMember()
        self.classData = [i + self.classMember for i in self.classData]
        return self.classData

    # @Checkpoint
    def step5_LoopingClassMember(self, count):
       # breakpoint()
        print("Doing step 5")

        for j in range(count):
            print("iter" + str(j))
            self.incrementClassMember()
            self.classData = [i + self.classMember for i in self.classData]

        return self.classData

    @Checkpoint
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
    # testCheckpoint(assert_dir, output_dir, 'step1_DoWorkNoArgs.json', a)
    # print(json.dumps(a))

    b = worker.step2_doWorkNextStep()
    # testCheckpoint(assert_dir, output_dir, 'step2_doWorkNextStep.json', b)

    c = worker.step3_Arguments(10)
    # testCheckpoint(assert_dir, output_dir, 'step3_Arguments.json', c)    

    d = worker.step4_ClassMemberChange()
    # testCheckpoint(assert_dir, output_dir, 'step4_ClassMemberChange.json', d)    

    # 5 loops
    e = worker.step5_LoopingClassMember(5)

    # print(json.dumps(b))
# functionize 
# todo - multiple iterations of function - could just check at the end? 
# make class
