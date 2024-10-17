#ifndef RunOnFCSHits_h
#define RunOnFCSHits_h

#include <string>
#include <iostream>   
#include <vector>
#include <fstream>

#include "InputVoxelisationParameters.h"
#include "FCS_Cell.h"

#include "TChain.h"
#include "TH2D.h"
#include "TGraphErrors.h"
#include "TProfile.h"

class RunOnFCSHits{
  
  public:
  RunOnFCSHits(InputVoxelisationParameters inputs);
  void Run();
  
  private:
  TChain* InitialiseChain();
  TChain* InitialiseChainFromFile();
  TChain* InitialiseChainFromFolder();
  std::tuple<float, float> GetUnitsmm(float eta_hit, float d_eta, float d_phi,  float cell_r, float cell_z);
  void CoordinateTransform(float s, float x, float y, float z, float extrapol_eta, float extrapol_phi, float extrapol_r, float extrapol_z, float &radius_mm, float &alpha_mm, float &alpha_absPhi_mm, double charge);
  std::vector<TH1D*> CreateHistosForVoxels();
  std::vector<TH1*> CreateHistosForR();
  double GetCharge(int pdgId);
  void WriteVoxalisedOutput(TChain* chain, int eventsToProcess);
  void LoopOverHits(std::vector<FCS_matchedcellvector**> allLayers, double charge);
  void RunOnEvents(TChain* chain, int eventsToProcess);
  void WriteBinContent(std::ofstream& writeFile, double binContent, int& nbins);
  void ClearVectors();
  std::string CsvFileName();
  std::string CsvValidationFileName();
  std::string CsvValidationCellsFileName();
  std::string CsvValidationG4HitsFileName();
  std::string CsvValidationHitsFileName();
  void WriteCsvFile(std::ofstream& writeFile, bool writeNumberOfVoxel);
  void WriteValidationCsvFile(std::ofstream&  file);
  void WriteValidationCellsCsvFile(std::ofstream&  file);
  void WriteValidationG4HitsCsvFile(std::ofstream&  file); 
  void WriteValidationHitsCsvFile(std::ofstream&  file);
  void GetCellsCoordinatesFromGeometry();
  Long64_t findImpactCell(int layer, float eta, float phi);
  void SetEventEnergyCorrection();
  int GetBinsInFours(double bins);
  void FillEnergyInCartesian(FCS_hit hit, float TTC_eta, float TTC_phi, float TTC_r, float TTC_z, float TTC_r_entry, float TTC_r_exit, float TTC_z_entry, float TTC_z_exit, double charge, int layer, TH1D* hist_hitenergy_weight);
  void FillEnergyInPolar(FCS_hit hit, float TTC_eta, float TTC_phi, float TTC_r, float TTC_z, float TTC_r_entry, float TTC_r_exit, float TTC_z_entry, float TTC_z_exit, double charge, int layer, TH1D* hist_hitenergy_weight);
  std::tuple<float, float> DeltasInMillilmiters(float x, float y, float z, float extrapol_eta, float extrapol_phi, float extrapol_r, float extrapol_z, double charge);
  void SetPhiMod();
  TGraphErrors* DefineTGraphEPhiMod();
  
  InputVoxelisationParameters m_inputs;
  std::string m_outputCsvDir;
  std::string m_outFileName;
  std::vector<TH1D*> m_histosVoxels;
  std::vector<TH1*> m_histosR;
  TProfile* m_profile;
  TH1D* m_normE;
  int m_numberOfErrors;
  
  // Tree from input files
	std::vector<std::vector<float>> *m_TTC_mid_eta = nullptr;
	std::vector<std::vector<float>> *m_TTC_mid_phi = nullptr;
	std::vector<std::vector<float>> *m_TTC_mid_r = nullptr;
	std::vector<std::vector<float>> *m_TTC_mid_z = nullptr;  
	std::vector<std::vector<float>> *m_TTC_ent_r = nullptr;
	std::vector<std::vector<float>> *m_TTC_ext_r = nullptr;
	std::vector<std::vector<float>> *m_TTC_ent_z = nullptr;  
	std::vector<std::vector<float>> *m_TTC_ext_z = nullptr;  
  std::vector<float> *m_newTTC_IDCaloBoundary_eta = nullptr;
  std::vector<int> *m_truthPDGID = nullptr;
  std::vector<float> *m_true_px = nullptr;
  std::vector<float> *m_true_py = nullptr;
  std::vector<float> *m_true_pz = nullptr;
  float m_total_cell_energy;
  float m_total_hit_energy;
  float m_total_g4hit_energy;
  //End TTree
  
  std::vector<double> m_cell_EtotLayer;
  std::vector<double> m_cell_cog_eta;
  std::vector<double> m_cell_cog_phi;
  std::vector<double> m_cell_width_eta;
  std::vector<double> m_cell_width_phi;
  double m_cell_Etot;

  std::vector<double> m_g4hit_EtotLayer;
  double m_g4hit_Etot;

  std::vector<double> m_hit_EtotLayer;
  double m_hit_Etot;

  std::vector<double> m_EtotLayer;
  std::vector<double> m_cog_eta;
  std::vector<double> m_cog_phi;
  std::vector<double> m_width_eta;
  std::vector<double> m_width_phi;
  double m_Etot;

  double m_cell_rescaling_weight;
  double m_event_rescaling_weight;
  std::vector<double> m_mean_weight;
  double m_phiMod;
  double m_trueEta;
  double m_truePhi;
  
  double m_EtotCurrentLayer;
  double m_currentCog_eta;
  double m_currentCog_phi;
  double m_currentWidth_eta;
  double m_currentWidth_phi;

  const int MaxNumberOfPrintedErrors = -1;
  
  //Det geometry
  Long64_t m_cell_identifier; // !
  Int_t m_cell_layer;         // !
  Float_t m_cell_eta_raw;         // !
  Float_t m_cell_phi_raw;         // !
  Float_t m_cell_phi;         // !
  Float_t m_cell_r_raw;           // !

  std::map<Long64_t, Float_t> m_cells_eta_raw;       // !
  std::map<Long64_t, Float_t> m_cells_phi_raw;       // !
  std::map<Long64_t, Float_t> m_cells_phi;       // !
  std::map<Long64_t, Float_t> m_cells_r_raw;       // !

  std::map<Int_t, std::vector<std::pair<Float_t, Float_t>>>  m_cell_coordinates; //!
  std::map<Int_t, std::vector<Long64_t>>  m_cell_identifiers;                    //!


  };

#endif