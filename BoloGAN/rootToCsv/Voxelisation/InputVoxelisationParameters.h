#ifndef InputVoxelisationParameters_h
#define InputVoxelisationParameters_h

#include <string>
#include <map>

#include "TH2.h"

class InputVoxelisationParameters{
  public: 
  
  InputVoxelisationParameters();
  void Print();
  
  int m_pid = 22;
  int m_pid_xml = 22;
  int m_energy = 65536;
  int m_etamin = 20;
  int m_etamax = 25;
  int m_nEvents = 10000;
  std::string m_inputDir = "/eos/atlas/atlascerngroupdisk/proj-simul/InputSamplesSummer18Complete/";
  std::string m_inputFileName = "/eos/atlas/atlascerngroupdisk/proj-simul/InputSamplesSummer18Complete/*.root";
  std::string m_binningFileName = "binning.xml";
  std::string m_outputDir = "nominal";
  std::string m_energyCorrectionScheme = "PerCellFromG4HitsEnergy";
  bool m_optimiseAlphaBins = false;
  bool m_isPolar = false;
  bool m_saveRootFile = true;
  bool m_useHitEnergy = true;
  bool m_mergeAlphaBinsInFirstRBin = false;
  bool m_useLargeR = false;
  bool m_symmetriseAlpha = true;

  int m_batchNum = 0;
  bool m_useFiles = false;
  int m_TotalBatches = 50;
  
  std::map<int, TH2D*> m_binsInLayers;

  void Validate();
 
  private:
  void CheckEnergyCorrectionScheme();
  void CalculateXMLPid();
  
};

#endif
