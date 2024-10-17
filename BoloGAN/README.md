# FastCaloGAN

A Fast Calorimeter Simulation using GANs


## Setup the environment for Tensorflow 2
At least TF2.2 is needed to use the swish activation function. 

To run on CERN HTCondor, most nodes support only cudalib 10.1 (CUDA0). This set a limit to TF2.3 as higher version require cudalib 11.0

The simplest way to run the GAN code is to use LCG installation; given the above constraints, the best solution is to use LCG_100cuda

source /cvmfs/sft.cern.ch/lcg/views/LCG_100cuda/x86_64-centos7-gcc8-opt/setup.sh

For the voxelisation please check the rootToCsv folder for specific instructions as the code there is written in C++ and requires a different environment.

## Common folder
This folder contains classes and bash script that are used in multiple places in tha FastCaloGAN tool.

### Bash scripts
There are two bash scripts called common.sh and functions.sh. 
The first contains the constants used to define etas, batches, energyRanges and so on.
The second contains the functions that are used in many scripts at different levels to set multiple variables depending on other variables such as PID and eta. All scripts are designed to have the same nested structure of the loops to easily share these functions.

### Python classes
These classes are used by the main python scripts to define all input variables needed for a correct execution of the post-voxelisation, training and model selection.
Each class is rather self explnatory, are rather short and od not contain any significant logic.
## Validation of voxelisation
The output of the voxelisation is a long list of files that needs to be merged and validated. This is done using the scripts in the posVoxelisation folder.
Simply run

source mergeAndCheckSliceOnCondor.sh

This script uses the variables defined in the common folder config.sh and functions.sh to define which particles/eta/energies are run.
The script actually combines several scripts present in the folder. 
First, the CSV are merged. This is needed as the high energy samples are processed in batches.
Then the merged CSV are checked making sure the expected number of events is present and that the data as the correct format (# of columns).
The same precedure is repeated for the ROOT files produced by the voxelisation
If all files in a slice are correctly processed, additional ROOT files are produced with voxel-level information. These are used in the python framework when comparing to the training datasets.
As an additional feacture, the script set any correctly processed file in a folder of the rootToCsv directory. These files are used in the voxelisation script to skip correctly produced files in case any sample need to be reprocessed.

## Training of the GANs
The model folder contains the class with the GAN and the scripts to submit it on the HTCondor GPUs at CERN.
There are three submission scripts, one is for stand-alone studies, the other two are for the seed GANs pre-train (saved as Baseline) and for full detector production (saved as Production).
Condor script, log and outputs are stored locally, the code is copied to a "code" folder on the eos space in which the checkpoints are stored. That code will be reused for evaluation and conversion to make sure the GAN definition and code is consistent for all steps.

## Plotting folder
This folder contains the checkpoint/model selection and several scripts to plot the performance of the GANs (vs eta, vs energy, detailed plots for all energy points, tables).


