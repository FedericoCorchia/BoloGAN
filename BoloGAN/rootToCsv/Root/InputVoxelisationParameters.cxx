#include "InputVoxelisationParameters.h"

#include <iostream>   
#include <stdexcept>

InputVoxelisationParameters::InputVoxelisationParameters(){
  
}

void InputVoxelisationParameters::Print(){
  std::cout<<"Running with these parameters"<<std::endl;
  std::cout<< std::boolalpha;
  std::cout<<"pid                    = "<<m_pid<<std::endl;
  std::cout<<"pid in XML             = "<<m_pid_xml<<std::endl;
  std::cout<<"energy                 = "<<m_energy<<std::endl;
  std::cout<<"etamin                 = "<<m_etamin<<std::endl;
  std::cout<<"etamax                 = "<<m_etamax<<std::endl;
  std::cout<<"nEvents                = "<<m_nEvents<<std::endl; 
  std::cout<<"useFiles               = "<<m_useFiles<<std::endl;
  if(m_useFiles){
    std::cout<<"inputFileName          = "<<m_inputFileName<<std::endl; 
  }
  else{
    std::cout<<"inputDir               = "<<m_inputDir<<std::endl; 
  }
  std::cout<<"binningFileName        = "<<m_binningFileName<<std::endl; 
  std::cout<<"outputDir              = "<<m_outputDir<<std::endl; 
  std::cout<<"energyCorrectionScheme = "<<m_energyCorrectionScheme<<std::endl; 
  std::cout<<"saveRootFile           = "<<m_saveRootFile<<std::endl; 
  std::cout<<"useHitEnergy           = "<<m_useHitEnergy<<std::endl;
  std::cout<<"mergeBinsfirstR        = "<<m_mergeAlphaBinsInFirstRBin<<std::endl; 
  std::cout<<"useLargeR              = "<<m_useLargeR<<std::endl; 
  std::cout<<"symmetriseAlpha        = "<<m_symmetriseAlpha<<std::endl; 
  std::cout<<"optimiseAlphaBins      = "<<m_optimiseAlphaBins<<std::endl;  
  std::cout<<"batchNum               = "<<m_batchNum<<std::endl;
  std::cout<<"TotalBatches           = "<<m_TotalBatches<<std::endl;
  
}

void InputVoxelisationParameters::Validate(){
  CalculateXMLPid();
  CheckEnergyCorrectionScheme();
}

void InputVoxelisationParameters::CheckEnergyCorrectionScheme(){
  if (m_energyCorrectionScheme != "PerEventFromCellEnergy" && 
      m_energyCorrectionScheme != "PerEventFromG4HitsEnergy" && 
      m_energyCorrectionScheme != "PerCellFromG4HitsEnergy" && 
      m_energyCorrectionScheme != "PerCellFromCellEnergy" && 
      m_energyCorrectionScheme != "None")
  { 
    std::cerr << "Incorrect argument provided: " <<m_energyCorrectionScheme<<" for energy correction scheme";
    throw std::runtime_error("");
  }
}

void InputVoxelisationParameters::CalculateXMLPid(){
  if (m_pid != 22 && m_pid != 11){
    m_pid_xml = 211;
  }
  else {
    m_pid_xml = m_pid;
  }
}