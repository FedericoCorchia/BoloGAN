#!/bin/bash
source ../common/config.sh
pids=22

for pid in ${pids}
do  
  SetVariablesGivenPid

  output_dir_root=${vox_dir}/rootFiles/validation/${particle}
  mkdir -p ${output_dir_root} 
  
  etas=20

  for eta in ${etas}
  do
    eta_min=${eta}
    eta_max=$((${eta}+5))
    for energy in 65536 #${energies[@]}
    do      
      echo "create validation rootfile from validation csv for pid: $pid, particle: $particle, energy: ${energy}, eta_min: ${eta_min}, eta_max: ${eta_max}"
      suffix=validation 
      fileName=pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_${suffix}
      python3 validation_trees.py -f ${fileName} -i ${csv_dir} -o ${output_dir_root} -v ${vox_dir} -p ${particle} -e ${energy} -eta ${eta} --DoEC

      suffix=cells_validation 
      fileName=pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_${suffix}
      python3 validation_trees.py -f ${fileName} -i ${csv_dir} -o ${output_dir_root} -v ${vox_dir} -p ${particle} -e ${energy} -eta ${eta} --DoEC

      suffix=g4hits_validation
      fileName=pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_${suffix}
      python3 validation_trees.py -f ${fileName} -i ${csv_dir} -o ${output_dir_root} -v ${vox_dir} -p ${particle} -e ${energy} -eta ${eta} 

      suffix=hits_validation
      fileName=pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_${suffix}
      python3 validation_trees.py -f ${fileName} -i ${csv_dir} -o ${output_dir_root} -v ${vox_dir} -p ${particle} -e ${energy} -eta ${eta} 
    done
  done
done

