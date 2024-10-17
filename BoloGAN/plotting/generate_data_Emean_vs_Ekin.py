import argparse
import ROOT
import os,sys,ctypes
import math
import numpy as np

from ROOT import TCanvas, TGraph, TGraphErrors, TMultiGraph
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.SetMacroPath('./utils/')
ROOT.gROOT.Macro( "rootlogon.C" )
ROOT.gROOT.LoadMacro( "AtlasUtils.C" )

sys.path.append('../model/')
sys.path.append('../common/')
sys.path.append('../../scripts')

from VoxInputParameters import VoxInputParameters
from DataParameters import DataParametersFromXML
from XMLHandler import XMLHandler
from DataReader import DataLoader

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

parser = argparse.ArgumentParser(description="Plots Etot mean and RMS")
parser.add_argument('-e1', '--eta_min', default='')
parser.add_argument('-e2', '--eta_max', default='')
parser.add_argument('-ip', '--particle', default='')
parser.add_argument('-v', '--vox_dir', default='')
parser.add_argument('-d', '--output_dir', default='')
parser.add_argument('-o', '--best_checkpoints_dir', default='')
parser.add_argument('-p', '--pid', default='')
parser.add_argument('-r', '--energy_range', default='')
args = parser.parse_args()

particle = args.particle
vox_dir = args.vox_dir
eta_min = int(args.eta_min)
eta_max = int(args.eta_max)
output_dir = args.output_dir
best_checkpoints_dir = args.best_checkpoints_dir
pid=int(args.pid)
energy_range = args.energy_range

###################################################################

if pid == 22 or pid == 11 :
    minFactor = 3
    maxFactor = 3  
else :
    minFactor = 4
    maxFactor = 3.5

voxInputs = VoxInputParameters(vox_dir, particle, eta_min, eta_max, xmlFileName = "binning.xml")
xml = XMLHandler(voxInputs)
dataParameters = DataParametersFromXML(xml, energy_range)
ekins = DataLoader.momentumsToEKins(dataParameters.momentums, voxInputs.mass)

RatioFile = (output_dir + "Ratio_Ekin_100bins_%s_%d.txt" % (particle,eta_min))

print("here")
f = open(RatioFile, 'w')
for index, momentum in enumerate(dataParameters.momentums):

    file_1 = ROOT.TFile.Open(vox_dir + 'rootFiles/%s/pid%s_E%s_eta_%s_%s.root' % (particle,pid,momentum,eta_min,eta_max), 'read')
    tree_1 = file_1.Get('rootTree')

    file_2 = ROOT.TFile.Open(best_checkpoints_dir + '/GAN_ROOT_files/%s/pid%s_E%s_eta_%s_%s_GAN.root' % (particle,pid,momentum,eta_min,eta_max), 'read')
    tree_2 = file_2.Get('rootTree')
    
    ROOT.TH1.StatOverflows(True)   
    h = ROOT.TH1F("h","",30,0,momentum*1.5) 
    tree_1.Draw('etot>>h',"","off")
    xmax=h.GetBinCenter(h.GetMaximumBin())
    minX = max(0, xmax-minFactor*h.GetRMS())
    maxX = xmax+maxFactor*h.GetRMS()

    print(" Momentum ", momentum)
    h1 = ROOT.TH1F("h1","",30,minX,maxX) 
    h2 = ROOT.TH1F("h2","",30,minX,maxX) 
    tree_1.Draw('etot>>h2',"","off")
    tree_2.Draw('etot>>h1',"","off")
    h1.Scale(1/h1.GetEntries())
    h2.Scale(1/h2.GetEntries())

    RMS_Gan = h1.GetRMS()
    RMS_Vox = h2.GetRMS()

    mean_Gan = h1.GetMean()
    mean_Vox = h2.GetMean()

    ekin = ekins[index]
    ratio_mean_Gan = mean_Gan/ekin
    ratio_rms_Gan = RMS_Gan/ekin   

    f.write("%s %.5f %.5f %.3f \n" % (math.log(ekin), ratio_mean_Gan, ratio_rms_Gan, 0))

f.close()

