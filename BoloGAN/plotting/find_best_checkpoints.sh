#!/bin/bash
source ../common/config.sh

pids="211"
etaSelection=seed

saveAllPlots="False"
resetChi2="True"
resetAll="False"

min_epoch="400000"  
step="1000"

echo " Running in: $PWD"

for pid in ${pids}
do
  SetVariablesGivenPid
  #samplesRangeList="UltraLow12" #"High12"

  for samplesRange in ${samplesRangeList} 
  do
    GAN_name=Baseline_${particle} #_BN_lr2em4 #_BN_dgratio5 #_BatchNorm #_BN_best155
    SetFolderFromGANName
    InitBestCheckpointFolders
    #etas="200"
  
    for eta in ${etas} #$(eval echo "{${minEta}..${maxEta}..5}")
    do
      eta_min=${eta}
      eta_max=$((${eta}+5))

      tag_log=${best_checkpoint_tag}_${particle}_${eta_min}_${eta_max}_${GAN_name}_${samplesRange}
      output_file=${output_dir}/${tag_log}.out
      script=${script_dir}/${tag_log}.sh
      log_file=${log_dir}/${tag_log}.log
      error_file=${error_dir}/${tag_log}.error
      condor_template=condorTEMPLATE.sub
      condor_file=${script_dir}/condor_${tag_log}.sub
      
      cp selectBestEpoch_Energy.py ${script_dir}
      cp plots_chi2_vs_epoch.py ${script_dir}
      cp -r utils ${script_dir}
      cp $condor_template ${condor_file}
      sed -i "s!@SCRIPT@!${script}!g" ${condor_file}
      sed -i "s!@LOG@!${log_file}!g" ${condor_file}
      sed -i "s!@ERROR@!${error_file}!g" ${condor_file}
      sed -i "s!@OUTPUT@!${output_file}!g" ${condor_file}
      sed -i "s!@MAXRUNTIME@!${MaxRuntime}!g" ${condor_file}
      sed -i "s!@MEM@!${memory}!g" ${condor_file}
      sed -i "s!@TAG@!${binningName}_${tag_log}!g" ${condor_file}
      sed -i "s!@MAIL@!${USER}@cern.ch!g" ${condor_file}    

      #Delete files inside script so that if condor jobs is restared the chi2 is deleted again
      chi2File=${best_checkpoints_dir}/chi2/chi2_${pid}_${eta_min}_${eta_max}.txt
      bestchi2File=${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt

      if [[ ${resetChi2} == "True" ]]
      then
        rm ${chi2File}
        rm ${bestchi2File}
        touch ${chi2File}
        chmod 774 ${chi2File}
        
      fi

cat > $script << EOF
#!/bin/bash

lastEpoch=\$(eval tail -n 1 ${chi2File} | awk '{print \$1;}')
if [ ! -z \${lastEpoch} ] #If not empy, change starting epoch
then
  max_epoch=\${lastEpoch}
fi

echo activate Tensorflow 2
source  /cvmfs/sft.cern.ch/lcg/views/LCG_101cuda/x86_64-centos7-gcc8-opt/setup.sh 

cd ${script_dir}

if [[ ${best_checkpoint_criteria} == "EandCOG" ]];then

   time python3 selectBestEpoch_EandCOGs.py -b "${input_dir}/../${task}/${binningFile}"  -emin $min_epoch -emax $max_epoch -step $step -idg ${input_dir_checkpoint} -v ${input_dir} -p ${pid} -e1 ${eta_min} -e2 ${eta_max} -s ${saveAllPlots} -o ${best_checkpoints_dir} 
else
   time python3 selectBestEpoch_Energy.py -emin $min_epoch -emax $max_epoch -step $step -idg ${input_dir_checkpoint} -v ${vox_dir} -p ${pid} -e1 ${eta_min} -e2 ${eta_max} -s ${saveAllPlots} -o ${best_checkpoints_dir} --seed -r ${samplesRange}
fi
  
mapfile -t myArray < ${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt
best_checkpoint=\${myArray[0]%% *}
echo BEST CHECKPOINT \${best_checkpoint}

time python3 plots_chi2_vs_epoch.py -e ${eta_min} -p ${pid} -d ${best_checkpoints_dir}/chi2 -o ${best_checkpoints_dir}/chi2_vs_epoch

EOF

      echo $script
      chmod 775 $script
      #source ${script}
      condor_submit ${condor_file}
    done
  done
done
