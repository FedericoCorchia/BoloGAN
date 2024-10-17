#!/usr/bin/env python3

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

import numpy as np
import math
import argparse 
import os,sys,ctypes
import ROOT 
import shutil

ROOT.gROOT.SetMacroPath('./utils/')
ROOT.gROOT.Macro( "rootlogon.C" )
ROOT.gROOT.LoadMacro( "AtlasUtils.C" )
ROOT.gROOT.SetBatch(True)

sys.path.append('../models/tf/WGAN-GP/')

from conditional_wgangp import WGANGP
from InputParameters import InputParameters
from TrainingInputParameters import TrainingInputParameters
from VoxelNormalisation import VoxelNormalisation
from DataReader import DataLoader
from Label import Label
from XMLHandler import XMLHandler
from helper_functions import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
parser = argparse.ArgumentParser(description="Plot total energy")
parser.add_argument('-n',  '--n_events', default='10000')
parser.add_argument('-emin',  '--minEpoch', default='')
parser.add_argument('-emax',  '--maxEpoch', default='')
parser.add_argument('-step',  '--step', default='')
parser.add_argument('-v',  '--input_vox', default='')
parser.add_argument('-p',  '--pid', default='')
parser.add_argument('-e1',  '--eta_min', default='')
parser.add_argument('-e2',  '--eta_max', default='')
parser.add_argument('-idg', '--input_dir_gan', default='')
parser.add_argument('-o', '--output', default='')

args = parser.parse_args()
minEpoch=int(args.minEpoch)
maxEpoch=int(args.maxEpoch)
step=int(args.step)
n_events=int(args.n_events)
input_vox= args.input_vox
pid=int(args.pid)
eta_min=args.eta_min
eta_max=args.eta_max
input_dir_gan = args.input_dir_gan
output_gif = args.output

lparams = {'xoffset' : 0.1, 'yoffset' : 0.27, 'width'   : 0.8, 'height'  : 0.35}
canvases = []   

histos_vox = []
input_files_vox = []

