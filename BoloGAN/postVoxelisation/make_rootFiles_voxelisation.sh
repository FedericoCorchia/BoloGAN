#!/bin/bash
source ../common/config.sh

pids="211"
#useSeed="true"



echo "Runnnign in folder ${vox_dir}"

for pid in ${pids}
do  
  SetVariablesGivenPid 
  etas="20"
  #energies=(262144)  

  for eta in ${etas} #$(eval echo "{${minEta}..${maxEta}..5}")
  do
    eta_min=${eta}
    eta_max=$((${eta}+5))
    for energy in ${energies[@]}
    do
      #echo "create rootfile with tree for voxelisation, pid: $pid, particle: $particle, energy: ${energy}, eta_min: ${eta_min}, eta_max: ${eta_max}"
      suffix=voxalisation
      dir=${vox_dir}/csvFiles/
      fileName=pid${pid}_E${energy}_eta_${eta_min}_${eta_max}
      python3 voxalisation_trees.py -f ${fileName} -i ${csv_dir} -o ${root_vox_dir} -v ${vox_dir} -p ${particle} -e ${energy} -eta ${eta} -n 100000  #&> rootVox_${particle}_${energy}_${eta}.log &
    done
  done
done

