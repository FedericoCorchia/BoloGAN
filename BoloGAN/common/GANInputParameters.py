from SetOptionsFromPath import SetOptionsFromPath
from VoxInputParameters import VoxInputParameters
import json

class GANInputParameters():
  def __init__(self):
    self.batchsize = 128
    self.D_lr = self.G_lr = 1e-4
    self.D_beta1 = self.G_beta1 = 0.55
    self.conditional_dim = 2
    self.lam = 10

    self.latent_dim = 50
    self.generatorLayers = [50, 100,200]

    self.n_disc = 5

    self.discriminatorLayers = []
    self.nvoxels = 0
    self.useBatchNormalisation = False
    self.activationFunction = ""
    self.energy_range = ""

  def Print(self):
    [generatorLayersString, discriminatorLayersString] = list(map(GANInputParameters.layerSizesToString, [self.generatorLayers, self.discriminatorLayers]))
    print("Initialised GAN with HP")
    print("  * BEnergy range               : " + str(self.energy_range))
    print("  * Batch Size                  : " + str(self.batchsize))
    print("  * Lambda                      : " + str(self.lam))
    print("  * Training d/g                : " + str(self.n_disc))
    print("  * Generator learning rate     : " + str(self.G_lr))
    print("  * Discriminator learning rate : " + str(self.D_lr))
    print("  * Generator momentum          : " + str(self.G_beta1))
    print("  * Discriminator momentum      : " + str(self.D_beta1))
    print("  * Latent space                : " + str(self.latent_dim))
    print("  * Generator layers            : " + generatorLayersString)
    print("  * Discriminator layers        : " + discriminatorLayersString)
    print("  * Image size                  : " + str(self.nvoxels))
    print("  * Use Batch Normalisation     : " + str(self.useBatchNormalisation))
    print("  * Activation function         : " + str(self.activationFunction))

 
  @staticmethod
  def layerSizesToString(layerSizes):
    return ", ".join([str(layer) for layer in layerSizes])
 
class GANInputParametersFromXML(GANInputParameters):
  def __init__(self, xml, energy_range):
    super().__init__()
    self.energy_range = energy_range
    xml.SetGANPropertisFromEnergyRanges(energy_range)
    self.nvoxels = xml.GetTotalNumberOfBins()
    self.latent_dim = xml.latentDim
    self.generatorLayers = list(map(int, xml.generator.split(",")))
    if hasattr(xml, 'discriminator'):
      self.discriminatorLayers = list(map(int, xml.discriminator.split(",")))
    else:
      #self.discriminatorLayers = [self.nvoxels*2, self.nvoxels*2, self.nvoxels*2]
      self.discriminatorLayers = [self.nvoxels, self.nvoxels, self.nvoxels]
    self.G_lr = self.D_lr = xml.learningRate
    self.batchsize = xml.batchSize
    self.lam = xml.lam
    self.n_disc = xml.gdratio
    self.G_beta1 = self.D_beta1 = xml.beta
    self.useBatchNormalisation = xml.useBatchNormalisation
    self.activationFunction = xml.activationFunction

    self.Print()

class GANInputParametersFromPath(GANInputParameters):
  def __init__(self, output_dir_gan):
    super().__init__()
    self.latent_dim = SetOptionsFromPath.getLatentDimension(output_dir_gan)
    self.generatorLayers = SetOptionsFromPath.getGeneratorLayers(output_dir_gan)
    self.discriminatorLayers = SetOptionsFromPath.getDiscriminatorLayers(output_dir_gan)
    self.n_disc = SetOptionsFromPath.getDiscriminatorIterations(output_dir_gan)
    if (SetOptionsFromPath.GetGANArchitecture(output_dir_gan)):
      ## HPO values
      self.batchsize = 1024
      self.lam = 3
      self.D_lr = self.G_lr = 5e-5
    self.Print()
    
class GANInputParametersFromJSON(GANInputParameters):
  def __init__(self):
    super().__init__()
    with open('input.json', 'r') as fp:
      idds_params = json.load(fp)[1]
      print('Get point from iDDS', idds_params)
      self.D_lr = idds_params.get('D_lr', self.D_lr)
      self.G_lr = idds_params.get('G_lr', self.G_lr)
      self.D_beta1 = idds_params.get('D_beta1', self.D_beta1)
      self.G_beta1 = idds_params.get('G_beta1', self.G_beta1)
      self.batchsize = idds_params.get('batch_size', self.batchsize)
      self.lam = idds_params.get('lam', self.lam)

    self.Print()
 
