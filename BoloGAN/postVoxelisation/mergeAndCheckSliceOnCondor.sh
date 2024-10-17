#!/bin/bash

### Run ./script.sh 

source ../common/config.sh
echo " Running in: $PWD"
MaxRuntime=$((2*60*60))

echo Create log error output and script dirs 
#binning_file_vox="binning_v2.3.xml"
binning_file_vox="binning_v2.4.1.xml"
sub_dir=submission_run3_${binning_file_vox}
log_dir=${sub_dir}/log/checkSlice
output_dir=${sub_dir}/output/checkSlice
error_dir=${sub_dir}/error/checkSlice
job_dir=${sub_dir}/jobs/checkSlice

validation_root_dir=${vox_dir}/rootFiles/validation/
mkdir -p ${validation_root_dir} 

rm -rf ${log_dir}
rm -rf ${output_dir}
rm -rf ${error_dir}
rm -rf ${job_dir} 

mkdir -p ${log_dir}
mkdir -p ${output_dir}
mkdir -p ${error_dir}
mkdir -p ${job_dir}

completedSlicesDir=completedSlices_run3_${binning_file_vox}
mkdir -p ${completedSlicesDir}
existingFilesDir=../rootToCsv/existingFiles_run3_${binning_file_vox} #existingFilesDir=../rootToCsv/existingFiles_run3_${binning_file_vox}_FixPions
mkdir -p ${existingFilesDir}
subDirVox=../rootToCsv/${sub_dir}
mkdir -p log
mkdir -p log_graph
rm tag_logs.txt

mkdir -p ${vox_dir}/dataBatches
mkdir -p ${vox_dir}/rootBatches


for pid in ${pids}
do
  SetVariablesGivenPid
  #etas="140"
  etas=20

  for eta in ${etas}
  do
    sliceName=${completedSlicesDir}/pid${pid}_eta_${eta}.txt
    echo "Checking ${sliceName}"
    if [[ -f ${sliceName} ]]; then
      echo "Skipping pid${pid}_eta_${eta}, all Done"
      continue
    fi

    tag_log=checkSlice_pid${pid}_eta_${eta}
    if [[ -f ${tag_log} ]]; then
      rm ${tag_log}
    fi
    job=${job_dir}/${tag_log}.sh
    echo "${tag_log}" >> tag_logs.txt 

cat > $job << EOF
#!/bin/bash
source  /cvmfs/sft.cern.ch/lcg/views/LCG_100cuda/x86_64-centos7-gcc8-opt/setup.sh
cd $PWD

source ../common/config.sh
pid=${pid}
SetVariablesGivenPid
eta=${eta}
eta_min=${eta}
eta_max=\$((${eta}+5))

if [[ ($pid == "22" || $pid == "11" ) && \$eta_min > 110 && \$eta_min < 155 ]]; then
  for energyIndex in ${!energies[@]}
  do
    maxBatches=\$((\${TotalBatches[\$energyIndex]}))
    if [[ \$maxBatches > 1 ]]; then
      TotalBatches[\$energyIndex]=\$((\${TotalBatches[\$energyIndex]} * 4))
    fi
  done
fi
echo \${TotalBatches[@]}

if grep -q "file probably overwritten" ${subDirVox}/output/ExtractToVox_pid${pid}*eta_${eta}*; 
then
  echo "Error in output files"
  grep -c "file probably overwritten" ${subDirVox}/output/ExtractToVox_pid${pid}*eta_${eta}*