minFactors = [3.5, 3.5, 3.5, 4.5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

if pid == 22 or pid == 11 :
  minFactor = 3
  maxFactor = 3  
else :
  minFactor = 4
  maxFactor = 3.5

particleName=""
particle=""
if pid == 22:
  particleName="#gamma"
  particle="photons"
elif pid == 211:
  particleName="#pi"
  particle="pions"
elif pid == 11:
  particleName="e"
  particle="electrons"

inputs = InputParameters(input_vox, particle, eta_min, eta_max)
inputsTraining = TrainingInputParameters(0, 0, 0, input_dir_gan, "", 0)
xml = XMLHandler(inputs)

maxEnergyVoxel = xml.GetTotalNumberOfEnergyBins()
firstPosition=inputsTraining.min_expE-8
if firstPosition < 0: 
  firstPosition = 0

dl = DataLoader(inputs, inputsTraining, xml)
if ( inputsTraining.voxel_normalisation == VoxelNormalisation.MaxVoxelAll):
  maxVoxel = dl.getMaxVoxelAll()
  print("MaxVoxel from All: " + str(maxVoxel))
elif ( inputsTraining.voxel_normalisation == VoxelNormalisation.MaxVoxelMid):
  maxVoxel = dl.getMaxVoxelMid()
  print("MaxVoxel from Mid: " + str(maxVoxel))
elif (inputsTraining.voxel_normalisation == VoxelNormalisation.midE):
  midEnergy = dl.getMidEnergy()
  print("Mid energy is: " + str(midEnergy))

ekins = dl.GetEkins()
E_max = np.max(ekins) #same E_max as DataReader

wgan = WGANGP(inputs, input_dir_gan)

print("Opening vox files")
for index, energy in enumerate(inputsTraining.momentums):    
  print(" Energy ", energies[item])
  input_file_vox = (input_vox + '/rootFiles/%s/pid%i_E%s_eta_%s_%s_nominal.root' % (particle, pid, energies[item], eta_min, eta_max))
  infile_vox = ROOT.TFile.Open(input_file_vox, 'read') 
  input_files_vox.append(infile_vox)
  tree = infile_vox.Get('rootTree') 
  
  h = ROOT.TH1F("h","",100,0,energies[item]*2) 
  tree.Draw("etot>>h","","off")
  xmax=h.GetBinCenter(h.GetMaximumBin());
  minX = max(0, xmax-minFactor*h.GetRMS()) #max(0, xmax-minFactors[item]*h.GetRMS())
  maxX = xmax+maxFactor*h.GetRMS()
  print("min "+ str(minX) + " max " + str(maxX))
      
  h_vox = ROOT.TH1F("h_vox","",30,minX,maxX) 
  tree.Draw("etot>>h_vox","","off")
  h_vox.Scale(1/h_vox.GetEntries())
  histos_vox.append(h_vox)

print ("Running from %i to %i in step of %i" %(minEpoch, maxEpoch, step))
for epoch in range(minEpoch, maxEpoch+step, step):
    print (epoch)
    histos_gan =[]
    canvas = ROOT.TCanvas('canvas_h', 'Total Energy comparison plots', 900, 900)
    canvases.append(canvas)
    canvas.Divide(4,4)
    chi2_tot = 0.
    ndf_tot = 0
    input_files_gan = []

    for item in range(0,len(energies)):   
      energy=energies[item]

      lab = Label(ekin_sample, n_events, E_max, eta_min, inputsTraining.label_definition)
      label = lab.GetLabelsAndPhiMod()
    
      data = wgan.load(epoch, particle, label, n_events, input_dir_gan,eta_min,eta_max)
   
      if (voxelNormalisation == "Energy" or voxelNormalisation == "normE"):
        data = data * energy       #needed for conditional
      elif (voxelNormalisation == "MaxVoxelMid"):
        dl = DataLoader(path, pid, eta_min, eta_max, 15, 15)
        maxVoxel = dl.getMaxVoxelMid()
        data = data * maxVoxel
        


      h_vox = histos_vox[item]
      h_gan = ROOT.TH1F("h_gan","",30,h_vox.GetXaxis().GetXmin(),h_vox.GetXaxis().GetXmax()) 

      for i in range (0, min(n_events,data.shape[0])):
        E_tot = data[i,:].sum(axis=0)
        h_gan.Fill(E_tot)

      h_gan.Scale(1/h_gan.GetEntries())
      h_gan.SetLineColor(ROOT.kRed)

      m = [h_vox.GetBinContent(h_vox.GetMaximumBin()),h_gan.GetBinContent(h_gan.GetMaximumBin())]
      h_vox.GetYaxis().SetRangeUser(0,max(m) *1.25)
      histos_gan.append(h_gan)
      h_vox.GetYaxis().SetTitle("Entries")      
      h_vox.GetXaxis().SetTitle("Energy [GeV]")      
      igood = ctypes.c_int(0)

     

      print("Epoch %s Energy %s \n" % (epoch, energy))

      # Plotting

      canvas.cd(item+1)
      histos_vox[item].Draw("HIST")
      histos_gan[item].Draw("HIST same")

      # Legend box                                                                                                                                                                            
      if (energy > 1024):
          energy_legend =  str(round(energy/1000,1)) + "GeV"
      else:
          energy_legend =  str(energy) + "MeV"
      t = ROOT.TLatex()
      t.SetNDC()
      t.SetTextFont(42)
      t.SetTextSize(0.1)
      t.DrawLatex(0.2, 0.83, energy_legend)
   
    # Total Energy chi2
    print("Epoch %s Total Energy \n" % (epoch))

    # Legend box particle
    leg = MakeLegend( lparams )
    leg.SetTextFont( 42 )
    leg.SetTextSize(0.1)
    canvas.cd(16)
    leg.AddEntry(h_vox,"Geant4","l") #Geant4
    leg.Draw()
    leg.AddEntry(h_gan,"GAN","l")  #WGAN-GP
    leg.Draw('same')
    legend = (particleName + ", " + str('{:.2f}'.format(int(eta_min)/100,2)) + "<|#eta|<" + str('{:.2f}'.format((int(eta_min)+5)/100,2)))
    ROOT.ATLAS_LABEL_BIG( 0.1, 0.9, ROOT.kBlack, legend )

    # Legend box Epoc&chi2 

    t = ROOT.TLatex()
    t.SetNDC()
    t.SetTextFont(42)
    t.SetTextSize(0.1)
    t.DrawLatex(0.1, 0.18, "Epoch: %s" % (epoch))


    #Copy best epoch files, including plots
    inputFile_Plot_png="%s/png/Plot_comparison_tot_energy_pid%s_eta_%s_%s_%s.png" % (output_gif, pid,eta_min,eta_max,epoch)
    inputFile_Plot_pdf="%s/pdf/Plot_comparison_tot_energy_pid%s_eta_%s_%s_%s.pdf" % (output_gif, pid,eta_min,eta_max,epoch)
    inputFile_Plot_C="%s/C/Plot_comparison_tot_energy_pid%s_eta_%s_%s_%s.C" % (output_gif, pid,eta_min,eta_max,epoch)
    inputFile_Plot_eps="%s/eps/Plot_comparison_tot_energy_pid%s_eta_%s_%s_%s.eps" % (output_gif, pid,eta_min,eta_max,epoch)
    canvas.SaveAs(inputFile_Plot_png) 
    canvas.SaveAs(inputFile_Plot_pdf) 
    canvas.SaveAs(inputFile_Plot_eps) 
    canvas.SaveAs(inputFile_Plot_C) 
 
