#!/usr/bin/env python3

import argparse 
import sys
import tf2onnx

sys.path.append('../../model/')
sys.path.append('../../common/')

from VoxInputParameters import VoxInputParameters
from XMLHandler import XMLHandler
from GANInputParameters import GANInputParametersFromXML
from conditional_wgangp import WGANGP

parser = argparse.ArgumentParser(description="Plot observables")
parser.add_argument('-e1', '--eta_min', default='')
parser.add_argument('-e2', '--eta_max', default='')
parser.add_argument('-v',  '--vox_dir', default='')
parser.add_argument('-ip', '--particle', default='')
parser.add_argument('-i', '--input_dir_gan', default='')
parser.add_argument('-o', '--output_dir', default='')
parser.add_argument('-r', '--energy_range', default='')

args = parser.parse_args()

eta_min = int(args.eta_min)
eta_max = int(args.eta_max)
particle = args.particle
input_dir_gan = args.input_dir_gan
output_dir = args.output_dir
vox_dir = args.vox_dir
energy_range = args.energy_range
 
for eta in range(eta_min,eta_max,5):
    print("----Converting eta %d-%d ---------" %(eta, eta+5))
    try:
        voxInputs = VoxInputParameters(vox_dir, particle, eta, eta+5, xmlFileName = "binning.xml")
        xml = XMLHandler(voxInputs)
        ganParameters = GANInputParametersFromXML(xml, energy_range)
        wgan = WGANGP(voxInputs, ganParameters)
        generatorModel = wgan.GetGenerator()
        output_path = "%s/neural_net_%s_eta_%s_%s_%s.onnx" % (output_dir, voxInputs.pid, voxInputs.eta_min, voxInputs.eta_max, ganParameters.energy_range)
        onnxModel = tf2onnx.convert.from_keras(generatorModel, output_path=output_path)

    except:
        print("Something went wrong in slice %s, moving to next one" % (eta))
        print("exception message ", sys.exc_info()[0])    
