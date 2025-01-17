# BoloGAN

GAN-based fast simulation system of the ATLAS calorimeter. Submission for [CaloChallenge](https://calochallenge.github.io/homepage/).

### Important Notes
1. This repository is a public copy of the official BoloGAN one internal to CERN, only limited to the parts allowable for public release. CaloChallenge samples have been produced only through parts allowable for public release. The code of BoloGAN inside this repository is as it was when it produced the samples for the CaloChallenge;
2. The programme was originally intended to be run on CERN resources (LXPLUS). As running on external resources would imply a large amount of technicalities because of the different environment, we have developed an Apptainer (formerly Singularity) container ("BoloGANtainer") to make it possible for you to run it on your own cluster without needing to mind for such issues. As it is too heavy for a repository, to get BoloGANtainer feel free to email me at corchia@bo.infn.it and I’ll be happy to send it to you. **All instructions below require usage of the container.**

## Basics
**BoloGAN** is a Machine Learning system based on GANs (Generative Adversarial Networks) to run fast simulation of the ATLAS calorimeter. After its GANs have been trained, they are used to run simulation with more speed and less resource request than with "traditional" simulation (properly *full simulation*, done with the *Geant4* programme) but preserving good accuracy.

## Structure of BoloGAN
For GAN training, you must first run the training phase proper and then the evaluation phase, where the best GAN training checkpoint is chosen. The important scripts are the ones below:

- ```common/config.sh```: you find here the general variables, i.e. the ones used by all BoloGAN scripts (the only exception is variable ```vox_dir```, defining the folder where output and processing data are stored during training and evaluation of the best training checkpoint, which is instead at the beginning of ```common/functions.sh```);
- ```model/launch_V2_seed_local.sh```: it runs GAN training. GANs are trained for 1M epochs and one checkpoint is saved every 1000 epochs;
- ```plotting/find_best_checkpoints_seed_local.sh```: it runs evaluation of each GAN training checkpoint and chooses the best one. It compares samples generated by each checkpoint with the reference samples: the checkpoint yielding the lowest reduced chisquare is the one which produced the most similar results to the reference samples and thus the best one. It also produces plots showing this comparison.

Each of the scripts above also launches other scripts, each looking after a specific sub-task. Then there are many others which deal with functions of the programme not of our interest (e.g. the voxelisation phase: the programme can also start from raw data and voxelise them, but for the CaloChallenge we only deal with already voxelised data) or are legacy options.

## How to Run BoloGAN (through container BoloGANtainer)
1. Download training data and put them inside a directory (I'll call it ```data```). This programme does NOT use the ```.hdf5``` versions of the training data but the ```.csv``` ones (available [here](http://opendata-qa.cern.ch/record/15012) - this link is also present on the CaloChallenge website);
2. Create a directory meant to host output and processing files (I'll call it "workingdir");
3. ```$ export DATADIR=<path_to_data>``` i.e. the directory ```data``` with training data;
4. ```$ export WORKINGDIR=<path_to_workingdir>```
5. ```$ apptainer run -B $WORKINGDIR -B $DATADIR <path_to_BoloGANtainer.sif> init``` - prepares directory ```$WORKINGDIR``` so that it is ready for training;
6. ```$ apptainer run -B $WORKINGDIR -B $DATADIR <path_to_BoloGANtainer.sif> train [pions/photons]``` - runs training for pions or photons;
7. ```$ apptainer run -B $WORKINGDIR -B $DATADIR <path_to_BoloGANtainer.sif> bestiter [pions/photons]``` - runs evaluation of the best iteration for pions or photons.

For batch submission, insert all above points inside the scripts you use to launch the job, as foreseen by the job scheduler on your cluster.

IMPORTANT: some clusters deny Apptainer containers permission to access files even though correctly bind-mounted and with proper permissions, preventing the programme from running. If this is the case, add the ```-u``` flag to all Apptainer commands. If this also fails, use the ```--fakeroot``` flag instead.

### If You Have GPUs Available (Strongly Recommended to Use if You Have Them - Requires CUDA-11 and CuDNN)
1. Do all operations required on your cluster to enable GPU usage (load modules, set the environment...);
2. Create a new environment variable named ```BOLOGAN_LD_LIBRARY_PATH``` and copy into it the content of the standard environment variable ```LD_LIBRARY_PATH``` (this to make the content of ```LD_LIBRARY_PATH``` also available inside the container - the latter would normally overwrite it);
3. To all ```apptainer run``` commands exposed in the previous section add the ```—-nv``` flag and bind (```-B```) also the content of ```BOLOGAN_LD_LIBRARY_PATH```.

For batch submission, insert all above points inside the scripts you use to launch the job, as foreseen by the job scheduler on your cluster.

## Authors
- Federico Andrea Guillaume Corchia, University and INFN, Bologna, Italy

- Lorenzo Rinaldi, University and INFN, Bologna, Italy

- Matteo Franchini, University and INFN, Bologna, Italy


