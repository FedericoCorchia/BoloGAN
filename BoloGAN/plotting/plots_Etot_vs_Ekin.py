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

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

parser = argparse.ArgumentParser(description="Plots Etot mean and RMS")
parser.add_argument('-p', '--pid', default='')
parser.add_argument('-e1', '--eta_min', default='')
parser.add_argument('-e2', '--eta_max', default='')
parser.add_argument('-ip', '--particle', default='')
parser.add_argument('-d', '--output_dir', default='')
args = parser.parse_args()

particle = args.particle
eta_min = int(args.eta_min)
eta_max = int(args.eta_max)
output_dir = args.output_dir
pid=int(args.pid)

###################################################################


print(output_dir + "/Ratio_Ekin_100bins_%s_%d.txt" % (particle, eta_min))
data = np.loadtxt(output_dir + "/Ratio_Ekin_100bins_%s_%d.txt" % (particle, eta_min))
x = data[:,0]
y_ratio_mean_gan = data[:,1]
y_ratio_rms_gan  = data[:,2]
x_err = data[:,3]

file_graphs = ROOT.TFile.Open(output_dir + '/TGraph_GAN_ekin.root', 'update')
gr = TGraphErrors( len(x), x.flatten(), y_ratio_mean_gan.flatten(), x_err.flatten(), y_ratio_rms_gan.flatten())

gr.SetLineColor(ROOT.kRed)
gr.SetLineStyle(2)
gr.SetMarkerColor(ROOT.kRed)
gr.SetMarkerStyle(23)

gr.Write("%d_%d_%d" % (pid, eta_min, eta_max))
file_graphs.Write()
file_graphs.Close()
