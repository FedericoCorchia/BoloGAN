import numpy as np
import math

from EnergyLabelDefinition import EnergyLabelDefinition
from DataReader import DataLoader

class Label:
    def __init__(self, energy, nevents, E_min, E_max, eta_min, energyLabelType): 
        self.nevents = nevents
        self.energy = energy
        self.E_min = E_min
        self.E_max = E_max
        self.eta_min = int(eta_min)/100.
        self.eta_max = (int(eta_min) + 5)/100.
        self.energyLabel = 0
        self.SetEnergyLabel(energyLabelType)
        self.SetmaxPhiMod()       

    def SetmaxPhiMod(self):
        if(abs(self.eta_min)<1.425):
          self.maxPhiMod = math.pi/512
        else:
          self.maxPhiMod = math.pi/384

    
    def SetEnergyLabel(self, energyLabelType):
        print ("Nevents ", self.nevents)
        print ("Energy ", self.energy)
        print ("MaxE ", self.E_max)
        print ("energyLabelType ", energyLabelType)

        self.energyLabel = DataLoader.energyLabel(energyLabelType, self.energy, self.E_min, self.E_max)
        print ("energyLabel ", self.energyLabel)

        #if (energyLabelType == EnergyLabelDefinition.LogE):
        #  return math.log(self.energy/self.E_min) / math.log(self.E_max/self.E_min)
        #elif (energyLabelType == EnergyLabelDefinition.MaxE):
        #  return self.energy/self.E_max
        #elif (energyLabelType == EnergyLabelDefinition.Log2E):
        #  return math.log(self.energy,2)

    def GetLabelsAndPhiMod(self):
        energyArray = np.array([self.energyLabel] * self.nevents)

        #The line below can be used to condition on eta
        #etaArray = np.random.uniform(low=self.eta_min, high=self.eta_max, size=self.nevents)
        etaArray = np.zeros(self.nevents) 

        labels = np.vstack((energyArray, etaArray)).T

        #print("<Label>: Labels, PhiMod and Eta are:")
        #print(energyArray)
        #print(phiModArray)
        #print(etaArray)
        return labels
        
    def phiMod(self, x):
        if self.eta_max<1.425:
          return math.fmod(x,math.pi/512.)/self.maxPhiMod #/0.006
        else:
          return math.fmod(x,math.pi/384.)/self.maxPhiMod
        
