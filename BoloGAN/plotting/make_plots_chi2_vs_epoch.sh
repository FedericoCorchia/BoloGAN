#!/bin/bash
source ../common/config.sh
#pids="211"
#useSeed="true"

echo $GAN_name

for pid in ${pids}
do
  SetVariablesGivenPid
  for samplesRange in ${samplesRangeList} 
  do
    GAN_name=Baseline_${particle} 
    SetFolderFromGANName
    InitBestCheckpointFolders  
    for eta in ${etas}
    do
      eta_min=${eta}
      time python3 ${PWD}/plots_chi2_vs_epoch.py -e ${eta_min} -p ${pid} -d ${best_checkpoints_dir}/chi2 -o ${best_checkpoints_dir}/chi2_vs_epoch
    done
  done
done
