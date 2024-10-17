#!/bin/bash
source ../common/config.sh

echo " Running in: $PWD"

mkdir -p ${output_dir_plots}
mkdir -p ${output_dir_plots}/png/
mkdir -p ${output_dir_plots}/pdf/
mkdir -p ${output_dir_plots}/eps/

for pid in ${pids}
do
  SetVariablesGivenPid
  #samplesRangeList="UltraLow12" #"High12"

  for samplesRange in ${samplesRangeList} 
  do
    GAN_name=Baseline_${particle} 
    SetFolderFromGANName
    InitBestCheckpointFolders
  
    for eta in ${etas}
    do
      eta_min=${eta}
      eta_max=$((${eta}+5))

      for energyIndex in ${!energies[@]}
      do 
        energy=${energies[$energyIndex]} 
        ganPlotFile=${gan_root_files}/${particle}/pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_GAN.root
        time  python3 ${PWD}/comparison_plots.py  --DoGAN -v ${vox_dir} -gp ${ganPlotFile} -ip ${particle} -e1 ${eta_min} -e2 ${eta_max} -e ${energy} -p ${pid} -d ${output_dir_plots} -of ${output_dir_plots}/pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_comparison_best_checkpoint.root -n pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_comparison_best_checkpoint
      done

    done
  done
done
