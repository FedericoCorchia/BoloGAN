#!/bin/bash

### Run using: source merge_rootFiles.sh

source ../common/config.sh
#pids="22"
here=$PWD
copyBatches="true"
#useSeed="false"

echo "running in $PWD"

if [[ ! -d ${vox_dir}/rootBatches ]]; then
  mkdir ${vox_dir}/rootBatches
fi

for pid in ${pids}
do
  SetVariablesGivenPid 
  #Override energies and etas here
  #etas="100"

  for eta in ${etas}
  do
    source merge_rootFilesInSlice.sh
  done
done


cd ${here}












