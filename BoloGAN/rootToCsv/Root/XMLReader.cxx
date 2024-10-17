#include "XMLReader.h"

#include <iostream>
#include <sstream>

#include "TMath.h"
   
XMLReader::XMLReader(std::string binningFileName, InputVoxelisationParameters* inputs) : 
                     m_binningFileName(binningFileName), 
                     m_inputs(inputs) {
                           
  ReadXML();
}

void XMLReader::SetRangeForAlpha(){
  if (m_inputs->m_symmetriseAlpha)
    m_minAlpha = 0;
  else
    m_minAlpha = -TMath::Pi();

}

void XMLReader::ReadXML(){   
   std::cout<<"Opening XML file: "<<m_binningFileName<<std::endl;
   xmlDocPtr doc = xmlParseFile( m_binningFileName.c_str() );
   for( xmlNodePtr nodeRoot = doc->children; nodeRoot != NULL; nodeRoot = nodeRoot->next) {
      if (xmlStrEqual( nodeRoot->name, BAD_CAST "Bins" )) {
         m_inputs->m_isPolar = ReadBooleanAttribute( "isPolar", nodeRoot);
         m_inputs->m_mergeAlphaBinsInFirstRBin = ReadBooleanAttribute( "mergeAlphaBinsInFirstRBin", nodeRoot);
         m_inputs->m_optimiseAlphaBins = ReadBooleanAttribute( "optimisedAlphaBins", nodeRoot);

         for( xmlNodePtr nodeParticle = nodeRoot->children; nodeParticle != NULL; nodeParticle = nodeParticle->next ) {
            if (xmlStrEqual( nodeParticle->name, BAD_CAST "Particle" )) {
               int nodePid = atof( (const char*) xmlGetProp( nodeParticle, BAD_CAST "pid" ) );
               for( xmlNodePtr nodeBin = nodeParticle->children; nodeBin != NULL; nodeBin = nodeBin->next ) {
                  if (xmlStrEqual( nodeBin->name, BAD_CAST "Bin" )) {
                     int nodeEtaMin = atof( (const char*) xmlGetProp( nodeBin, BAD_CAST "etaMin" ) );
                     int nodeEtaMax = atof( (const char*) xmlGetProp( nodeBin, BAD_CAST "etaMax" ) );

                     if(nodePid == m_inputs->m_pid_xml && nodeEtaMin <= m_inputs->m_etamin && nodeEtaMax >= m_inputs->m_etamax)
                     {         
                        std::cout<<"Using bining for eta in region "<< nodeEtaMin<< "<=|eta|<=" << nodeEtaMax <<std::endl;
                        m_inputs->m_symmetriseAlpha = ReadBooleanAttribute( "symmetriseAlpha", nodeParticle);;
                        SetRangeForAlpha();
                        for( xmlNodePtr nodeLayer = nodeBin->children; nodeLayer != NULL; nodeLayer = nodeLayer->next ) {
                           if( xmlStrEqual( nodeLayer->name, BAD_CAST "Layer" ) ) {
                             DefineHisto(nodeLayer);
                           }          
                        }
                     }
                  }         
               }
            }
         }
      }
   }
   
   std::cout<<"Done XML file"<<std::endl;
   std::cout<<"Summary of TH2F file"<<std::endl;
   for (int i = 0; i<24; i++){
      std::cout<<"Layer "<< i << " " << m_inputs->m_binsInLayers[i]->GetNbinsX() *  m_inputs->m_binsInLayers[i]->GetNbinsY()<<std::endl;
   }     
}

bool XMLReader::ReadBooleanAttribute(std::string name, xmlNodePtr node){
   std::cout<<"Retrieving "<<name<<std::endl;
   std::string attribute = (const char*) xmlGetProp( node, BAD_CAST name.c_str() );
   bool value = attribute == "true" ? true : false; 
   std::cout<<name<<": "<<value<<std::endl;
   return value;
}

void XMLReader::DefineHisto(xmlNodePtr nodeLayer){
  if (m_inputs->m_isPolar){
    DefineHistoPolarCoordinates(nodeLayer);
  }
  else{
    DefineHistoCartesianCoordinates(nodeLayer);
  }
}  