else
  #remove existingFile flag, so that it is recreated correctly in case of reruns
  for energy in ${energies[@]}
  do
    fileName=pid${pid}_E\${energy}_eta_\${eta_min}_\${eta_max}
    fullFileName="${existingFilesDir}/\${fileName}.txt"
    if [[ -f \${fullFileName} ]]; then
      rm \${fullFileName}
    fi 
  done
  
  rm log_checkSlice_pid${pid}_eta_${eta}.txt
  touch log_checkSlice_pid${pid}_eta_${eta}.txt

  echo "Merge CSV files"
  source merge_csvFilesInSlice.sh
  echo "Running CSV check"
  python ${PWD}/checkCSVFilesInSlice.py -f ${vox_dir} -l ${subDirVox} -e ${eta} -p ${pid} -b \${TotalBatches[@]} -v voxelisation > log_checkSlice_pid${pid}_eta_${eta}.txt
  echo "  done vox"
  python ${PWD}/checkCSVFilesInSlice.py -f ${vox_dir} -l ${subDirVox} -e ${eta} -p ${pid} -b \${TotalBatches[@]} -v validation >> log_checkSlice_pid${pid}_eta_${eta}.txt
  echo "  done val"
  if [[ "\$(grep -c "All OK" log_checkSlice_pid${pid}_eta_${eta}.txt)" != "2" ]]
  then
    echo "Merge CSV files again"
    source merge_csvFilesInSlice.sh
    echo "Running CSV check"
    python ${PWD}/checkCSVFilesInSlice.py -f ${vox_dir} -l ${subDirVox} -e ${eta} -p ${pid} -b \${TotalBatches[@]} -v voxelisation > log_checkSlice_pid${pid}_eta_${eta}.txt
    python ${PWD}/checkCSVFilesInSlice.py -f ${vox_dir} -l ${subDirVox} -e ${eta} -p ${pid} -b \${TotalBatches[@]} -v validation >> log_checkSlice_pid${pid}_eta_${eta}.txt
  fi

  echo "Merge ROOT files"
  source merge_rootFilesInSlice.sh
  echo "Running ROOT file check"
  python ${PWD}/checkROOTFilesInSlice.py -f ${vox_dir} -e ${eta} -p ${pid} >> log_checkSlice_pid${pid}_eta_${eta}.txt
  echo "Check log file"
  cd $PWD
  if [[ "\$(grep -c "All OK" log_checkSlice_pid${pid}_eta_${eta}.txt)" == "3" ]]
  then
    echo "Log ok, creating rootfile with tree for voxelisation, pid: $pid, particle: $particle, eta_min: \${eta_min}, eta_max: \${eta_max}"
    for energy in ${energies[@]}
    do
      fileName=pid${pid}_E\${energy}_eta_\${eta_min}_\${eta_max}
      inputDir=${csv_dir}/pid${pid}/eta_\${eta_min}_\${eta_max}/
      #echo \$energy
      python3 voxalisation_trees.py -f \${fileName} -i \${inputDir} -o ${root_vox_dir} -v ${vox_dir} -p ${particle} -e \${energy} -eta ${eta}  
      #echo validation_trees.py -f \${fileName}_validation -i \${inputDir} -o ${validation_root_dir} -v ${vox_dir} -p ${particle} -e \${energy} -eta ${eta} --DoEC 
      python3 validation_trees.py -f \${fileName}_validation -i \${inputDir} -o ${validation_root_dir} -v ${vox_dir} -p ${particle} -e \${energy} -eta ${eta} --DoEC 
    done  
    python ${PWD}/checkROOTFilesInSlice.py -f ${vox_dir} -e ${eta} -p ${pid} --checkGraph > log_checkSlice_pid${pid}_eta_${eta}_graph.txt
    if [[ "\$(grep -c "All OK" log_checkSlice_pid${pid}_eta_${eta}_graph.txt)" == "1" ]]
    then
      mv log_checkSlice_pid${pid}_eta_${eta}.txt log/log_checkSlice_pid${pid}_eta_${eta}.txt
      mv log_checkSlice_pid${pid}_eta_${eta}_graph.txt log_graph/log_checkSlice_pid${pid}_eta_${eta}.txt
      touch ${completedSlicesDir}/pid${pid}_eta_${eta}.txt
      for energy in ${energies[@]}
      do
        fileName=pid${pid}_E\${energy}_eta_\${eta_min}_\${eta_max}
        touch ${existingFilesDir}/\${fileName}.txt
      done 
    else
      echo "Slice failed, setting correctly processed samples"
      for energy in ${energies[@]}
      do
        fileName=pid${pid}_E\${energy}_eta_\${eta_min}_\${eta_max}
        if ! grep -Fq "\$fileName" log_checkSlice_pid${pid}_eta_${eta}_graph.txt; then
          touch ${existingFilesDir}/\${fileName}.txt
          echo \$fileName added to processed 
        fi
      done 
    fi
  else
    # Setting to "correctly processed" any sample that is not in the log
    echo "Slice failed, setting correctly processed samples"
    for energy in ${energies[@]}
    do
      fileName=pid${pid}_E\${energy}_eta_\${eta_min}_\${eta_max}
      if ! grep -Fq "'\$fileName'" log_checkSlice_pid${pid}_eta_${eta}.txt; then
        touch ${existingFilesDir}/\${fileName}.txt
        echo \$fileName added to processed 
      fi
    done  
  fi
fi

EOF

    echo Running $job
    chmod 775 $job
    source ${job}
  done
done

condor_file=${job_dir}/condor_check.sub
output_file=${output_dir}/'$(arg)'.out
job=${job_dir}/'$(arg)'.sh
log_file=${log_dir}/'$(arg)'.log
error_file=${error_dir}/'$(arg)'.error
file_name='$(arg)'
condor_template=condorTEMPLATE.sub
queue_="queue arg from ${PWD}/tag_logs.txt"

cp $condor_template ${condor_file}
sed -i "s!@JOB@!${job}!g" ${condor_file}
sed -i "s!@LOG@!${log_file}!g" ${condor_file}
sed -i "s!@ERROR@!${error_file}!g" ${condor_file}
sed -i "s!@OUTPUT@!${output_file}!g" ${condor_file}
sed -i "s!@MAXRUNTIME@!${MaxRuntime}!g" ${condor_file}
sed -i "s!@TAG@!${binningName}_${file_name}!g" ${condor_file}
sed -i "s!@USER@!${USER}@cern.ch!g" ${condor_file}
sed -i "s!@QUEUE@!${queue_}!g" ${condor_file}
#condor_submit ${condor_file}

