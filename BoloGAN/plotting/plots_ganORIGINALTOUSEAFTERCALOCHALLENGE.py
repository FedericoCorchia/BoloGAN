#!/usr/bin/env python3

import numpy as np
import argparse
import ROOT
import os,sys

sys.path.append('../model/')
sys.path.append('../common/')

ROOT.gROOT.SetBatch(True)

from conditional_wgangp import WGANGP
from VoxInputParameters import VoxInputParameters
from DataParameters import DataParametersFromXML
from GANInputParameters import GANInputParametersFromXML
from VoxelNormalisation import VoxelNormalisation
from DataReader import DataLoader
from Label import Label
from XMLHandler import XMLHandler
from helper_functions import *

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="Plot observables")
  parser.add_argument('-ep', '--epoch', default=500)
  parser.add_argument('-e1', '--eta_min', default='')
  parser.add_argument('-e2', '--eta_max', default='')
  parser.add_argument('-p', '--pid', default='')
  parser.add_argument('-n', '--nEvents', default=10000)
  parser.add_argument('-o', '--output_dir_gan', default='')
  parser.add_argument('-ip', '--particle', default='')
  parser.add_argument('-i', '--path', default='')
  parser.add_argument('-idg', '--input_dir_gan', default='')
  parser.add_argument('-v', '--vox_dir', default='')
  parser.add_argument('-etot', '--etot', default='False')
  parser.add_argument('-r', '--energy_range', default='')

  args = parser.parse_args()

  output_dir_gan = args.output_dir_gan
  epoch = int(args.epoch)
  pid = args.pid
  eta_min = args.eta_min
  eta_max = args.eta_max
  n_events = int(args.nEvents)
  particle = args.particle
  input_dir_gan = args.input_dir_gan
  vox_dir = args.vox_dir
  htotOnly = args.etot
  energy_range = args.energy_range
 
  voxInputs = VoxInputParameters(vox_dir, particle, eta_min, eta_max)
  xml = XMLHandler(voxInputs)
  dataParameters = DataParametersFromXML(xml, energy_range)
  ekins = DataLoader.momentumsToEKins(dataParameters.momentums, voxInputs.mass)
  E_min = np.min(ekins) # Same E_min as DataReader.
  E_max = np.max(ekins) # Same E_max as DataReader.
  ganParameters = GANInputParametersFromXML(xml, energy_range)
  wgan = WGANGP(voxInputs, ganParameters)

  phiMod = np.zeros(n_events) #label[1]
  etas = np.zeros(n_events) #label[2]

  if ( dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelAll):
    dl = DataLoader(inputs, trainingInputs, xmlReader)
    maxVoxel = dl.getMaxVoxelAll()
    print("MaxVoxel from All: " + str(maxVoxel))
  elif ( dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelMid):
    dl = DataLoader(inputs, trainingInputs, xmlReader)
    maxVoxel = dl.getMaxVoxelMid()
    print("MaxVoxel from Mid: " + str(maxVoxel))
  elif (dataParameters.voxel_normalisation == VoxelNormalisation.midE):
    dl = DataLoader(inputs, trainingInputs, xmlReader)
    midEnergy = dl.getMidEnergy()
    print("Mid energy is: " + str(midEnergy))

  for index, energy in enumerate(dataParameters.momentums):    
    print ("Energy ", energy)
    ekin_sample = ekins[index]
    lab = Label(ekin_sample, n_events, E_min, E_max, eta_min, dataParameters.label_definition)
    label = lab.GetLabelsAndPhiMod()
    
    checkpointfile = "%s/model_%s_eta_%s_%s" % (output_dir_gan, particle, eta_min, eta_max) 
    data = wgan.GenerateEventsFromBest(checkpointfile, label, n_events)
  
    if (dataParameters.voxel_normalisation == VoxelNormalisation.normE):
      data = data * ekin_sample       #needed for conditional
      #print("Normalisation value ", energy)
    elif (dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelAll):
      data = data * maxVoxel
      #print("Normalisation value ", maxVoxel)
    elif (dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelMid):
      data = data * maxVoxel
      #print("Normalisation value ", maxVoxel)
    elif (dataParameters.voxel_normalisation == VoxelNormalisation.midE):
      #print(data[0])
      #print(data[0].sum())
      data = data * midEnergy
      #print("Normalisation value ", dl.getMidEnergy)
        
    if not os.path.exists(output_dir_gan + '/GAN_ROOT_files/%s/' % (particle)):
        os.makedirs(output_dir_gan + '/GAN_ROOT_files/%s/' % (particle), exist_ok=True)

    output_file_gan =  "%s/GAN_ROOT_files/%s/pid%s_E%d_eta_%s_%s_GAN.root" % (output_dir_gan, particle, pid, energy, eta_min, eta_max)
    output_file = ROOT.TFile((output_file_gan) ,"RECREATE")
    rootTree = ROOT.TTree("rootTree","A ROOT tree");
    
    fill_ttree(xml, energy, htotOnly, data.numpy(), phiMod, etas, rootTree, n_events)

    output_file.Write()
    output_file.Close()

