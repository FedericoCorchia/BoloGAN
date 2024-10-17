from EnergyLabelDefinition import EnergyLabelDefinition
from VoxelNormalisation import VoxelNormalisation
from SampleRange import SampleRange

class SetOptionsFromPath:
  #def __init__(self):
  #  self.energyLabel = 0
  #  self.voxelNormalisation = 0
  #  self.sampleRange = 0
  #  self.mergeBinAlphaFirstBinR = False
  
  @staticmethod
  def GetBaseOptions(path):
    mergeBinAlphaFirstBinR = False
    if ("mergeAlpha" in path):
      mergeBinAlphaFirstBinR = True
    
    symmetriseAlpha = False
    if ("Sim" in path):
      symmetriseAlpha = True

    #print("Running in folder: %s" % path)
    #print("-Merge alpha bins   : %s" % str(mergeBinAlphaFirstBinR))
    #print("-Symmetrised alpha  : %s" % str(symmetriseAlpha))

    return mergeBinAlphaFirstBinR, symmetriseAlpha
  
  @staticmethod
  def GetGANArchitecture(path):
    index = path.find('GAN_') + 4
    ganSuffix = path[index:]

    optimised = False
    if ("OPT" in ganSuffix):
      print(ganSuffix) 
      optimised = True
    
    return optimised
    
  @staticmethod
  def GetGANOptions(path):
    index = path.find('GAN_') + 4
    ganSuffix = path[index:]
    
    energyLabel = EnergyLabelDefinition.MaxE
    for enLabel in (EnergyLabelDefinition):
      if enLabel.name in ganSuffix:
        energyLabel = enLabel
    
    voxelNormalisation = VoxelNormalisation.normE
    for voxNorn in (VoxelNormalisation):
      if voxNorn.name in ganSuffix:
        voxelNormalisation = voxNorn
    
    sampleRange = SampleRange.All
    for range in (SampleRange):
      if range.name in ganSuffix:
        sampleRange = range
        
    #print("The GAN settings are:")
    #print("-Energy label       : %s" % energyLabel.name)
    #print("-Voxel normalisation: %s" % voxelNormalisation.name)
    #print("-Sample range       : %s" % sampleRange.name)
    
    return energyLabel, voxelNormalisation, sampleRange