#!/usr/bin/env python3

import tensorflow as tf
 
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, BatchNormalization, Concatenate, concatenate

import numpy as np
import math
import argparse 
import os,sys,ctypes
import ROOT 
import shutil
import ctypes



ROOT.gROOT.SetMacroPath('../plotting/utils/')
ROOT.gROOT.Macro( "rootlogon.C" )
ROOT.gROOT.LoadMacro( "AtlasUtils.C" )
ROOT.gROOT.SetBatch(True)
sys.path.append('../model/')
sys.path.append('../plotting/')
sys.path.append('../common/')
from helper_functions import *

from VoxInputParameters import VoxInputParameters
from XMLHandler import XMLHandler

parser = argparse.ArgumentParser(description="Plot observables")
parser.add_argument('-e1', '--eta_min', default='')
parser.add_argument('-e2', '--eta_max', default='')
parser.add_argument('-v',  '--vox_dir', default='')
parser.add_argument('-ip', '--particle', default='')
parser.add_argument('-i', '--input_dir_gan', default='')
parser.add_argument('-idg', '--input_dir_gan_root', default='')
parser.add_argument('-o', '--output_dir', default='')
parser.add_argument('-p', '--pid', default='')
parser.add_argument('-e', '--epoch', default='')
parser.add_argument('-plot ', '--makeValidationPlotsFalse', default=False)

args = parser.parse_args()

eta_min = args.eta_min
eta_max = args.eta_max
particle = args.particle
pid = int(args.pid)
input_dir_gan = args.input_dir_gan
input_dir_gan_root = args.input_dir_gan_root
output_dir = args.output_dir
vox_dir = args.vox_dir
epoch = args.epoch
makeValidationPlots=args.makeValidationPlotsFalse

latent_dim=50
n_events=10000

if pid == 22:
  particleName="#gamma"
  particle="photons"
elif pid == 211:
  particleName="#pi"
  particle="pions"
elif pid == 11:
  particleName="e"
  particle="electrons"


def energy_list():
    energies = []
    exp = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    for i in exp:
       energies.append(2**i)
    return energies

#def load(particle, label, nevents, input_dir_gan,eta_min,eta_max):
#     init = tf.initialize_all_variables()
#     energyArray = np.full((nevents,1), label)
#
#     with tf.Session() as sess:
#       sess.run(init)
#       self.saver.restore(sess, input_dir_gan + "/%s/checkpoints_eta_%s_%s/model_%s.ckpt" % (particle,eta_min,eta_max,epoch))
#       samples = sess.run(self.G_sample, feed_dict={self.z: self.sample_z(nevents, self.latent_dim), self.y : energyArray})
#     return samples

#binning.xml is supposed to be in the sam folder as the csv files used for training
print("Opening XML file in " + vox_dir + "binning.xml")
   
voxInputs = VoxInputParameters(vox_dir, particle, eta_min, eta_max, xmlFileName = "binning.xml")
xml = XMLHandler(voxInputs)
img_dim = xml.GetTotalNumberOfBins()

## Build keras model
noise = Input(shape=(latent_dim,), name="Noise")
condition = Input(shape=(3,), name="mycond")
con = concatenate([noise,condition])
G = Dense(50,activation='relu',kernel_initializer='glorot_normal',name='l0')(con)
G = Dense(100,activation='relu',kernel_initializer='glorot_normal',name='l1')(G)
G = Dense(200,activation='relu',kernel_initializer='glorot_normal',name='l2')(G)
G = Dense(img_dim,activation='relu',name='l3')(G)
generator = Model(inputs=[noise, condition], outputs=G)

## Get checkpoint file
checkpointfile = "%s/model_%s_%s_%s.ckpt" % (input_dir_gan, particle, eta_min, eta_max)

## Peek into the file, see what the variables are called
from tensorflow.python.tools import inspect_checkpoint as chkp
chkp.print_tensors_in_checkpoint_file(checkpointfile,tensor_name='', all_tensors=True)

## Open the checkpoint file
print("here")

###If tf1.14
#reader = tf.train.NewCheckpointReader(checkpointfile)
###If tf2.0rc
reader = tf.train.load_checkpoint(checkpointfile)
print("here")
##check shapes of tensors
print(reader.get_tensor('Variable').shape)
print(reader.get_tensor('Variable_1').shape)
print(reader.get_tensor('Variable_8').shape)
print(reader.get_tensor('Variable_9').shape)
print(reader.get_tensor('Variable_10').shape)
print("here")

## We know the generator variables start at 8, and go Weights, Bias and so on (looking at the code)
tensorvar = 8
#tensorvar = 10
for x in range(4):
    print("here")
    weighttuple = (reader.get_tensor('Variable_{0}'.format(tensorvar)),reader.get_tensor('Variable_{0}'.format(tensorvar+1)))
    ## Get the weights, create a list of (layer_w,layer_b) for the current layer, and set the weights in the keras model
    generator.get_layer('l{0}'.format(x)).set_weights(weighttuple)
    tensorvar+=2

## Bob's your uncle and now you should have the weights in h5 format through keras
generator.save_weights(output_dir + '/checkpoint_%s_eta_%s_%s.h5' % (particle,eta_min,eta_max))

weight = generator.get_weights()
np.savetxt('weight.csv' , weight , fmt='%s', delimiter=',')

