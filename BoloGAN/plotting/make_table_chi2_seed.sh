#!/bin/bash

source ../common/config.sh
etaSelection=seed

echo " Running in: $PWD"
pids="11 22"

for pid in ${pids}
do
  SetVariablesGivenPid
  samplesRangeList="High12" #"UltraLow12" #"High12"

  for samplesRange in ${samplesRangeList} 
  do
    GAN_name=Baseline_${particle}
    SetFolderFromGANName

    tableFile=${best_checkpoints_dir}/chiTable_${pid}_${samplesRange}_${GAN_name}.tex
    rm ${tableFile}
    echo "\begin{table}[]" >>${tableFile}
    echo "\footnotesize" >>${tableFile}
    echo "\centering" >>${tableFile}
    echo "\begin{tabular}{|l|l|l|}" >>${tableFile}
    echo "\hline" >>${tableFile}
    echo "$\eta$ x100 range & Best iteration & $\chi^2$/ndf \\\\" >>${tableFile}
    echo "\hline" >>${tableFile}

    for eta in ${etas}
    do
      eta_min=${eta}
      eta_max=$((${eta}+5))

      chi2File=${best_checkpoints_dir}/chi2/chi2_${pid}_${eta_min}_${eta_max}.txt
      bestchi2File=${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt

      mapfile -t myArray < ${best_checkpoints_dir}/chi2/epoch_best_chi2_${pid}_${eta_min}_${eta_max}.txt
      best_checkpoint=${myArray[0]%% *}
      chi2=$(grep ${best_checkpoint} ${chi2File})
      echo "${eta_min}-${eta_max} & ${chi2%% *} & ${chi2##* }  \\\\">> ${tableFile}
    done
    echo "\hline" >>${tableFile}
    echo "\end{tabular}" >>${tableFile}
    echo "\caption{Summary of best epoch selection for ${particle} in range ${samplesRange} for GAN \$ ${GAN_name} \$.}" >>${tableFile}
    echo "\label{tab:BestEpochSummary_${particle}}" >>${tableFile}
    echo "\end{table}" >>${tableFile}
  done
done