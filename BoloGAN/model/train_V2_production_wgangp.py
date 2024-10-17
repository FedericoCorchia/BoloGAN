import argparse
import sys
sys.path.append('../common/')

from conditional_wgangp import WGANGP
from VoxInputParameters import VoxInputParameters
from XMLHandler import XMLHandler
from GANInputParameters import GANInputParametersFromXML
from DataParameters import DataParametersFromXML
from TrainingInputParameters import TrainingInputParametersFromSeed
    
if __name__=='__main__':
  parser = argparse.ArgumentParser(description="Train Gan")
  parser.add_argument('-ip', '--particle', default='')
  parser.add_argument('-e', '--firstEpoch', default='')
  parser.add_argument('-emin', '--eta_min', default='')
  parser.add_argument('-emax', '--eta_max', default='')
  parser.add_argument('-i', '--input_dir', default='')
  parser.add_argument('-r', '--energy_range', default='')
  parser.add_argument('-odg', '--output_dir_gan', default='')
  args = parser.parse_args()

  particle = args.particle
  eta_min = str(args.eta_min)
  eta_max = str(args.eta_max)
  start_epoch = args.firstEpoch
  input_dir = args.input_dir
  output_dir_gan = args.output_dir_gan
  energy_range = args.energy_range

  epochs = 1000000
  sample_interval = 1000
  training_strategy = "All"

  voxInputs = VoxInputParameters(input_dir, particle, eta_min, eta_max, xmlFileName="binning.xml")
  xml = XMLHandler(voxInputs)
  dataParameters = DataParametersFromXML(xml, energy_range)
  ganParameters = GANInputParametersFromXML(xml, energy_range)
  loading_dir=input_dir+"/Baseline_"+particle+"_lwtnn/"+energy_range+"/best_checkpoints_E"
  inputsTraining = TrainingInputParametersFromSeed(start_epoch, epochs, sample_interval, output_dir_gan, training_strategy, loading_dir)  
  wgan = WGANGP(voxInputs, ganParameters)
  wgan.train(inputsTraining, dataParameters) 