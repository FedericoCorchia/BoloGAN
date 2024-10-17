#!/usr/bin/env python3
import numpy as np
import math
import argparse 
import os,sys,ctypes
import shutil
import ctypes
import glob

sys.path.append('../model/')
sys.path.append('../common/')
sys.path.append('../../scripts')

from conditional_wgangp import WGANGP

import ROOT
ROOT.gROOT.SetMacroPath('./utils/')
ROOT.gROOT.Macro( "rootlogon.C" )
ROOT.gROOT.LoadMacro( "AtlasUtils.C" )
ROOT.gROOT.SetBatch(True)

from VoxInputParameters import VoxInputParameters
from DataParameters import DataParametersFromXML
from GANInputParameters import GANInputParametersFromXML
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
parser.add_argument('-v',  '--vox_dir', default='')
parser.add_argument('-ip',  '--particle', default='')
parser.add_argument('-e1',  '--eta_min', default='')
parser.add_argument('-e2',  '--eta_max', default='')
parser.add_argument('-idg', '--input_dir_gan', default='')
parser.add_argument('-s', '--save_plots', default='')
parser.add_argument('-o', '--output', default='')
parser.add_argument('-r', '--energy_range', default='')
parser.add_argument('--seed', dest='seed', action='store_true')
parser.add_argument('--no-seed', dest='seed', action='store_false')
parser.set_defaults(seed=False)

args = parser.parse_args()
minEpoch=int(args.minEpoch)
maxEpoch=int(args.maxEpoch)
step=int(args.step)
n_events=int(args.n_events)
vox_dir= args.vox_dir
particle=args.particle
eta_min=args.eta_min
eta_max=args.eta_max
input_dir_gan = args.input_dir_gan
save_plots = args.save_plots
output_best_checkpoints = args.output
isSeed = args.seed
energy_range = args.energy_range

preliminary = False

lparams = {'xoffset' : 0.1, 'yoffset' : 0.27, 'width'   : 0.8, 'height'  : 0.35}
canvases = []   

histos_vox = []
input_files_vox = []

