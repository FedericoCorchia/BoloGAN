#!/usr/bin/env python3

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

import numpy as np
import math
import argparse 
import os,sys,ctypes
import ROOT 
import ctypes
import shutil

ROOT.gROOT.SetMacroPath('./utils/')
ROOT.gROOT.Macro( "rootlogon.C" )
ROOT.gROOT.LoadMacro( "AtlasUtils.C" )
ROOT.gROOT.SetBatch(True)

sys.path.append('../models/tf/WGAN-GP/')

from conditional_wgangp import WGANGP
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
parser.add_argument('-b', '--binning', default='')
parser.add_argument('-norm', '--normalisation', default='Energy')
parser.add_argument('-l', '--label', default='LogE')
parser.add_argument('-v',  '--input_vox', default='')
parser.add_argument('-p',  '--pid', default='')
parser.add_argument('-e1',  '--eta_min', default='')
parser.add_argument('-e2',  '--eta_max', default='')
parser.add_argument('-idg', '--input_dir_gan', default='')
parser.add_argument('-s', '--save_plots', default='')
parser.add_argument('-o', '--output', default='')

args = parser.parse_args()
minEpoch=int(args.minEpoch)
maxEpoch=int(args.maxEpoch)
step=int(args.step)
n_events=int(args.n_events)
input_vox=args.input_vox
pid=int(args.pid)
eta_min=args.eta_min
eta_max=args.eta_max
input_dir_gan = args.input_dir_gan
save_plots = args.save_plots
output_best_checkpoints = args.output

histos_cog = ["delta_eta_1","delta_eta_2","delta_phi_1","delta_phi_2"]
branches_used = ["etot","delta_eta_1","delta_eta_2","delta_phi_1","delta_phi_2"]

lparams = {'xoffset' : 0.1, 'yoffset' : 0.27, 'width'   : 0.8, 'height'  : 0.35}
    
histos_vox = []
for i in range (0,5):
  variable = []
  histos_vox.append(variable)

input_files_vox = []

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

maxVoxel = 0
midEnergy = 0

inputs = TrainingInputParameters(minEpoch, maxEpoch, step, input_dir_gan, particle,eta_min,eta_max, "sequential", 0)
xml = XMLHandler(input_vox, pid, eta_min, eta_max, inputs.mergeBinAlphaFirstBinR)
maxEnergyVoxel = xml.GetTotalNumberOfEnergyBins()
E_max = np.max(inputs.energies) #same E_max as DataReader

if ( inputs.voxel_normalisation == VoxelNormalisation.MaxVoxelAll):
  dl = DataLoader(input_vox, pid, eta_min, eta_max, inputs.min_expE, inputs.max_expE, inputs.label_definition, inputs.voxel_normalisation)
  maxVoxel = dl.getMaxVoxelAll()
  print("MaxVoxel from All: " + str(maxVoxel))
elif ( inputs.voxel_normalisation == VoxelNormalisation.MaxVoxelMid):
  dl = DataLoader(input_vox, pid, eta_min, eta_max, inputs.min_expE, inputs.max_expE, inputs.label_definition, inputs.voxel_normalisation)
  maxVoxel = dl.getMaxVoxelMid()
  print("MaxVoxel from Mid: " + str(maxVoxel))
elif (inputs.voxel_normalisation == VoxelNormalisation.midE):
  dl = DataLoader(input_vox, pid, eta_min, eta_max, inputs.min_expE, inputs.max_expE, inputs.label_definition, inputs.voxel_normalisation)
  midEnergy = dl.getMidEnergy()
  print("Mid energy is: " + str(midEnergy))

wgan = WGANGP(particle,eta_min,eta_max,input_vox, inputs.mergeBinAlphaFirstBinR)

print("Opening vox files")
for index, energy in enumerate(inputs.energies):
  input_file_vox = (input_vox + '/rootFiles/%s/pid%i_E%s_eta_%s_%s_voxalisation.root' % (particle, pid, energy, eta_min, eta_max))
  infile_vox = ROOT.TFile.Open(input_file_vox, 'read') 
  input_files_vox.append(infile_vox)
  tree = infile_vox.Get('rootTree')
  
  print(" Energy ", energy)
  
  h = ROOT.TH1F("h","",100,0,energy*2) 
  tree.Draw("etot>>h","","off")
  xmax=h.GetBinCenter(h.GetMaximumBin());
  minX = max(0, xmax-minFactor*h.GetRMS()) 
  maxX = xmax+maxFactor*h.GetRMS()
  del h 
  print("min "+ str(minX) + " max " + str(maxX))
      
  h_vox = ROOT.TH1F("h_vox","",30,minX,maxX) 
  tree.Draw("etot>>h_vox","","off")
  h_vox.Scale(1/h_vox.GetEntries())
  histos_vox[0].append(h_vox)

  i = 1
  for histo in histos_cog:
    print(" COG ", histo)
    
    h = ROOT.TH1F("h","",100,-20,20) 
    tree.Draw(histo+">>h","","off")
    xmax=h.GetBinCenter(h.GetMaximumBin());
    minX = xmax-3*h.GetRMS()
    maxX = xmax+3*h.GetRMS()
    print("max: " + str(h.GetMaximumBin()) + " xmax: " + str(xmax) + " min "+ str(minX) + " max " + str(maxX))   
    del h 
        
    name="h_cog_"+histo
    h_cog = ROOT.TH1F(name,"",30,minX,maxX) 
    tree.Draw(histo+">>"+name,"","off")
    h_cog.Scale(1/h_cog.GetEntries())
    histos_vox[i].append(h_cog)
    i = i + 1

