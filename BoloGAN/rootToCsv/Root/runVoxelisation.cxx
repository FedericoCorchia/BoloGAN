#include <iostream>   
#include <sstream>   
#include <string>   

#include "XMLReader.h"
#include "RunOnFCSHits.h"

bool ToBool(char *arg){
   //std::cout<<"Argument for boolean: "<<arg<<std::endl;
   std::stringstream ss(arg);
   bool b;
  
   if(!(ss >> std::boolalpha >> b)) {
      std::cerr << "Incorrect argument provided.\n";
   }
  
   return b;
}

int main(int nArg, char **arg) {
  
   int numberOfParametersToExpect = 14;
   if(nArg != numberOfParametersToExpect){ //start from zero which is the executable
      std::cout << "ERROR: Wrong number of input parameters!" << std::endl;
      std::cout << nArg << " used instead of " << numberOfParametersToExpect << std::endl;
      for (int i = 0; i < nArg; ++i){
         std::cout<<i<<": "<<arg[i]<<std::endl;
      }
		return -1;
	}

   InputVoxelisationParameters inputs = InputVoxelisationParameters();
   inputs.m_pid=std::stoi(arg[1]);
   inputs.m_energy=std::stoi(arg[2]);
   inputs.m_etamin=std::stoi(arg[3]);
   inputs.m_etamax = inputs.m_etamin + 5;
   inputs.m_nEvents=std::stoi(arg[4]);
   inputs.m_useFiles=ToBool(arg[5]);
   if (inputs.m_useFiles){
      inputs.m_inputFileName=arg[6];
   }
   else{
      inputs.m_inputDir=arg[6];
   }
   inputs.m_binningFileName=arg[7];
   inputs.m_outputDir=arg[8];
   inputs.m_energyCorrectionScheme=arg[9];
   inputs.m_saveRootFile=ToBool(arg[10]);
   inputs.m_useHitEnergy=ToBool(arg[11]);
   inputs.m_batchNum=std::stoi(arg[12]);
   inputs.m_TotalBatches=std::stoi(arg[13]);

   inputs.Validate();
  
   std::string xmlFullFileName = inputs.m_outputDir +"/"+inputs.m_binningFileName;

   XMLReader xmlReader(xmlFullFileName, &inputs);
   inputs.Print();

   std::cout<<"Relevant layers: "<<inputs.m_binsInLayers.size()<<std::endl;

   RunOnFCSHits loop(inputs);
   loop.Run();
  
	return 0; 
}
