#include "RunOnFCSHits.h"

#include "TFile.h"
#include "TLorentzVector.h"
#include "TTree.h"
#include "TChain.h"
#include "TSystem.h"
#include "TApplication.h"

#include <iostream>
#include <math.h> 
 
#include <sys/stat.h>

RunOnFCSHits::RunOnFCSHits(InputVoxelisationParameters par) : 
                           m_inputs(par){
  m_outputCsvDir = Form("%s/csvFiles/pid%d/eta_%d_%d/",m_inputs.m_outputDir.c_str(), m_inputs.m_pid, m_inputs.m_etamin, m_inputs.m_etamax); 
  std::cout<<"Csv files folder is "<<m_outputCsvDir<<std::endl;
  gSystem->mkdir(m_outputCsvDir.c_str(),kTRUE);
  
  m_outFileName = Form("pid%d_E%.0d_eta_%d_%d", m_inputs.m_pid, m_inputs.m_energy, m_inputs.m_etamin, m_inputs.m_etamax);
  if (m_inputs.m_TotalBatches > 1){
    m_outFileName = Form("pid%d_E%.0d_eta_%d_%d_%d", m_inputs.m_pid, m_inputs.m_energy, m_inputs.m_etamin, m_inputs.m_etamax, m_inputs.m_batchNum);
  }
  std::cout<<"Csv files prefix is "<<m_outFileName<<std::endl;
  
  m_numberOfErrors = 0;
}

TChain* RunOnFCSHits::InitialiseChain(){
  if (m_inputs.m_useFiles == true){  
    return InitialiseChainFromFile();
  }
  else {
    return InitialiseChainFromFolder();
  }
}

TChain* RunOnFCSHits::InitialiseChainFromFile(){
  TChain * chain = new TChain("FCS_ParametrizationInput");
  chain->Add(m_inputs.m_inputFileName.c_str(), -1);  
  return chain;
}
 
TChain* RunOnFCSHits::InitialiseChainFromFolder(){
  TChain * chain = new TChain("FCS_ParametrizationInput");

  TString dir;
  std::string filesInFolder;
  if (m_inputs.m_pid == 22 || m_inputs.m_pid == 11 || m_inputs.m_pid == 211){
    dir = Form("%s | grep pid%d_E%d | grep eta_m%d_m%d", m_inputs.m_inputDir.c_str(), m_inputs.m_pid, m_inputs.m_energy, m_inputs.m_etamax, m_inputs.m_etamin);
    filesInFolder = "/*.root.1";
  }
  else {
    dir = Form("%s", m_inputs.m_inputDir.c_str());
    filesInFolder = "";
  }

  std::cout<<"Input dir "<<dir<<std::endl;
  gSystem->Exec(TString("ls ") + dir + TString(" > $TMPDIR/FCS_ls.$PPID.list"));
  TString tmpname = gSystem->Getenv("TMPDIR");
  tmpname += "/FCS_ls.";
  tmpname += gSystem->GetPid();
  tmpname += ".list";

  std::ifstream infile;
  infile.open(tmpname);
  while (!infile.eof()) {
    std::string filename;
    getline(infile, filename);
    if (filename != "") {
      std::string fullFileName = m_inputs.m_inputDir + filename + filesInFolder;
      std::cout<<"Filename is: "<<fullFileName<<std::endl;
      chain->Add((fullFileName).c_str(), -1);      
    }
    //std::cout<<chain->GetEntries()<<std::endl;
  }
  infile.close();

  return chain;
}

std::tuple<float, float> RunOnFCSHits::GetUnitsmm(float eta_hit, float d_eta, float d_phi,  float cell_r, float cell_z)
{
	float phi_dist2r = 1.0;

	float dist000 = TMath::Sqrt(cell_r * cell_r + cell_z * cell_z);

	float eta_jakobi = TMath::Abs(2.0 * TMath::Exp(-eta_hit) / (1.0 + TMath::Exp(-2 * eta_hit)));

	d_eta = d_eta * eta_jakobi * dist000;
	d_phi = d_phi * cell_r * phi_dist2r;

	return std::make_tuple(d_eta, d_phi);
}

std::tuple<float, float> RunOnFCSHits::DeltasInMillilmiters(float x, float y, float z, float extrapol_eta, float extrapol_phi, float extrapol_r, float extrapol_z, double charge){
  TVector3 v = TVector3(x,y,z);
  
  float deta_hit_minus_extrapol = v.Eta() - extrapol_eta;
  float dphi_hit_minus_extrapol = TVector2::Phi_mpi_pi(v.Phi() - extrapol_phi);

  if (extrapol_eta<0) deta_hit_minus_extrapol *= -1;
  if (charge<0) dphi_hit_minus_extrapol *= -1; 
  
  //float r= TMath::Sqrt(x*x + y*y);
  //std::tie(m_deta_hit_minus_extrapol_mm, m_dphi_hit_minus_extrapol_mm) = GetUnitsmm(v.Eta(), deta_hit_minus_extrapol, dphi_hit_minus_extrapol, r, z);
  return GetUnitsmm(extrapol_eta, deta_hit_minus_extrapol, dphi_hit_minus_extrapol, extrapol_r, extrapol_z);
}

void RunOnFCSHits::CoordinateTransform(float s, float x, float y, float z, float extrapol_eta, float extrapol_phi, float extrapol_r, float extrapol_z, float &radius_mm, float &alpha_mm, float &alpha_absPhi_mm, double charge){
   if (s <=20){     
      float deta_hit_minus_extrapol_mm, dphi_hit_minus_extrapol_mm;
      std::tie(deta_hit_minus_extrapol_mm, dphi_hit_minus_extrapol_mm) = DeltasInMillilmiters(x, y, z, extrapol_eta, extrapol_phi, extrapol_r, extrapol_z, charge);
      //float test_deta_mm, test_dphi_mm;
      //std::tie(test_deta_mm, test_dphi_mm) = GetUnitsmm(extrapol_eta, 0.003, 0, extrapol_r, extrapol_z);
      //std::cout<<"Dalila voxels "<<test_deta_mm<<" "<<test_dphi_mm<<std::endl;
      alpha_mm = TMath::ATan2(dphi_hit_minus_extrapol_mm, deta_hit_minus_extrapol_mm);
      
      alpha_absPhi_mm = TMath::ATan2(TMath::Abs(dphi_hit_minus_extrapol_mm), deta_hit_minus_extrapol_mm);
      
      radius_mm = TMath::Sqrt(dphi_hit_minus_extrapol_mm * dphi_hit_minus_extrapol_mm + deta_hit_minus_extrapol_mm * deta_hit_minus_extrapol_mm);
    }
    else { 
      /// Use x, y instread of eta, phi for FCal
      float delta_x = x - std::cos(extrapol_phi) * extrapol_r;
      float delta_y = y - std::sin(extrapol_phi) * extrapol_r;

      alpha_mm = TMath::ATan2(delta_y, delta_x);
      radius_mm = TMath::Sqrt(delta_x * delta_x + delta_y * delta_y); 
   }
}

