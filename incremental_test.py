import json
import sys
from datetime import datetime
import os
from shutil import copy

# def compare_if_exists

def doWorkNextStep(inputs):
    
    some_result = []
    for x in inputs:
        some_result.append(x*2)

    return some_result


def step3(inputs):
    
    some_result = []
    for x in inputs:
        some_result.append(x*2+1)

    return some_result

def doWork(inputs):
    
    some_result = []
    for x in range(inputs):
        some_result.append(x)
    return some_result

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

# if the checkpoint exists in 
def testCheckpoint(assert_dir, log_dir, output_file, data):
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

if __name__ == "__main__":
    
    # read config - running this scenario
    config = readconfig(sys.argv[1])

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
    output_dir = makeOutputDir(top_level_output_dir, config['testcase'])
    print("All outputs going to: " + output_dir)

    # write command line arguments to the log
    with open(output_dir + '/args.txt', 'w+') as f:
        # print(sys.argv[0:])
        f.write(' '.join(sys.argv[0:]))

    # move config.json to log
    copy(sys.argv[1], output_dir)

    # do work
    a = doWork(config['input_arg'])
    testCheckpoint(assert_dir, output_dir, 'doWork.json', a)
    # print(json.dumps(a))

    b = doWorkNextStep(a)
    testCheckpoint(assert_dir, output_dir, 'doWorkNextStep.json', b)

    c = step3(b)
    testCheckpoint(assert_dir, output_dir, 'step3.json', c)    
    # print(json.dumps(b))

# functionize 
# todo - multiple iterations of function - could just check at the end? 
# make class