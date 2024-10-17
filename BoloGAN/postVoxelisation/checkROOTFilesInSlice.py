#!/usr/bin/env python3

import argparse 
import ROOT

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
parser = argparse.ArgumentParser(description="Plot total energy")
parser.add_argument('-f',  '--inputFolder', default='')
parser.add_argument('-e',  '--eta', default='')
parser.add_argument('-p',  '--pid', default='')
parser.add_argument('--checkGraph', action='store_true')

args = parser.parse_args()
vox_dir=args.inputFolder
eta=int(args.eta)
pid=int(args.pid)
checkGraph=args.checkGraph

missingSamples = []

#print(pid)
minimum = 6
if pid == 211:
  minimum = 8
if pid == 2212:
  minimum = 10

#print (minimum)

for e in range(minimum, 23):
  p = 2**e
  #print(p)
  
  fileName = f"%s/rootFiles/pid%s/eta_%d_%d/pid%s_E%s_eta_%d_%d.root" % (vox_dir, pid, eta, eta + 5, pid, p, eta, eta + 5) 

  file = ROOT.TFile.Open(fileName)
  
  if file == None:
    print("Cannot open File: " + fileName)
    #subFile = f"%s/jobs/condor_ExtractToVox_pid%s_E%s_eta_%d_%d.sub" % (vox_dir, pid, p, eta, eta + 5) 
    missingSamples.append("pid%s_E%s_eta_%d_%d" % (pid, p, eta, eta + 5))

  # This should be checked AFTER the make_voxelisation script is run
  elif checkGraph:
    graph = file.Get("E_phiMod_shifted")
    if graph == None:
      print("File is missing graph: " + fileName)
      #subFile = f"%s/jobs/condor_ExtractToVox_pid%s_E%s_eta_%d_%d.sub" % (vox_dir, pid, p, eta, eta + 5) 
      missingSamples.append("pid%s_E%s_eta_%d_%d" % (pid, p, eta, eta + 5))
    
if len(missingSamples) > 0 :
  for sample in missingSamples: 
    print(sample)
else:
  print("All OK")