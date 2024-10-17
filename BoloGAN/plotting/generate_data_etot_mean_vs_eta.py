import argparse
import ROOT
import os,sys,ctypes
from helper_functions import *
from ROOT import TCanvas, TGraph, TGraphErrors, TMultiGraph
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.SetMacroPath( "/afs/cern.ch/work/l/ldifelic/FastCaloGAN/plotting/utils/")
ROOT.gROOT.Macro( "rootlogon.C" )
ROOT.gROOT.LoadMacro( "AtlasUtils.C" )

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

parser = argparse.ArgumentParser(description="Plots Etot mean and RMS")
parser.add_argument('-emin', '--min_epoch', default=500)
parser.add_argument('-g', '--rungan', default=False)
parser.add_argument('-e', '--energy', default='')
parser.add_argument('-e1', '--eta_min', default='')
parser.add_argument('-e2', '--eta_max', default='')
parser.add_argument('-ip', '--particle', default='')
parser.add_argument('-in', '--input_dir_nom', default='')
parser.add_argument('-gp', '--root_file_GAN_plots', default='')
parser.add_argument('-igr', '--input_dir_gra', default='')
parser.add_argument('-ogr', '--output_dir_gra', default='')
parser.add_argument('-d', '--output_dir', default='')
parser.add_argument('-p', '--pid', default='')
args = parser.parse_args()

min_epoch = int(args.min_epoch)
particle = args.particle
input_dir_nom = args.input_dir_nom
root_file_GAN_plots = args.root_file_GAN_plots
input_dir_gra = args.input_dir_gra
output_dir_gra = args.output_dir_gra
eta_min = int(args.eta_min)
eta_max = int(args.eta_max)
rungan = bool(args.rungan)
energy = int(args.energy)
output_dir = args.output_dir
pid=int(args.pid)

###################################################################

minFactors = [3.5, 3.5, 3.5, 4.5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

if pid == 22 or pid == 11 :
  minFactor = 3
  maxFactor = 3  
else :
  minFactor = 4
  maxFactor = 3.5

def overlay_histos(tree_1, tree_2, minX, maxX):
    h1 = ROOT.TH1F("h1","",30,minX,maxX) 
    h2 = ROOT.TH1F("h2","",30,minX,maxX) 
    tree_1.Draw('etot>>h2',"","off")
    tree_2.Draw('etot>>h1',"","off")
    h1.Scale(1/h1.GetEntries())
    h2.Scale(1/h2.GetEntries())

    RMS = h1.GetRMS()
    RMS_Vox = h2.GetRMS()

    mean = h1.GetMean()
    mean_Vox = h2.GetMean()

    mean_error = h1.GetMeanError()
    mean_Vox_error = h2.GetMeanError()

    RMSFile = output_dir + "/RMS_and_mean_%s_%s.txt" % (energy,particle)
    print(RMSFile)
    f = open(RMSFile, 'a')
    f.write("%s %.3f %.3f %.3f %.3f %.3f %.3f %.3f \n" % (eta_min/100, RMS/1000, RMS_Vox/1000, mean/1000, mean_Vox/1000,0, mean_error/1000, mean_Vox_error/1000))
    f.close()
  
def make_plots(tree_1,tree_2, output_dir,particle,energy,eta_min):

      h = ROOT.TH1F("h","",30,0,energy*1.5) 
      tree_1.Draw('etot>>h',"","off")
      xmax=h.GetBinCenter(h.GetMaximumBin())
      minX = max(0, xmax-minFactor*h.GetRMS())
      maxX = xmax+maxFactor*h.GetRMS()
      overlay_histos(tree_1, tree_2, minX, maxX)  

file_1 = ROOT.TFile.Open(input_dir_nom + 'rootFiles/%s/pid%s_E%s_eta_%s_%s_nominal.root' % (particle,pid,energy,eta_min,eta_max), 'read')
print(input_dir_nom + 'rootFiles/%s/pid%s_E%s_eta_%s_%s_nominal.root' % (particle,pid,energy,eta_min,eta_max))
tree_1 = file_1.Get('rootTree')

if (rungan == True):
 file_2 = ROOT.TFile.Open(root_file_GAN_plots, 'read')
 print(root_file_GAN_plots)
 tree_2 = file_2.Get('rootTree')
else:
 file_2 = ROOT.TFile.Open(input_dir_gra +'rootFiles/Plots_Energy_voxalization_validation/%s/pid%s_E%s_eta_%s_%s_highGranularity.root' % (particle,pid,energy,eta_min,eta_max), 'read')
 tree_2 = file_2.Get('rootTree')
 file_output = ROOT.TFile(output_dir_gra + 'pid%s_E%s_eta_%s_%s_comparison_highGranulatiry.root' % (pid,energy,eta_min,eta_max),"RECREATE")
 

make_plots(tree_1,tree_2, output_dir,particle,energy,eta_min)
