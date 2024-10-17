import math

from SampleRange import SampleRange
from SetOptionsFromPath import SetOptionsFromPath
#from XMLHandler import XMLHandler

class VoxInputParameters():
  def __init__(self,vox_dir, particle, eta_min, eta_max, showParams=True, xmlFileName="binning.xml"):
    self.vox_dir = vox_dir 
    self.particle = particle 
    self.particleLatexName =""
    self.eta_min = int(eta_min) 
    self.eta_max = int(eta_max)
    self.SetPID()
    self.SetMass()
    self.SetmaxPhiMod()
    self.showParams = showParams
    self.xmlFileName = xmlFileName
    
    #These were always done via XML, for future optimisation we may need more options from path or other solutions
    self.mergeBinAlphaFirstBinR = None
    self.symmetriseAlpha = None
    self.optimisedAlpha = None
    self.isPolar = None
    self.region = 0

    if self.showParams:
      self.PrintBasicParameters()

  def SetmaxPhiMod(self):
    if(abs(self.eta_min)<1.425):
      self.maxPhiMod = math.pi/512
    else:
      self.maxPhiMod = math.pi/384

  def SetMass(self):
    self.mass = 0
    if self.pid == 22:
      self.mass = 0
    elif self.pid == 11:
      self.mass = 0.512
    elif self.pid == 211:
      self.mass = 139.6          
    elif self.pid == 2212:
      self.mass = 938.27
          
  def PrintBasicParameters(self):
    print ("Basic parameters")
    print (" Running in folder " + self.vox_dir + " using xml file: " + self.xmlFileName)
    print (" Particle ID " + str(self.pid) + " with mass: " + str(self.mass))
    print (" For eta slice " + str(self.eta_min) + " to " + str(self.eta_max))
    print ("")
        
  def PrintOtherParameters(self):
    print ("Other voxelisation parameters")
    print (" mergeBinAlphaFirstBinR : " + str(self.mergeBinAlphaFirstBinR))
    print (" symmetriseAlpha        : " + str(self.symmetriseAlpha))
    print (" optimisedAlpha         : " + str(self.optimisedAlpha))
    print (" isPolar                : " + str(self.isPolar))
    print (" region                 : " + str(self.isPolar))
    print ("")

  def SetPID(self):
    if (self.particle == "photons"):
      self.pid = 22
      self.pidForXML = 22
      self.particleLatexName = "#gamma"
    elif (self.particle == "pions"):
      self.pid = 211
      self.pidForXML = 211
      self.particleLatexName = "#pi^{#pm}"
    elif (self.particle == "electrons"):
      self.pid = 11
      self.pidForXML = 11
      self.particleLatexName = "e^{-}"
    elif (self.particle == "protons"):
      self.pid = 2212
      self.pidForXML = 211
      self.particleLatexName = "p^{+}"
    else:
      print("Invalid particle: " + self.particle)
      exit()
    