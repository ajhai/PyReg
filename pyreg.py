"""
    Simple script to run regression on given directory.
    
    .out - Output from running the testcase
    .exp - Expected output from the testcase
    .diff - Diff between expected output and output generated from the testcase (temporary file)
    .rb/java/c - File to test
"""

import argparse
import os
import glob
import subprocess
import shutil
import difflib


map_file = None
ext = None
binary_path = None
target = None


#Get the list of testcases from target
#If we are a single file, return just that
def listTests():
    list = []
    
    if os.path.isdir(os.path.abspath(target)):
        if ext is not None:
            list = glob.glob(os.path.abspath(target) + "/*." + ext)
        else:
            list = glob.glob(os.path.abspath(target) + "/*")
    else:
        list.append(os.path.abspath(target))

    return list


def getVarDict():
    #Open var map and create a dictionary out of it
    dict = {}

    if map_file is not None:
        f = open(map_file, "r")
        for line in f:
            mapp = line.split(' ')
            dict[mapp[0]] = mapp[1].strip()

    return dict


#Create a temp file out of test file replacing variables from var map
def replaceVars(testFile):
    #Create a temp file with vars replaced in given test file
    tempFile = testFile + ".tmp"

    if map_file is None:
        shutil.copyfile(testFile, tempFile)
    else:
        f = open(testFile, "r") 
        testdata = f.read()
        vars = getVarDict()
        for key in vars.iterkeys():
            #print key, vars[key]
            testdata = testdata.replace("<%" + key + "%>", vars[key])

        f.close()
        f = open(tempFile, "w")
        f.write(testdata)
        f.close()

    return tempFile


#Regress the given test and return the exit status
def regress(test):
    #Find the name of the testcase
    testbase = os.path.splitext(test)[0]
    testname = os.path.basename(testbase)

    #Replace variables with data from map file 
    print "\nRegressing " + testname
    testfile = replaceVars(test)
    
    out = open(testbase + ".out", "w")
    error = open(testbase + ".err", "w")

    p = subprocess.Popen([binary_path, testfile], stdout=out, stderr=error, stdin=subprocess.PIPE)
    p.wait()
    
    out.close
    error.close

    #Delete temp file
    os.remove(testfile)

    #If we have err data, let us fail the testcase
    error = open(testbase + ".err", "r")
    errdata = error.read()
    if (len(errdata) > 0):
        print testname + " failed with following error\n"
        print errdata
        error.close()
        return False

    error.close()

    #We have run the test. Now let us compare the output
    if os.path.exists(testbase + ".exp") is False:
        f = open(testbase + ".exp", "w")
        f.close

    diffdata = ''

    for line in difflib.unified_diff(open(testbase + ".exp").readlines(), open(testbase + ".out").readlines(), fromfile=testbase + ".exp", tofile=testbase + ".out"):
        diffdata += line

    if len(diffdata) > 0:
        #We have diff
        print testname + " failed"
        print diffdata
        f = open(testbase + ".diff", "w")
        f.write(diffdata)
        f.close()
        return False
    else:
        print testname + " passed"

    return True


#By this time we have all the data needed in global vars
#Just use that data and fireoff regression
def startRegression():
    failures = []

    list = listTests()

    for test in list:
        if regress(test) is False:
            failures.append(os.path.basename(test))

    if len(failures) > 0:
        print "\nFollowing tests failed: "
        for test in failures:
            print test
    else:
        print "\nAll tests passed"


#Process the parsed arguments and assign them to the global vars
def processArgs(args):
    global target, ext, binary_path, map_file

    #Make sure that the target is valid
    if os.path.exists(args.target):
        target = args.target
    elif args.e is not None and os.path.exists(args.target + "." + args.e):
        target = str(args.target) + "." + str(args.e)
    else:
        print "File/directory doesn't exist"
        exit(1)

    #If we are trying to accept a testcase, we can forget about everything else
    if args.a is not None:
        try:
            shutil.copyfile(args.target + ".out", args.target + ".exp")
            print "Accepted " + args.target
            exit(0)
        except IOError as e:
            print "Failed to accept testcase"
            exit(1)

    #Same way let us check for variable map and binary path
    if args.m is not None:
        try:
            with open(args.m) as f: pass
            map_file = args.m
        except IOError as e:
            print "Invalid variable map file"
            exit(1)
        
    try:
        with open(args.b) as f: pass
        binary_path = args.b
    except IOError as e:
        print "Invalid binary path"
        exit(1)

    if args.e is not None:
        ext = args.e

    startRegression()
    exit(0)


if __name__ == '__main__':
    #parse the arguments
    parser = argparse.ArgumentParser(description = 'PyReg - Simple regression script')
    parser.add_argument('-m', help = 'Config file with variable mappings')
    parser.add_argument('-e', help = 'Test case file extension')
    parser.add_argument('-a', help = 'Accept a test case output')
    parser.add_argument('-b', help = 'Binary path to regress the testcases with', required = True)
    parser.add_argument('target', metavar='Target', type=str, help='Testcase name or directory to regress')
    processArgs(parser.parse_args())
