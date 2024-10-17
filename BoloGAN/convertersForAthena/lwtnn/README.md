HOW TO CONVERT MODELS INTO LWTNN

1. Make sure pids, binningName (both in common/config.sh) and vox_dir (in common/functions.sh) are properly set
2. Set pids and etas accordingly in convertersForAthena/lwtnn/make_conversion_production.sh
3. Rename OUTPUT_PATH/Baseline_PARTICLE_lwtnn/PARTICLE_SUBFOLDER_FOR_EXAMPLE_ALL_HIGH12_OR_ULTRALOW12/best_checkpoints_E/model_PARTICLE_region_1.SUFFIX into OUTPUT_PATH/Baseline_PARTICLE_lwtnn/PARTICLE_SUBFOLDER_FOR_EXAMPLE_ALL_HIGH12_OR_ULTRALOW12/best_checkpoints_E/model_PARTICLE_eta_ETAMIN_ETAMAX.SUFFIX (e.g. /eos/atlas/atlascerngroupdisk/proj-simul/AF3_Run3/VoxalisationOutputs/corchia/nominal_v2.4.0/truePions/nominal_v2.4.0/Baseline_pions_lwtnn/All/best_checkpoints_E/model_pions_region_1.index into /eos/atlas/atlascerngroupdisk/proj-simul/AF3_Run3/VoxalisationOutputs/corchia/nominal_v2.4.0/truePions/nominal_v2.4.0/Baseline_pions_lwtnn/All/best_checkpoints_E/model_pions_eta_20_25.index)
4. source /cvmfs/sft.cern.ch/lcg/views/LCG_100cuda/x86_64-centos7-gcc8-opt/setup.sh in FastCaloGAN top folder (if not already done)
5. cd convertersForAthena/lwtnn
6. source make_conversion_production.sh