#!/bin/bash

source ../common/config.sh

echo " Running in: $PWD"
#MaxRuntime=$((18*60*60))
memory=7000

user=${USER}
tryResume="True"

minEpoch=1000
maxEpoch=999000

minEta=20
maxEta=20
pid="211" #11 211" 
suffix=${GAN_name} #"normE_LogE" "normXmaxMid_LogE" "normXmaxMid_MaxE" "normE_MaxE" 
#input_dir="/afs/cern.ch/user/m/mfauccig/eos/VoxalisationOutputs/test_extreme_depthVariables_2018_mergeAlpha_phiMod/"

##Run on EOS
output_dir_gan="${input_dir}/${suffix}/"
##Run on work
#output_dir_gan="$PWD/${binningName}/${suffix}/"


echo Create log error and output dirs 
log_dir=${output_dir_gan}/log
output_dir=${output_dir_gan}/output
error_dir=${output_dir_gan}/error
script_dir=${output_dir_gan}/scripts

mkdir -p ${log_dir}
mkdir -p ${output_dir}
mkdir -p ${error_dir}
mkdir -p ${script_dir}

echo create checkpoint dir
checkpoint_dir=${output_dir_gan}/checkpoints
mkdir -p ${checkpoint_dir}

if [[ ${pid} == "22" ]];then
  particle="photons"
elif [[ ${pid} == "11" ]];then
  particle="electrons"
else
  particle="pions"
fi

for eta in $(eval echo "{${minEta}..${maxEta}..5}") 
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
      for epoch in $(eval echo "{${minEpoch}..${maxEpoch}..1000}")
      do
        FILE=${checkpoint_dir_full}/model_${epoch}.ckpt.meta
        if test -f "$FILE"; then
          echo -ne "${particle}, eta_min: ${eta_min}, eta_max: ${eta_max} was trained up to ${epoch}\r"
          startingEpoch=${epoch}
        else
          echo "${particle}, eta_min: ${eta_min}, eta_max: ${eta_max} was trained up to $((${epoch}-1000))"
          break
        fi
      done
    fi
  else
    echo "Restarting training from zero"
  fi
  

  echo Running gan for particle: ${particle}, eta_min: ${eta_min}, eta_max: ${eta_max} starting from epoch ${startingEpoch}
  tag_log=tf2_gan_${particle}_eta_${eta_min}_${eta_max}_${suffix}
  condor_file=${script_dir}/condor_${tag_log}.sub
  job=${script_dir}/${tag_log}.sh

  log_file=${tag_log}.log
  error_file=${tag_log}.error
  output_file=${tag_log}.out
  condor_template=condorTEMPLATE.sub

  cp $condor_template ${condor_file}
  cp *.py ${script_dir}

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
#source ~/venvtf2.41gpu/bin/activate
#source ~/venvtf2.3gpu/bin/activate
source ~/venvtf2gpu/bin/activate
root --version

cd ${script_dir}
echo $path
time python3 train_conditional_wgangp.py -odg ${checkpoint_dir} -e ${startingEpoch} -i ${input_dir} -ip ${particle} -emin ${eta_min} -emax ${eta_max}
EOF

  echo "Submitting config: ${condor_file}"
  chmod 775 $job
  condor_submit ${condor_file}
  #${job}

done
