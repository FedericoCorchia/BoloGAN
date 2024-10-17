#!/bin/bash

source ../..//common/config.sh
here=$PWD

#output_dir="$pwd/output_converters"
#input_for_service="input_for_service"

#output_dir=${best_checkpoints_dir}/output_converters 
#input_for_service=${best_checkpoints_dir}/input_for_service

pids="22"

for pid in ${pids}
do
  SetVariablesGivenPid
  samplesRangeList="High12" #"UltraLow12" #"High12"

  for samplesRange in ${samplesRangeList}
  do
    GAN_name=Production_${particle}
    SetFolderFromGANName
    InitBestCheckpointFolders

    output_dir=${best_checkpoints_dir}/output_converters 
    input_for_service=${best_checkpoints_dir}/input_for_service
       
    mkdir -p ${output_dir} 
    mkdir -p ${input_for_service} 

    code_dir=${gan_dir}/code
    cp tf_cGAN_to_keras_v2.py ${code_dir}
    cd ${code_dir}

    #Moved the loop inside python to only call TF once
    etaMin=300
    etaMax=305
    python3 tf_cGAN_to_keras_v2.py -e1 ${etaMin} -e2 ${etaMax} -v ${vox_dir} -ip ${particle} -i ${best_checkpoints_dir} -o ${output_dir} -r ${samplesRange}

    etas="300"
    for eta in $etas  
    do
      eta_min=${eta}
      eta_max=$((${eta}+5))

            
      #architecture.json inputs.json weights.h5 > neural_net.json
      architecture="${output_dir}/generator_model_${particle}_eta_${eta_min}_${eta_max}_${samplesRange}.json"
      inputs="${output_dir}/variables_${particle}_eta_${eta_min}_${eta_max}_${samplesRange}.json" #"variables_pions_region_1.json" #${output_dir}/variables_${particle}_eta_${eta_min}_${eta_max}.json"
      weights="${output_dir}/checkpoint_${particle}_eta_${eta_min}_${eta_max}_${samplesRange}.h5"
      neural_net="${input_for_service}/neural_net_${pid}_eta_${eta_min}_${eta_max}_${samplesRange}.json"
      
      echo "lwtnn/converters/kerasfunc2json.py $architecture $weights > $inputs"      
      #lwtnn/converters/kerasfunc2json.py $architecture $weights > $inputs
      /cvmfs/sft.cern.ch/lcg/releases/lwtnn/2.11.1-2ee64/x86_64-centos7-gcc8-opt/converters/kerasfunc2json.py $architecture $weights > $inputs

      echo "lwtnn/converters/kerasfunc2json.py $architecture $weights $inputs > $neural_net"
      #lwtnn/converters/kerasfunc2json.py $architecture $weights $inputs > $neural_net
      /cvmfs/sft.cern.ch/lcg/releases/lwtnn/2.11.1-2ee64/x86_64-centos7-gcc8-opt/converters/kerasfunc2json.py $architecture $weights $inputs > $neural_net
    
    done  
  done
done
cd $here