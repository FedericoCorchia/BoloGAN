GAN_type="E" #E_only_conditioning E_normabsPhiMod_abseta

for binningName in test_binning_2021_absphiMod_abseta_PerEventFromCellEnergy test_binning_2021_absphiMod_abseta_PerEventFromG4HitsEnergy test_binning_2021_absphiMod_abseta_PerCellFromG4HitsEnergy test_binning_2021_absphiMod_abseta_PerCellFromCellEnergy #test_binning_2021_absphiMod test_binning_2021_alphaSim_absphiMod test_binning_2021_absphiMod_highStat
do
  for samplesRange in High12_OPT_${GAN_type} Mid1218_OPT_${GAN_type} #All_OPT_${GAN_type} Low12_OPT_${GAN_type} High12_OPT_${GAN_type} Mid1218_OPT_${GAN_type} High18_OPT_${GAN_type} 
  do
    source make_rootFiles_GAN.sh
    source make_plots_gan_and_comparison.sh
  done
done
