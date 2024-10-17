import argparse
import ROOT
import os,sys,ctypes

sys.path.append('../common/')
from VoxInputParameters import VoxInputParameters
from TrainingInputParameters import TrainingInputParameters
from helper_functions import *

ROOT.gROOT.SetBatch(True)
ROOT.gROOT.SetMacroPath( "./utils/" )
ROOT.gROOT.Macro( "rootlogon.C" )
ROOT.gROOT.LoadMacro( "AtlasUtils.C" )


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

parser = argparse.ArgumentParser(description="Plot GAN and POST-VOX")
parser.add_argument('-emin', '--min_epoch', default=500)
parser.add_argument('-s', '--step', default=1000) 
parser.add_argument('--DoVOX', action='store_false')
parser.add_argument('--DoGAN', action='store_true')
parser.add_argument('-e', '--energy', default='')
parser.add_argument('-e1', '--eta_min', default='')
parser.add_argument('-e2', '--eta_max', default='')
parser.add_argument('-ip', '--particle', default='')
parser.add_argument('-v', '--vox_dir', default='')
parser.add_argument('-gp', '--root_file_GAN_plots', default='')
parser.add_argument('-oga', '--output_dir_gan', default='')
parser.add_argument('-odv', '--output_dir_val', default='')
parser.add_argument('-d', '--output_dir', default='')
parser.add_argument('-p', '--pid', default='')
parser.add_argument('-of', '--output_fileName', default='')
parser.add_argument('-n', '--name', default='')
args = parser.parse_args()

step = int(args.step)
particle = args.particle
vox_dir = args.vox_dir
root_file_GAN_plots = args.root_file_GAN_plots
output_dir_gan = args.output_dir_gan
output_dir_val = args.output_dir_val
eta_min = int(args.eta_min)
eta_max = int(args.eta_max)
DoGAN=args.DoGAN
DoVOX=args.DoVOX
energy = int(args.energy)
output_dir = args.output_dir
output_fileName = args.output_fileName
name = args.name
pid=int(args.pid)
###################################################################

