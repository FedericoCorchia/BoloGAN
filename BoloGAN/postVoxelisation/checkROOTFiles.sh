#!/bin/bash

### Run ./script.sh 

source ../utils/config.sh
echo " Running in: $PWD"

pid="22"
useSeed=true

SetVariablesGivenPid

for eta in ${etas}
do
  echo $eta
  python checkROOTFilesInSlice.py -f ${vox_dir} -e ${eta} -p ${pid}
done
