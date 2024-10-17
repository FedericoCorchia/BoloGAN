#!/bin/bash

### Run ./script.sh -b binning_file_vox.xml -p 22/11/211 --etaSelection all

source ../common/config.sh

dir=$PWD

echo " Running in: ${dir}"

MaxRuntime=$((120*60*60))
saveRootFiles="true"
eventsToVoxel=10000
useHitEnergy="true"
useFiles="false"

energyCorrectionScheme="PerEventFromG4HitsEnergy"
if [[ "${vox_dir}" == *"PerEventFromCellEnergy"* ]]; then
  energyCorrectionScheme="PerEventFromCellEnergy"
elif
 [[ "${vox_dir}" == *"PerEventFromG4HitsEnergy"* ]]; then
  energyCorrectionScheme="PerEventFromG4HitsEnergy"
elif
 [[ "${vox_dir}" == *"PerCellFromG4HitsEnergy"* ]]; then
  energyCorrectionScheme="PerCellFromG4HitsEnergy"
elif
 [[ "${vox_dir}" == *"PerCellFromCellEnergy"* ]]; then
  energyCorrectionScheme="PerCellFromCellEnergy"
fi

echo "Energy correction scheme =" ${energyCorrectionScheme}


#inputFolder="/eos/atlas/atlascerngroupdisk/proj-simul/InputSamplesSummer18Complete/"
#inputFolder="/eos/atlas/atlascerngroupdisk/proj-simul/InputSamplesReprocessing2019/"
inputFolder="/eos/atlas/atlascerngroupdisk/proj-simul/AF3_Run3/InputSampleProduction2022/"
#inputFolder="/eos/atlas/atlascerngroupdisk/proj-simul/AF3_Run3/InputSampleProduction2022_FixPions/"

if [ $# -lt 6 ]; then
  echo Need one argument, for example;
  echo ./extractAlltoVox_condor.sh -b binning.xml -p 22/11/211 --etaSelection all
  return;
fi

while [ $# -gt 1 ] ; do
case $1 in
  -b) 
    binning_file_vox=$2
    shift 2
    ;;
  -p|--pid) 
    pid=$2
    shift 2 
    ;;
  -e|--etaSelection) 
    etaSelection=$2
    shift 2
    ;;
  *)
    shift 1 
    ;;
esac
done

echo "Producing voxelisation in folder ${vox_dir} with ${binning_file_vox} for ${pid} and eta selection ${etaSelection}"
mkdir -p ${vox_dir}

cp ${binning_file_vox} ${vox_dir}/${binningFile}

echo Create log error output and script dirs 
sub_dir=submission_run3_${binning_file_vox}
log_dir=${sub_dir}/log
output_dir=${sub_dir}/output
error_dir=${sub_dir}/error
job_dir=${sub_dir}/jobs

mkdir -p ${log_dir}
mkdir -p ${output_dir}
mkdir -p ${error_dir}
mkdir -p ${job_dir}


SetVariablesGivenPid

tag_logs=tag_logs_${particle}.txt
rm -v ${tag_logs}
touch ${tag_logs}


### Here to set special run with only one energy or eta
### Test Run3 samples for UltraLow
#TotalBatches=(1 1)
#energies=(256 512 1024 2048 4096 8192 16384)
#energies=(32768 65536)
#etas="20"

echo ${TotalBatches[@]}
for energyIndex in ${!energies[@]}
do 
  energy=${energies[$energyIndex]} 
  etas=20 #etas=$(eval echo "{0..200..5}")

  for eta in ${etas}
  do
    eta_min=${eta}
    eta_max=$((${eta}+5))
    
    fileNameToChekIfSampleAlreadyProcessed=pid${pid}_E${energy}_eta_${eta_min}_${eta_max}
    if [[ -f "existingFiles_run3_${binning_file_vox}_FixPions/${fileNameToChekIfSampleAlreadyProcessed}.txt" ]]; then
      echo "$fileNameToChekIfSampleAlreadyProcessed exists, skipping"
      continue
    fi

    if [[ ${useFiles} == "true" ]]; then
      ID=${dbID_dict[${pid}${energy}${eta_min}]}
      numFiles=$( ls ${inputFolder} | grep ${ID} | wc -l)
      batches=$((${numFiles} -1 ))
    fi
    
    maxBatches=$((${TotalBatches[$energyIndex]}))
    if (( ($pid == "22" || $pid == "11" ) && $maxBatches > 1 && $eta_min > 110 && $eta_min < 155 )); then
      maxBatches=$((${TotalBatches[$energyIndex]} * 4))
    fi
    maxBatchesRange=$((${maxBatches}-1))
    for batch in $(eval echo {0..$maxBatchesRange})
    do
      echo "Do voxalisation csv files for pid: $pid, energy: ${energy}, eta_min: ${eta_min}, eta_max: ${eta_max}, batch_id: ${batch}, number of batches: ${maxBatches}"

      tag_log=ExtractToVox_pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_${batch}
      job=${job_dir}/${tag_log}.sh
      echo "${tag_log}" >> ${tag_logs}

      if [[ ${useFiles} == "true" ]]; then
        inputData=${inputFolder}calohit.G4.${ID}.${batch}.root
        echo "Input file is: ${inputData}" 
      elif [[ ${useFiles} == "false" ]]; then     
        inputData=${inputFolder}
        #echo "Input folder is: ${inputData}" 
      fi 

      script="${PWD}/runVoxelisation ${pid} ${energy} ${eta} ${eventsToVoxel} ${useFiles} ${inputData} ${binningFile} ${vox_dir} ${energyCorrectionScheme} ${saveRootFiles} ${useHitEnergy} ${batch} ${maxBatches}" 


cat > $job << EOF
#!/bin/bash
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source /cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/user/atlasLocalSetup.sh 

source ${PWD}/setup.sh

cd ${PWD}

echo "$script"
${script}

EOF

      #echo Running $job
      chmod 775 $job
      #source ${job}
    done
  done
done

condor_file=${job_dir}/condor.sub
output_file=${output_dir}/'$(arg)'.out
job=${job_dir}/'$(arg)'.sh
log_file=${log_dir}/'$(arg)'.log
error_file=${error_dir}/'$(arg)'.error
file_name='$(arg)'
condor_template=condorTEMPLATE.sub
queue_="queue arg from ${dir}/${tag_logs}"

cp $condor_template ${condor_file}
sed -i "s!@JOB@!${job}!g" ${condor_file}
sed -i "s!@LOG@!${log_file}!g" ${condor_file}
sed -i "s!@ERROR@!${error_file}!g" ${condor_file}
sed -i "s!@OUTPUT@!${output_file}!g" ${condor_file}
sed -i "s!@MAXRUNTIME@!${MaxRuntime}!g" ${condor_file}
sed -i "s!@TAG@!${binningName}_${file_name}!g" ${condor_file}
sed -i "s!@USER@!${USER}@cern.ch!g" ${condor_file}
sed -i "s!@MEM@!${memory}!g" ${condor_file}
sed -i "s!@QUEUE@!${queue_}!g" ${condor_file}
condor_submit ${condor_file}

