#!/bin/bash

### Run ./script.sh 

source ../utils/config.sh
echo " Running in: $PWD"

pid="11"
useSeed=true

SetVariablesGivenPid

etas="145" 

for eta in ${etas}
do
  echo $eta
  python checkCSVFilesInSlice.py -f ${vox_dir} -e ${eta} -p ${pid}  #&> "csvCheck_${pid}_${eta}.txt" &
done
