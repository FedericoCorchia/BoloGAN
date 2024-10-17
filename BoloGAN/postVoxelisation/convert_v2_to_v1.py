#!/usr/bin/env python3

import numpy as np
import pandas as pd
import argparse 
import sys

sys.path.append('../common/')
from VoxInputParameters import VoxInputParameters
from XMLHandler import XMLHandler

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#parser = argparse.ArgumentParser(description="Plot total energy")
#parser.add_argument('-f',  '--inputFolder', default='')
#parser.add_argument('-e',  '--eta', default='')
#parser.add_argument('-p',  '--pid', default='')
#parser.add_argument('-b',  '--totalBatches', default='')

#args = parser.parse_args()
vox_dir="/eos/atlas/atlascerngroupdisk/proj-simul/VoxalisationOutputs/nominal_v1_highstat"
eta_min=20
eta_max=25
particle="photons"
pid=22

maximum=23
minimum=8


inputs = VoxInputParameters(vox_dir, particle, eta_min, eta_max, False)
xml = XMLHandler(inputs)

newOrder=[]
for l in xml.relevantlayers:
    for a in range (0, xml.a_bins[l]):
        for r in range (0, xml.r_bins[l]):
            newOrder.append(r*xml.a_bins[l] + a + xml.GetBinEdges()[l])

print(newOrder)


for e in range(minimum, maximum):
    p = 2**e
  
    fileName = "%s/csvFiles/pid%s_E%s_eta_%d_%d_voxalisation.csv" % (vox_dir, pid, p, eta_min, eta_max) 
    df = pd.read_csv(fileName, header=None, engine='python', dtype=np.float64)
    first_column = df.columns[0]
    second_column = df.columns[1]
    df = df.drop([first_column, second_column], axis=1) #Removing the first two element which is phiMod and eta

    df = df[[df.columns[i] for i in newOrder]]
    fileNameOut = "%s/csvForPublic/pid%s_E%s_eta_%d_%d_voxalisation.csv" % (vox_dir, pid, p, eta_min, eta_max) 
    df.to_csv(fileNameOut, index=False, header=False)