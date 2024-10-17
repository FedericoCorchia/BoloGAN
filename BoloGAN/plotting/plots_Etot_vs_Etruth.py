import argparse
import math
import numpy as np
import ROOT
import os,sys,ctypes
sys.path.append('../common/')

from ROOT import TCanvas, TGraph, TGraphErrors, TMultiGraph, TPad
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.SetMacroPath('./utils/')
ROOT.gROOT.Macro( "rootlogon.C" )
ROOT.gROOT.LoadMacro( "AtlasUtils.C" )

from VoxInputParameters import VoxInputParameters
from XMLHandler import XMLHandler
from DataParameters import DataParametersFromXML
from helper_functions import *

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

parser = argparse.ArgumentParser(description="Plots Etot mean and RMS")
parser.add_argument('-e1', '--eta_min', default='')
parser.add_argument('-ip', '--particle', default='')
parser.add_argument('-v', '--vox_dir', default='')
parser.add_argument('-odg', '--output_dir_gan', default='')
parser.add_argument('-d', '--output_dir', default='')
parser.add_argument('-p', '--pid', default='')
args = parser.parse_args()

particle = args.particle
vox_dir = args.vox_dir
output_dir_gan = args.output_dir_gan
eta_min = int(args.eta_min)
eta_max = eta_min + 5
output_dir = args.output_dir
pid=int(args.pid)

###################################################################

particleName=""
if pid == 22:
  particleName="#gamma"
  minFactor = 3
  maxFactor = 3  
  minRatio = 0.95
  maxRatio =  1.03
  minRatio2 = 0.8
  maxRatio2 = 1.5
elif pid == 211:
  particleName="#pi^{#pm}"
  minFactor = 4
  maxFactor = 3.5
  minRatio = 0.91
  maxRatio =  1.03
  minRatio2 = 0.8
  maxRatio2 = 1.5
elif pid == 11:
  particleName="e^{-}"
  minFactor = 3
  maxFactor = 3  
  minRatio = 0.91
  maxRatio =  1.03
  minRatio2 = 0.9
  maxRatio2 = 2.1

RatioFile = (output_dir + "Ratio_Energy_%s_%d.txt" % (particle,eta_min))
f = open(RatioFile, 'w')

voxInputs = VoxInputParameters(vox_dir, particle, eta_min, eta_max)
xml = XMLHandler(voxInputs)
dataParameters = DataParametersFromXML(xml, "All")

for index, energy in enumerate(dataParameters.momentums):     

    file_1 = ROOT.TFile.Open(vox_dir + 'rootFiles/%s/pid%s_E%s_eta_%s_%s_voxalisation.root' % (particle,pid,energy,eta_min,eta_max), 'read') 
    tree_1 = file_1.Get('rootTree')

    file_2 = ROOT.TFile.Open(output_dir_gan + '/%s/%s_%s/pid%s_E%s_eta_%s_%s_GAN.root' % (particle,eta_min,eta_max,pid,energy,eta_min,eta_max), 'read')
    tree_2 = file_2.Get('rootTree')
 
    h = ROOT.TH1F("h","",30,0,energy*1.5) 
    tree_1.Draw('etot>>h',"","off")
    xmax=h.GetBinCenter(h.GetMaximumBin())
    minX = max(0, xmax-minFactor*h.GetRMS())
    maxX = xmax+maxFactor*h.GetRMS()


    print(" Energy ", energy)

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

    RMS_Gan_err = h1.GetRMSError()/energy
    RMS_Vox_err = h2.GetRMSError()/energy

    mean_Gan_err = h1.GetMeanError()/energy
    mean_Vox_err = h2.GetMeanError()/energy

    ratio_mean_Gan = mean_Gan/(energy)
    ratio_mean_Vox = mean_Vox/(energy)

    ratio_rms_Gan = RMS_Gan/energy
    ratio_rms_Vox = RMS_Vox/energy

    f.write("%s %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f  \n" % (math.log10(energy), ratio_mean_Gan, ratio_mean_Vox, ratio_rms_Gan, ratio_rms_Vox, 0, RMS_Gan_err, RMS_Vox_err, mean_Gan_err, mean_Vox_err))

f.close()

print(output_dir + "Ratio_Energy_%s_%d.txt" % (particle, eta_min))
data = np.loadtxt(output_dir + "Ratio_Energy_%s_%d.txt" % (particle, eta_min))
x = data[:,0]
y_ratio_mean_gan = data[:,1]
y_ratio_mean_vox = data[:,2]
y_ratio_rms_gan  = data[:,3]
y_ratio_rms_vox  = data[:,4]
x_err = data[:,5]
y_ratio_mean_gan_err = data[:,6]
y_ratio_mean_vox_err = data[:,7]
y_ratio_rms_gan_err  = data[:,8]
y_ratio_rms_vox_err  = data[:,9]

x_offset = x + 0.05

canvas = ROOT.TCanvas('canvas_mean', 'Mean of total energy', 800, 800)

p3 = TPad("p3","p3",0.,0.,1.,0.25)
p3.Draw()
p3.SetTopMargin(0.001)
p3.SetBottomMargin(0.3)

p2 = TPad("p2","p2",0.,0.25,1.,0.5)
p2.Draw()
p2.SetTopMargin(0.001)
p2.SetBottomMargin(0.001)

p1 = TPad("p1","p1",0,0.5,1.,1)  
p1.Draw()
p1.SetBottomMargin(0.001)
p1.cd()

mgr = TMultiGraph()

gr = TGraphErrors( len(x), x_offset.flatten(), y_ratio_mean_gan.flatten(), x_err.flatten(), y_ratio_rms_gan.flatten())
gr.SetName("gr")
gr.SetLineColor(ROOT.kRed)
gr.SetLineStyle(2)
gr.SetMarkerColor(ROOT.kRed)
gr.SetMarkerStyle(23)

