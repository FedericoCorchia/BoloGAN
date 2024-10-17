import os
import numpy as np
import pandas as pd
import math
import tensorflow as tf

use_uproot = False
if use_uproot:
    print('Using refactored code with TF2 and uproot')
    import uproot
    from scipy.interpolate import interp1d, InterpolatedUnivariateSpline
else:
    import ROOT
import copy

import random, numpy
random.seed(10)
numpy.random.seed(10)

from numpy import array

from VoxInputParameters import VoxInputParameters
from DataParameters import DataParameters
from VoxelNormalisation import VoxelNormalisation
from EnergyLabelDefinition import EnergyLabelDefinition

class DataLoader:
    def __init__(self, inputs, dataParameters): 
        self.inputs = inputs
        self.dataParameters = dataParameters

        self.ekin_all = []
        self.phimod_all = []
        self.eta_all = []
        self.Energies_all = []
        self.X_all = []
        self.Labels_all = []  
        self.maxVoxelAll = 0    
        self.maxVoxelMid = 0
        self.maxVoxels = []

        print ("************* DATA READER ***************")
        print ("Loading data")
        
        self.ekins = DataLoader.momentumsToEKins(self.dataParameters.momentums, self.inputs.mass)
        
        self.midEnergy = self.ekins[self.dataParameters.exp_mid_position]
        self.LoadData()

    def LoadData(self):
        print("----Loading files----")
        #print ("  Label is " + self.dataParameters.label_definition.name)
        #print ("  Normalised using " + self.dataParameters.voxel_normalisation.name)
        for index, p in enumerate(self.dataParameters.momentums):
            fileName = f"%s/csvFiles/pid%s/eta_%d_%d/pid%s_E%s_eta_%d_%d_voxalisation.csv" % (self.inputs.vox_dir, self.inputs.pid, self.inputs.eta_min, self.inputs.eta_max, self.inputs.pid, p, self.inputs.eta_min, self.inputs.eta_max)
            print("Opening file " + fileName)
            df = pd.read_csv(fileName, header=None, engine='python', dtype=np.float64)
            df = df.fillna(0)

            rootFileName = f"%s/rootFiles/pid%s/eta_%d_%d/pid%s_E%s_eta_%d_%d.root" % (self.inputs.vox_dir, self.inputs.pid, self.inputs.eta_min, self.inputs.eta_max, self.inputs.pid, p, self.inputs.eta_min,self.inputs.eta_max)
           
            phimod = df.iloc[ : , 0 ].to_numpy()
            etaColumn = abs(df.iloc[ : , 1 ].to_numpy())
            
            first_column = df.columns[0]
            second_column = df.columns[1]
