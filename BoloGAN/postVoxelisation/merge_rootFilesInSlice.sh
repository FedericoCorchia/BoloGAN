here=$PWD
cd ${vox_dir}/rootFiles/pid${pid}/eta_${eta_min}_${eta_max}
moveBatches="false"

for energyIndex in ${!energies[@]}
do 
  energy=${energies[$energyIndex]} 
  
  if [[ ${TotalBatches[$energyIndex]} == 1 ]]; then
    echo "Nothing to do for pid${pid}_E${energy}"      
    continue
  fi   

  eta_min=${eta}
  eta_max=$((${eta}+5))
  
  rootNames="pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_*.root"
  targetFileName="pid${pid}_E${energy}_eta_${eta_min}_${eta_max}.root"
  
  #if [[ -f "$targetFileName" && ! -f "$rootNames" ]]; then
  #   and split files do not exists (moved)"
  
  if compgen -G "$rootNames" > /dev/null; then
    hadd -f -k ${targetFileName} ${rootNames}
    echo "pid${pid}_E${energy}_eta_${eta_min}_${eta_max} done"

    if [[ ${moveBatches} == "true" ]]; then
      #move data batches from rootFiles to dataBatches
      mv ${rootNames} ${vox_dir}/rootBatches/eta_${eta_min}_${eta_max}
    fi

  elif [[ -f "$targetFileName" ]]; then
    echo "Merged file $targetFileName exists"
  else
    echo "Missing files: $rootNames"
  fi

done

cd ${here}