gr_vox = TGraphErrors( len(x), x.flatten(), y_ratio_mean_vox.flatten(), x_err.flatten(),y_ratio_rms_vox.flatten() )
gr_vox.SetName("gr_vox")
gr_vox.SetLineColor(ROOT.kBlack)
gr_vox.SetMarkerColor(ROOT.kBlack)
gr_vox.SetMarkerStyle(20)

mgr.Add(gr)
mgr.Add(gr_vox)
mgr.Draw('AP')
mgr.GetXaxis().SetTitle("Log_{10} p_{truth}/MeV")
mgr.GetYaxis().SetTitle("#LTE#GT/p_{truth} and RMS/p_{truth}")
mgr.GetYaxis().SetTitleSize(mgr.GetYaxis().GetTitleSize()*1.1)
mgr.GetYaxis().SetTitleOffset(0)
mgr.GetXaxis().SetLimits(2.2, 6.9)
mgr.Draw("AP")

mgr.GetHistogram().SetMaximum(1.25);
if pid == 22:
  mgr.GetHistogram().SetMaximum(1.25);

#legend1 = (particleName + " " + str('{:.2f}'.format(int(eta_min)/100,2)) + "<|#eta|<" + str('{:.2f}'.format((int(eta_min)+5)/100,2)))
#legend2 = "Bars represent RMS"
#legend="#splitline{"+legend1+"}{"+legend2+"}"
legend = (particleName + " " + str('{:.2f}'.format(int(eta_min)/100,2)) + "<|#eta|<" + str('{:.2f}'.format((int(eta_min)+5)/100,2)))
ROOT.ATLAS_LABEL_SQUARE( 0.19, 0.85, ROOT.kBlack, legend )
#canvas.cd()

lparams = {'xoffset' : 0.65, 'yoffset' : 0.73, 'width'   : 0.30, 'height'  : 0.20}
leg = MakeLegend( lparams )
leg.SetTextFont( 42 )
leg.SetTextSize(0.05)
leg.AddEntry(gr_vox,"G4","p")
leg.Draw()
leg.AddEntry(gr,"FastCaloGAN","p")
leg.Draw('same')

############ Mid pad
p2.cd()
p2.SetGridy()
y_ratio = y_ratio_mean_gan.flatten()/y_ratio_mean_vox.flatten()
y_ratio_err = (y_ratio_mean_vox_err.flatten()/y_ratio_mean_vox.flatten() + y_ratio_mean_gan_err.flatten()/y_ratio_mean_gan.flatten()) * y_ratio
r = TGraphErrors(len(x),x.flatten(),y_ratio,x_err.flatten(),y_ratio_err); 
r.SetTitle("");

mgr2 = TMultiGraph()
mgr2.Add(r)
mgr2.Draw( 'P' )
mgr2.GetXaxis().SetLabelSize(0.1)
mgr2.GetYaxis().SetLabelSize(0.1)
mgr2.GetXaxis().SetTitleSize(0.11)
mgr2.GetYaxis().SetTitleSize(0.11)

mgr2.GetYaxis().SetRangeUser(y_ratio.min()-0.01, y_ratio.max()+0.01)
mgr2.GetYaxis().SetRangeUser(minRatio, maxRatio)
mgr2.GetYaxis().SetNdivisions(404)
mgr2.GetYaxis().SetTitleOffset(0.5)
mgr2.GetYaxis().SetTitle("#LTE#GT FGAN/G4")
mgr2.GetXaxis().SetLimits(2.2, 6.9)
mgr2.GetXaxis().SetTitleOffset(mgr2.GetXaxis().GetTitleOffset()*0.8)
mgr2.GetXaxis().SetTitle("Log_{10}(p_{truth}/MeV)")
mgr2.Draw("AP");


############ Bottom pad
p3.cd()
p3.SetGridy()
y_ratio = y_ratio_rms_gan.flatten()/y_ratio_rms_vox.flatten()
y_ratio_err = (y_ratio_rms_vox_err.flatten()/y_ratio_rms_vox.flatten() + y_ratio_rms_gan_err.flatten()/y_ratio_rms_gan.flatten()) * y_ratio
r = TGraphErrors(len(x),x.flatten(),y_ratio,x_err.flatten(),y_ratio_err); 
r.SetTitle("");

mgr3 = TMultiGraph()
mgr3.Add(r)
mgr3.Draw( 'P' )
mgr3.GetXaxis().SetLabelSize(0.1)
mgr3.GetYaxis().SetLabelSize(0.1)
mgr3.GetXaxis().SetTitleSize(0.11)
mgr3.GetYaxis().SetTitleSize(0.11)

mgr3.GetYaxis().SetRangeUser(y_ratio.min()-0.01, y_ratio.max()+0.01)
mgr3.GetYaxis().SetRangeUser(minRatio2, maxRatio2)
mgr3.GetYaxis().SetNdivisions(404)
mgr3.GetYaxis().SetTitleOffset(0.5)
mgr3.GetYaxis().SetTitle("RMS FGAN/G4")
mgr3.GetXaxis().SetLimits(2.2, 6.9)
mgr3.GetXaxis().SetTitleOffset(mgr2.GetXaxis().GetTitleOffset()*0.8)
mgr3.GetXaxis().SetTitle("Log_{10}(p_{truth}/MeV)")
mgr3.Draw("AP");


canvas.Update()
canvas.SaveAs(output_dir + '/png/Mean_vs_Etruth_%s_%d.png' % (particle, eta_min))
canvas.SaveAs(output_dir + '/png/Mean_vs_Etruth_%s_%d.pdf' % (particle, eta_min))