//function to create an histogram for evey histo
std::vector<TH1D*> RunOnFCSHits::CreateHistosForVoxels(){
   std::vector<TH1D*> histos;
   for (auto element : m_inputs.m_binsInLayers){
      int layer = element.first;
      TH2D* h = element.second;
           
      int max = 1000;

      int xBinNum = h->GetNbinsX();
      if (xBinNum == 1) continue;
      int yBinNum = h -> GetNbinsY();
      for (int i = 1; i <= xBinNum; ++i){
          if (layer == 0 &&  i == 1) max = 2000;
          if (layer == 0 && ( i == 2 || i == 3)) max = 500;
          if (layer == 0 && ( i == 3 || i == 4 || i == 5 || i == 6 || i == 7 || i == 8)) max = 300;
          if (layer == 1 &&  i == 1 ) max = 2200;
          if (layer == 1 &&  i == 2  ) max = 1200;
          if (layer == 1 &&  i == 3 ) max = 800;
          if (layer == 1 && i == 4 ) max = 600;
          if (layer == 1 && i == 5 )  max = 500;
          if (layer == 1 && ( i == 6 || i == 7 || i == 8 || i == 9)) max = 300 ;
          if (layer == 1 && i == 10 )  max = 200 ;
          if (layer == 1 && ( i == 11 || i == 12)) max = 150;
          if (layer == 1 && ( i == 13 || i == 14)) max = 100;
          if (layer == 1 && ( i == 15 || i == 16)) max = 50;
          if (layer == 2 && i == 1 ) max = 3000;
          if (layer == 2 && i == 2 ) max = 2000;
          if (layer == 2 && i == 3 ) max = 3500;
          if (layer == 2 && i == 4 ) max = 2800;
          if (layer == 2 && i == 5 ) max = 1500;
          if (layer == 2 && ( i == 6 || i == 7 || i == 8 )) max = 1000;
          if (layer == 2 &&  i == 9 ) max = 800;
          if (layer == 2 && (i == 10 || i == 11)) max = 600;
          if (layer == 2 && i == 12 ) max = 400;
          if (layer == 2 && i == 13 ) max = 300;
          if (layer == 2 && i == 14 ) max = 200;
          if (layer == 2 && i == 15 ) max = 150;
          if (layer == 2 &&( i == 16 || i == 17 )) max = 100;
          if (layer == 2 && i == 18 ) max = 80;
          if (layer == 2 && i == 19 ) max = 50;
          if (layer == 3 && i == 1 ) max = 1200;
          if (layer == 3 && i == 2 ) max = 600;
          if (layer == 3 && i == 3 ) max = 200;
          if (layer == 3 && i == 4 ) max = 100;
          if (layer == 3 && i == 5 ) max = 50;
          if (layer == 12 && ( i == 1 || i == 2 || i == 3 )) max = 600;
          if (layer == 12 && i == 4 ) max = 200;
          if (layer == 12 && i == 5 ) max = 100;
  
          max = max * sqrt(m_inputs.m_energy/65536.0);

          for (int j = 1; j <= yBinNum; ++j){
            
            TString name = Form("layer%d_r%d_alpha%d",layer, i, j);
            TH1D* h1 = new TH1D(name,name,100,0,max);
            histos.push_back(h1);
         }         
      }
    }
    
   std::cout<<"Histos for voxels: "<<histos.size()<<std::endl;

   return histos;
 }
 
std::vector<TH1*> RunOnFCSHits::CreateHistosForR(){
  std::vector<TH1*> histos;
  for (auto element : m_inputs.m_binsInLayers){
    int layer = element.first;
    TString name = Form("r%d",layer);
    TH1D* r = new TH1D(name,name,10000,0,10000);
    histos.push_back(r);
    name = Form("r%dw",layer);
    TH1D* rw = new TH1D(name,name,10000,0,10000);
    histos.push_back(rw);
    name = Form("e%d",layer);
    TH1D* e = new TH1D(name,name,11000,-1000,10000);
    histos.push_back(e);
    name = Form("t%d",layer);
    TH1D* t = new TH1D(name,name,10000,0,10000);
    histos.push_back(t);
    name = Form("t_r_%d",layer);
    TH2D* tr = new TH2D(name,name,1000,0,200,1000,0,10000);
    histos.push_back(tr);
  }
  
  return histos;
}
 
double RunOnFCSHits::GetCharge(const int pdgID){
  if(pdgID==11 || pdgID==211 || pdgID==2212 || pdgID==321) return 1.;
  else if (pdgID==-11 || pdgID==-211 || pdgID==-2212 || pdgID==-321) return -1.;
  else if ( pdgID==22 || fabs(pdgID)==2112 || pdgID==111 || pdgID==130 ) return 0;

  return -999.;
}


