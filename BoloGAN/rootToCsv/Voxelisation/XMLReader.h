#ifndef XMLReader_h
#define XMLReader_h

#include <string>
#include <map>
#include <vector>

#include <libxml/xmlmemory.h>
#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/xmlreader.h>
#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>

#include "InputVoxelisationParameters.h"

#include "TH2.h"

class XMLReader{
  public: 
  
  XMLReader(std::string binningFileName, InputVoxelisationParameters* inputs);
  
  private:
  const std::string m_binningFileName;
  InputVoxelisationParameters* m_inputs;
  
  double m_minAlpha;
  
  void DefineHisto(xmlNodePtr nodeLayer);
  void ReadXML();
  bool ReadBooleanAttribute(std::string name, xmlNodePtr node);
  void SetRangeForAlpha();
  TH2D* DefineHistoFromEdges(xmlNodePtr nodeLayer, std::string name, int binsInAlpha);
  TH2D* DefineHistoFromBinsAndRange(xmlNodePtr nodeLayer, std::string name, int binsInAlpha);
  void DefineHistoPolarCoordinates(xmlNodePtr nodeLayer);
  void DefineHistoCartesianCoordinates(xmlNodePtr nodeLayer);
  TH2D* DefineHistoCartesianFromSingleEdge(xmlNodePtr nodeLayer, std::string name);
  TH2D* DefineHistoCartesianFromTwoEdges(xmlNodePtr nodeLayer, std::string name);
  std::vector<double> GetEdges(xmlNodePtr nodeLayer, std::string name);


};

#endif