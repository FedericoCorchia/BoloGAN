#!/bin/bash
source ../common/config.sh

echo " Running in: $PWD"

#pids="11"
pids="22"
etas="20"

for pid in ${pids}
do
  SetVariablesGivenPid
  samplesRangeList="Low12 High12" #COMMENT IF ONLY USING "ALL"

  for samplesRange in ${samplesRangeList} 
  do
    GAN_name=Baseline_${particle}_lwtnn #_swish_2xD _lwtnn #REVERT TO Production IF YOU ADOPT PRODUCTION LATER ON!
    SetFolderFromGANName
    InitBestCheckpointFolders
    #etas=$(eval echo "{350..495..5}")

    for eta in ${etas}
    do
      eta_min=${eta}
      eta_max=$((${eta}+5))


      code_dir=${gan_dir}/code
      tag_log=makeRootFiles_${particle}_${eta_min}_${eta_max}_${GAN_name}_${samplesRange}
      output_file=${output_dir}/${tag_log}.out
      script=${script_dir}/${tag_log}.sh
      log_file=${log_dir}/${tag_log}.log
      error_file=${error_dir}/${tag_log}.error
      condor_template=condorTEMPLATE.sub
      condor_file=${script_dir}/condor_${tag_log}.sub
      
      cp plots_gan.py ${code_dir}

      cp $condor_template ${condor_file}
      sed -i "s!@SCRIPT@!${script}!g" ${condor_file}
      sed -i "s!@LOG@!${log_file}!g" ${condor_file}
      sed -i "s!@ERROR@!${error_file}!g" ${condor_file}
      sed -i "s!@OUTPUT@!${output_file}!g" ${condor_file}
      sed -i "s!@MAXRUNTIME@!${MaxRuntime}!g" ${condor_file}
      sed -i "s!@MEM@!${memory}!g" ${condor_file}
      sed -i "s!@TAG@!${tag_log}!g" ${condor_file}
      sed -i "s!@MAIL@!${USER}@cern.ch!g" ${condor_file}    
      #end condor stuff
      
      chi2File=${best_checkpoints_dir}/chi2/chi2_${pid}_${eta_min}_${eta_max}.txt
      bestchi2File=${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt

      echo "Loading best checkpoint for eta_min:${eta_min} eta_max:${eta_max} and particle:${particle}"
      mapfile -t myArray < ${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt
      best_checkpoint=${myArray[0]%% *}
      echo "Best checkpoint is: ${best_checkpoint}"

cat > $script << EOF
#!/bin/bash

echo activate Tensorflow 2

cd ${code_dir}

python3 plots_gan.py -ip ${particle} -p ${pid} -e1 ${eta_min} -e2 ${eta_max} -v ${vox_dir} -o ${best_checkpoints_dir} -etot "False" -r ${samplesRange}

cd -

EOF

      echo $script
      chmod 775 $script
      source ${script}
      #condor_submit ${condor_file}
     
    done
  done
done
