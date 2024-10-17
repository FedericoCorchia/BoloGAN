Sim_tf.py --simulator 'FastCaloGAN' \
--geometryVersion 'default:ATLAS-R2-2016-01-00-01_VALIDATION' \
--inputEVNTFile valid1.410000.PowhegPythiaEvtGen_P2012_ttbar_hdamp172p5_nonallhad.evgen.EVNT.e4993/EVNT.08166201._000001.pool.root.1 \
--outputHITSFile ttbar.HITs.pool.root \
--maxEvents 100 \
--preExec 'EVNTtoHITS:from G4AtlasApps.SimFlags import simFlags;simFlags.VertexFromCondDB.set_Value_and_Lock(False);from ISF_FastCaloSimServices.ISF_FastCaloSimJobProperties import ISF_FastCaloSimFlags;ISF_FastCaloSimFlags.FastCaloGANInputFolderName="/afs/cern.ch/user/m/mfauccig/eos/VoxalisationOutputs/nominal/GAN_michele_normE_MaxE/input_for_service_new/";ISF_FastCaloSimFlags.DNNInputArchitecture="FastCaloGAN"' \
--postExec 'svcMgr.MessageSvc.Format="% F%50W%S%7W%R%T %0W%M";svcMgr.MessageSvc.defaultLimit = 100000;svcMgr.ISF_DNNCaloSimSvc.OutputLevel=INFO;' \


time Reco_tf.py --inputHITSFile "ttbar.HITs.pool.root" \
--outputESDFile "ESD.ttbar_FastCaloGAN.pool.root" \
--outputAODFile "xAOD.ttbar_FastCaloGAN.pool.root" \
--maxEvents=-1 \
--preExec "rec.doTrigger=False; " \
--autoConfiguration everything

rm tmp.RDO

#cp xAOD.pion_E2097152_eta_20_25_FastCaloGAN.pool.root /eos/atlas/atlascerngroupdisk/proj-simul/OutputSamples/FastCaloGAN_v1

#ISF_FastCaloSimFlags.RunSingleGAN=True;\
