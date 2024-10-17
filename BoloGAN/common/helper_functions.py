#!/usr/bin/env python3

import numpy as np
import math
import argparse
import ROOT
import os,sys
from array import array

from XMLHandler import XMLHandler

ROOT.gROOT.SetBatch(True)

def calculate_COG(eta, phi, energy):
    eta_cog = (eta * energy).sum(axis=0)/energy.sum(axis=0)
    phi_cog = (phi * energy).sum(axis=0)/energy.sum(axis=0)
    return eta_cog, phi_cog

def calculate_Widths(eta, phi, energy):
    eta_width = (eta * eta * energy).sum(axis=0)/energy.sum(axis=0)
    phi_width = (phi * phi * energy).sum(axis=0)/energy.sum(axis=0)
    return eta_width, phi_width

def MakeLegend( params ):
    leg = ROOT.TLegend( params['xoffset'], params['yoffset'], params['xoffset'] + params['width'], params['yoffset'] + params['height'])
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.05)
    return leg

def GetCOGandWidths(eta_layer, phi_layer, energy_layer):
    #print(energy_layer)
    eta_cog = 0
    phi_cog = 0
    eta_width = 0
    phi_width = 0

    if (sum(energy_layer)!= 0):
        eta_cog , phi_cog = calculate_COG(eta_layer, phi_layer, energy_layer)
        eta_width , phi_width = calculate_Widths(eta_layer, phi_layer, energy_layer)
        #print("new layer")
        #print(eta_cog)
        #print(phi_cog)
        #print(eta_width)
        #print(phi_width)
        if (eta_cog * eta_cog <= eta_width):
          eta_width = math.sqrt(eta_width - eta_cog * eta_cog) 
        if (phi_cog * phi_cog <= phi_width):
          phi_width = math.sqrt(phi_width - phi_cog * phi_cog)
        
    return eta_cog, phi_cog, eta_width, phi_width

def DefineGraph(rootFile):
  graph = rootFile.Get("E_phiMod_shifted")
  if graph != None:
    return graph

  profile = rootFile.Get("prof_E_phiMod")
  normE = rootFile.Get("normE")

  meanForCorrection=normE.GetMean()
  graph = ROOT.TGraphErrors()
  graph.SetName("E_phiMod_shifted")
  for binIdx in range(1, profile.GetNbinsX()):
    content=profile.GetBinContent(binIdx)/meanForCorrection
    error=profile.GetBinError(binIdx)
    if(content>0.01):
      graph.SetPoint(binIdx-1,profile.GetBinCenter(binIdx),content)
      graph.SetPointError(binIdx-1,0.00001,error)

  graph.Write()

  return graph;

def fill_ttree(xml, energy, htotOnly, data, phiMod, etas, rootTree, n_events, correctPhiMod=False, graph=""):
   correctPhiMod=False #REMOVE ONCE DONE WITH CALOCHALLENGE
   bin_edges = xml.GetBinEdges()
   eta_all_layers, phi_all_layers = xml.GetEtaPhiAllLayers()
   relevantLayers = xml.GetRelevantLayers()
   layersBinnedInAlpha = xml.GetLayersWithBinningInAlpha()

   E_tot = array( 'f', [ 0 ] )
   E_tot_phiModCorrected = array( 'f', [ 0 ] )
   E_totNorm = array( 'f', [ 0 ] )
   PhiMod = array( 'f', [ 0 ] )
   Eta = array( 'f', [ 0 ] )

   rootTree.Branch("etot", E_tot, "etot/F");
   rootTree.Branch("etot_phiModCorrected", E_tot_phiModCorrected, "etot_phiModCorrected/F");
   rootTree.Branch("etotNorm", E_totNorm, "etotNorm/F");
   rootTree.Branch("phiMod", PhiMod, "phiMod/F");
   rootTree.Branch("eta", Eta, "eta/F");
   
   E_layers = {}
   extrapWeights = {}

   for l in relevantLayers:
     E_layer = array( 'f', [ 0 ] )
     E_layers[l] = E_layer
     rootTree.Branch("e_"+str(l),  E_layers[l] , "e_"+str(l)+"/F", );
          
   cog_etas = {}
   cog_phis = {}
   width_etas = {}
   width_phis = {}
   for l in layersBinnedInAlpha:
     cog_eta = array( 'f', [ 0 ] )
     cog_phi = array( 'f', [ 0 ] )
     width_eta = array( 'f', [ 0 ] )
     width_phi = array( 'f', [ 0 ] )
     cog_etas[l] = cog_eta
     cog_phis[l] = cog_phi
     width_etas[l] = width_eta
     width_phis[l] = width_phi
     layer = str(l)
     rootTree.Branch("cog_eta_"+layer, cog_etas[l], "cog_eta_"+layer+"/F", );
     rootTree.Branch("cog_phi_"+layer, cog_phis[l], "cog_phi_"+layer+"/F", );
     rootTree.Branch("width_eta_"+layer, width_etas[l], "width_eta_"+layer+"/F", );
     rootTree.Branch("width_phi_"+layer, width_phis[l], "width_phi_"+layer+"/F", );
     
   correctPhiMod = False
   for i in range (0, min(n_events,data.shape[0])):
      phiModCorrection = 0
      if correctPhiMod:
        phiModCorrection = graph.Eval(phiMod[i])
      #else:
      #  print("PhiMod not defined!")
      
      
      PhiMod[0] = phiMod[i]
      Eta[0] = etas[i]
      E_tot[0] = 0
      E_totNorm[0] = 0
      for l in relevantLayers:
        layer_energy = data[i,bin_edges[l]:bin_edges[l+1]].sum(axis=0)

        E_tot[0] += layer_energy
        E_totNorm[0] += E_layers[l][0]/energy
        E_layers[l][0] = layer_energy/phiModCorrection
        E_tot_phiModCorrected[0] = E_tot[0]/phiModCorrection
                   
      if (htotOnly != "True"):
        E_event = data[i,:]/phiModCorrection
        
        for l in range(0,24):
          if l in layersBinnedInAlpha: 
            cog_etas[l][0], cog_phis[l][0], width_etas[l][0], width_phis[l][0] = GetCOGandWidths(eta_all_layers[l] , phi_all_layers[l], E_event[bin_edges[l]:bin_edges[l+1]])
                    
      rootTree.Fill()

