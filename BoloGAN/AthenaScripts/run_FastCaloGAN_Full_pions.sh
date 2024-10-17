Sim_tf.py --simulator 'G4FastCaloDNN' \
--geometryVersion 'default:ATLAS-R2-2016-01-00-01_VALIDATION' \
--inputEVNTFile EVNT.pion.E2097152_caloSurf.pool.root.1 \
--outputHITSFile pion.G4FastCalo_light.HITs.pool.root \
--maxEvents 1000 \
--preExec 'EVNTtoHITS:from G4AtlasApps.SimFlags import simFlags;simFlags.VertexFromCondDB.set_Value_and_Lock(False);\
from ISF_FastCaloSimServices.ISF_FastCaloSimJobProperties import ISF_FastCaloSimFlags;\
ISF_FastCaloSimFlags.FastCaloGANInputFolderName=".";\
ISF_FastCaloSimFlags.DNNInputArchitecture="FastCaloGAN"' \
--postExec 'svcMgr.MessageSvc.Format="% F%50W%S%7W%R%T %0W%M";svcMgr.MessageSvc.defaultLimit = 1000;svcMgr.ISF_DNNCaloSimSvc.OutputLevel=VERBOSE;' \


time Reco_tf.py --inputHITSFile "pion.G4FastCalo_light.HITs.pool.root" \
--outputESDFile "ESD.pion_E2097152_eta_20_25_FastCaloGAN.pool.root" \
--outputAODFile "xAOD.pion_E2097152_eta_20_25_FastCaloGAN.pool.root" \
--maxEvents=-1 \
--preExec "rec.doTrigger=False; " \
--autoConfiguration everything

rm tmp.RDO

cp xAOD.pion_E2097152_eta_20_25_FastCaloGAN.pool.root /eos/atlas/atlascerngroupdisk/proj-simul/OutputSamples/FastCaloGAN_v1

#ISF_FastCaloSimFlags.RunSingleGAN=True;\
