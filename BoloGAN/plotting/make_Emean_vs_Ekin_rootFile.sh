#!/bin/bash
source ../common/config.sh
echo $GAN_name

echo " Running in: $PWD"

pids="22 11 211"

for pid in ${pids}
do
  SetVariablesGivenPid

  for eta in ${etas}
  do
    eta_min=${eta}
    eta_max=$((${eta}+5))
    python3 ${PWD}/plots_Etot_vs_Ekin.py -ip ${particle} -e1 ${eta_min} -e2 ${eta_max} -d ${vox_dir}/plots -p ${pid}
  done 
done
