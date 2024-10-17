#!/bin/bash
source ../common/config.sh
echo $GAN_name

echo " Running in: $PWD"

pids="11"
pids=211

for pid in ${pids}
do
  SetVariablesGivenPid
  #samplesRangeList="UltraLow12" #"UltraLow12" #"High12"

  for samplesRange in ${samplesRangeList} 
  do
    GAN_name=Production_${particle}_lwtnn #_swish_2xD _lwtnn
    SetFolderFromGANName
    InitBestCheckpointFolders
    #etas=$(eval echo "{385..495..5}")

    for eta in ${etas}
    do
      eta_min=${eta}
      eta_max=$((${eta}+5))
      python3 ${PWD}/generate_data_Emean_vs_Ekin.py -v ${vox_dir} -ip ${particle} -e1 ${eta_min} -e2 ${eta_max} -p ${pid} -o ${best_checkpoints_dir} -d ${output_dir_plots} -r ${samplesRange}
     done 
  done
done