print ("Running from %i to %i in step of %i" %(minEpoch, maxEpoch, step))
for epoch in range(minEpoch, maxEpoch+step, step):
  #try:
    print (epoch)
    histos_gan = []
    input_files_gan = []
    canvases = []

    for index, energy in enumerate(inputs.energies):     
      lab = Label(energy, n_events, E_max, inputs.label_definition)
      label, phiMod = lab.GetLabelsAndPhiMod()

      data = wgan.load(epoch, particle, label, n_events, input_dir_gan,eta_min,eta_max)
   
      if (inputs.voxel_normalisation == VoxelNormalisation.normE):
        data = data * energy       #needed for conditional
        #print("Normalisation value ", energy)
      elif (inputs.voxel_normalisation == VoxelNormalisation.MaxVoxelAll):
        data = data * maxVoxel
        #print("Normalisation value ", maxVoxel)
      elif (inputs.voxel_normalisation == VoxelNormalisation.MaxVoxelMid):
        data = data * maxVoxel
        #print("Normalisation value ", maxVoxel)
      elif (inputs.voxel_normalisation == VoxelNormalisation.midE):
        #print(data[0])
        #print(data[0].sum())
        data = data * midEnergy
        #print("Normalisation value ", dl.getMidEnergy)
        
      print ("Creating temp ROOT file for energy %s" % (energy) )
      output_file_gan = output_best_checkpoints + "/tmp/pid%s_E%s_eta_%s_%s_GAN.root" % (pid, energy, eta_min, eta_max)
      output_file = ROOT.TFile((output_file_gan) ,"RECREATE")
      rootTree = ROOT.TTree("rootTree","A ROOT tree");
      print ("fill file")
      print(input_vox)
      fill_ttree(input_vox, eta_min, eta_max, pid, False, data, phiMod, rootTree, n_events, inputs.mergeBinAlphaFirstBinR)
      print ("write file")
      output_file.Write()
      print ("append file")
      input_files_gan.append(output_file)
      del rootTree

      #for i in range (0, min(n_events,data.shape[0])):
      #  E_tot = data[i,:].sum(axis=0)
        
    index_branch = 0
    chi2_tot_all = 0.
    ndf_tot_all = 0
    for branch in branches_used:
      print(branch)
      name="canvas_"+branch
      canvas = ROOT.TCanvas(name, 'Total Energy comparison plots', 900, 900)
      canvases.append(canvas)
      canvas.Divide(4,4)
      chi2_tot = 0.
      ndf_tot = 0
      for index, energy in enumerate(inputs.energies):
        #print(energy)
        
        h_vox = histos_vox[index_branch][index]
        name="h_gan_%d_%s" % (energy, branch)
        h_gan = ROOT.TH1F(name,"",30,h_vox.GetXaxis().GetXmin(),h_vox.GetXaxis().GetXmax()) 
        
        #print("h_vox", h_vox.GetEntries()," ", h_vox.GetMaximum())
        file = input_files_gan[index]
        tree = file.Get('rootTree')
        tree.Draw(branch+">>"+name,"","off")

        h_gan.Scale(1/h_gan.GetEntries())
        h_gan.SetLineColor(ROOT.kRed)

        m = [h_vox.GetBinContent(h_vox.GetMaximumBin()),h_gan.GetBinContent(h_gan.GetMaximumBin())]
        h_vox.GetYaxis().SetRangeUser(0,max(m) *1.25)
        
        #print("h_gan", h_gan.GetEntries()," ", h_gan.GetMaximum())
        histos_gan.append(h_gan)

        chi2 = ctypes.c_double(0.)
        ndf = ctypes.c_int(0)
        igood = ctypes.c_int(0)

        h_vox.Chi2TestX(h_gan, chi2, ndf, igood, "WW")
       
        ndf = ndf.value
        chi2=chi2.value
        chi2_tot += chi2
        ndf_tot += ndf

        print("Epoch %s Energy %s : chi2/ndf = %.1f / %i = %.1f\n" % (epoch, energy, chi2, ndf, chi2/ndf))

        # Plotting
        canvas.cd(index+1)
        h_vox.Draw("HIST")
        h_gan.Draw("HIST same")

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
      chi2_o_ndf = chi2_tot / ndf_tot
      print("Epoch %s, barcnh %s : chi2/ndf = %.1f / %i = %.3f\n" % (epoch, branch, chi2_tot, ndf_tot, chi2_o_ndf))

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
      t.DrawLatex(0.1, 0.07, "#scale[0.8]{#chi^{2}/NDF = %.0f/%i = %.1f}" % (chi2_tot, ndf_tot, chi2_o_ndf))

      index_branch += 1
      chi2_tot_all += chi2_tot
      ndf_tot_all += ndf_tot  
    
      
    
    #### Calculate total chi2 for all variables
    chi2_o_ndf = chi2_tot_all / ndf_tot_all
    print("Epoch %s all variables : chi2/ndf = %.1f / %i = %.3f\n" % (epoch, chi2_tot_all, ndf_tot_all, chi2_o_ndf))
    chi2File = "%s/chi2/chi2_%s_%s_%s.txt" % (output_best_checkpoints, pid, eta_min, eta_max)
    f = open(chi2File, 'a')
    f.write("%s %.3f\n" % (epoch, chi2_o_ndf))
    f.close()
    
    #for item in range(0,len(energies)):
    #  file = input_files_gan[item]
    #  file.Close()

    #Copy best epoch files, including plots
    epochs, chi2_o_ndf_list = np.loadtxt(chi2File, delimiter=' ', unpack=True)
    if round(chi2_o_ndf,3) <= np.amin(chi2_o_ndf_list):
      print ("Better chi2, creating files in %s/../best_checkpoints" %(input_dir_gan))
      for i, branch in enumerate(branches_used):
        inputFile_Plot_png="%s/png/Plot_comparison_%s_pid%s_eta_%s_%s.png" % (output_best_checkpoints, branch, pid,eta_min,eta_max)
        inputFile_Plot_pdf="%s/pdf/Plot_comparison_%s_pid%s_eta_%s_%s.pdf" % (output_best_checkpoints, branch, pid,eta_min,eta_max)
        canvases[i].SaveAs(inputFile_Plot_png) 
        canvases[i].SaveAs(inputFile_Plot_pdf) 

      inputFile_Meta = "%s/%s/checkpoints_eta_%s_%s/model_%s.ckpt.meta" % (input_dir_gan, particle, eta_min,eta_max,epoch)
      inputFile_Index = "%s/%s/checkpoints_eta_%s_%s/model_%s.ckpt.index" % (input_dir_gan, particle, eta_min,eta_max,epoch)
      inputFile_Data = "%s/%s/checkpoints_eta_%s_%s/model_%s.ckpt.data-00000-of-00001" % (input_dir_gan, particle, eta_min,eta_max,epoch)
      outputFile_Meta = "%s/model_%s_%s_%s.ckpt.meta" % (output_best_checkpoints, particle, eta_min,eta_max)
      outputFile_Index = "%s/model_%s_%s_%s.ckpt.index" % (output_best_checkpoints, particle, eta_min,eta_max)
      outputFile_Data = "%s/model_%s_%s_%s.ckpt.data-00000-of-00001" % (output_best_checkpoints, particle, eta_min,eta_max)
      shutil.copyfile(inputFile_Meta, outputFile_Meta)
      shutil.copyfile(inputFile_Index, outputFile_Index)
      shutil.copyfile(inputFile_Data, outputFile_Data)
      print("Epoch with lowest chi2/ndf is %s with a value of %.3f" % (epoch, chi2_o_ndf))
      #Now save best epoch number to file
      chi2File = "%s/chi2/epoch_best_chi2_%s_%s_%s.txt" % (output_best_checkpoints, pid, eta_min,eta_max)
      f = open(chi2File, 'w')
      f.write("%s %.3f\n" % (epoch, chi2_o_ndf))
      f.close()

      if not os.path.exists(output_best_checkpoints + '/GAN_ROOT_files/%s/' % (particle)):
        os.makedirs(output_best_checkpoints + '/GAN_ROOT_files/%s/' % (particle), exist_ok=True)

      for index, energy in enumerate(inputs.energies):
        tmp_root = output_best_checkpoints + "/tmp/pid%s_E%s_eta_%s_%s_GAN.root" % (pid, energy, eta_min, eta_max)
        best_epoch_root = output_best_checkpoints + "/GAN_ROOT_files/%s/pid%s_E%s_eta_%s_%s_GAN.root" % (particle, pid, energy, eta_min, eta_max)
        shutil.copyfile(tmp_root, best_epoch_root)

    else:
      print ("Current chi2 was: %f, the best chi2 is %f " %(round(chi2_o_ndf,3), np.amin(chi2_o_ndf_list)))

    if (save_plots == "True") :
      for i, branch in enumerate(branches_used):
        inputFile_Plot_png="%s/png/Plot_comparison_%s_pid%s_eta_%s_%s_%s.png" % (output_best_checkpoints, branch, pid,eta_min,eta_max,epoch)
        inputFile_Plot_pdf="%s/pdf/Plot_comparison_%s_pid%s_eta_%s_%s_%s.pdf" % (output_best_checkpoints, branch, pid,eta_min,eta_max,epoch)
        canvases[i].SaveAs(inputFile_Plot_png) 
        canvases[i].SaveAs(inputFile_Plot_pdf) 

  #except:
  #  print("Something went wrong in epoch %s, moving to next one" % (epoch))

