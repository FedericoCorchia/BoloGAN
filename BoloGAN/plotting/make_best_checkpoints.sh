#!/bin/bash
source ../utils/config.sh
echo $GAN_name

resetChi2="True"
resetAll="False"
if [ ${resetAll} == "True" ]
then
  rm -rf  ${best_checkpoints_dir}
  mkdir ${best_checkpoints_dir}
fi

echo Create log error output and script dirs 
log_dir=${best_checkpoints_dir}/log
output_dir=${best_checkpoints_dir}/output
error_dir=${best_checkpoints_dir}/error
script_dir=${best_checkpoints_dir}/scripts
rm -rf ${log_dir}
rm -rf ${output_dir}
rm -rf ${error_dir}
mkdir -p ${log_dir}
mkdir -p ${output_dir}
mkdir -p ${error_dir}
mkdir -p ${script_dir}

mkdir -p ${output_gan}
mkdir -p ${output_gan}/tmp
mkdir -p ${best_checkpoints_dir}
mkdir -p ${best_checkpoints_dir}/chi2_vs_epoch
mkdir -p ${best_checkpoints_dir}/png
mkdir -p ${best_checkpoints_dir}/pdf
mkdir -p ${best_checkpoints_dir}/chi2

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
  
  for eta in $(eval echo "{${minEta}..${maxEta}..5}")
  do
    eta_min=${eta}
    eta_max=$((${eta}+5))

    tag_log=${best_checkpoint_tag}_${particle}_${eta_min}_${eta_max}
    output_file=${output_dir}/${tag_log}.out
    script=${script_dir}/${tag_log}.sh
    log_file=${log_dir}/${tag_log}.log
    error_file=${error_dir}/${tag_log}.error
    condor_template=condorTEMPLATE.sub
    condor_file=${script_dir}/condor_${tag_log}.sub

    cp $condor_template ${condor_file}
    sed -i "s!@SCRIPT@!${script}!g" ${condor_file}
    sed -i "s!@LOG@!${log_file}!g" ${condor_file}
    sed -i "s!@ERROR@!${error_file}!g" ${condor_file}
    sed -i "s!@OUTPUT@!${output_file}!g" ${condor_file}
    sed -i "s!@MAXRUNTIME@!${MaxRuntime}!g" ${condor_file}
    sed -i "s!@MEM@!${memory}!g" ${condor_file}
    sed -i "s!@TAG@!${tag_log}!g" ${condor_file}
    sed -i "s!@MAIL@!${USER}@cern.ch!g" ${condor_file}    

    #Delete files inside script so that if condor jobs is restared the chi2 is deleted again
    chi2File=${best_checkpoints_dir}/chi2/chi2_${pid}_${eta_min}_${eta_max}.txt
    bestchi2File=${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt

    if [ ${resetChi2} == "True" ]
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
source ${tf2venv}/bin/activate

if [[ ${best_checkpoint_criteria} == "EandCOG" ]];then

   time python3 ${PWD}/selectBestEpoch_EandCOGs.py -b "${input_dir}/../${task}/${binningFile}"  -emin $min_epoch -emax $max_epoch -step $step  -norm ${norm} -l ${label} -idg ${input_dir_checkpoint} -v ${input_dir} -p ${pid} -e1 ${eta_min} -e2 ${eta_max} -s "False" -o ${best_checkpoints_dir} -g ${output_gan}
else
   time python3 ${PWD}/selectBestEpoch_Energy.py -emin $min_epoch -emax $max_epoch -step $step  -norm ${norm} -l ${label} -idg ${input_dir_checkpoint} -v ${input_dir} -p ${pid} -e1 ${eta_min} -e2 ${eta_max} -s "False" -o ${best_checkpoints_dir}
fi
  
mapfile -t myArray < ${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt
best_checkpoint=\${myArray[0]%% *}
echo BEST CHECKPOINT \${best_checkpoint}

EOF

    echo $script
    chmod 775 $script
    source ${script}
    #condor_submit ${condor_file}
  done
done
