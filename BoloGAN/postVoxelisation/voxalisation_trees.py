#!/usr/bin/env python3

import argparse
import ROOT
import sys
import pandas as pd

sys.path.append('../common/')
from VoxInputParameters import VoxInputParameters
from TrainingInputParameters import TrainingInputParameters
from helper_functions import *

ROOT.gROOT.SetBatch(True)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
if __name__== "__main__":
  parser = argparse.ArgumentParser(description="Plot observables")
  parser.add_argument('-f', '--fileName', default='')
  parser.add_argument('-o', '--output_path', default='')
  parser.add_argument('-i', '--path_input_file', default='')
  parser.add_argument('-v', '--vox_dir', default='')
  parser.add_argument('-p', '--particle', default='')
  parser.add_argument('-e', '--energy', default='')
  parser.add_argument('-eta', '--eta', default='')
  parser.add_argument('-n', '--nEvents', default=10000)
  args = parser.parse_args()

  fileName = args.fileName
  output_path = args.output_path
  path_input_file = args.path_input_file
  vox_dir = args.vox_dir
  n_events = int(args.nEvents)
  particle = args.particle
  energy = int(args.energy)
  eta_min = int(args.eta)
  eta_max = eta_min + 5
  
  inputs = VoxInputParameters(vox_dir, particle, eta_min, eta_max, False)
  xml = XMLHandler(inputs)
  
  df = pd.read_csv(path_input_file + fileName + "_voxalisation.csv", header=None, engine='python', dtype=np.float64)
  df = df.fillna(0)
  first_column = df.columns[0]
  second_column = df.columns[1]
  phiMod=df[first_column].to_numpy()
  phimod = df.iloc[ : , 0 ].to_numpy()
  etas=df[second_column].to_numpy()
  df = df.drop([first_column, second_column], axis=1) #Removing the first two element which is phiMod and eta
  data=df.to_numpy()

  if not os.path.exists(output_path + '/%s/' % (particle)):
    os.makedirs(output_path + '/%s/' % (particle), exist_ok=True)

  rootVoxFileName = f"%s/rootFiles/pid%s/eta_%d_%d/%s.root" % (inputs.vox_dir, inputs.pid, eta_min, eta_max, fileName)
  rootFile = ROOT.TFile(rootVoxFileName, "UPDATE")
  
  graph = DefineGraph(rootFile)
  
  rootFileName=f"%s/%s/%s.root" % (output_path, particle, fileName)
  print("Creating ROOT file: " + rootFileName) 
  output_file = ROOT.TFile(rootFileName ,"RECREATE") 
  rootTree = ROOT.TTree("rootTree","A ROOT tree");
  fill_ttree(xml, energy, False, data, phiMod, etas, rootTree, n_events, True, graph)
  output_file.Write()
  output_file.Close()

 
