#!/bin/bash
source ../common/config.sh
pids="211"

mkdir -p ${voxalisation_validation_dir}/pdf
mkdir -p ${voxalisation_validation_dir}/png
mkdir -p ${voxalisation_validation_dir}/eps
output_dir_root=${voxalisation_validation_dir}/rootFiles
mkdir -p ${output_dir_root}

for pid in ${pids}
do  
  SetVariablesGivenPid ${pid}
  etas=20

  for eta in ${etas}
  do
    eta_min=${eta}
    eta_max=$((${eta}+5))
    for energy in ${energies[@]}
    do
              
    echo "Do voxalisation comparison plots with tree for pid: $pid, particle: $particle, energy: ${energy}, eta_min: ${eta_min}, eta_max: ${eta_max}"
      name_output=pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_comparison_voxalisation
        
    python3 ${PWD}/comparison_plots.py -of ${output_dir_root}/${name_output}.root --DoVOX -ip ${particle} -e1 ${eta_min} -e2 ${eta_max} -e ${energy} -p ${pid} -v ${vox_dir} -odv ${voxalisation_validation_dir} -n ${name_output}
    done
  done
done
