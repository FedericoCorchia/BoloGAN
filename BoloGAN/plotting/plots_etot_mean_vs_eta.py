import argparse
import ROOT
import os,sys,ctypes
sys.path.append('../common/')

from ROOT import TCanvas, TPad, TGraph, TGraphErrors, TMultiGraph
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.SetMacroPath('./utils/')
ROOT.gROOT.Macro( "rootlogon.C" )
ROOT.gROOT.LoadMacro( "AtlasUtils.C" )
sys.path.append('../models/tf/WGAN-GP/')

from helper_functions import *

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

parser = argparse.ArgumentParser(description="Plots Etot mean and RMS")
parser.add_argument('-e', '--energy', default='')
parser.add_argument('-ip', '--particle', default='')
parser.add_argument('-d', '--output_dir', default='')
args = parser.parse_args()

energy = int(args.energy)
particle = args.particle
output_dir = args.output_dir

energy_legend =  str(round(energy/1000,1)) + " GeV"

symbol = {'photons': "#gamma ",
              'pions': "#pi^{#pm} ",
              'electrons': "e^{-} "}
#legend1 = (symbol[particle] +  " E=" + energy_legend)
#legend2 = "Bars represent RMS"
#legend="#splitline{"+legend1+"}{"+legend2+"}"
legend = (symbol[particle] +  " E=" + energy_legend)

if particle == 'photons':
  maxRatio = 1.012
  minRatio = 0.981
  maxRatio2 = 1.65
  minRatio2 = 0.8
  if energy == 8192:
    maxYAxis = 10
    minYAxis = 5.8
    maxRatio = 1.015
    minRatio = 0.985
  if energy == 65536:
    maxYAxis = 76
    minYAxis = 53
  if energy == 524288:
    maxYAxis = 590
    minYAxis = 470

elif particle == 'electrons':
  maxRatio = 1.012
  minRatio = 0.986
  maxRatio2 = 1.55
  minRatio2 = 0.8
  if energy == 8192:
    maxYAxis = 10
    minYAxis = 5.8
    maxRatio = 1.015
    minRatio = 0.985
  if energy == 65536:
    maxYAxis = 77
    minYAxis = 52
  if energy == 524288:
    maxYAxis = 590
    minYAxis = 470
    
else :
  maxRatio = 1.045
  minRatio = 0.93
  maxRatio2 = 1.45
  minRatio2 = 0.9
  if energy == 8192:
    maxYAxis = 9
    minYAxis = 2.8
    minRatio = 0.92
  if energy == 65536:
    maxYAxis = 70
    minYAxis = 33
  if energy == 524288:
    maxYAxis = 570
    minYAxis = 330
    minRatio = 0.97


data = np.loadtxt(output_dir + "/RMS_and_mean_%s_%s.txt" % (energy,particle))

x = data[:,0]
x_offset = x + 0.02
y_rms = data[:,1]
y_rms_vox = data[:,2]

y_mean = data[:,3]
y_mean_vox = data[:,4]
x_err = data[:,5]

#x = data[::2,0]
#x_offset = x + 0.02
#y_rms = data[::2,1]
#y_rms_vox = data[::2,2]

#y_mean = data[::2,3]
#y_mean_vox = data[::2,4]
#x_err = data[::2,5]

mean_err = data[:,6]
mean_vox_err = data[:,7]
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

gr = TGraphErrors( len(x), x_offset.flatten(), y_mean.flatten(),x_err.flatten(),y_rms.flatten() )
gr.SetLineColor(ROOT.kRed)
gr.SetLineStyle(2)
gr.SetMarkerColor(ROOT.kRed)
gr.SetMarkerStyle(23)

gr_vox = TGraphErrors( len(x), x.flatten(), y_mean_vox.flatten(),x_err.flatten(),y_rms_vox.flatten() )
gr_vox.SetLineColor(ROOT.kBlack)
gr_vox.SetMarkerColor(ROOT.kBlack)
gr_vox.SetMarkerStyle(20)

