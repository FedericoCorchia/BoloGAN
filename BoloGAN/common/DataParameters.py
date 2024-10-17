from SetOptionsFromPath import SetOptionsFromPath
from EnergyLabelDefinition import EnergyLabelDefinition
from VoxelNormalisation import VoxelNormalisation
from SampleRange import SampleRange
from XMLHandler import XMLHandler

class DataParameters():
  def __init__(self):
    self.label_definition = None 
    self.voxel_normalisation = None
    self.sample_range = None
    
  def SetMomentumAndMidPosition(self):
    self.momentums = self.DefineMomentumList()
    self.exp_mid = int((self.max_expE + self.min_expE)/2)
    self.exp_mid_position = self.exp_mid - self.min_expE
    
  def Print(self):
    print ("Training data parameters")
    print (" * Label             : " + self.label_definition.name)
    print (" * vox normalisation : " + self.voxel_normalisation.name)
    print (" * correct phiMod    : " + str(self.correctPhiMod))
    print (" * Range             : " + self.sample_range.name)    
    print (" * Exponents range   : " + str(self.min_expE) + " to " + str(self.max_expE))
    print (" * Momentum list     : " + str(self.momentums))
    print (" * Mid point         : " + str(self.exp_mid) + " which is in position " +  str(self.exp_mid_position) )
    print ("")

  def SetRangeOfSamples(self, sample_range):
    if sample_range == SampleRange.All:
      return 8, 22
    elif sample_range == SampleRange.Low12:
      return 8, 12
    elif sample_range == SampleRange.Low13:
      return 8, 13 
    elif sample_range == SampleRange.Low14:
      return 8, 14 
    elif sample_range == SampleRange.Low15:
      return 8, 15 
    elif sample_range == SampleRange.High12:
      return 12, 22
    elif sample_range == SampleRange.High15:
      return 15, 22
    elif sample_range == SampleRange.High16:
      return 16, 22
    elif sample_range == SampleRange.High17:
      return 17, 22
    elif sample_range == SampleRange.High18:
      return 18, 22
    elif sample_range == SampleRange.High19:
      return 19, 22
    elif sample_range == SampleRange.Mid1218:
      return 12, 18
    elif sample_range == SampleRange.Mid1318:
      return 13, 18
    elif sample_range == SampleRange.Mid1217:
      return 12, 17
    elif sample_range == SampleRange.Mid1317:
      return 13, 17
    elif sample_range == SampleRange.Cell:
      return 10, 18
    elif sample_range == SampleRange.Single65:
      return 16, 16
    elif sample_range == SampleRange.UltraLow12:
      return 6, 12
    elif sample_range == SampleRange.Low10:
      return 8, 10
    elif sample_range == SampleRange.Mid1017:
      return 10, 17
    elif sample_range == SampleRange.High10:
      return 10, 22

  def DefineMomentumList(self):
    momentums = []
    for i in range(self.min_expE, self.max_expE+1):
       momentums.append(2**i)
    return momentums

  def InitExponentials(self):
    self.min_expE, self.max_expE = self.SetRangeOfSamples( self.sample_range )

    self.correctPhiMod = False
    hasFilesWithGraph = (self.xml.inputs.pid == 11 or self.xml.inputs.pid == 22)
    print(hasFilesWithGraph)
    if (self.max_expE >= 14 and hasFilesWithGraph):
      self.correctPhiMod = False #TURN BACK TO True ONCE DONE WITH CALOCHALLENGE
   
    self.SetMomentumAndMidPosition()
    self.Print()
    
class DataParametersFromPath(DataParameters):
  def __init__(self, GAN_dir):
    super().__init__()
    self.label_definition, self.voxel_normalisation, self.sample_range = SetOptionsFromPath.GetGANOptions(GAN_dir)
    self.InitExponentials()

class DataParametersFromXML(DataParameters):
  def __init__(self, xml, energy_range):
    super().__init__()
    self.xml = xml
    self.label_definition = EnergyLabelDefinition.MaxE
    for enLabel in (EnergyLabelDefinition):
      if enLabel.name in xml.label_definition:
        self.label_definition = enLabel
    
    self.voxel_normalisation = VoxelNormalisation.normE
    for voxNorn in (VoxelNormalisation):
      if voxNorn.name in xml.voxel_normalisation:
        self.voxel_normalisation = voxNorn
    
    self.sample_range = SampleRange.All
    for range in (SampleRange):
      if range.name in energy_range:
        self.sample_range = range
        
    self.InitExponentials()