minFactors = [3.5, 3.5, 3.5, 4.5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

maxVoxel = 0
midEnergy = 0

voxInputs = VoxInputParameters(vox_dir, particle, eta_min, eta_max, xmlFileName = "binning.xml")
xml = XMLHandler(voxInputs)
dataParameters = DataParametersFromXML(xml, energy_range)
ekins = DataLoader.momentumsToEKins(dataParameters.momentums, voxInputs.mass)
E_min = np.min(ekins) # Same E_min as DataReader.
E_max = np.max(ekins) # Same E_max as DataReader.
ganParameters = GANInputParametersFromXML(xml, energy_range)
wgan = WGANGP(voxInputs, ganParameters)

if voxInputs.pid == 22 or voxInputs.pid == 11 :
  minFactor = 3
  maxFactor = 3  
else :
  minFactor = 4
  maxFactor = 3.5

firstPosition=dataParameters.min_expE-8
if firstPosition < 0: 
  firstPosition = 0

if ( dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelAll):
  dl = DataLoader(voxInputs, dataParameters)
  maxVoxel = dl.getMaxVoxelAll()
  print("MaxVoxel from All: " + str(maxVoxel))
elif ( dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelMid):
  dl = DataLoader(voxInputs, dataParameters)
  maxVoxel = dl.getMaxVoxelMid()
  print("MaxVoxel from Mid: " + str(maxVoxel))
elif (dataParameters.voxel_normalisation == VoxelNormalisation.midE):
  dl = DataLoader(voxInputs, dataParameters)
  midEnergy = dl.getMidEnergy()
  print("Mid energy is: " + str(midEnergy))

print("Opening vox files")
for index, energy in enumerate(dataParameters.momentums):    
  #print(" Energy ", energy)
  input_file_vox = (vox_dir + '/rootFiles/%s/pid%i_E%s_eta_%s_%s.root' % (particle,  voxInputs.pid, energy, eta_min, eta_max))
  print(" Opening file: " + input_file_vox)
  infile_vox = ROOT.TFile.Open(input_file_vox, 'read') 
  input_files_vox.append(infile_vox)
  tree = infile_vox.Get('rootTree') 

  #REMOVE ONCE FINISHED WITH CALOCHALLENGE
#  energyHistoName = "etot_phiModCorrected"
#  if voxInputs.GANVersion == 1:
#    energyHistoName = "etot"
  energyHistoName = "etot"
  h = ROOT.TH1F("h","",100,0,energy*2) 
  tree.Draw(energyHistoName+">>h","","off")
  #END OF ADDED POINT
  
  h = ROOT.TH1F("h","",100,0,energy*2) 
  tree.Draw("etot>>h","","off") #  tree.Draw("etot_phiModCorrected>>h","","off")
  xmax=h.GetBinCenter(h.GetMaximumBin());
  minX = max(0, xmax-minFactor*h.GetRMS()) #max(0, xmax-minFactors[item]*h.GetRMS())
  maxX = xmax+maxFactor*h.GetRMS()
  print("min "+ str(minX) + " max " + str(maxX))
      
  h_vox = ROOT.TH1F("h_vox","",30,minX/1000,maxX/1000) 
  tree.Draw("etot/1000>>h_vox","","off") #  tree.Draw("etot_phiModCorrected/1000>>h_vox","","off")
  h_vox.Scale(1/h_vox.GetEntries())
  histos_vox.append(h_vox)

print ("Running from %i to %i in step of %i" %(minEpoch, maxEpoch, step))
for epoch in range(minEpoch, maxEpoch+step, step):
  try:
    print (epoch)
    histos_gan =[]
    if (energy_range == "High12"):
      canvas = ROOT.TCanvas('canvas_h', 'Total Energy comparison plots', 900, 675)
      canvas.Divide(4,3)
      legendPadIndex = 12
    elif (energy_range == "UltraLow12"):
      canvas = ROOT.TCanvas('canvas_h', 'Total Energy comparison plots', 900, 450)
      canvas.Divide(4,2)
      legendPadIndex = 8
    else:
      canvas = ROOT.TCanvas('canvas_h', 'Total Energy comparison plots', 900, 900)
      canvas.Divide(4,4)
      legendPadIndex = 16

    canvases.append(canvas)

    chi2_tot = 0.
    ndf_tot = 0
    input_files_gan = []

    for index, energy in enumerate(dataParameters.momentums):     
      ekin_sample = ekins[index]

      lab = Label(ekin_sample, n_events, E_min, E_max, eta_min, dataParameters.label_definition)
      label = lab.GetLabelsAndPhiMod()
   
      data = wgan.load(epoch, label, n_events, '/'.join([input_dir_gan, particle, 'checkpoints_eta_%s_%s' % (eta_min, eta_max)]))
      if (dataParameters.voxel_normalisation == VoxelNormalisation.normE):
        data = data * ekin_sample       #needed for conditional
        #print("Normalisation value ", energy)
      elif (dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelAll):
        data = data * maxVoxel
        #print("Normalisation value ", maxVoxel)
      elif (dataParameters.voxel_normalisation == VoxelNormalisation.MaxVoxelMid):
        data = data * maxVoxel
        #print("Normalisation value ", maxVoxel)
      elif (dataParameters.voxel_normalisation == VoxelNormalisation.midE):
        #print(data[0])
        #print(data[0].sum())
        data = data * midEnergy
        #print("Normalisation value ", dl.getMidEnergy)
        
      h_vox = histos_vox[index]
      h_gan = ROOT.TH1F("h_gan","",30,h_vox.GetXaxis().GetXmin(),h_vox.GetXaxis().GetXmax())


      E_tot = data.numpy().sum(axis=1)
      for e in E_tot:
        h_gan.Fill(e/1000)
      
      h_gan.Scale(1/h_gan.GetEntries())
      h_gan.SetLineColor(ROOT.kRed)
      h_gan.SetLineStyle(7)
      m = [h_vox.GetBinContent(h_vox.GetMaximumBin()),h_gan.GetBinContent(h_gan.GetMaximumBin())]
      h_vox.GetYaxis().SetRangeUser(0,max(m) *1.25)
      histos_gan.append(h_gan)
      h_vox.GetYaxis().SetTitle("Entries")

      xAxisTitle = "Energy [GeV]"
      h_vox.GetXaxis().SetTitle(xAxisTitle)  
      h_vox.GetXaxis().SetNdivisions(506)
      chi2 = ctypes.c_double(0.)
      ndf = ctypes.c_int(0)
      igood = ctypes.c_int(0)
      histos_vox[index].Chi2TestX(h_gan, chi2, ndf, igood, "WW")
      ndf = ndf.value
      chi2=chi2.value
      chi2_tot += chi2
      ndf_tot += ndf

      if (ndf != 0):
        print("Epoch %s Energy %s : chi2/ndf = %.1f / %i = %.1f\n" % (epoch, energy, chi2, ndf, chi2/ndf))

      # Plotting

      canvas.cd(index+1)
      histos_vox[index].Draw("HIST")
      histos_gan[index].Draw("HIST same")

      # Legend box                                                                                                                                                                            
      if (energy > 1024):
          energy_legend =  str(round(energy/1000,1)) + " GeV"
      else:
          energy_legend =  str(energy) + " MeV"
      t = ROOT.TLatex()
      t.SetNDC()
      t.SetTextFont(42)
      t.SetTextSize(0.1)
      t.DrawLatex(0.2, 0.83, energy_legend)
   
    # Total Energy chi2
    chi2_o_ndf = chi2_tot / ndf_tot
    print("Epoch %s Total Energy : chi2/ndf = %.1f / %i = %.3f\n" % (epoch, chi2_tot, ndf_tot, chi2_o_ndf))
    chi2File = "%s/chi2/chi2_%s_%s_%s.txt" % (output_best_checkpoints,  voxInputs.pid, eta_min, eta_max)
    if chi2_o_ndf > 0:
      f = open(chi2File, 'a')
      f.write("%s %.3f\n" % (epoch, chi2_o_ndf))
      f.close()
    else:
      print("Something went wrong, chi2 will not be written. Chi2/ndf is %f " % (chi2_o_ndf))
      print(E_tot)
      continue

    # Legend box particle
    leg = MakeLegend( lparams )
    leg.SetTextFont( 42 )
    leg.SetTextSize(0.1)
    canvas.cd(legendPadIndex)
    leg.AddEntry(h_vox,"Geant4","l") #Geant4
    leg.Draw()
    leg.AddEntry(h_gan,"GAN","l")  #WGAN-GP
    leg.Draw('same')
    legend = (voxInputs.particleLatexName + ", " + str('{:.2f}'.format(int(eta_min)/100,2)) + "<|#eta|<" + str('{:.2f}'.format((int(eta_min)+5)/100,2)))
    if preliminary:
      ROOT.ATLAS_PREL_LABEL_BIG( 0.1, 0.9, ROOT.kBlack, legend )
    else:
      ROOT.ATLAS_LABEL_BIG( 0.1, 0.9, ROOT.kBlack, legend )

    # Legend box Epoc&chi2 

    t = ROOT.TLatex()
    t.SetNDC()
    t.SetTextFont(42)
    t.SetTextSize(0.1)
    t.DrawLatex(0.1, 0.18, "Iteration: %s" % (epoch))
    t.DrawLatex(0.1, 0.07, "#scale[0.8]{#chi^{2}/NDF = %.0f/%i = %.1f}" % (chi2_tot, ndf_tot, chi2_o_ndf))


    #Copy best epoch files, including plots
    epochs, chi2_o_ndf_list = np.loadtxt(chi2File, delimiter=' ', unpack=True)
    
    etaOrRegion = "eta_%s_%s" % (eta_min,eta_max)
    if isSeed:
      etaOrRegion = "region_%s" % (voxInputs.region)
      
    checkpointName =  "Plot_comparison_tot_energy_pid%s_%s" % (voxInputs.pid,etaOrRegion)
    
    folderAppendix=""
    if preliminary:
      folderAppendix="_preliminary"

    if round(chi2_o_ndf,3) <= np.amin(chi2_o_ndf_list) and chi2_o_ndf > 0:
      print ("Better chi2, creating files in %s/../best_checkpoints" %(input_dir_gan))
      inputFile_Plot_png="%s/png%s/%s.png" % (output_best_checkpoints, folderAppendix, checkpointName)
      inputFile_Plot_eps="%s/eps%s/%s.eps" % (output_best_checkpoints, folderAppendix, checkpointName)
      inputFile_Plot_pdf="%s/pdf%s/%s.pdf" % (output_best_checkpoints, folderAppendix, checkpointName)
      canvas.SaveAs(inputFile_Plot_png) 
      canvas.SaveAs(inputFile_Plot_eps) 
      canvas.SaveAs(inputFile_Plot_pdf) 

      checkPointNumber=int(epoch/1000)    
      inputFile_Index = "%s/%s/checkpoints_eta_%s_%s/model-%s.index" % (input_dir_gan, particle, eta_min, eta_max, checkPointNumber)
      outputFile_Index = "%s/model_%s_%s.index" % (output_best_checkpoints, particle, etaOrRegion)
      shutil.copyfile(inputFile_Index, outputFile_Index)

      inputFile_Data = "%s/%s/checkpoints_eta_%s_%s/model-%s.data*" % (input_dir_gan, particle, eta_min, eta_max, checkPointNumber)
      for file in glob.glob(inputFile_Data):
        new_name = file.replace('%s/%s/checkpoints_eta_%s_%s/model-%s' % (input_dir_gan, particle, eta_min, eta_max, checkPointNumber), '%s/model_%s_%s' % (output_best_checkpoints, particle, etaOrRegion))
        shutil.copyfile(file, new_name)
        
      print("Epoch with lowest chi2/ndf is %s with a value of %.3f" % (epoch, chi2_o_ndf))
      #Now save best epoch number to file
      chi2File = "%s/chi2/epoch_best_chi2_%s_%s_%s.txt" % (output_best_checkpoints, voxInputs.pid, eta_min, eta_max)
      f = open(chi2File, 'w')
      f.write("%s %.3f\n" % (epoch, chi2_o_ndf))
      f.close() 

    if (save_plots == "True") :
      inputFile_Plot_png="%s/png/%s.png" % (output_best_checkpoints, checkpointName)
      inputFile_Plot_eps="%s/eps/%s.eps" % (output_best_checkpoints, checkpointName)
      inputFile_Plot_pdf="%s/pdf/%s.pdf" % (output_best_checkpoints, checkpointName)
      canvas.SaveAs(inputFile_Plot_png) 
      canvas.SaveAs(inputFile_Plot_eps) 
      canvas.SaveAs(inputFile_Plot_pdf) 

  except:
    print("Something went wrong in epoch %s, moving to next one" % (epoch))
    print("exception message ", sys.exc_info()[0])     