#            df = df.drop([first_column], axis=1) #Removing the first element which is phiMod
#            df = df.drop([second_column], axis=1) #Removing the first element which is eta
           
            Energies=df.to_numpy()
            nevents=len(Energies)
            
            #Correction for phiMod, only for energy ranges that have it enabled
            if (self.dataParameters.correctPhiMod):
              if use_uproot:
                graph_uproot = uproot.open(rootFileName)['E_phiMod_shifted']
                fX, fY = graph_uproot.bases[0].member('fX'), graph_uproot.bases[0].member('fY')
                linear_interp = interp1d(fX, fY)
                linear_interp_extrap = InterpolatedUnivariateSpline(fX, fY, k=1)
                corrections = [ 1/linear_interp_extrap(x) for x in phimod ]
              else:
                rootFile = ROOT.TFile(rootFileName)
                graph = rootFile.Get("E_phiMod_shifted")
                corrections = [ 1/graph.Eval(x) for x in phimod ] #need to divide to correct the shape

              corrections = array([corrections,]).transpose()
              Energies = np.multiply(Energies, corrections)

            #Set array to zero to remove conditioning
            phimod = np.zeros(nevents)
            etaColumn = np.zeros(nevents)

            print("Loaded momentum " + str(p)) 
            print("from file " + fileName)
            print("with " + str(nevents) + " events")
            print("Vector of data of size " + str(len(Energies[0]))) 
            assert not np.any(np.isnan(Energies))
           
            ekin = np.array([self.ekins[index]] * nevents)
            
            self.ekin_all.append(ekin)
            self.phimod_all.append(phimod/self.inputs.maxPhiMod) 
            self.eta_all.append(etaColumn)
            self.Energies_all.append(Energies)
            self.E_min = np.min(self.ekins)
            self.E_max = np.max(self.ekins)

        self.CreateLabelsArray()
             
    def CreateLabelsArray(self):
        for index, ekin in enumerate(self.ekins):
            self.DefineEnergyLabels(index)
            #labels = np.vstack((self.ekin_all[index], self.phimod_all[index], self.eta_all[index])).T
            labels = np.vstack((self.ekin_all[index], self.eta_all[index])).T
            self.Labels_all.append(labels)
            self.NormaliseData(index)
            self.X_all.append(self.Energies_all[index])
        
    def DefineEnergyLabels(self, index):       
        ekin = self.ekin_all[index][0]
        label = DataLoader.energyLabel(self.dataParameters.label_definition, ekin, self.E_min, self.E_max)

        nevents = len(self.ekin_all[index])
        self.ekin_all[index] = np.array([label]*nevents)
                    
    def NormaliseData(self, index):
        if index == 0 :
            self.DefineNormalisationFactors()
        
        self.ApplyNormalisation(index)

    def DefineNormalisationFactors(self):
        if (self.dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelAll):
            self.maxVoxelAll = max(arr.max() for arr in self.X_all)
        if (self.dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelMid):
            self.maxVoxelMid = np.max(self.X_all[self.exp_mid_position]) 

    def ApplyNormalisation(self, index):
        Energies=self.Energies_all[index]
        ekin=self.ekins[index]
        
        if (self.dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelAll):
            Energies = Energies/self.maxVoxelAll            
            print("Data was normalised by %f" % self.maxVoxelAll)
        if (self.dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelMid):
            Energies = Energies/self.maxVoxelMid            
            print("Data was normalised by %f" % self.maxVoxelMid)
        if (self.dataParameters.voxel_normalisation == VoxelNormalisation.normE):
            Energies = Energies/ekin
            print("Data was normalised by %f" % ekin)
        if (self.dataParameters.voxel_normalisation == VoxelNormalisation.midE):
            print(Energies[0])
            Energies = Energies/self.midEnergy
            print("Data was normalised by %f" % self.midEnergy)
            print(Energies[0])
        if (self.dataParameters.voxel_normalisation == VoxelNormalisation.LogEnergy):
            logMom = math.log(ekin)
            Energies = Energies/logMom
            print("Data was normalised by %f" % logMom)
        if (self.dataParameters.voxel_normalisation
            == VoxelNormalisation.maxVoxelCurrent):
            maxVoxel = np.max(Energies)
            self.maxVoxels.append(maxVoxel)
            Energies = Energies/maxVoxel
            print("Data was normalised by %f" % maxVoxel)
        
        self.Energies_all[index] = Energies
        
    def getDim(self):
        return len(self.Energies_all[0][0])
        
    def getMaxVoxelMid(self):
        return self.maxVoxelMid 

    def getMaxVoxelAll(self):
        return self.maxVoxelAll

    def getMidEnergy(self):
        return self.midEnergy

    def getMaxVoxels(self):
        return self.maxVoxels

    def getAllTrainData(self, min, max):
        x_all = []
        label_all = []

        for i in range(min, max+1): 
            sampleIndex = i - self.dataParameters.min_expE
            x = copy.copy(self.X_all[sampleIndex])
            label = self.Labels_all[sampleIndex]

            x_all.extend(x)
            label_all.extend(label)

        x_all = [tf.convert_to_tensor(np.asarray(x), dtype=tf.float32) for x in x_all]
        label_all = [tf.convert_to_tensor(np.array(label), dtype=tf.float32) for label in label_all]

        return x_all, label_all
        
    @staticmethod
    def energyLabel(labelType, energy, E_min, E_max):
      if (labelType == EnergyLabelDefinition.LogE):
          print("return value %f, ekin %f, e_min %f, e_max %f" % (math.log(energy/E_min) / math.log(E_max/E_min), energy, E_min, E_max))
          return math.log(energy/E_min) / math.log(E_max/E_min)
      elif (labelType == EnergyLabelDefinition.MaxE):
          print("Label normalised by %d" % E_max)
          return energy/E_max 
      elif (labelType == EnergyLabelDefinition.Exp):
          print("Label log2 emergy %f" % energy)
          return math.log(energy, 2)

    @staticmethod
    def momentumsToEKins(momentums, mass):
      ekins = []
      for momentum in momentums:
        ekin = math.sqrt(momentum*momentum+mass*mass) - mass
        print(" %d %f " % (momentum, ekin))
        ekins.append(ekin)
      
      return ekins