mgr.Add(gr)
mgr.Add(gr_vox)
mgr.Draw( 'ALP' )
mgr.GetXaxis().SetTitle("|#eta|")
mgr.GetYaxis().SetTitle("#LTE#GT and RMS [GeV]")
mgr.GetYaxis().SetTitleSize(mgr.GetYaxis().GetTitleSize()*1.1)
mgr.GetYaxis().SetTitleOffset(0.5)
mgr.GetXaxis().SetLimits(-0.2, 5.2)
mgr.GetYaxis().SetRangeUser(minYAxis,maxYAxis)
mgr.Draw("ALP");

ROOT.ATLAS_LABEL_SQUARE( 0.19, 0.85, ROOT.kBlack, legend )

lparams = {'xoffset' : 0.65, 'yoffset' : 0.73, 'width'   : 0.30, 'height'  : 0.20}
leg = MakeLegend( lparams )
leg.SetTextFont( 42 )
leg.SetTextSize(0.05)
leg.AddEntry(gr_vox,"G4","p")
leg.Draw()
leg.AddEntry(gr,"FastCaloGAN","p")
leg.Draw('same')

p2.cd()
p2.SetGridy()
y_ratio = y_mean.flatten()/y_mean_vox.flatten()
y_ratio_err = x_err.flatten()/y_mean_vox.flatten()
r = TGraphErrors( len(x), x.flatten(), y_ratio, x_err.flatten(), y_ratio_err); 
r.SetTitle("");

mgr2 = TMultiGraph()
mgr2.Add(r)
mgr2.GetXaxis().SetLabelSize(0.1)
mgr2.GetYaxis().SetLabelSize(0.1)
mgr2.GetXaxis().SetTitleSize(0.11)
mgr2.GetYaxis().SetTitleSize(0.11)

mgr2.GetYaxis().SetRangeUser(y_ratio.min()-0.01, y_ratio.max()+0.01)
mgr2.GetYaxis().SetRangeUser(minRatio, maxRatio)
mgr2.GetYaxis().SetNdivisions(408)
mgr2.GetYaxis().SetTitleOffset(0.5)
mgr2.GetYaxis().SetTitle("#LTE#GT FGAN/G4")
mgr2.GetXaxis().SetTitle("|#eta|")
mgr2.GetXaxis().SetTitleOffset(mgr2.GetXaxis().GetTitleOffset()*0.8)
mgr2.GetXaxis().SetLimits(-0.2, 5.2)
mgr2.Draw("AP");

#line = TLine(0.1, 0.5, 0.9, 0.5)
#line.SetNDC(ROOT.kTRUE)
#line.SetLineColor(ROOT.kBlack)
#line.Draw("same")

p3.cd()
p3.SetGridy()
y_ratio = y_rms.flatten()/y_rms_vox.flatten()
y_ratio_err = x_err.flatten()/y_mean_vox.flatten()
r = TGraphErrors(len(x),x.flatten(),y_ratio,x_err.flatten(),y_ratio_err); 
r.SetTitle("");

mgr3 = TMultiGraph()
mgr3.Add(r)
mgr3.Draw( 'P' )
mgr3.GetXaxis().SetLabelSize(0.1)
mgr3.GetYaxis().SetLabelSize(0.1)
mgr3.GetXaxis().SetTitleSize(0.11)
mgr3.GetYaxis().SetTitleSize(0.11)

mgr3.GetYaxis().SetRangeUser(minRatio2, maxRatio2)
mgr3.GetYaxis().SetNdivisions(408)
mgr3.GetYaxis().SetTitleOffset(0.5)
mgr3.GetYaxis().SetTitle("RMS FGAN/G4")
mgr3.GetXaxis().SetTitle("|#eta|")
mgr3.Draw("AP");
   
canvas.Update()
canvas.SaveAs(output_dir + 'Mean_vs_eta_%s_%s.png' % (energy,particle))
canvas.SaveAs(output_dir + 'Mean_vs_eta_%s_%s.pdf' % (energy,particle))
