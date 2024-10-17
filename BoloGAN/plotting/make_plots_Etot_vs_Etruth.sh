#!/bin/bash
source ../utils/config.sh
echo $GAN_name

echo " Running in: $PWD"


for pid in ${pids}
do

  if [[ ${pid} == "22" ]];then
     particle=photons
  elif [[ $pid == "11" ]];then
     particle=electrons
  else
     particle=pions
  fi
  
  time  python3 ${PWD}/plots_Etot_vs_Etruth.py -v ${vox_dir} -odg ${gan_root_files} -ip ${particle} -e1 ${minEta} -p ${pid} -d ${output_dir_plots} 

 done
