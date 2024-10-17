# How To Setup and Compile the C++ Code To Run Voxelisation the First Time

DO NOT PERFORM THE GENERAL SOURCING FOR FASTCALOGAN. DO NOT DO `setupATLAS`. ONLY DO THE FOLLOWING:

From inside the rootToCsv folder:

1. `source setup.sh` (this script defines the correct environment)

2. `cmake ../` (build must be made in the rootToCsv folder and in no subfolder)

3. `make`

# How To Setup the C++ Code To Run Voxelisation After the First Time

Just do `source setup.sh` in the rootToCsv folder before running.