void XMLReader::DefineHistoPolarCoordinates(xmlNodePtr nodeLayer)
{
  int binsInAlpha = atof( (const char*) xmlGetProp( nodeLayer, BAD_CAST "n_bin_alpha" ) );
  int layer = atof( (const char*) xmlGetProp( nodeLayer, BAD_CAST "id" ) );
  std::string name = "hist_layer" + std::to_string(layer);
  
  std::cout <<"layer count: " << name ; 
  std::cout<<" Layer: "<<layer<<" binsInAlpha: "<<binsInAlpha<<std::endl;
  
  if( xmlHasProp( nodeLayer, BAD_CAST "r_edges" ) ) {
     m_inputs->m_binsInLayers[layer] = DefineHistoFromEdges(nodeLayer, name, binsInAlpha);
  }
  else{
     m_inputs->m_binsInLayers[layer] = DefineHistoFromBinsAndRange(nodeLayer, name, binsInAlpha);
  }
}

TH2D* XMLReader::DefineHistoFromEdges(xmlNodePtr nodeLayer, std::string name, int binsInAlpha){
  std::vector<double> edges = GetEdges(nodeLayer, "r_edges");
  
  int nbins = std::max((int)(edges.size()-1),1 ); //prevent warning
  
  return new TH2D(name.c_str(), name.c_str(), nbins, &edges[0], binsInAlpha, m_minAlpha, TMath::Pi());
}

TH2D* XMLReader::DefineHistoFromBinsAndRange(xmlNodePtr nodeLayer, std::string name, int binsInAlpha){
  int nBins = atoi( (const char*) xmlGetProp( nodeLayer, BAD_CAST "nbins" ) );
  std::cout<<" bins r: "<< nBins<<std::endl;
  double min = atof( (const char*) xmlGetProp( nodeLayer, BAD_CAST "r_min" ) );
  std::cout<<" min_r: "<<min<<std::endl;
  double max = atof( (const char*) xmlGetProp( nodeLayer, BAD_CAST "r_max" ) );                                 
  std::cout<<" max_r: " <<max<<std::endl;
  return new TH2D(name.c_str(), name.c_str(), nBins, min, max, binsInAlpha, m_minAlpha, TMath::Pi());
}

void XMLReader::DefineHistoCartesianCoordinates(xmlNodePtr nodeLayer)
{
  int layer = atof( (const char*) xmlGetProp( nodeLayer, BAD_CAST "id" ) );
  std::string name = "hist_layer" + std::to_string(layer);
  
  std::cout <<"layer count: " << name ; 
  
  if( xmlHasProp( nodeLayer, BAD_CAST "eta_phi_edges" ) ) {
     m_inputs->m_binsInLayers[layer] = DefineHistoCartesianFromSingleEdge(nodeLayer, name);
  }
  else{
     m_inputs->m_binsInLayers[layer] = DefineHistoCartesianFromTwoEdges(nodeLayer, name);
  }
}

TH2D* XMLReader::DefineHistoCartesianFromSingleEdge(xmlNodePtr nodeLayer, std::string name){
  std::vector<double> edges = GetEdges(nodeLayer, "eta_phi_edges");
  
  int nbins = std::max((int)(edges.size()-1),1 ); //prevent warning
  
  return new TH2D(name.c_str(), name.c_str(), nbins, &edges[0], nbins, &edges[0]);
}

std::vector<double> XMLReader::GetEdges(xmlNodePtr nodeLayer, std::string name){
  std::vector<double> edges;
  std::string s( (const char*)xmlGetProp( nodeLayer, BAD_CAST name.c_str() ) );

  std::istringstream ss(s);
  std::string token;

  while(std::getline(ss, token, ',')) {
     edges.push_back(atof( token.c_str() ));
  }

  std::cout<<"Edges: "<< s<<std::endl;
  
  return edges;
}

TH2D* XMLReader::DefineHistoCartesianFromTwoEdges(xmlNodePtr nodeLayer, std::string name){
  std::vector<double> eta_edges = GetEdges(nodeLayer, "eta_edges");
  std::vector<double> phi_edges = GetEdges(nodeLayer, "phi_edges");
  
  int nbins_eta = std::max((int)(eta_edges.size()-1),1 ); //prevent warning
  int nbins_phi = std::max((int)(phi_edges.size()-1),1 ); //prevent warning
  
  return new TH2D(name.c_str(), name.c_str(), nbins_eta, &eta_edges[0], nbins_phi, &phi_edges[0]);
}


