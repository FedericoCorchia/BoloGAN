#!/bin/bash

source ../utils/config.sh

#chi2File=${best_checkpoints_dir}/chi2/chi2_${pid}_${eta_min}_${eta_max}.txt
#bestchi2File=${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt
output_dir=${best_checkpoints_dir}/output_converters 
input_for_service=${best_checkpoints_dir}/input_for_service

for pid in ${pids}
do
  if [[ ${pid} == "22" ]];then
       particle=photons
  elif [[ $pid == "11" ]];then
       particle=electrons
  else
       particle=pions
  fi
  
  for eta in $(eval echo "{${minEta}..${maxEta}..5}")
  do
      eta_min=${eta}
      eta_max=$((${eta}+5))
       
      echo Launch tf2 converter to Keras conditional GAN for best epoch, particle: ${particle}, pid: ${pid}, eta_min: ${eta_min}, eta_max: ${eta_max}       
      echo "Loading best checkpoint for eta_min:${eta_min} eta_max:${eta_max} and particle:${particle}"

      bestEpochFile=${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt
      FILE=/etc/resolv.conf
      if [[ ! -f "${bestEpochFile}" ]]; then
        echo "Best epoch was not selected!!! Skipping"
        #continue
      fi

      mapfile -t myArray < ${bestEpochFile}
      best_checkpoint=${myArray[0]%% *}
      echo BEST CHECKPOINT ${best_checkpoint}
      if [[ ${best_checkpoint} = "" ]]; then
        echo "Best epoch was not selected!!! Skipping"
        #continue
        best_checkpoint=0
      fi

      mkdir -p ${output_dir} 
      mkdir -p ${input_for_service} 
      python3 ${PWD}/tf_cGAN_to_keras.py -idg ${gan_root_files} -e ${best_checkpoint} -e1 ${eta_min} -e2 ${eta_max} -v ${input_dir} -ip ${particle} -p ${pid} -i ${best_checkpoints_dir} -o ${output_dir}
            
      lwtnn/converters/kerasfunc2json.py ${output_dir}/generator_model_${particle}_eta_${eta_min}_${eta_max}.json ${output_dir}/checkpoint_${particle}_eta_${eta_min}_${eta_max}.h5 > ${output_dir}/inputs_${particle}_eta_${eta_min}_${eta_max}.json
   
      lwtnn/converters/kerasfunc2json.py ${output_dir}/generator_model_${particle}_eta_${eta_min}_${eta_max}.json ${output_dir}/checkpoint_${particle}_eta_${eta_min}_${eta_max}.h5 ${output_dir}/inputs_${particle}_eta_${eta_min}_${eta_max}.json > ${input_for_service}/neural_net_${pid}_eta_${eta_min}_${eta_max}.json
      
  done
done
