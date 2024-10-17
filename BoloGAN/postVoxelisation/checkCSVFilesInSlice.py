#!/usr/bin/env python3

import numpy as np
import pandas as pd
import argparse 
import subprocess
import os,sys

sys.path.append('../common/')
from VoxInputParameters import VoxInputParameters
from XMLHandler import XMLHandler

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def checkFile(fileName, expectedColumns):
  print("Check file " + fileName + " that should have " + str(expectedColumns) + " columns")
  try:
    if os.path.isfile(fileName):
      try:
        df = pd.read_csv(fileName, header=None, engine='python', dtype=np.float64)
        nevents=len(df)
        ncolumns=len(df.columns)
        print(fileName + " could be open without problems, # events: " + str(nevents) + " # columns: " + str(ncolumns))
        if ncolumns != expectedColumns:
          print("Wrong number of columns, either corrucpt file or from a different voxelisation, should be removed")
          #try:
          #  os.remove(fileName)
          #except Exception as err:
          #  print(err) 
          #  print("Could not delete file: " + fileName)

      except:
        print("Problem with file " + fileName + ", deleting it") 
        try:
          os.remove(fileName)
        except Exception as err:
          print(err)
          print("Could not delete file: " + fileName)
        print("File deleted") 
    else:
      print("File missing: " + fileName + ", likely delete in previous run")

  except:
    print("Cannot find file " + fileName + ", try deleting it") 
    try:
      os.remove(fileName)
    except Exception as err:
      print(err)
      print("Could not delete file: " + fileName)
    print("File deleted") 
     



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
parser = argparse.ArgumentParser(description="Plot total energy")
parser.add_argument('-f',  '--inputFolder', default='')
parser.add_argument('-l',  '--logFolder', default='')
parser.add_argument('-e',  '--eta', default='')
parser.add_argument('-p',  '--pid', default='')
parser.add_argument('-b',  '--totalBatches', default='', nargs='+')
parser.add_argument('-v',  '--validation', default='')

args = parser.parse_args()
vox_dir=args.inputFolder
log_dir=args.logFolder
eta=int(args.eta)
pid=int(args.pid)
totalBatches=list(map(int, args.totalBatches))
isValidation=args.validation == "validation"

particle="photons"
if pid == 211:
  particle="pions"
if pid == 2212:
  particle="protons"

voxInputs = VoxInputParameters(vox_dir, particle, eta, eta+5)
xml = XMLHandler(voxInputs)
expectedColumns = xml.GetTotalNumberOfBins() + 2

if isValidation:
  expectedColumns = 147

print(expectedColumns)
print(totalBatches)
missingSamples = []

maximum=23
minimum = 6
if pid == 211:
  minimum = 8
if pid == 2212:
  minimum = 10

for energyIndex in range(minimum, maximum):
  p = 2**energyIndex
  print("Validating momentum %d" % (p))
  
  voxOrVal="voxalisation"
  if isValidation:
    voxOrVal="validation"
  fileName = "%s/csvFiles/pid%s/eta_%d_%d/pid%s_E%s_eta_%d_%d_%s.csv" % (vox_dir, pid, eta, eta + 5, pid, p, eta, eta + 5, voxOrVal) 
  
  try:
    df = pd.read_csv(fileName, header=None, engine='python', dtype=np.float64)

    nevents=len(df)
    ncolumns=len(df.columns)
    printWarning = False
    
    if energyIndex == 22 and (nevents < 800 or nevents > 1100):
      printWarning = True
    if energyIndex == 21 and (nevents < 1600 or nevents > 2200):
      printWarning = True
    if energyIndex == 20 and (nevents < 2400 or nevents > 3300):
      printWarning = True
    if energyIndex == 19 and (nevents < 4000 or nevents > 5500):
      printWarning = True
    if energyIndex <= 18 and (nevents < 8000 or nevents > 11000):
      printWarning = True
      
    if printWarning:
      print("Possible problem in File: " + fileName)
      print(" # events: " + str(nevents))
      print(" # columns: " + str(ncolumns))
    #else:
    #  print(fileName + " is ok")

  except FileNotFoundError as err:
    print(err)
    print("Missing File: " + fileName)
    subFile = "%s/jobs/condor_ExtractToVox_pid%s_E%s_eta_%d_%d.sub" % (log_dir, pid, p, eta, eta + 5) 
    missingSamples.append("pid%s_E%s_eta_%d_%d" % (pid, p, eta, eta + 5))
    
    try:
      f = open(subFile)
      subprocess.call("condor_submit "+subFile)
    except FileNotFoundError as err:
      print("Missing also sub file!")
      pass
    pass
    
  except pd.errors.ParserError as err:
    print(err)
    print("Error reading " + fileName)
    max=totalBatches[energyIndex - minimum]
    print("Should have " + str(max) + " batches")
    for batch in range(0,max):
      fileName = "%s/csvFiles/pid%s/eta_%d_%d/pid%s_E%s_eta_%d_%d_%d_%s.csv" % (vox_dir, pid, eta, eta + 5, pid, p, eta, eta + 5,batch, voxOrVal)
      checkFile(fileName, expectedColumns)
      #print(fileName)
      
    missingSamples.append("pid%s_E%s_eta_%d_%d" % (pid, p, eta, eta + 5))
    pass
    
  except pd.errors.EmptyDataError as err:
    print(err)
    print("Empty file " + fileName)
    missingSamples.append("pid%s_E%s_eta_%d_%d" % (pid, p, eta, eta + 5))
    pass
     
  except Exception as err:
    print(err)
    print("Something was wrong with file " + fileName)
    max=totalBatches[energyIndex - minimum]
    print("Should have "+ str(max)+" batches")
    for batch in range(0,max):
      fileName = "%s/csvFiles/pid%s/eta_%d_%d/pid%s_E%s_eta_%d_%d_%d_%s.csv" % (vox_dir, pid, eta, eta + 5, pid, p, eta, eta + 5,batch, voxOrVal)
      checkFile(fileName, expectedColumns)

    missingSamples.append("pid%s_E%s_eta_%d_%d" % (pid, p, eta, eta + 5))
    pass
     
if len(missingSamples) > 0 :
  print(missingSamples)
else:
  print("All OK")