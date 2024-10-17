HOW TO TRAIN GANs

1. Make sure the following are properly set:
   - "pids" (the particle type): set this in common/config.sh
   - "binningName" (voxel binning): set this in common/config.sh
   - "vox_dir" (the folder where the output is saved): set this in common/functions.sh
2. source /cvmfs/sft.cern.ch/lcg/views/LCG_100cuda/x86_64-centos7-gcc8-opt/setup.sh in FastCaloGAN top folder (if not already done)
3. cd model
4. source launch_V2_seed_condor.sh
