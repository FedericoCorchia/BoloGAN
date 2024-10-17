#!/bin/bash

source ../common/config.sh
etaSelection=all

echo " Running in: $PWD"
MaxRuntime=$((24*60*60))
memory=7000

minEpoch=1
maxEpoch=999

user=${USER}
tryResume="True"

#pids="2212"

for pid in ${pids}
do
  SetVariablesGivenPid
  #echo $samplesRangeList
  #samplesRangeList="High12" #"UltraLow12" #"High12"

  for samplesRange in ${samplesRangeList} 
  do
    GAN_name=Production_${particle}_lwtnn
    SetFolderFromGANName

    echo Running in ${gan_dir}

    echo Create log error and output dirs 
    sub_dir=$PWD/submission_${GAN_name}
    log_dir=${sub_dir}/log
    output_dir=${sub_dir}/output
    error_dir=${sub_dir}/error
    script_dir=${sub_dir}/scripts
    code_dir=${gan_dir}/code

    mkdir -p ${log_dir}
    mkdir -p ${output_dir}
    mkdir -p ${error_dir}
    mkdir -p ${script_dir}
    mkdir -p ${code_dir}

    echo create checkpoint dir
    checkpoint_dir=${gan_dir}/checkpoints
    mkdir -p ${checkpoint_dir}

    cp *.py ${code_dir}
    cp ../common/*.py ${code_dir}

    #etas=$(eval echo "{215..225..5}") #"{255..495..5}")

    for eta in ${etas}
    do
      eta_min=${eta}
      eta_max=$((${eta}+5))
      checkpoint_dir_full=${checkpoint_dir}/${particle}/checkpoints_eta_${eta_min}_${eta_max}

      startingEpoch=0

      FILE1=${checkpoint_dir_full}/model_${maxEpoch}.ckpt.meta
      FILE2=${checkpoint_dir_full}/model_${minEpoch}.ckpt.meta
      echo testing $FILE1
      
      if [[ $tryResume == "True" ]]; then
        echo "Try to resume training"
        if test -f "$FILE1"; then
          echo "${particle}, eta_min: ${eta_min}, eta_max: ${eta_max} was trained successfully"
        continue
        elif [ ! -f "$FILE2" ]; then
          echo "${particle}, eta_min: ${eta_min}, eta_max: ${eta_max} was not trained at all, starting from 0"
          startingEpoch=0
        else
          for epoch in $(eval echo "{${minEpoch}..${maxEpoch}}")
          do
            FILE=${checkpoint_dir_full}/model_${epoch}.ckpt.meta
            if test -f "$FILE"; then
              echo -ne "${particle}, eta_min: ${eta_min}, eta_max: ${eta_max} was trained up to ${epoch}\r"
              startingEpoch=${epoch}
            else
              echo "${particle}, eta_min: ${eta_min}, eta_max: ${eta_max} was trained up to $((${epoch}-1))"
              break
            fi
          done
        fi
      else
        echo "Restarting training from zero"
      fi
      

      echo Running gan for particle: ${particle}, eta_min: ${eta_min}, eta_max: ${eta_max} starting from epoch ${startingEpoch}
      tag_log=${GAN_name}_${samplesRange}_eta_${eta_min}_${eta_max}
      condor_file=${script_dir}/condor_${tag_log}.sub
      job=${script_dir}/${tag_log}.sh

      log_file=${tag_log}.log
      error_file=${tag_log}.error
      output_file=${tag_log}.out
      condor_template=condorTEMPLATE.sub

      cp $condor_template ${condor_file}

      sed -i "s!@ERROR_DIR@!${error_dir}!g" ${condor_file}
      sed -i "s!@LOG_DIR@!${log_dir}!g" ${condor_file}
      sed -i "s!@SCRIPT_DIR@!${script_dir}!g" ${condor_file}
      sed -i "s!@OUTPUT_DIR@!${output_dir}!g" ${condor_file}
      sed -i "s!@JOB@!${job}!g" ${condor_file}
      sed -i "s!@LOG@!${log_file}!g" ${condor_file}
      sed -i "s!@ERROR@!${error_file}!g" ${condor_file}
      sed -i "s!@OUTPUT@!${output_file}!g" ${condor_file}
      sed -i "s!@TAG@!${binningName}_${tag_log}!g" ${condor_file}
      sed -i "s!@MAXRUNTIME@!${MaxRuntime}!g" ${condor_file}
      sed -i "s!@JOBFLAVOUR@!${JobFlavour}!g" ${condor_file}
      sed -i "s!@MEM@!${memory}!g" ${condor_file}
      sed -i "s!@USER@!${user}!g" ${condor_file}

cat > $job << EOF
#!/bin/bash

echo "Setup ..." 
source /cvmfs/sft.cern.ch/lcg/views/LCG_100cuda/x86_64-centos7-gcc8-opt/setup.sh

root --version

cd ${code_dir}
echo $path
time python3 train_V2_production_wgangp.py -odg ${checkpoint_dir} -e ${startingEpoch} -i ${vox_dir} -ip ${particle} -emin ${eta_min} -emax ${eta_max} -r ${samplesRange}
EOF

      echo "Submitting config: ${condor_file}"
      chmod 775 $job
      condor_submit ${condor_file}
      #${job}

    done
  done  
done