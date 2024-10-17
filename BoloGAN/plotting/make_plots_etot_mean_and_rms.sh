#!/bin/bash
source ../utils/config.sh
echo $GAN_name

doGen="False"
energies="65536"

echo " Running in: $PWD"
echo " Generating data: $doGen"


for pid in ${pids}
do

  if [[ ${pid} == "22" ]];then
     particle=photons
  elif [[ $pid == "11" ]];then
     particle=electrons
  else
     particle=pions
  fi
  
  if [ $doGen == "True" ]     
  then
    for energy in ${energies}
    do     
      rm ${output_dir_plots}/RMS_and_mean_${energy}_${particle}.txt
      #Delete files inside script so that if condor jobs is restared the chi2 is deleted again
      for eta in $(eval echo "{${minEta}..${maxEta}..5}")
      do
        eta_min=${eta}
        eta_max=$((${eta}+5))
 
        chi2File=${best_checkpoints_dir}/chi2/chi2_${pid}_${eta_min}_${eta_max}.txt
        bestchi2File=${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt
         
        echo "Loading best checkpoint for eta_min:${eta_min} eta_max:${eta_max} and particle:${particle}"
        mapfile -t myArray < ${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt
        best_checkpoint=${myArray[0]%% *}
        echo BEST CHECKPOINT ${best_checkpoint}
        
        ganPlotFile=${output_dir_gan}/pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_GAN_${best_checkpoint}.root
        python3 ${PWD}/generate_data_etot_mean_vs_eta.py -in ${vox_dir} -gp ${ganPlotFile} -emin ${best_checkpoint} -ip ${particle} -e1 ${eta_min} -e2 ${eta_max} -e ${energy} -p ${pid} -d ${output_dir_plots} -g True 
      done
    done
  fi
  
  for energy in ${energies}
  do     
    python3 ${PWD}/plots_etot_mean_vs_eta.py -d ${output_dir_plots} -ip ${particle} -e ${energy}
  done
done