void RunOnFCSHits::RunOnEvents(TChain* chain, int eventsToProcess){
  FCS_matchedcellvector *vec_0=0; 
  FCS_matchedcellvector *vec_1=0; 
  FCS_matchedcellvector *vec_2=0; 
  FCS_matchedcellvector *vec_3=0; 
  FCS_matchedcellvector *vec_4=0; 
  FCS_matchedcellvector *vec_5=0; 
  FCS_matchedcellvector *vec_6=0; 
  FCS_matchedcellvector *vec_7=0; 
  FCS_matchedcellvector *vec_8=0; 
  FCS_matchedcellvector *vec_9=0; 
  FCS_matchedcellvector *vec_10=0; 
  FCS_matchedcellvector *vec_11=0; 
  FCS_matchedcellvector *vec_12=0; 
  FCS_matchedcellvector *vec_13=0; 
  FCS_matchedcellvector *vec_14=0; 
  FCS_matchedcellvector *vec_15=0; 
  FCS_matchedcellvector *vec_16=0; 
  FCS_matchedcellvector *vec_17=0; 
  FCS_matchedcellvector *vec_18=0; 
  FCS_matchedcellvector *vec_19=0; 
  FCS_matchedcellvector *vec_20=0; 
  FCS_matchedcellvector *vec_21=0; 
  FCS_matchedcellvector *vec_22=0; 
  FCS_matchedcellvector *vec_23=0; 
  FCS_matchedcellvector *vec_24=0; 
       
  chain->SetBranchAddress("Sampling_0",&vec_0 );
  chain->SetBranchAddress("Sampling_1",&vec_1 );
  chain->SetBranchAddress("Sampling_2",&vec_2 );
  chain->SetBranchAddress("Sampling_3",&vec_3 );
  chain->SetBranchAddress("Sampling_4",&vec_4 );
  chain->SetBranchAddress("Sampling_5",&vec_5 );
  chain->SetBranchAddress("Sampling_6",&vec_6 );
  chain->SetBranchAddress("Sampling_7",&vec_7 );
  chain->SetBranchAddress("Sampling_8",&vec_8 );
  chain->SetBranchAddress("Sampling_9",&vec_9 );
  chain->SetBranchAddress("Sampling_10",&vec_10);
  chain->SetBranchAddress("Sampling_11",&vec_11);
  chain->SetBranchAddress("Sampling_12",&vec_12);
  chain->SetBranchAddress("Sampling_13",&vec_13);
  chain->SetBranchAddress("Sampling_14",&vec_14);
  chain->SetBranchAddress("Sampling_15",&vec_15);
  chain->SetBranchAddress("Sampling_16",&vec_16);
  chain->SetBranchAddress("Sampling_17",&vec_17);
  chain->SetBranchAddress("Sampling_18",&vec_18);
  chain->SetBranchAddress("Sampling_19",&vec_19);
  chain->SetBranchAddress("Sampling_20",&vec_20);
  chain->SetBranchAddress("Sampling_21",&vec_21);
  chain->SetBranchAddress("Sampling_22",&vec_22);
  chain->SetBranchAddress("Sampling_23",&vec_23);
  chain->SetBranchAddress("Sampling_24",&vec_24);

  std::vector<FCS_matchedcellvector**> allLayers;
  allLayers.push_back(&vec_0 );
  allLayers.push_back(&vec_1 ); 
  allLayers.push_back(&vec_2 ); 
  allLayers.push_back(&vec_3 ); 
  allLayers.push_back(&vec_4 ); 
  allLayers.push_back(&vec_5 ); 
  allLayers.push_back(&vec_6 ); 
  allLayers.push_back(&vec_7 ); 
  allLayers.push_back(&vec_8 ); 
  allLayers.push_back(&vec_9 ); 
  allLayers.push_back(&vec_10);  
  allLayers.push_back(&vec_11);  
  allLayers.push_back(&vec_12);  
  allLayers.push_back(&vec_13);  
  allLayers.push_back(&vec_14);  
  allLayers.push_back(&vec_15);  
  allLayers.push_back(&vec_16);  
  allLayers.push_back(&vec_17);  
  allLayers.push_back(&vec_18);  
  allLayers.push_back(&vec_19);  
  allLayers.push_back(&vec_20);  
  allLayers.push_back(&vec_21);  
  allLayers.push_back(&vec_22);  
  allLayers.push_back(&vec_23);  
  allLayers.push_back(&vec_24); 


	//std::vector<std::vector<float>> *TTC_mid_eta = nullptr;
	//std::vector<std::vector<float>> *TTC_mid_phi = nullptr;
	//std::vector<std::vector<float>> *TTC_mid_r = nullptr;
	//std::vector<std::vector<float>> *TTC_mid_z = nullptr;

	chain->SetBranchAddress("newTTC_mid_eta",    &m_TTC_mid_eta);
	chain->SetBranchAddress("newTTC_mid_phi",    &m_TTC_mid_phi);
	chain->SetBranchAddress("newTTC_mid_r",      &m_TTC_mid_r);
	chain->SetBranchAddress("newTTC_mid_z",      &m_TTC_mid_z);
	chain->SetBranchAddress("newTTC_entrance_r", &m_TTC_ent_r);
	chain->SetBranchAddress("newTTC_back_r",     &m_TTC_ext_r);
	chain->SetBranchAddress("newTTC_entrance_z", &m_TTC_ent_z);
	chain->SetBranchAddress("newTTC_back_z",     &m_TTC_ext_z);

	chain->SetBranchAddress("newTTC_IDCaloBoundary_eta",  &m_newTTC_IDCaloBoundary_eta);

  chain->SetBranchAddress("TruthPDG", &m_truthPDGID); 
	chain->SetBranchAddress("TruthPx",  &m_true_px);
	chain->SetBranchAddress("TruthPy",  &m_true_py);
	chain->SetBranchAddress("TruthPz",  &m_true_pz);
  
  chain->SetBranchAddress("total_cell_energy",  &m_total_cell_energy); 
	chain->SetBranchAddress("total_hit_energy",   &m_total_hit_energy);
	chain->SetBranchAddress("total_g4hit_energy", &m_total_g4hit_energy);
  
  m_histosVoxels = CreateHistosForVoxels();
  m_histosR = CreateHistosForR();
  m_profile = new TProfile("prof_E_phiMod","prof_E_phiMod",40,0,0.01);
  m_normE = new TH1D("normE","normE",1000,0,2);

  std::cout<<"Start loop"<<std::endl;

  std::ofstream writeFile;
  writeFile.open(CsvFileName().data()); 

  std::ofstream writeValidationFile;
  writeValidationFile.open(CsvValidationFileName().data());

  std::ofstream writeValidationCellsFile;
  writeValidationCellsFile.open(CsvValidationCellsFileName().data());

  std::ofstream writeValidationG4HitsFile;
  writeValidationG4HitsFile.open(CsvValidationG4HitsFileName().data());

  std::ofstream writeValidationHitsFile;
  writeValidationHitsFile.open(CsvValidationHitsFileName().data());

  int d = 0;
  
  int firstEvent = m_inputs.m_batchNum*eventsToProcess/m_inputs.m_TotalBatches;
  int lastEvent = (m_inputs.m_batchNum+1)*eventsToProcess/m_inputs.m_TotalBatches;
  if (m_inputs.m_useFiles == true) {
    firstEvent = 0; 
    lastEvent = eventsToProcess;
  }
  
  int eventsInBatch = lastEvent - firstEvent;

  int selectedEvents = 0;

  std::cout<<"Running on events "<<firstEvent<<"-"<<lastEvent<<", ("<<eventsInBatch<<" events in total), batch " << m_inputs.m_batchNum+1 << "/" << m_inputs.m_TotalBatches<<std::endl;
  for (int ientry=firstEvent; ientry<lastEvent; ientry++) // loop over the events chain->GetEntries()
  {
    ClearVectors();
    double a = eventsInBatch/100;
    if (ientry-firstEvent >= d * a){
      std::cout<< "\r" << d << " %" << std::flush;
      d++;
    }
    bool writeNumberOfVoxel = false;
    if (ientry == lastEvent -1){
      std::cout<< "\r100%" << std::endl;
      writeNumberOfVoxel = true;
    }
    
    if (m_numberOfErrors == MaxNumberOfPrintedErrors){
      std::cout<<"Stop printing errors after 100 occurrences"<<std::endl;
      m_numberOfErrors++;
    }
    
    chain->GetEntry(ientry);
    int pdg = m_truthPDGID->at(0);
    double charge = GetCharge(pdg);
    
    TVector3 trueP = TVector3(m_true_px->at(0),m_true_py->at(0),m_true_pz->at(0));
    m_trueEta = fabs(trueP.Eta());
    m_truePhi = trueP.Phi();

    if(fabs(m_newTTC_IDCaloBoundary_eta->at(0)*100) < m_inputs.m_etamin || fabs(m_newTTC_IDCaloBoundary_eta->at(0)*100) > m_inputs.m_etamax) continue;
    selectedEvents++;
    //std::cout<<selectedEvents<<std::endl;

    SetEventEnergyCorrection();
    
    LoopOverHits(allLayers, charge);
    WriteCsvFile(writeFile, writeNumberOfVoxel);
    WriteValidationCsvFile(writeValidationFile);
    WriteValidationCellsCsvFile(writeValidationCellsFile);
    WriteValidationG4HitsCsvFile(writeValidationG4HitsFile);
    WriteValidationHitsCsvFile(writeValidationHitsFile);
  }
  
  writeFile.close();
  writeValidationFile.close();
  writeValidationCellsFile.close();
  writeValidationG4HitsFile.close();
  writeValidationHitsFile.close();
}

