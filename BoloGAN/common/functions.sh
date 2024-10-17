#!/bin/bash

function SetVoxelisationDir(){
  vox_dir="${WORKINGDIR}/caloChallenge/"
  

  csv_dir=${vox_dir}/csvFiles/ 
  echo $csv_dir 
  root_vox_dir=${vox_dir}/rootFiles/
  mkdir -p ${root_vox_dir}

  voxalisation_validation_dir=${vox_dir}/validation_plots
  mkdir -p $voxalisation_validation_dir
}

function SetFolderFromGANName(){
  echo $GAN_name
  gan_dir="${vox_dir}/${GAN_name}/${samplesRange}"
  input_dir_checkpoint="${gan_dir}/checkpoints/"

  best_checkpoint_criteria=E # E EandCOG
  best_checkpoint_tag="best_checkpoints_${best_checkpoint_criteria}" #_absPhi"
  best_checkpoints_dir="${gan_dir}/${best_checkpoint_tag}"

  ### Folder with ROOT file for GAN best epochs
  #output_gan=${best_checkpoints_dir}/
  ###old
  output_gan=${gan_dir}/

  plot_dir_gan="plots_Energy_conditional_GAN${GAN_name}"

  gan_root_files=${best_checkpoints_dir}/GAN_ROOT_files/
  output_dir_plots=${best_checkpoints_dir}/plots/
  mkdir -p ${output_dir_plots}
}

function InitBestCheckpointFolders(){
  if [[ ${resetAll} == "True" ]]
  then
    rm -rf  ${best_checkpoints_dir}
    mkdir ${best_checkpoints_dir}
  fi

  echo Create log error output and script dirs 
  sub_dir=$PWD/bestCheckpointSelection_${GAN_name}
  log_dir=${sub_dir}/log
  output_dir=${sub_dir}/output
  error_dir=${sub_dir}/error
  script_dir=${sub_dir}/scripts
  
  rm -rf ${log_dir}
  rm -rf ${output_dir}
  rm -rf ${error_dir}
  mkdir -p ${log_dir}
  mkdir -p ${output_dir}
  mkdir -p ${error_dir}
  mkdir -p ${script_dir}

  mkdir -p ${best_checkpoints_dir}
  mkdir -p ${best_checkpoints_dir}/tmp
  mkdir -p ${best_checkpoints_dir}/chi2_vs_epoch
  mkdir -p ${best_checkpoints_dir}/png
  mkdir -p ${best_checkpoints_dir}/eps
  mkdir -p ${best_checkpoints_dir}/pdf
  mkdir -p ${best_checkpoints_dir}/chi2

  mkdir -p ${best_checkpoints_dir}/png_preliminary
  mkdir -p ${best_checkpoints_dir}/eps_preliminary
  mkdir -p ${best_checkpoints_dir}/pdf_preliminary

}
 
function SetVariablesGivenPid(){
  if [[ ${pid} == "22" ]];then
    particle=photons
    TotalBatches=(${TotalBatchesEgamma[@]})
    energies=($energiesEgamma)
    samplesRangeList=${rangeEgamma}
    idx=0
  elif [[ ${pid} == "11" ]];then
    particle=electrons
    TotalBatches=(${TotalBatchesEgamma[@]})
    energies=($energiesEgamma)
    samplesRangeList=${rangeEgamma}
    idx=1
  elif [[ ${pid} == "211" ]];then
    particle=pions
    TotalBatches=(${TotalBatchesPion[@]})
    energies=($energiesPion)
    samplesRangeList="All"
    idx=2
  elif [[ ${pid} == "2212" ]];then
    particle=protons
    TotalBatches=(${TotalBatchesOtherHadrons[@]})
    energies=($energiesOtherHadrons)
    samplesRangeList="High10"
    idx=2
  fi
 
  max_epoch="999000"  
  if [[ ${etaSelection} == "seed" ]]; then
    echo Using the seed etas
    etas=${etasSeeds[$idx]}
    max_epoch="999000"  
  fi
  if [[ ${etaSelection} == "noSeed" ]]; then
    echo Using the non-seed etas
    ary=(${etasAll})
    # note that number 1 is stored in _index_ 0
    for eta in ${etasSeeds[$idx]}; do
        unset "ary[$((eta/5))]"
    done
    etas=$(eval echo ${ary[@]// / })
    #echo $etas
  fi
}

function GetRegionNumberGivenEta(){
  etaLimits=${etasSeeds[$idx]}
  region=0
  for e in $etaLimits
  do
    region=$(($region+1)) 
    if (( ${eta} > ${e})); then
      return
    fi
  done
}
