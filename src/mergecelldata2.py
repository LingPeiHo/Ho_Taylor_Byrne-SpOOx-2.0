#!/usr/bin/env python
# coding: utf-8
import argparse
import sys
import os

def FindAll(name, path):
    # name of file
    # starting path
    # only look dir
    result = []
    for root, dirs, files in os.walk(path):
        if name in dirs:
            path = os.path.join(root, name)
            # only use the ROI data otherwise will start concantenating all the subdirs
            if "ROI" in path:
                result.append(os.path.join(root, name))
    return result

def GetSampleDir(cellDataFile):
    print("cellDataFile = ", cellDataFile)
    dirname = os.path.dirname
    return(dirname(dirname(dirname(cellDataFile))))

def GetSourceDir(cellDataFile):
    print("cellDataFile = ", cellDataFile)
    dirname = os.path.dirname
    return(dirname(dirname(dirname(dirname(cellDataFile)))))

def GetHeader(file):
    with open(file) as f:
        return(f.readline())

def ConcatenateFiles(dirList, inputFile, outputFile):
    # get the header from the first file in the listand write it only once
    header = GetHeader(os.path.join(dirList[0],inputFile))
    with open(outputFile, "w") as outfile:
        outfile.write(header)
        # go through the list of files and write out each one
        for dir in dirList:
            filename = os.path.join(dir,inputFile)
            with open(filename) as infile:
                #skip the header of the file 
                next(infile)
                contents = infile.read()
                outfile.write(contents)



parser = argparse.ArgumentParser(description='''Generate merged cellData.tab files so can run analyses at the source/sample level based on the files one level below
''', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--indir', dest='indir',
                    help='initial directory level')
#parser.add_argument('--excludeList', dest='excludeList',
#                    help='list of strings to exclude if they appear in search e.g. "SAMPLE_11/" "SAMPLE_10/" "SAMPLE_17/"')
parser.add_argument('--infile', dest='infile', default = "cellData.tab",
                    help='the file it will look to merge')		
parser.add_argument('--outfile', dest='outfile', default = "cellData.tab",
                    help='the file to write out')		
parser.add_argument('--directory', dest='directory', default = "signalextraction",
                    help='the name of the directory to write to')		

if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)		   

args = parser.parse_args()

#  typical path 
# /t1-data/project/covidhyperion/staylor/covid2/tree/TONSIL/SAMPLE_1/ROI_2/signalextraction/cellData.tab
#indir = "/t1-data/project/covidhyperion/staylor/covid2/tree/COVID/SAMPLE_16"
#directory = "signalextraction"
#infile = "cellData.tab"
#outfile = "cellData.tab"
#excludeList = ["SAMPLE_11/", "SAMPLE_10/", "SAMPLE_17/"]
#includeList="SAMPLE_1/  SAMPLE_10/  SAMPLE_11/  SAMPLE_16/  SAMPLE_17/"
#excludeList =[]

infile=args.infile
directory = args.directory
indir=args.indir
outfile=args.outfile

allCellDataFiles = FindAll(directory, indir)
#print("allCellDataFiles",allCellDataFiles)

newDir = os.path.join(indir, directory)
os.makedirs(newDir, exist_ok=True)
outfile = os.path.join(newDir,outfile)

print("Writing files from:\n","\n".join(allCellDataFiles),"\n*** to ***\n",os.path.join(indir,outfile))

ConcatenateFiles(allCellDataFiles, infile, os.path.join(indir,outfile))