void RunOnFCSHits::ClearVectors(){
  m_cog_eta.clear();
  m_cog_phi.clear();
  m_width_eta.clear();
  m_width_phi.clear();
  m_EtotLayer.clear();
  
  m_cell_cog_eta.clear();
  m_cell_cog_phi.clear();
  m_cell_width_eta.clear();
  m_cell_width_phi.clear();
  m_cell_EtotLayer.clear();
  
  m_g4hit_EtotLayer.clear();
  m_hit_EtotLayer.clear();

  m_mean_weight.clear();
}

std::string RunOnFCSHits::CsvFileName(){
  std::string csvFileName = m_outputCsvDir + "/" + m_outFileName + "_voxalisation.csv";
  std::cout << "Writing CSV output file: " << csvFileName << std::endl;
  return csvFileName;
}

std::string RunOnFCSHits::CsvValidationFileName(){
  return m_outputCsvDir + "/" + m_outFileName + "_validation.csv";
}

std::string RunOnFCSHits::CsvValidationCellsFileName(){
  return m_outputCsvDir + "/" + m_outFileName + "_cells_validation.csv";
}

std::string RunOnFCSHits::CsvValidationG4HitsFileName(){
  return m_outputCsvDir + "/" + m_outFileName + "_g4hits_validation.csv";
}

std::string RunOnFCSHits::CsvValidationHitsFileName(){
  return m_outputCsvDir + "/" + m_outFileName + "_hits_validation.csv";
}

void RunOnFCSHits::SetEventEnergyCorrection(){
  m_event_rescaling_weight = 1;
  if (m_inputs.m_energyCorrectionScheme == "PerEventFromG4HitsEnergy"){
    
    if (m_total_g4hit_energy != 0){
      m_event_rescaling_weight  = m_total_g4hit_energy/m_total_hit_energy;
    }
    else if (m_numberOfErrors < MaxNumberOfPrintedErrors){
      std::cout<<"Total G4hits is zero while for FCSHit is not zero, problem?"<<std::endl;
      m_numberOfErrors++;
    }
  }
  else if (m_inputs.m_energyCorrectionScheme == "PerEventFromCellEnergy"){
    if (m_total_cell_energy != 0){
      m_event_rescaling_weight  = m_total_cell_energy/m_total_hit_energy;
    }
    else if (m_numberOfErrors < MaxNumberOfPrintedErrors){
      std::cout<<"Total energy is zero while for FCSHits is not zero, problem?"<<std::endl;
      m_numberOfErrors++;
    }
  }
}

