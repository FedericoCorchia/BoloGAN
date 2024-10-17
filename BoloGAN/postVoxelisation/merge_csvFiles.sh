#!/bin/bash

### Run using: source merge_csvFiles.sh

source ../common/config.sh
#pids="11"
here=$PWD
copyBatches="true"
#useSeed=noSeed

# Go to where data is stored 
cd ${vox_dir}
echo "running in $PWD"

#make directory to store all the batches of voxelized data
if [[ ! -d dataBatches ]]; then
  mkdir dataBatches 
  cd dataBatches
  mkdir cells_validation
  mkdir g4hits_validation
  mkdir hits_validation
  mkdir validation
  mkdir voxalisation
  cd .. 
  echo "Folders with batches created"
fi 

#concatenate the batches of data and move them into csvFiles 
for pid in ${pids}
do
  SetVariablesGivenPid 

  for eta in ${etas}
  do
    source merge_csvFilesInSlice.sh
    
  done 
done

cd ${here}












