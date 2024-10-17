source ../../common/config.sh
here=$PWD
echo $here

pids=22

for pid in ${pids}
do  
  SetVariablesGivenPid
  samplesRangeList="High12"

  for samplesRange in ${samplesRangeList}
  do
    GAN_name=Production_${particle}_swish_2xD
    SetFolderFromGANName
    InitBestCheckpointFolders

    input_for_service=${best_checkpoints_dir}/input_for_service
       
    mkdir -p ${input_for_service} 

    code_dir=${gan_dir}/code
    cp tf_to_onnx.py ${code_dir}
    cd ${code_dir}

    #Moved the loop inside python to only call TF once
    etaMin=0
    etaMax=5
    #python3 tf_cGAN_to_keras_v2.py -e1 ${etaMin} -e2 ${etaMax} -v ${vox_dir} -ip ${particle} -i ${best_checkpoints_dir} -o ${input_for_service} -r ${samplesRange}
    etas=20

    for eta in $etas  
    do
      echo "Runnin ONNX on eta:" $eta
      eta_min=${eta}
      eta_max=$((${eta}+5))
      python3 tf_to_onnx.py -e1 ${eta_min} -e2 ${eta_max} -v ${vox_dir} -ip ${particle} -i ${best_checkpoints_dir} -o ${input_for_service} -r ${samplesRange}
    done
  done
done

cd $here
