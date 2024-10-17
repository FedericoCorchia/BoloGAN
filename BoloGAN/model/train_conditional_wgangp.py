import argparse

import sys
sys.path.append('../common/')

from conditional_wgangp import WGANGP
from InputParameters import InputParameters
from TrainingInputParameters import TrainingInputParameters
from EnergyLabelDefinition import EnergyLabelDefinition
from VoxelNormalisation import VoxelNormalisation
from SampleRange import SampleRange
    
if __name__=='__main__':
  parser = argparse.ArgumentParser(description="Train Gan")
  parser.add_argument('-ip', '--particle', default='')
  parser.add_argument('-e', '--firstEpoch', default='')
  parser.add_argument('-emin', '--eta_min', default='')
  parser.add_argument('-emax', '--eta_max', default='')
  parser.add_argument('-i', '--input_dir', default='')
  parser.add_argument('-odg', '--output_dir_gan', default='')
  args = parser.parse_args()

  particle = args.particle
  eta_min = str(args.eta_min)
  eta_max = str(args.eta_max)
  start_epoch = args.firstEpoch
  input_dir = args.input_dir
  output_dir_gan = args.output_dir_gan

  epochs = 2000000
  sample_interval = 1000
  total_time = []
  training_strategy = "Sequential"

  voxInputs = InputParameters(input_dir, particle, eta_min, eta_max)
  inputsTraining = TrainingInputParameters(start_epoch, epochs, sample_interval, output_dir_gan, training_strategy, total_time)
  wgan = WGANGP(voxInputs, output_dir_gan)
  wgan.train(inputsTraining)
  time_sum = sum(total_time)
  print (time_sum)
