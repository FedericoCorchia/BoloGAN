import xml.etree.ElementTree as ET
import numpy as np
import math

from VoxInputParameters import VoxInputParameters

try:
    import ROOT
    found_ROOT = True
except ModuleNotFoundError:
    print("No root in this environment, will not use the functions linked to ROOT")
    found_ROOT = False
    # Error handling
    pass

class XMLHandler:

  def __init__(self, inputs):
    self.inputs = inputs
    self.correctCentre = False
    
    tree = ET.parse(self.inputs.vox_dir + "/" + self.inputs.xmlFileName)
    root = tree.getroot()
    
    #Complete the voxelisation input options reading the XML file
    self.inputs.optimisedAlpha = True if root.attrib['optimisedAlphaBins'] == "true" else False
    self.inputs.isPolar = True if root.attrib['isPolar'] == "true" else False 
    self.inputs.mergeBinAlphaFirstBinR = True if root.attrib['mergeAlphaBinsInFirstRBin'] == "true" else False     
    
    self.r_bins = []
    self.a_bins = []
    self.nBinAlphaPerlayer = []
    self.alphaListPerLayer = []
    
    self.r_edges = []
    self.r_midvalue = []
    self.r_midvalueCorrected = []
    self.relevantlayers = []
    self.layerWithBinningInAlpha = []

    self.eta_edges = []
    self.phi_edges = []
    self.eta_bins = []
    self.phi_bins = []
    
    self.etaRegion = 0
    
    for particle in root:
      for region in particle.findall('Bin'):
        if int(particle.attrib['pid']) == self.inputs.pidForXML and int(region.attrib['etaMin']) <= self.inputs.eta_min and int(region.attrib['etaMax']) >= self.inputs.eta_max:
          self.selectedParticleNode = particle
          self.selectedRegionNode = region
          self.inputs.symmetriseAlpha = True if particle.attrib['symmetriseAlpha'] == "true" else False 
          self.inputs.region = int(region.attrib['regionId'])
          self.GetGANPropertiesFromNode(self.selectedParticleNode)
          self.GetGANPropertiesFromNode(self.selectedRegionNode)     

          for layer in region:
            if (self.inputs.isPolar):
              self.ReadPolarCoordinates(layer)
            else:
              self.ReadCartesianCoordinates(layer)

    self.totalBins = 0
    self.bin_number = []

    self.eta_all_layers = []
    self.phi_all_layers = []

    if (self.inputs.isPolar):
      self.SetEtaAndPhiFromPolar()
    else:
      self.SetEtaAndPhiFromCartesian()
    
    self.bin_edges = [0]
    for i in range(len(self.bin_number)):
      self.bin_edges.append(self.bin_number[i] + self.bin_edges[i])

    if self.inputs.showParams:
      self.inputs.PrintOtherParameters()

  def ReadPolarCoordinates(self, subelem):
    bins = 0
    r_list = []
    if 'r_edges' in  subelem.attrib:
        str_r = subelem.attrib.get('r_edges')
        r_list = [float(s) for s in str_r.split(',')]
        bins = len(r_list) - 1
    else:
        bins = int(subelem.attrib.get('nbins'))
        rMin = int(subelem.attrib.get('r_min'))
        rMax = int(subelem.attrib.get('r_max'))
        for bin in range(0,bins+1):
            r_list.append(rMin + bin*(rMax-rMin)/bins)
       
    self.r_edges.append(r_list)
    self.r_bins.append(bins)
    layer = subelem.attrib.get('id')

    bins_in_alpha=int(subelem.attrib.get('n_bin_alpha'))
    self.a_bins.append(bins_in_alpha)
    self.r_midvalue.append(self.get_midpoint(r_list))
    if bins_in_alpha > 1:
      self.layerWithBinningInAlpha.append(int(layer))

      #print(layer)
    if found_ROOT and self.correctCentre:
      self.r_midvalueCorrected.append(self.GetMeanPointFromDistributionOfR(layer,r_list))
    
    #print(len(self.r_midvalue))
    #print(len(self.r_midvalueCorrected))
        
  def GetGANPropertiesFromNode(self, node):
    if 'latentDim' in node.attrib:
      self.latentDim = int(node.attrib['latentDim'])
    if 'generator' in node.attrib:
      self.generator = node.attrib['generator']
    if 'discriminator' in node.attrib:
      self.discriminator = node.attrib['discriminator']
    if 'learningRate' in node.attrib:
      self.learningRate = float(node.attrib['learningRate'])
    if 'batchSize' in node.attrib:
      self.batchSize = int(node.attrib['batchSize'])
    if 'lambda' in node.attrib:
      self.lam = float(node.attrib['lambda'])
    if 'gdratio' in node.attrib:
      self.gdratio = int(node.attrib['gdratio'])
    if 'beta' in node.attrib:
      self.beta = float(node.attrib['beta'])

    if 'label_definition' in node.attrib:
      self.label_definition = node.attrib['label_definition']
    if 'voxel_normalisation' in node.attrib:
      self.voxel_normalisation = node.attrib['voxel_normalisation']

  def SetGANPropertisFromEnergyRanges(self, energy_range):
    print("Searching for " + energy_range)
    for range in self.selectedParticleNode.find('EnergyRanges').findall('Range'):
      print("In range: " + range.attrib['name'])
      if range.attrib['name'] == energy_range:
        self.useBatchNormalisation = range.attrib['useBatchNormalisation'] == "True"
        self.activationFunction = range.attrib['activationFunction']
        self.GetGANPropertiesFromNode(range) 

  def GetMeanPointFromDistributionOfR(self, layer, r_list):
    rootFileName = self.inputs.vox_dir + "/rootFiles/pid"+str(self.inputs.pid)+"_E1048576_eta_"+str(self.inputs.eta_min)+"_"+str(self.inputs.eta_max)+".root"
    file = ROOT.TFile.Open(rootFileName, 'read')
    if file == None:
      print("Changing file, None")
      rootFileName = self.inputs.vox_dir + "/rootFiles/pid"+str(self.inputs.pid)+"_E2097152_eta_"+str(self.inputs.eta_min)+"_"+str(self.inputs.eta_max)+".root"
      file = ROOT.TFile.Open(rootFileName, 'read')
    if file.IsZombie():
      print("Changing file, zombie")
      rootFileName = self.inputs.vox_dir + "/rootFiles/pid"+str(self.inputs.pid)+"_E2097152_eta_"+str(self.inputs.eta_min)+"_"+str(self.inputs.eta_max)+".root"
      file = ROOT.TFile.Open(rootFileName, 'read')
    if file.GetNkeys() == 0:
      print("Changing file, no keys")
      rootFileName = self.inputs.vox_dir + "/rootFiles/pid"+str(self.inputs.pid)+"_E2097152_eta_"+str(self.inputs.eta_min)+"_"+str(self.inputs.eta_max)+".root"
      file = ROOT.TFile.Open(rootFileName, 'read')
       
    histoName="r"+layer+"w"
    h = file.Get(histoName)
    middle_points = []
    for i in range(len(r_list)-1):
      h.GetXaxis().SetRangeUser(r_list[i],r_list[i+1])
      middle_points.append(h.GetMean())
    
    return middle_points  

  def ReadCartesianCoordinates(self, subelem):
    bins = 0

    if 'eta_phi_edges' in  subelem.attrib:
      str = subelem.attrib.get('eta_phi_edges')
      list = [float(s) for s in str.split(',')]
      bins = len(list) - 1    
      self.eta_edges.append(list)
      self.phi_edges.append(list)
      self.eta_bins.append(bins)
      self.phi_bins.append(bins)
      
    else:
      if 'eta_edges' in  subelem.attrib:
        str = subelem.attrib.get('eta_edges')
        list = [float(s) for s in str.split(',')]
        bins = len(list) - 1  
        self.eta_edges.append(list)
        self.eta_bins.append(bins)

      if 'phi_edges' in  subelem.attrib:
        str = subelem.attrib.get('phi_edges')
        list = [float(s) for s in str.split(',')]
        bins = len(list) - 1  
        self.phi_edges.append(list)
        self.phi_bins.append(bins)
        
  def fill_r_a_lists(self, layer):
    no_of_rbins = self.r_bins[layer]
    list_mid_values = self.r_midvalue[layer]
    if found_ROOT and self.correctCentre:
      list_mid_values = self.r_midvalueCorrected[layer]
    list_a_values = self.alphaListPerLayer[layer]
    
    r_list = []
    a_list = []
    actual_no_alpha_bins = 0
    for i0 in range (0, no_of_rbins):
      actual_no_alpha_bins = self.nBinAlphaPerlayer[layer][i0]
      if (self.inputs.mergeBinAlphaFirstBinR == True and i0 == 0):
        actual_no_alpha_bins = 1
        list_mid_values[i0] = 0 #setting mid point to zero for first bin as the merged bin will be a circle which midpoint is the centre at r=0
      for j0 in range(0, actual_no_alpha_bins):       
        r_list.append(list_mid_values[i0])
        #print("Layer " + str(layer) + " bin in r: " + str(i0) + "/"+str(no_of_rbins))
        #print("N_bin alpha: " + str(j0) + "/"+ str(actual_no_alpha_bins) + " value of list alpha" + str(list_a_values[i0][j0]) + " with lenght " +str(len(list_a_values)))
        a_list.append(list_a_values[i0][j0])
    return r_list, a_list
    
  def get_midpoint(self, arr):
    middle_points = []
    for i in range(len(arr)-1):
        middle_value = arr[i] + float((arr[i+1] - arr[i]))/2
        middle_points.append(middle_value)
    return middle_points

  def SetEtaAndPhiFromPolar(self):
    self.minAlpha = 0
    if not self.inputs.symmetriseAlpha:
      #print("Alpha not symmetric")
      self.minAlpha = -math.pi
    
    self.SetNumberOfBins()
    
    #print("Total bins : %d" % self.totalBins)
            
    r_all_layers = []
    alpha_all_layers = []
    
    for layer in range(len(self.r_bins)):
        #print("the layer is : " + str(layer))
        #print(r_bins[layer]) 
        #print(a_bins[layer]) 
        #print(r_midvalue[layer]) 
        #print(alpha[layer])

        r_list, a_list = self.fill_r_a_lists(layer)              
        r_all_layers.append(r_list)
        alpha_all_layers.append(a_list)

    for layer in range(len(self.r_bins)):
        eta = r_all_layers[layer] * np.cos(alpha_all_layers[layer])
        self.eta_all_layers.append(eta)
        phi = r_all_layers[layer] * np.sin(alpha_all_layers[layer])
        self.phi_all_layers.append(phi)

        #print("the layer is : " + str(layer))
        #print(eta) 
        #print(phi) 
  
  def SetNumberOfBins(self):
    for layer in range(len(self.r_bins)):
      #print(str(i) + " " + str(mergeBinAlphaFirstBinR) + " " + str(totalBins))
      bin_no = 0
      alphaBinList = []
      nBinAlpha = []

      if (self.inputs.optimisedAlpha and self.a_bins[layer] > 1):
        edges = self.r_edges[layer]
        centres = self.r_midvalue[layer]
        for j in range(len(centres)):
          bins = self.AlphaBinPerRBin(edges[j], edges[j+1], centres[j])
          centres_alpha = self.get_midpoint(np.linspace(self.minAlpha , math.pi , bins+1))
          alphaBinList.append(centres_alpha)
          nBinAlpha.append(bins)
          bin_no += bins       
      else:
        bin_no = self.r_bins[layer]*self.a_bins[layer]
        #print(bin_no)
        centres_alpha = self.get_midpoint(np.linspace(self.minAlpha , math.pi , self.a_bins[layer]+1))
        for j in range(self.r_bins[layer]):  
          alphaBinList.append(centres_alpha)
          nBinAlpha.append(self.a_bins[layer])

      if self.inputs.mergeBinAlphaFirstBinR:
        bin_no = (self.r_bins[layer]-1)*self.a_bins[layer]+1
        #print("here")
        
      #print(nBinAlpha)
      #print(alphaBinList)
      self.alphaListPerLayer.append(alphaBinList)
      self.nBinAlphaPerlayer.append(nBinAlpha)

      self.totalBins += bin_no
      self.bin_number.append(bin_no)
      if self.r_bins[layer] > 0:
        self.relevantlayers.append(layer)
      

  def AlphaBinPerRBin(self, lowEdge, upEdge, binCentre):
    #print("Up "+str(upEdge)+" Low "+str(lowEdge)+" centre "+str(binCentre))
    widthBin = upEdge - lowEdge
    circumference = binCentre*2*math.pi
    if self.inputs.symmetriseAlpha:
          circumference = binCentre*math.pi
    bins = circumference / widthBin
    if (bins < 4):
      return 4
    elif (bins < 8):
      return 8
    elif (bins < 16):
      return 16
    else :
      return 32

  def SetEtaAndPhiFromCartesian(self):
    #print (len(self.eta_bins))
    for layer in range(len(self.eta_bins)):
      eta = self.get_midpoint(self.eta_edges[layer])
      self.eta_all_layers.append(eta)
      phi = self.get_midpoint(self.phi_edges[layer])
      self.phi_all_layers.append(phi)

      bin_no = self.eta_bins[layer]*self.phi_bins[layer]
      self.totalBins += bin_no
      self.bin_number.append(bin_no)
      if self.eta_bins[layer] > 0:
        self.relevantlayers.append(layer)    
    
  def GetTotalNumberOfBins(self):
    return self.totalBins
    
  def GetBinEdges(self):
    return self.bin_edges
  
  def GetEtaPhiAllLayers(self):
    return self.eta_all_layers, self.phi_all_layers
    
  def GetRelevantLayers(self):
    return self.relevantlayers
  
  def GetLayersWithBinningInAlpha(self):
    return self.layerWithBinningInAlpha
    
  def GetEtaRegion(self):
    return self.etaRegion