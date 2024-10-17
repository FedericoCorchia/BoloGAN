#!/usr/bin/env python3

import numpy as np
import argparse 
from array import array
import ROOT
from ROOT import TCanvas, TGraph

ROOT.gROOT.SetMacroPath('./utils/')
ROOT.gROOT.Macro( "rootlogon.C" )
ROOT.gROOT.LoadMacro( "AtlasUtils.C" )
ROOT.gROOT.SetBatch(True)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

if __name__ == "__main__":

 parser = argparse.ArgumentParser(description="Plot observables")
 parser.add_argument('-e', '--eta_min', default='')
 parser.add_argument('-p', '--pid', default='')
 parser.add_argument('-d', '--gan_dir', default='')
 parser.add_argument('-o', '--output_dir', default='')

 args = parser.parse_args()
 pid=int(args.pid)
 eta_min=int(args.eta_min)
 gan_dir=args.gan_dir
 output_dir=args.output_dir

 data = np.loadtxt("%s/chi2_%s_%s_%s.txt" % (gan_dir, pid, eta_min, int(eta_min)+5) )
 
 x = data[0:350,0]
 y = data[:,1]

 canvas = ROOT.TCanvas('canvas_chi2', 'Total chi2 Comparison plots', 800, 600)
 canvas.SetRightMargin(0.08)
 
 gr = TGraph( len(x), x.flatten(), y.flatten() )
 gr.Draw( 'ALP' )
 gr.GetYaxis().SetRangeUser(0,350);
 gr.GetXaxis().SetTitle("Epochs")
 gr.GetYaxis().SetTitle("#chi^{2}/NDF")
 gr.Draw("ALP");

 particleName=""
 particle=""
 if pid == 22:
   particleName="#gamma"
   particle="photons"
 elif pid == 211:
   particleName="#pi^{#pm}"
   particle="pions"
 elif pid == 11:
   particleName="e^{#pm}"
   particle="electrons"

 legend = (particleName + " " + str('{:.2f}'.format(eta_min/100,2)) + "<|#eta|<" + str('{:.2f}'.format((eta_min+5)/100,2)))
 ROOT.ATLAS_LABEL_LONG( 0.6, 0.88, ROOT.kBlack, legend )

 canvas.Update()
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d_injection.png' % (pid,eta_min,eta_min+5))

 x = data[113:,0]
 y = data[113:,1]
 # x = data[0:,0]
 # y = data[0:,1]
 
 n=20
 means = np.convolve(y, np.ones((n,))/n, mode='valid')
 minY = min(y)
 minYPosition = np.where(y == minY)
 
 canvas = ROOT.TCanvas('canvas_chi2', 'Total chi2 Comparison plots', 800, 600)
 canvas.SetRightMargin(0.08)
 
 gr = TGraph( len(x), x.flatten(), y.flatten() )
 #gr.GetXaxis().SetLimits(320,1060)
 gr.GetYaxis().SetRangeUser(0,52)
 gr.GetXaxis().SetTitle("Iteration")
 gr.GetYaxis().SetTitle("#chi^{2}/NDF")
 gr.Draw("AP")
 
 #gr2 = TGraph( len(x-n*3), x.flatten(), means.flatten() )
 #gr2.SetLineColor(ROOT.kRed)
 #gr2.SetLineWidth(2)
 #gr2.Draw("L") 

 gr2 = TGraph( 1, x[minYPosition], minY )
 gr2.SetMarkerColor(ROOT.kRed)
 gr2.Draw("P")
 

 ROOT.ATLAS_LABEL_LONG( 0.55, 0.87, ROOT.kBlack, legend )

 canvas.Update()
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d.png' % (pid,eta_min,eta_min+5))
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d.pdf' % (pid,eta_min,eta_min+5))
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d.eps' % (pid,eta_min,eta_min+5))
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d.root' % (pid,eta_min,eta_min+5))
 
 gr.GetYaxis().SetRangeUser(0,10);
 canvas.Update()
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d_small.png' % (pid,eta_min,eta_min+5))
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d_small.pdf' % (pid,eta_min,eta_min+5))
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d_small.eps' % (pid,eta_min,eta_min+5))

 gr.GetYaxis().SetRangeUser(0,100);
 canvas.Update()
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d_med.png' % (pid,eta_min,eta_min+5))
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d_med.pdf' % (pid,eta_min,eta_min+5))
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d_med.eps' % (pid,eta_min,eta_min+5))

 gr.GetYaxis().SetRangeUser(0,150);
 canvas.Update()
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d_large.png' % (pid,eta_min,eta_min+5))
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d_large.pdf' % (pid,eta_min,eta_min+5))
 canvas.SaveAs(output_dir + '/Chi1_vs_epoch_%d_eta_%d_%d_large.eps' % (pid,eta_min,eta_min+5))
