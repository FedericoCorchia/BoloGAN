#!/bin/bash
source ../common/config.sh
etaSelection=seed
step="1000"

currentDir=$PWD

enableZip="False"
saveAllPlots="False"
resetChi2="True" #REVERT TO False ONCE DONE
resetAll="True" #REVERT TO False ONCE DONE
if [[ ${resetAll} == "True" ]]
then
  best_checkpoints_dir="/eos/atlas/atlascerngroupdisk/proj-simul/AF3_Run3/VoxalisationOutputs/corchia/caloChallengeHighStats/Baseline_pions_lwtnn/All/best_checkpoints_E" #REMOVE WHOLE LINE ONCE DONE
  rm -rf  ${best_checkpoints_dir}
  mkdir ${best_checkpoints_dir}
fi

#pids="22 11"

for pid in ${pids}
do
  SetVariablesGivenPid
  #echo $samplesRangeList
  #samplesRangeList="High12" #"UltraLow12" #"High12"
  etas="20" #etas="20 100 120 140 160"
  min_epoch="500000" #during regular runs: 100000  
  max_epoch="1000000"  
  
  for samplesRange in ${samplesRangeList} 
  do
    GAN_name=Baseline_${particle}_lwtnn
    SetFolderFromGANName
    InitBestCheckpointFolders
    
    echo Running in ${gan_dir}
  
    for eta in  ${etas}
    do
      eta_min=${eta}
      eta_max=$((${eta}+5))

      code_dir=${gan_dir}/code
      tag_log=${best_checkpoint_tag}_${particle}_${eta_min}_${eta_max}_${GAN_name}_${samplesRange}
      output_file=${output_dir}/${tag_log}.out
      script=${script_dir}/${tag_log}.sh
      log_file=${log_dir}/${tag_log}.log
      error_file=${error_dir}/${tag_log}.error
      condor_template=condorTEMPLATE.sub
      condor_file=${script_dir}/condor_${tag_log}.sub

      cp selectBestEpoch_Energy.py ${code_dir}
      cp plots_chi2_vs_epoch.py ${code_dir}
      cp -r utils ${code_dir}/

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
  min_epoch=\${lastEpoch}
fi

tgzFile=checkpoint_${eta_min}_${eta_max}.tgz
#Check if slice was already compressed, unpack to rerun
if [[ -f "\$tgzFile" && "$enableZip" == "true" ]]; then
  echo "Unzipping checkpoints to re-evaluate best checkpoint"
  cd ${input_dir_checkpoint}/${particle}
  tar -xvzf \$tgzFile
  cd -
else
  echo "First run or zip disabled, nothing to do"
fi

echo activate Tensorflow 2
source  /cvmfs/sft.cern.ch/lcg/views/LCG_101cuda/x86_64-centos7-gcc8-opt/setup.sh 

cd ${code_dir}

if [[ ${best_checkpoint_criteria} == "EandCOG" ]];then
   time python3 selectBestEpoch_EandCOGs.py -b "${input_dir}/../${task}/${binningFile}"  -emin $min_epoch -emax $max_epoch -step $step -idg ${input_dir_checkpoint} -v ${input_dir} -p ${pid} -e1 ${eta_min} -e2 ${eta_max} -s ${saveAllPlots} -o ${best_checkpoints_dir} 
else
   #echo skip
   echo "Run selection"
   time python3 selectBestEpoch_Energy.py -emin $min_epoch -emax $max_epoch -step $step -idg ${input_dir_checkpoint} -v ${vox_dir} -ip ${particle} -e1 ${eta_min} -e2 ${eta_max} -s ${saveAllPlots} -o ${best_checkpoints_dir} -r ${samplesRange} --seed
fi

mapfile -t myArray < ${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt
best_checkpoint=\${myArray[0]%% *}
echo BEST CHECKPOINT \${best_checkpoint}

echo "Make chi2 vs iteration plot"
time python3 plots_chi2_vs_epoch.py -e ${eta_min} -p ${pid} -d ${best_checkpoints_dir}/chi2 -o ${best_checkpoints_dir}/chi2_vs_epoch

if [[ "$enableZip" == "true" ]]; then 
  if [[ -f "${input_dir_checkpoint}/${particle}/\$tgzFile" ]]; then 
    cd ${input_dir_checkpoint}/${particle}
    echo "Zipped checkpoint exists already, delete unzipped checkpoints"
    rm -rf checkpoints_eta_${eta_min}_${eta_max}
  else
    echo "Zip checkpoint folder"
    cd ${input_dir_checkpoint}/${particle}
    tar -zcvf \${tgzFile} --remove-files checkpoints_eta_${eta_min}_${eta_max}
    cd -
  fi
fi

EOF

      echo $script
      chmod 775 $script
      #source ${script}
      condor_submit ${condor_file}
      cd $currentDir
    done
  done
done