void RunOnFCSHits::LoopOverHits(std::vector<FCS_matchedcellvector**> allLayers, double charge){
  double Etot = 0;
  double cell_Etot = 0;
  double g4hit_Etot = 0;
  double hit_Etot = 0;
  TH1D* hist_hitenergy_weight = new TH1D("hist_hitenergy_weight","hist_hitenergy_weight",2000, -2., 3);
  
  for (auto element : m_inputs.m_binsInLayers){
    int layer = element.first;
    //std::cout<<"Layer "<<layer<<std::endl;
    m_EtotCurrentLayer = 0;
    m_currentCog_eta = 0;
    m_currentCog_phi = 0;
    m_currentWidth_eta = 0;
    m_currentWidth_phi = 0;

    double cell_EtotLayer = 0;
    double cell_cog_eta = 0;
    double cell_cog_phi = 0;
    double cell_width_eta = 0;
    double cell_width_phi = 0;
    double g4hit_EtotLayer = 0;
    double hit_EtotLayer = 0;
    
    auto vec = *allLayers[element.first];
    for (int j=0; (unsigned) j <(*vec).size(); j++){ // loop over cells in sampling 
      Long64_t cell_ID = ((FCS_matchedcell)(*vec)[j]).cell.cell_identifier; //loop over hits in the cell
      float cell_energy = ((FCS_matchedcell)(*vec)[j]).cell.energy;
      float cell_g4hit_energy = 0;
      float cell_hit_energy = 0;
      float cell_s = ((FCS_matchedcell)(*vec)[j]).cell.sampling;

      float TTC_eta     = (*m_TTC_mid_eta).at(0).at(cell_s);
      float TTC_phi     = (*m_TTC_mid_phi).at(0).at(cell_s);
      float TTC_r       = (*m_TTC_mid_r).at(0).at(cell_s);
      float TTC_z       = (*m_TTC_mid_z).at(0).at(cell_s);
      float TTC_r_entry = (*m_TTC_ent_r).at(0).at(cell_s);
      float TTC_r_exit  = (*m_TTC_ext_r).at(0).at(cell_s);
      float TTC_z_entry = (*m_TTC_ent_z).at(0).at(cell_s);
      float TTC_z_exit  = (*m_TTC_ext_z).at(0).at(cell_s);

      double cell_eta = m_cells_eta_raw[cell_ID];
      double cell_phi = m_cells_phi_raw[cell_ID];
      
      float deta_hit_minus_extrapol = cell_eta - TTC_eta;
      float dphi_hit_minus_extrapol = TVector2::Phi_mpi_pi(cell_phi - TTC_phi);

      if (TTC_eta<0) deta_hit_minus_extrapol *= -1;
      if (charge<0) dphi_hit_minus_extrapol *= -1; 
      
      float cell_eta_mm, cell_phi_mm;
      std::tie(cell_eta_mm, cell_phi_mm) = GetUnitsmm(TTC_eta, deta_hit_minus_extrapol, dphi_hit_minus_extrapol, TTC_r, TTC_z);
      
      //std::cout<<"Cell"<<std::endl;
      //std::cout<<cell_eta_mm<<" "<<cell_phi_mm<<std::endl;
      
      float r = sqrt(cell_eta_mm*cell_eta_mm + cell_phi_mm*cell_phi_mm);
      if (m_inputs.m_useLargeR || r <1000){
        cell_cog_eta+=cell_eta_mm*cell_energy;
        cell_cog_phi+=cell_phi_mm*cell_energy;          
        cell_width_eta+=cell_eta_mm*cell_eta_mm*cell_energy;
        cell_width_phi+=cell_phi_mm*cell_phi_mm*cell_energy;
      }
        
      cell_EtotLayer+=cell_energy;
            
      for (int ihit=0; (unsigned) ihit<((FCS_matchedcell)(*vec)[j]).hit.size(); ihit++){
        cell_hit_energy += ((FCS_matchedcell)(*vec)[j]).hit[ihit].hit_energy;
      }
      
      hit_EtotLayer += cell_hit_energy;

      for (int ihit=0; (unsigned) ihit<((FCS_matchedcell)(*vec)[j]).g4hit.size(); ihit++){
        cell_g4hit_energy += ((FCS_matchedcell)(*vec)[j]).g4hit[ihit].hit_energy;
      }
      
      g4hit_EtotLayer += cell_g4hit_energy;

      m_cell_rescaling_weight = 1;
      if (m_inputs.m_energyCorrectionScheme == "PerCellFromG4HitsEnergy"){
        if (cell_g4hit_energy != 0){
          m_cell_rescaling_weight  = cell_g4hit_energy/cell_hit_energy;
        }
        else if (m_numberOfErrors < MaxNumberOfPrintedErrors){
          std::cout<<"Cell G4hits is zero while FCSHits are not zero, problem?"<<std::endl;
          m_numberOfErrors++;
        }
      }
      else if (m_inputs.m_energyCorrectionScheme == "PerCellFromCellEnergy"){
        if (cell_energy != 0){
          m_cell_rescaling_weight  = cell_energy/cell_hit_energy;
        }
        else if (m_numberOfErrors < MaxNumberOfPrintedErrors){
          std::cout<<"Cell energy is zero while FCSHits are not zero, problem?"<<std::endl;
          m_numberOfErrors++;
        }
      }
      //std::cout<<"FCSHit energy: "<<cell_hit_energy<<"Cell-FCSHits ratio: "<<cell_energy/cell_hit_energy<<" G4Hits-FCSHits ratio: "<<cell_g4hit_energy/cell_hit_energy<<std::endl;
      
      //std::cout<<"Hits"<<std::endl;
      for (int ihit=0; (unsigned) ihit<((FCS_matchedcell)(*vec)[j]).hit.size(); ihit++){
        // check what is the hit position

        if (m_inputs.m_isPolar){
          FillEnergyInPolar(((FCS_matchedcell)(*vec)[j]).hit[ihit], TTC_eta, TTC_phi, TTC_r, TTC_z, TTC_r_entry, TTC_r_exit, TTC_z_entry, TTC_z_exit, charge, layer, hist_hitenergy_weight);
        }
        else{
          FillEnergyInCartesian(((FCS_matchedcell)(*vec)[j]).hit[ihit], TTC_eta, TTC_phi, TTC_r, TTC_z, TTC_r_entry, TTC_r_exit, TTC_z_entry, TTC_z_exit, charge, layer, hist_hitenergy_weight);          
        }                
      } 
    }
    
    //std::cout<<cog_eta<<std::endl;
    //std::cout<<width_eta<<std::endl;

    if (m_EtotCurrentLayer != 0){
      m_currentCog_eta=m_currentCog_eta/m_EtotCurrentLayer;
      m_currentCog_phi=m_currentCog_phi/m_EtotCurrentLayer;   

      m_currentWidth_eta=sqrt(m_currentWidth_eta/m_EtotCurrentLayer-(m_currentCog_eta*m_currentCog_eta));
      m_currentWidth_phi=sqrt(m_currentWidth_phi/m_EtotCurrentLayer-(m_currentCog_phi*m_currentCog_phi));
    }
    
    if (cell_EtotLayer != 0){
      cell_cog_eta=cell_cog_eta/cell_EtotLayer;
      cell_cog_phi=cell_cog_phi/cell_EtotLayer;   

      cell_width_eta=sqrt(cell_width_eta/cell_EtotLayer-(cell_cog_eta*cell_cog_eta));
      cell_width_phi=sqrt(cell_width_phi/cell_EtotLayer-(cell_cog_phi*cell_cog_phi));
    }
    
    m_cog_eta.push_back(m_currentCog_eta);
    m_cog_phi.push_back(m_currentCog_phi);
    m_width_eta.push_back(m_currentWidth_eta);
    m_width_phi.push_back(m_currentWidth_phi);
    m_EtotLayer.push_back(m_EtotCurrentLayer);
    
    m_cell_cog_eta.push_back(cell_cog_eta);
    m_cell_cog_phi.push_back(cell_cog_phi);
    m_cell_width_eta.push_back(cell_width_eta);
    m_cell_width_phi.push_back(cell_width_phi);
    m_cell_EtotLayer.push_back(cell_EtotLayer);
 
    m_g4hit_EtotLayer.push_back(g4hit_EtotLayer);
    m_hit_EtotLayer.push_back(hit_EtotLayer);
    
    Etot+=m_EtotCurrentLayer;
    cell_Etot+=cell_EtotLayer;
    g4hit_Etot+=g4hit_EtotLayer;
    hit_Etot+=hit_EtotLayer;
    
    m_mean_weight.push_back(hist_hitenergy_weight->GetMean());
    
    hist_hitenergy_weight->Reset();
  }
  
  delete hist_hitenergy_weight;
  m_Etot=Etot;
  m_cell_Etot=cell_Etot;
  m_g4hit_Etot=g4hit_Etot;
  m_hit_Etot=hit_Etot;
  
  SetPhiMod();
  double normalisedEnergy = m_Etot/m_inputs.m_energy;
  m_profile->Fill(m_phiMod, normalisedEnergy);
  m_normE->Fill(normalisedEnergy);
}

