here=$PWD
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
  
  if [[ ${moveBatches} == "true" ]]; then
    #move data batches from csvFiles to dataBatches
    mkdir -p ${vox_dir}/dataBatches/pid${pid}/eta_${eta_min}_${eta_max}/cells_validation
    mkdir -p ${vox_dir}/dataBatches/pid${pid}/eta_${eta_min}_${eta_max}/g4hits_validation
    mkdir -p ${vox_dir}/dataBatches/pid${pid}/eta_${eta_min}_${eta_max}/hits_validation
    mkdir -p ${vox_dir}/dataBatches/pid${pid}/eta_${eta_min}_${eta_max}/validation
    mkdir -p ${vox_dir}/dataBatches/pid${pid}/eta_${eta_min}_${eta_max}/voxalisation

    cd ${vox_dir}/
    mv $PWD/csvFiles/pid${pid}/eta_${eta_min}_${eta_max}/pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_*_cells_validation.csv  $PWD/dataBatches/pid${pid}/eta_${eta_min}_${eta_max}/cells_validation
    mv $PWD/csvFiles/pid${pid}/eta_${eta_min}_${eta_max}/pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_*_g4hits_validation.csv  $PWD/dataBatches/pid${pid}/eta_${eta_min}_${eta_max}/g4hits_validation
    mv $PWD/csvFiles/pid${pid}/eta_${eta_min}_${eta_max}/pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_*_hits_validation.csv $PWD/dataBatches/pid${pid}/eta_${eta_min}_${eta_max}/hits_validation
    mv $PWD/csvFiles/pid${pid}/eta_${eta_min}_${eta_max}/pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_[0-9]_validation.csv $PWD/dataBatches/pid${pid}/eta_${eta_min}_${eta_max}/validation
    mv $PWD/csvFiles/pid${pid}/eta_${eta_min}_${eta_max}/pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_[0-9][0-9]_validation.csv $PWD/dataBatches/pid${pid}/eta_${eta_min}_${eta_max}/validation
    mv $PWD/csvFiles/pid${pid}/eta_${eta_min}_${eta_max}/pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_*_voxalisation.csv $PWD/dataBatches/pid${pid}/eta_${eta_min}_${eta_max}/voxalisation
    echo "Batches copied"
  fi
  cd ${vox_dir}/csvFiles/pid${pid}/eta_${eta_min}_${eta_max}/

  rm pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_voxalisation.csv
  rm pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_validation.csv

  cat pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_*_cells_validation.csv > pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_cells_validation.csv
  cat pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_*_g4hits_validation.csv > pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_g4hits_validation.csv
  cat pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_*_hits_validation.csv > pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_hits_validation.csv  
  cat pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_*[[:digit:]]_validation.csv > pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_validation.csv
  cat pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_*_voxalisation.csv > pid${pid}_E${energy}_eta_${eta_min}_${eta_max}_voxalisation.csv
 
  echo "pid${pid}_E${energy}_eta_${eta_min}_${eta_max} done"       

done

cd ${here}