canvases = []   
lparams = {'xoffset' : 0.1, 'yoffset' : 0.27, 'width'   : 0.8, 'height'  : 0.35}
histos_ganTf = []
input_files_ganTf = []
minFactors = [3.5, 3.5, 3.5, 4.5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

if pid == 22 or pid == 11 :
  minFactor = 3
  maxFactor = 3  
else :
  minFactor = 4
  maxFactor = 3.5

if makeValidationPlots:
  energies = energy_list()
  E_max = np.max(energies) #same E_max as DataReader
  for item in range(0,len(energies)):    
    #print(" Energy ", energies[item])
    input_file_ganTf = (input_dir_gan_root + '/pid%i_E%s_eta_%s_%s_GAN_%s.root' % (pid, energies[item], eta_min, eta_max,epoch))
    infile_ganTf = ROOT.TFile.Open(input_file_ganTf, 'read') 
    input_files_ganTf.append(infile_ganTf)
    tree = infile_ganTf.Get('rootTree') 
    
    h = ROOT.TH1F("h","",100,0,energies[item]*2) 
    tree.Draw("etot>>h","","off")
    xmax=h.GetBinCenter(h.GetMaximumBin());
    minX = max(0, xmax-minFactor*h.GetRMS()) #max(0, xmax-minFactors[item]*h.GetRMS())
    maxX = xmax+maxFactor*h.GetRMS()
    #print("min "+ str(minX) + " max " + str(maxX))
        
    h_ganTf = ROOT.TH1F("h_ganTf","",30,minX,maxX) 
    tree.Draw("etot>>h_ganTf","","off")
    h_ganTf.Scale(1/h_ganTf.GetEntries())
    histos_ganTf.append(h_ganTf)

  histos_gan =[]
  canvas = ROOT.TCanvas('canvas_h', 'Total Energy comparison plots', 900, 900)
  canvases.append(canvas)
  canvas.Divide(4,4)
  chi2_tot = 0.
  ndf_tot = 0

  for item in range(0,len(energies)):
   ene=energies[item]
   ns = np.random.uniform(-1, 1, (n_events, latent_dim))
   energy = np.ones((n_events, 1))*ene/E_max
   data = generator.predict([ns, energy])
   data = data * ene

   h_ganTf = histos_ganTf[item]
   h_gan = ROOT.TH1F("h_gan","",30,h_ganTf.GetXaxis().GetXmin(),h_ganTf.GetXaxis().GetXmax()) 

   for i in range (0, min(n_events,data.shape[0])):
     E_tot = data[i,:].sum(axis=0)
     E_tot = E_tot 
     h_gan.Fill(E_tot)

   h_gan.Scale(1/h_gan.GetEntries())
   h_gan.SetLineColor(ROOT.kRed)
   
   m = [h_ganTf.GetBinContent(h_ganTf.GetMaximumBin()),h_gan.GetBinContent(h_gan.GetMaximumBin())]
   h_ganTf.GetYaxis().SetRangeUser(0,max(m) *1.25)
        
   histos_gan.append(h_gan)

   chi2 = ROOT.Double(0.)
   ndf = ctypes.c_int(0)
   igood = ctypes.c_int(0)

   histos_ganTf[item].Chi2TestX(histos_gan[item],chi2,ndf,igood,"WW")

   ndf = ndf.value

   print("Epoch %s Energy %s : chi2/ndf = %.1f / %i = %.1f\n" % (epoch, energy, chi2, ndf, chi2/ndf))

   canvas.cd(item+1)
   histos_ganTf[item].Draw("HIST")
   histos_gan[item].Draw("HIST same")

   if (ene > 1024):
        energy_legend =  str(round(ene/1000,1)) + "GeV"
   else:
        energy_legend =  str(ene) + "MeV"
   t = ROOT.TLatex()
   t.SetNDC()
   t.SetTextFont(42)
   t.SetTextSize(0.1)
   t.DrawLatex(0.2, 0.83, energy_legend)

   chi2_o_ndf = chi2 / ndf
   print("Epoch %s Total Energy : chi2/ndf = %.1f / %i = %.3f\n" % (epoch, chi2, ndf, chi2_o_ndf))


   # Legend box particle
   leg = MakeLegend( lparams )
   leg.SetTextFont( 42 )
   leg.SetTextSize(0.1)
   canvas.cd(16)
   leg.AddEntry(h_ganTf,"GAN Tf","l") #TensorFlow
   leg.Draw()
   leg.AddEntry(h_gan,"GAN Keras","l")  #keras conversion
   leg.Draw('same')
   legend = (particleName + ", " + str('{:.2f}'.format(int(eta_min)/100,2)) + "<|#eta|<" + str('{:.2f}'.format((int(eta_min)+5)/100,2)))
   ROOT.ATLAS_LABEL_BIG( 0.1, 0.9, ROOT.kBlack, legend )

   # Legend box Epoc&chi2 

   t = ROOT.TLatex()
   t.SetNDC()
   t.SetTextFont(42)
   t.SetTextSize(0.1)
   t.DrawLatex(0.1, 0.18, "Epoch: %s" % (epoch))
  t.DrawLatex(0.1, 0.07, "#scale[0.8]{#chi^{2}/NDF = %.0f/%i = %.1f}" % (chi2, ndf, chi2_o_ndf)) 


  inputFile_Plot_png="Plot_comparison_tot_energy_pid%s_eta_%s_%s.png" % (pid,eta_min,eta_max)
  canvas.SaveAs(inputFile_Plot_png) 

# serialize model to JSON
generator_model_json = generator.to_json()
with open(output_dir + "/generator_model_%s_eta_%s_%s.json" % (particle, eta_min, eta_max), "w") as json_file:
     json_file.write(generator_model_json)