void RunOnFCSHits::SetPhiMod(){
  double deltaPhi = 0;
  for (auto element : m_inputs.m_binsInLayers){
    int layer = element.first;
    if (m_EtotLayer[layer] <= 0) continue;
    float TTC_eta     = (*m_TTC_mid_eta).at(0).at(layer);
    float TTC_phi     = (*m_TTC_mid_phi).at(0).at(layer);
    Long64_t impactcell_id = findImpactCell(layer, TTC_eta, TTC_phi);
    //std::cout<<"impactcell_id: "<<impactcell_id<<std::endl;
    //std::cout<<m_cells_phi[impactcell_id] << " " <<  m_cells_phi_raw[impactcell_id] <<std::endl;
    
    double phi_correction = m_cells_phi[impactcell_id] - m_cells_phi_raw[impactcell_id];
    //std::cout<<"phi_correction: "<<phi_correction<<std::endl;
    //std::cout<<"EtotLayer: "<<m_EtotLayer[layer]<<std::endl;
    deltaPhi+=m_EtotLayer[layer]/m_Etot*phi_correction; 
  }
  //std::cout<<"Etot: "<<m_Etot<<std::endl;
  //std::cout<<"deltaPhi: "<<deltaPhi<<std::endl;
  if(fabs(m_trueEta)<1.425)
    m_phiMod = std::fmod(std::fabs(m_truePhi-deltaPhi),TMath::Pi()/512.);
  else
    m_phiMod = std::fmod(std::fabs(m_truePhi-deltaPhi),TMath::Pi()/384.);
}

void RunOnFCSHits::FillEnergyInPolar(FCS_hit hit, float TTC_eta, float TTC_phi, float TTC_r, float TTC_z, float TTC_r_entry, float TTC_r_exit, float TTC_z_entry, float TTC_z_exit, double charge, int layer, TH1D* hist_hitenergy_weight){
  float x,y,z,t,s,E;
  x = hit.hit_x;
  y = hit.hit_y;
  z = hit.hit_z;
  t = hit.hit_time;
  s = hit.sampling;
  E = hit.hit_energy * m_cell_rescaling_weight * m_event_rescaling_weight;

  float r,alpha,alpha_absPhi;
  CoordinateTransform(s, x, y, z, TTC_eta, TTC_phi, TTC_r, TTC_z, r, alpha, alpha_absPhi, charge);

  int nHitsto = 5;
  m_histosR[layer*nHitsto]->Fill(r);
  m_histosR[layer*nHitsto+1]->Fill(r,E);
  m_histosR[layer*nHitsto+2]->Fill(E);
  m_histosR[layer*nHitsto+3]->Fill(t);
  m_histosR[layer*nHitsto+4]->Fill(t,r);
  
  if (m_inputs.m_symmetriseAlpha){
    alpha = alpha_absPhi;
  }
  
  m_EtotCurrentLayer+=E;
  if (m_inputs.m_useLargeR || r <2000){
    double eta = r*cos(alpha);
    double phi = r*sin(alpha);
    //std::cout<<eta<<" "<<phi<<std::endl;

    m_currentCog_eta+=eta*E;
    m_currentCog_phi+=phi*E;          
    m_currentWidth_eta+=eta*eta*E;
    m_currentWidth_phi+=phi*phi*E;

    //std::cout<<cog_eta<<std::endl;
    //std::cout<<width_eta<<std::endl;
    
    if (layer != s) std::cout<<"Error "<<layer<<" "<<s<<std::endl;
    
    if (m_inputs.m_useHitEnergy){
       m_inputs.m_binsInLayers[s]->Fill(r, alpha, E);
    }
    else{
       m_inputs.m_binsInLayers[s]->Fill(r, alpha, 1);
    }   
  
    //Calculate depth of hits for exapolation correction
    float w(0.);
    float r_xyz = TMath::Sqrt(x*x + y*y);
    if (s <=20){ // Barrel: weight from r
      w = (r_xyz - TTC_r_entry)/(TTC_r_exit - TTC_r_entry);
    }
    else{ // End-Cap and FCal: weight from z
      w = (z - TTC_z_entry)/(TTC_z_exit - TTC_z_entry);
    }
    hist_hitenergy_weight->Fill(w,E);  
  }
}

