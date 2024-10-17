#!/usr/bin/env python3

import sys, os
import argparse
import ROOT
import pandas as pd
import numpy as np
from array import array

sys.path.append('../common/')
from VoxInputParameters import VoxInputParameters
from XMLHandler import XMLHandler

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
  parser.add_argument('--DoEC', action='store_true')
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
  DoEC=args.DoEC

  inputs = VoxInputParameters(vox_dir, particle, eta_min, eta_max, False)
  xml = XMLHandler(inputs)
  relevantLayers = xml.GetRelevantLayers()
  layersBinnedInAlpha = xml.GetLayersWithBinningInAlpha()

  csvValidationFileName = path_input_file + fileName + ".csv"
  print("Opening file: " + csvValidationFileName)
  df = pd.read_csv(csvValidationFileName, header=None, engine='python', dtype=np.float64)
  df = df.fillna(0)
  data=df.to_numpy()  
  
  if not os.path.exists(output_path + '/%s/' % (particle)):
    os.makedirs(output_path + '/%s/' % (particle), exist_ok=True)

  print("Creating ROOT file: " + output_path + '/' + particle + '/' + fileName + ".root") 
  output_file = ROOT.TFile(output_path + '/' + particle + '/' + fileName + ".root","RECREATE") 
  rootTree = ROOT.TTree("rootTree","A ROOT tree")

  E_tot = array( 'f', [ 0 ] )
  E_totNorm = array( 'f', [ 0 ] )

  rootTree.Branch("etot", E_tot, "etot/F", )
  rootTree.Branch("etotNorm", E_totNorm, "etotNorm/F", )

  E_layers = {}
  extrapWeights = {}
  cog_etas = {}
  cog_phis = {}
  width_etas = {}
  width_phis = {}

  for l in range(0,len(relevantLayers)):
    cog_eta = array( 'f', [ 0 ] )
    cog_phi = array( 'f', [ 0 ] )
    width_eta = array( 'f', [ 0 ] )
    width_phi = array( 'f', [ 0 ] )
    cog_etas[l] = cog_eta
    cog_phis[l] = cog_phi
    width_etas[l] = width_eta
    width_phis[l] = width_phi
    layer = str(relevantLayers[l])
    rootTree.Branch("cog_eta_"+layer, cog_etas[l], "cog_eta_"+layer+"/F", )
    rootTree.Branch("cog_phi_"+layer, cog_phis[l], "cog_phi_"+layer+"/F", )
    rootTree.Branch("width_eta_"+layer, width_etas[l], "width_eta_"+layer+"/F", )
    rootTree.Branch("width_phi_"+layer, width_phis[l], "width_phi_"+layer+"/F", )
   
    E_layer = array( 'f', [ 0 ] )
    E_layers[l] = E_layer
    rootTree.Branch("e_"+layer,  E_layers[l] , "e_"+layer+"/F", )

    extrapWeight = array( 'f', [ 0 ] )
    extrapWeights[l] = extrapWeight
    rootTree.Branch("extrapWeight_"+layer, extrapWeights[l], "extrapWeight_"+layer+"/F", )

  #print(len(df.columns))

  for i in range (0, min(n_events,data.shape[0])):
    if (DoEC):
      step=6
      energyIndex = 3
      etaIndex = 4
      phiIndex = 5
      widthEtaIndex = 6
      widthPhiIndex = 7
      extrapWeightIndex = 8
    else:
      step=2
      energyIndex = 3
      extrapWeightIndex = 4     
      
    E_tot[0] = data[i][0]
    E_totNorm[0] = data[i][0]/energy
    
    for index, l in enumerate(relevantLayers):
      E_layers[index][0] = data[i][energyIndex +l*step]
      extrapWeights[index][0] = data[i][extrapWeightIndex + step*l]
      if (DoEC):
        cog_etas[index][0] = data[i][etaIndex + step*l]
        cog_phis[index][0] = data[i][phiIndex + step*l]
        width_etas[index][0] = data[i][widthEtaIndex + step*l]
        width_phis[index][0] = data[i][widthPhiIndex + step*l]
      
    rootTree.Fill()
    
  output_file.Write()
  output_file.Close()
