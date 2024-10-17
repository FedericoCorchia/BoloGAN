source ../../common/config.sh
here=$PWD
echo $here

pids=22
etas=20

for pid in ${pids}
do  
  SetVariablesGivenPid

  for samplesRange in ${samplesRangeList}
  do
    GAN_name=Baseline_${particle}_lwtnn
    SetFolderFromGANName
    InitBestCheckpointFolders

    output_dir=${best_checkpoints_dir}/output_converters 
    input_for_service=${best_checkpoints_dir}/input_for_service
       
    mkdir -p ${output_dir} 
    mkdir -p ${input_for_service} 

    rm ${output_dir}/*.h5

    code_dir=${gan_dir}/code
    cp tf_cGAN_to_keras_v2.py ${code_dir}
    cd ${code_dir}

    #Moved the loop inside python to only call TF once
    etaMin=20
    etaMax=25
    #python3 tf_cGAN_to_keras_v2.py -e1 ${etaMin} -e2 ${etaMax} -v ${vox_dir} -ip ${particle} -i ${best_checkpoints_dir} -o ${output_dir} -r ${samplesRange}

    for eta in $etas  
    do
      echo "Runnin LWTNN on eta: " $eta
      eta_min=${eta}
      eta_max=$((${eta}+5))
      python3 tf_cGAN_to_keras_v2.py -e1 ${eta_min} -e2 ${eta_max} -v ${vox_dir} -ip ${particle} -i ${best_checkpoints_dir} -o ${output_dir} -r ${samplesRange}

      architecture="${output_dir}/generator_model_${particle}_eta_${eta_min}_${eta_max}_${samplesRange}.json"
      inputs="${output_dir}/variables_${particle}_eta_${eta_min}_${eta_max}_${samplesRange}.json" #"variables_pions_region_1.json" #${output_dir}/variables_${particle}_eta_${eta_min}_${eta_max}.json"
      weights="${output_dir}/checkpoint_${particle}_eta_${eta_min}_${eta_max}_${samplesRange}.h5"
      neural_net="${input_for_service}/neural_net_${pid}_eta_${eta_min}_${eta_max}_${samplesRange}.json"
      
      #echo "lwtnn/converters/kerasfunc2json.py $architecture $weights > $inputs"      
      /cvmfs/sft.cern.ch/lcg/releases/lwtnn/2.11.1-2ee64/x86_64-centos7-gcc8-opt/converters/kerasfunc2json.py $architecture $weights > $inputs

      #echo "lwtnn/converters/kerasfunc2json.py $architecture $weights $inputs > $neural_net"
      /cvmfs/sft.cern.ch/lcg/releases/lwtnn/2.11.1-2ee64/x86_64-centos7-gcc8-opt/converters/kerasfunc2json.py $architecture $weights $inputs > $neural_net

    done
  done
done

cd $here