void RunOnFCSHits::FillEnergyInCartesian(FCS_hit hit, float TTC_eta, float TTC_phi, float TTC_r, float TTC_z, float TTC_r_entry, float TTC_r_exit, float TTC_z_entry, float TTC_z_exit, double charge, int layer, TH1D* hist_hitenergy_weight){
  float x,y,z,s,E;
  x = hit.hit_x;
  y = hit.hit_y;
  z = hit.hit_z;
  s = hit.sampling;
  E = hit.hit_energy * m_cell_rescaling_weight * m_event_rescaling_weight;

  float deta_mm, dphi_mm;
  std::tie(deta_mm, dphi_mm) = DeltasInMillilmiters(x, y, z, TTC_eta, TTC_phi, TTC_r, TTC_z, charge);

  m_EtotCurrentLayer+=E;
  double r = sqrt(deta_mm*deta_mm + dphi_mm*dphi_mm);

  if (m_inputs.m_useLargeR || r <2000){
    if (layer != s) std::cout<<"Error "<<layer<<" "<<s<<std::endl;

    m_currentCog_eta+=deta_mm*E;
    m_currentCog_phi+=dphi_mm*E;          
    m_currentWidth_eta+=deta_mm*deta_mm*E;
    m_currentWidth_phi+=dphi_mm*dphi_mm*E;
    
    if (m_inputs.m_useHitEnergy){
       m_inputs.m_binsInLayers[s]->Fill(deta_mm, dphi_mm, E);
    }
    else{
       m_inputs.m_binsInLayers[s]->Fill(deta_mm, dphi_mm, 1);
    }
    
  
    //Calculate depth of hits for exapolation correction
    float w(0.);
    float r_xyz = TMath::Sqrt(x*x + y*y);
    if (s <=20){ // Barrel: weight from r
      w = (r_xyz - TTC_r_entry)/(TTC_r_exit - TTC_r_entry);
    }
    else{ // End-Cap and FCal: weight from z
      w = (z - TTC_z_entry)/(TTC_z_exit - TTC_z_entry);
    }
    hist_hitenergy_weight->Fill(w,E);  
  }
}

void RunOnFCSHits::WriteCsvFile(std::ofstream& writeFile, bool writeNumberOfVoxel){

  writeFile << m_phiMod << ", " << m_trueEta;
  
  int nVoxels = 0;
  std::vector<int> relevantLayers;
  for (auto element : m_inputs.m_binsInLayers){
    int layer = element.first;
    //std::cout<<"Layer: "<<layer<<std::endl;
    TH2D* h = element.second;
    //If only one bin in r means layer is empy, no value should be added
    int xBinNum = h -> GetNbinsX();
    if (xBinNum == 1) continue;
    
    relevantLayers.push_back(layer);
    
    int yBinNum = h->GetNbinsY();
    if (!m_inputs.m_optimiseAlphaBins || yBinNum==1){
      for (int i = 1; i <= xBinNum; ++i){
        double mergedHits = 0;
        for (int j = 1; j <= yBinNum; ++j){
          double binContent = h->GetBinContent(j*(xBinNum+2)+i);
          if (i==1 && yBinNum > 1 && m_inputs.m_mergeAlphaBinsInFirstRBin == true){
            mergedHits += binContent;
            if (j == yBinNum){
              binContent = mergedHits; 
            }
            else {
              continue;
            }
          }
          WriteBinContent(writeFile, binContent, nVoxels);
        }
      }
    }      
    else {
      for (int i = 1; i <= xBinNum; ++i){
        double widthX = h->GetXaxis()->GetBinWidth(i);
        double radious = h->GetXaxis()->GetBinCenter(i);
        double circumference = radious*2*TMath::Pi();
        if (m_inputs.m_symmetriseAlpha){
          circumference = radious*TMath::Pi();
        }
        double bins = circumference / widthX;
        int nBinsAlpha = GetBinsInFours(bins);
        //std::cout<<"Bin in r: "<<i<<std::endl;
        //std::cout<<"  AlphaBinsL: "<<nBinsAlpha<<"  obtained with w: "<<widthX<<" radious: "<<radious<<" circ:"<<circumference<<std::endl;
        std::vector<double> binContents(nBinsAlpha, 0);
        int indexBinContent = 0;
        for (int j = 1; j <= yBinNum; ++j){
          double binContent = h->GetBinContent(j*(xBinNum+2)+i);
          //std::cout<<indexBinContent<<" "<<binContents[indexBinContent]<<" "<<std::endl;
          binContents[indexBinContent] += binContent;
          if (j%(32/nBinsAlpha) == 0) indexBinContent ++;
        }
        for (auto binContent : binContents){
          WriteBinContent(writeFile, binContent, nVoxels);
        }
      }
    }
    
    h->Reset();    
  }

  /* Removed extrapolator weights as will not be used as input to the GAN, keeping them in the validation for Jonathan
  //Now write weights for each relevant layer
  for (int layer : relevantLayers){    
    writeFile << ", " << m_mean_weight[layer];
  }
  */

  writeFile << "\n"  ;  // to separate between the events 

  if (writeNumberOfVoxel)
    std::cout<<"Written "<<nVoxels<<" voxels"<<std::endl;
}

int RunOnFCSHits::GetBinsInFours(double bins){
  if (bins < 4)
    return 4;
  else if (bins < 8)
    return 8;
  else if (bins < 16)
    return 16;
  else return 32;
}

TGraphErrors* RunOnFCSHits::DefineTGraphEPhiMod(){
  double meanForCorrection = m_normE->GetMean();
  TGraphErrors* graph = new TGraphErrors();
  graph->SetName("E_phiMod_shifted");
  int count_entries=0;
  double mean=0.0;
  for(int b=1;b<=m_profile->GetNbinsX();b++){
    double content=m_profile->GetBinContent(b)/meanForCorrection;
    double error=m_profile->GetBinError(b);
    if(content>0.01) {
      graph->SetPoint(count_entries,m_profile->GetBinCenter(b),content);
      graph->SetPointError(count_entries,0.00001,error);
      count_entries++;
      mean+=content;
    }
  }

  return graph;
}


void RunOnFCSHits::WriteBinContent(std::ofstream& writeFile, double binContent, int& nVoxels){
  //std::cout<<"NVoxel:"<<nVoxels<<" bin content: "<<binContent<<std::endl;
  writeFile << ", " << binContent;
  m_histosVoxels[nVoxels]->Fill(binContent);
  nVoxels++;
}

