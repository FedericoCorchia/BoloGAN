import numpy as np
from resource import *
from sklearn.utils import shuffle

from DataReader import DataLoader
from InputParameters import InputParameters
from TrainingInputParameters import TrainingInputParameters
from XMLHandler import XMLHandler
from VoxelNormalisation import VoxelNormalisation
from EnergyLabelDefinition import EnergyLabelDefinition

#input_files_path = "/eos/atlas/atlascerngroupdisk/proj-simul/VoxalisationOutputs/test_binning_r1251020emb1_r251020emb2_alpha8_depthVariables_2019_absphiMod"
input_files_path = "/eos/atlas/atlascerngroupdisk/proj-simul/VoxalisationOutputs/test_binning_2021_absphiMod_abseta_PerEventFromG4HitsEnergy_2"
pid = 22
particle="photons"
eta_min = 20
eta_max = 25
min_expE = 16
max_expE = 16
label_definition = EnergyLabelDefinition.MaxE
voxel_normalisation = VoxelNormalisation.normE
start_epoch = 0
max_epochs = 1000000
batchIter = 0
batchsize = 1024

def getBatchIter(batchIter, numberOfBunches):           
    if (batchIter > numberOfBunches -1):
        batchIter = 0
    
    return batchIter

def getTrainData(X_shuffled, label_shuffled, batchIter, batchsize ):
    firstEvent = batchsize*batchIter
    lastEvent = batchsize*(batchIter+1) 
    
    batchIter=batchIter + 1

    return np.array(X_shuffled[firstEvent:lastEvent]), label_shuffled[firstEvent:lastEvent], batchIter

voxInputs = InputParameters(input_files_path, particle, eta_min, eta_max)
inputsTraining = TrainingInputParameters(start_epoch, max_epochs, 1000, "GAN_Single65", "Sequential", [])
xml = XMLHandler(voxInputs)

dl = DataLoader(voxInputs, inputsTraining, xml)
X, Labels  = dl.getAllTrainData(min_expE, max_expE)
numberOfEvents = len(X)
numberOfBunches = int(numberOfEvents / batchsize)

for epoch in range(start_epoch, max_epochs):
  batchIter = getBatchIter(batchIter, numberOfBunches)
  if (batchIter == 0):
      print("shuffling")
      X_shuffled, label_shuffled = shuffle(X, Labels)   
  X_train, cond_label, batchIter = getTrainData(X_shuffled, label_shuffled, batchIter, batchsize)
  memory = getrusage(RUSAGE_SELF).ru_maxrss
  print('Iter: {}; batchIter:{}; Mem: {}'.format(epoch, batchIter, memory))

  if any(np.array_equal(X[0], x) for x in X_train):
    print("X[0]")
    print(X[0])
    print("X_train[0]")
    print(X_train[0])
    print("In batch")