minFactors = [3.5, 3.5, 3.5, 4.5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

if pid == 22 or pid == 11 :
  minFactor = 3
  maxFactor = 3  
else :
  minFactor = 4
  maxFactor = 3.5

# Legend box                                                                                                                                                                                       
if (energy > 1024):
    energy_legend =  str(round(energy/1000,1)) + "GeV"
else:
    energy_legend =  str(energy) + "MeV"

symbol = {'photons': "#gamma, ",
              'pions': "#pi#pm, ",
              'electrons': "e^{-}, "}
legend = (symbol[particle] + str('{:.2f}'.format(eta_min/100,2)) + "<|#eta|<" + str('{:.2f}'.format((eta_min+5)/100,2)) + ", E=" + energy_legend)


inputs = VoxInputParameters(vox_dir, particle, eta_min, eta_max, False)
xml = XMLHandler(inputs)

relevantLayers = xml.GetRelevantLayers()
relevantLayers.append(24) #adding total energy plot
layerWithBinningInAlpha = xml.GetLayersWithBinningInAlpha()
print(layerWithBinningInAlpha)

def list_1():

    histo_list = {'e_0':"PreSamplerB Energy [GeV]","e_1":"EMB1 Energy [GeV]","e_2":"EMB2 Energy [GeV]","e_3":"EMB3 Energy [GeV]","e_4":"PreSamplerE Energy [GeV]","e_5":"EME1 Energy [GeV]","e_6":"EME2 Energy [GeV]","e_7":"EME3 Energy [GeV]","e_8":"HEC0 Energy [GeV]","e_9":"HEC1 Energy [GeV]","e_10":"HEC2 Energy [GeV]","e_11":"HEC3 Energy [GeV]","e_12":"TileBar0 Energy [GeV]","e_13":"TileBar1 Energy [GeV]","e_14":"TileBar2 Energy [GeV]","e_15":"TileGap1 Energy [GeV]","e_16":"TileGap2 Energy [GeV]","e_17":"TileGap3 Energy [GeV]","e_18":"TileExt0 Energy [GeV]","e_19":"TileExt1 Energy [GeV]","e_20":"TileExt2 Energy [GeV]","e_21":"FCal0 Energy [GeV]","e_22":"FCal1 Energy [GeV]","e_23":"FCal2 Energy [GeV]","etot":"E_{tot} [GeV]"}

    return histo_list

def list_2():
  
    histo_list = {"cog_eta_1":"EMB1 EC_{#eta} [mm]","cog_eta_2":"EMB2 EC_{#eta} [mm]","cog_eta_5":"EME1 EC_{#eta} [mm]","cog_eta_6":"EME2 EC_{#eta} [mm]","cog_eta_7":"EME3 EC_{#eta} [mm]","cog_eta_8":"HEC0 EC_{#eta} [mm]","cog_eta_9":"HEC1 EC_{#eta} [mm]","cog_eta_10":"HEC2 EC_{#eta} [mm]","cog_eta_12":"TileBar0 EC_{#eta} [mm]","cog_eta_13":"TileBar1 EC_{#eta} [mm]","cog_eta_21":"FCal0 EC_{#eta} [mm]","cog_eta_22":"FCal1 EC_{#eta} [mm]","cog_phi_1":"EMB1 EC_{#phi} [mm]","cog_phi_2":"EMB2 EC_{#phi} [mm]","cog_phi_5":"EME1 EC_{#phi} [mm]","cog_phi_6":"EME2 EC_{#phi} [mm]","cog_phi_7":"EME3 EC_{#phi} [mm]","cog_phi_8":"HEC0 EC_{#phi} [mm]","cog_phi_9":"HEC1 EC_{#phi} [mm]","cog_phi_10":"HEC2 EC_{#phi} [mm]","cog_phi_12":"TileBar0 EC_{#phi} [mm]","cog_phi_13":"TileBar1 EC_{#phi} [mm]","cog_phi_21":"FCal0 EC_{#phi} [mm]","cog_phi_22":"FCal1 EC_{#phi} [mm]"}
  
    return histo_list

def list_3():
  
    histo_list = {"width_eta_1":"EMB1 width_{#eta} [mm]","width_eta_2":"EMB2 width_{#eta} [mm]","width_eta_5":"EME1 width_{#eta} [mm]","width_eta_6":"EME2 width_{#eta} [mm]","width_eta_7":"EME3 width_{#eta} [mm]","width_eta_8":"Hwidth0 width_{#eta} [mm]","width_eta_9":"Hwidth1 width_{#eta} [mm]","width_eta_10":"Hwidth2 width_{#eta} [mm]","width_eta_12":"TileBar0 width_{#eta} [mm]","width_eta_13":"TileBar1 width_{#eta} [mm]","width_eta_21":"FCal0 width_{#eta} [mm]","width_eta_22":"FCal1 width_{#eta} [mm]","width_phi_1":"EMB1 width_{#phi} [mm]","width_phi_2":"EMB2 width_{#phi} [mm]","width_phi_5":"EME1 width_{#phi} [mm]","width_phi_6":"EME2 width_{#phi} [mm]","width_phi_7":"EME3 width_{#phi} [mm]","width_phi_8":"Hwidth0 width_{#phi} [mm]","width_phi_9":"Hwidth1 width_{#phi} [mm]","width_phi_10":"Hwidth2 width_{#phi} [mm]","width_phi_12":"TileBar0 width_{#phi} [mm]","width_phi_13":"TileBar1 width_{#phi} [mm]","width_phi_21":"FCal0 width_{#phi} [mm]","width_phi_22":"FCal1 width_{#phi} [mm]"}
  
    return histo_list

def list_4():

    histo_list = {'extrapWeight_0':"PreSamplerB extrap weight","extrapWeight_1":"EMB1 extrap weight","extrapWeight_2":"EMB2 extrap weight","extrapWeight_3":"EMB3 extrap weight","extrapWeight_4":"PreSamplerE extrap weight","extrapWeight_5":"EME1 extrap weight","extrapWeight_6":"EME2 extrap weight","extrapWeight_7":"EME3 extrap weight","extrapWeight_8":"HEC0 extrap weight","extrapWeight_9":"HEC1 extrap weight","extrapWeight_10":"HEC2 extrap weight","extrapWeight_11":"HEC3 extrap weight","extrapWeight_12":"TileBar0 extrap weight","extrapWeight_13":"TileBar1 extrap weight","extrapWeight_14":"TileBar2 extrap weight","extrapWeight_15":"TileGap1 extrap weight","extrapWeight_16":"TileGap2 extrap weight","extrapWeight_17":"TileGap3 extrap weight","extrapWeight_18":"TileExt0 extrap weight","extrapWeight_19":"TileExt1 extrap weight","extrapWeight_20":"TileExt2 extrap weight","extrapWeight_21":"FCal0 extrap weight","extrapWeight_22":"FCal1 extrap weight","extrapWeight_23":"FCal2 extrap weight"}

    return histo_list

def SaveCanvas(canvas, output_dir, histoName):
    print(canvas)
    print(output_dir)
    print(histoName)
    canvas.SaveAs(output_dir + '/png/' + histoName + ".png" )
    canvas.SaveAs(output_dir + '/pdf/' + histoName + ".pdf" )
    canvas.SaveAs(output_dir + '/eps/' + histoName + ".eps" )

def overlay_histos(tree_1, tree_2, name, output_dir, hist1, title, minX, maxX):
    h1 = ROOT.TH1F("h1","",30,minX,maxX) 
    h2 = ROOT.TH1F("h2","",30,minX,maxX) 
    tree_1.Draw('%s>>h1'%(hist1),"","off")
    tree_2.Draw('%s>>h2'%(hist1),"","off")
    h1.SetLineColor(ROOT.kBlack)
    h1.SetMarkerColor(ROOT.kBlack)
    h2.SetLineColor(ROOT.kRed)
    h2.SetMarkerColor(ROOT.kRed)
    h1.SetLineWidth(4)
    h2.SetLineWidth(4)
    h2.SetLineStyle(7)
    h1.Scale(1/h1.GetEntries())
    h2.Scale(1/h2.GetEntries())
    canvas = ROOT.TCanvas('canvas_%s' % (title), '', 900, 900)
    h1.Draw('Ehist')
    h1.GetXaxis().SetTitle('%s' % title)
    h1.GetYaxis().SetTitle("Events")
    m = [h1.GetBinContent(h1.GetMaximumBin()),h2.GetBinContent(h2.GetMaximumBin())]
    h1.GetYaxis().SetRangeUser(0,max(m) *1.25)
    h1.GetXaxis().SetTitleSize(0.04)
    h1.GetYaxis().SetTitleSize(0.04)
    h1.GetXaxis().SetLabelSize(0.035)
    h1.GetYaxis().SetLabelSize(0.035)
    h2.Draw('Ehistsame')
    ROOT.ATLAS_LABEL( 0.19, 0.88, ROOT.kBlack, legend )
    canvas.cd()
    lparams = {'xoffset' : 0.65, 'yoffset' : 0.82, 'width'   : 0.3, 'height'  : 0.10}
    leg = MakeLegend( lparams )
    leg.SetTextSize(0.03)
    leg.Draw()
    if (DoGAN):
      leg.AddEntry(h1,"Nominal","ep")
      leg.AddEntry(h2,"GAN","ep")
      SaveCanvas(canvas, output_dir, name + "_" + hist1)
    else:
      leg.AddEntry(h1,"Geant4","ep")
      leg.AddEntry(h2,"Voxelisation","ep")
      SaveCanvas(canvas, output_dir_val, name + "_" + hist1)
    leg.Draw('same')
    canvas.Write()

def overlay_profile(tree_1, tree_2, name, output_dir, ratio1, title, minX, maxX, minY, maxY):
    p1 = ROOT.TProfile("p1","",25,minX,maxX) 
    p2 = ROOT.TProfile("p2","",25,minX,maxX) 
    tree_1.Draw('%s>>p1'%(ratio1),"","")
    tree_2.Draw('%s>>p2'%(ratio1),"","")
    print(p2.GetEntries())
    p1.SetLineColor(ROOT.kBlack)
    p1.SetMarkerColor(ROOT.kBlack)
    p2.SetLineColor(ROOT.kRed)
    p2.SetMarkerColor(ROOT.kRed)
    p1.SetLineWidth(4)
    p2.SetLineWidth(4)
    p2.SetLineStyle(7)
    canvas = ROOT.TCanvas('canvas_%s' % (title), '', 900, 900)
    p1.Draw('Ehist')
    p1.SetTitle('%s' % title)
    m = [p1.GetBinContent(p1.GetMaximumBin()),p2.GetBinContent(p2.GetMaximumBin())]
    p1.GetYaxis().SetRangeUser(minY,maxY)   
    p1.GetXaxis().SetTitleSize(0.04)
    p1.GetYaxis().SetTitleSize(0.04)
    p1.GetYaxis().SetTitleOffset(p1.GetYaxis().GetTitleOffset()*1.1)
    p1.GetXaxis().SetLabelSize(0.035)
    p1.GetYaxis().SetLabelSize(0.035)
    p2.Draw('Ehistsame')
    ROOT.ATLAS_LABEL( 0.19, 0.88, ROOT.kBlack, legend )
    canvas.cd()
    lparams = {'xoffset' : 0.65, 'yoffset' : 0.82, 'width'   : 0.3, 'height'  : 0.10}
    leg = MakeLegend( lparams )
    leg.SetTextSize(0.03)
    leg.AddEntry(p1,"Nominal","ep")
    leg.Draw()
    if (DoGAN):
      leg.AddEntry(p2,"GAN","ep")
      SaveCanvas(canvas, output_dir, name + "_" + ratio1)
    else:
      leg.AddEntry(p2,"G4","ep")
      SaveCanvas(canvas, output_dir_val, name + "_" + ratio1)
    leg.Draw('same')
    canvas.Write()

def make_plots(tree_1,tree_2, name, output_dir,particle,energy,eta_min):
  histo_list_1 = list_1()
  for index, hist1 in enumerate(histo_list_1):
      if index not in relevantLayers:
        continue
      h = ROOT.TH1F("h","",30,-1,energy*1.5) 
      tree_1.Draw('%s>>h'%(hist1),"","off")
      xmax=h.GetBinCenter(h.GetMaximumBin())
      minX = max(0, xmax-minFactor*h.GetRMS())
      if hist1 == 'e_0' or hist1 == 'e_3':
        minX = 0
      maxX = xmax+maxFactor*h.GetRMS()
      overlay_histos(tree_1, tree_2, name, output_dir, hist1, histo_list_1[hist1], minX, maxX)  

  h = ROOT.TH1F("h","",30,0.7,1.1) 
  tree_1.Draw('etotNorm>>h',"","off")
  xmax=h.GetBinCenter(h.GetMaximumBin())
  h2 = ROOT.TH1F("h2","",30,xmax-3*h.GetRMS(),xmax+3*h.GetMeanError()) 
  tree_1.Draw('etotNorm>>h2',"","off")
  xmax=h2.GetBinCenter(h2.GetMaximumBin())
  overlay_profile(tree_1, tree_2, name, output_dir, "etotNorm:phiMod", ";phiMod;E_tot/E_true", 0, 0.0066, xmax-2*h2.GetRMS(), xmax+2*h2.GetRMS() )

  histo_list_2 = list_2()
  for hist2 in histo_list_2:
      if int(hist2[8:]) not in layerWithBinningInAlpha:
        continue
      h = ROOT.TH1F("h","",100,-10,10) 
      tree_1.Draw('%s>>h'%(hist2),"","off")
      xmax=h.GetBinCenter(h.GetMaximumBin())
      minX =xmax-minFactor*h.GetRMS()
      maxX = xmax+maxFactor*h.GetRMS()
      overlay_histos(tree_1, tree_2, name, output_dir, hist2, histo_list_2[hist2], minX, maxX)
   
  histo_list_3 = list_3()
  for hist3 in histo_list_3:
      if int(hist3[10:]) not in layerWithBinningInAlpha:
        continue
      h = ROOT.TH1F("h","",100,0,100) 
      tree_1.Draw('%s>>h'%(hist3),"","off")
      xmax=h.GetBinCenter(h.GetMaximumBin())
      minX =xmax-minFactor*h.GetRMS()
      maxX = xmax+maxFactor*h.GetRMS()
      overlay_histos(tree_1, tree_2, name, output_dir, hist3, histo_list_3[hist3], minX, maxX)
   
 # histo_list_4 = list_4()
 # for hist in histo_list_4:
 #     if int(hist[len("extrapWeight_"):]) not in relevantLayers:
 #       continue
 #     h = ROOT.TH1F("h","",100,-0.1,1.1) 
 #     tree_1.Draw('%s>>h'%(hist),"","off")
 #     xmax=h.GetBinCenter(h.GetMaximumBin())
 #     minX =xmax-minFactor*h.GetRMS()
 #     maxX = xmax+maxFactor*h.GetRMS()
 #     overlay_histos(tree_1, tree_2, name, output_dir, hist, histo_list_4[hist], minX, maxX)
   
  
#voxelisationFile='%s/rootFiles/%s/pid%s_E%s_eta_%s_%s_voxalisation.root' % (vox_dir,particle,pid,energy,eta_min,eta_max)
voxelisationFile='%s/rootFiles/%s/pid%s_E%s_eta_%s_%s.root' % (vox_dir,particle,pid,energy,eta_min,eta_max)
print("voxelisationFile: " + voxelisationFile)
file_1 = ROOT.TFile.Open(voxelisationFile, 'read')
#print(vox_dir + "vox_dir")
tree_1 = file_1.Get('rootTree')
if (DoGAN):
 file_2 = ROOT.TFile.Open(root_file_GAN_plots, 'read')
 file_output = ROOT.TFile(output_fileName,"RECREATE")
 tree_2 = file_2.Get('rootTree')
 make_plots(tree_1,tree_2,name, output_dir,particle,energy,eta_min)

else:
 validatioFileName='%s/rootFiles/validation/%s/pid%s_E%s_eta_%s_%s.root' % (vox_dir, particle,pid,energy,eta_min,eta_max)
 print("validatioFileName: " + validatioFileName)
 file_2 = ROOT.TFile.Open(validatioFileName, 'read')
 tree_2 = file_2.Get('rootTree')
 file_output = ROOT.TFile(output_fileName,"RECREATE")
 make_plots(tree_2,tree_1,name, output_dir,particle,energy,eta_min)