void RunOnFCSHits::WriteValidationCsvFile(std::ofstream&  file){
  file << m_Etot  << ", " << m_phiMod << ", " << m_trueEta; 
  for (auto element : m_inputs.m_binsInLayers){
    int layer = element.first;
    //std::cout<<layer<<std::endl;
    
    file << ", ";
    file << m_EtotLayer[layer];
    file << ", ";
    file << m_cog_eta[layer];
    file << ", ";
    file << m_cog_phi[layer];
    file << ", ";
    file << m_width_eta[layer];
    file << ", ";
    file << m_width_phi[layer];
    file << ", ";
    file << m_mean_weight[layer]; //here we write all, for validation
  }
  
  file << "\n"  ;  // to separate between the events 
}

void RunOnFCSHits::WriteValidationCellsCsvFile(std::ofstream&  file){
  file << m_cell_Etot  << ", " << m_phiMod << ", " << m_trueEta; 
  for (auto element : m_inputs.m_binsInLayers){
    int layer = element.first;
    //std::cout<<layer<<std::endl;
    
    file << ", ";
    file << m_cell_EtotLayer[layer];
    file << ", ";
    file << m_cell_cog_eta[layer];
    file << ", ";
    file << m_cell_cog_phi[layer];
    file << ", ";
    file << m_cell_width_eta[layer];
    file << ", ";
    file << m_cell_width_phi[layer];
    file << ", ";
    file << m_mean_weight[layer]; //here we write all, for validation
  }
  
  file << "\n"  ;  // to separate between the events 
}

void RunOnFCSHits::WriteValidationG4HitsCsvFile(std::ofstream&  file){
  file << m_g4hit_Etot  << ", " << m_phiMod << ", " << m_trueEta;  
  for (auto element : m_inputs.m_binsInLayers){
    int layer = element.first;
    //std::cout<<layer<<std::endl;
    
    file << ", ";
    file << m_g4hit_EtotLayer[layer];
    file << ", ";
    file << m_mean_weight[layer]; //here we write all, for validation
  }
  
  file << "\n"  ;  // to separate between the events 
}

void RunOnFCSHits::WriteValidationHitsCsvFile(std::ofstream&  file){
  file << m_hit_Etot  << ", " << m_phiMod << ", " << m_trueEta;  
  for (auto element : m_inputs.m_binsInLayers){
    int layer = element.first;
    //std::cout<<layer<<std::endl;
    
    file << ", ";
    file << m_hit_EtotLayer[layer];
    file << ", ";
    file << m_mean_weight[layer]; //here we write all, for validation
  }
  
  file << "\n"  ;  // to separate between the events 
}

void RunOnFCSHits::GetCellsCoordinatesFromGeometry(){
  TFile* input = TFile::Open("Geometry-ATLAS-R3S-2021-03-00-00.root");
  TTree* tree = (TTree*)input->Get("ATLAS-R3S-2021-03-00-00");
  int nentries = tree->GetEntries();

  tree->SetBranchAddress("calosample", &m_cell_layer);
  tree->SetBranchAddress("identifier", &m_cell_identifier);
  tree->SetBranchAddress("eta_raw",    &m_cell_eta_raw);
  tree->SetBranchAddress("phi_raw",    &m_cell_phi_raw);
  tree->SetBranchAddress("phi",        &m_cell_phi);
  tree->SetBranchAddress("r_raw",      &m_cell_r_raw);

  for (int icell = 0; icell < nentries; icell++) {
    tree->GetEntry(icell);

    m_cells_eta_raw[m_cell_identifier] = m_cell_eta_raw;
    m_cells_phi_raw[m_cell_identifier] = m_cell_phi_raw;
    m_cells_phi[m_cell_identifier] = m_cell_phi;
    m_cells_r_raw[m_cell_identifier] = m_cell_r_raw;

    //if (icell<100)
    //  std::cout<<m_cell_phi_raw << " " << m_cell_phi <<std::endl;

    m_cell_coordinates[m_cell_layer].push_back(std::make_pair(m_cell_eta_raw, m_cell_phi_raw));
    m_cell_identifiers[m_cell_layer].push_back(m_cell_identifier);
  }
}

Long64_t RunOnFCSHits::findImpactCell(int layer, float eta, float phi) {
  std::vector<float> distance;
  int index = 0;

  for (auto xy : m_cell_coordinates[layer]) {
    float deta = xy.first - eta;
    float dphi = xy.second - phi;
    float d = deta * deta + dphi * dphi;
    distance.push_back(d);
    //std::cout<<"index: "<<index<<" cell_id: "<<m_cell_identifiers[layer][index]<<"find impact, d: "<<d<<std::endl;
    index++;
  }

  int minElementIndex = std::min_element(distance.begin(), distance.end()) - distance.begin();

  //std::cout<<"Min index: "<<minElementIndex<<std::endl;
  //std::cout<<"Id min index: "<<m_cell_identifiers[layer][minElementIndex]<<std::endl;
  return m_cell_identifiers[layer][minElementIndex];
}

void RunOnFCSHits::Run() {
  std::cout<<"Running on directory " << m_inputs.m_inputDir << std::endl;
 
  GetCellsCoordinatesFromGeometry();

  TChain* chain = InitialiseChain();
  int nEvt = chain->GetEntries();
  Int_t eventsToProcess = std::min(nEvt,m_inputs.m_nEvents); 
  std::cout<<"Requested "<<m_inputs.m_nEvents<<" events, will run on "<<eventsToProcess<<" events (if less it's because there are fewer events then requested)"<<std::endl;  
  
  if (m_inputs.m_saveRootFile){    
    std::cout<<"Root files are being saved"<<std::endl;

    TString outputRootDir = Form("%s/rootFiles/pid%d/eta_%d_%d/",m_inputs.m_outputDir.c_str(),m_inputs.m_pid, m_inputs.m_etamin, m_inputs.m_etamax); 
    gSystem->mkdir(outputRootDir,kTRUE);

    TFile* output = new TFile(outputRootDir + m_outFileName + ".root","RECREATE");
    output->cd();
    RunOnEvents(chain, eventsToProcess);

    //Now that multiple file can be produced, the TGraph must be created at a later stage, after the files are merged
    //TGraphErrors* graph = DefineTGraphEPhiMod();
    //graph->Write();
 
    output->Write();
    output->Close();

   }
   else{
    std::cout<<"Root files are NOT being saved"<<std::endl;
    RunOnEvents(chain, eventsToProcess);
   }
}



