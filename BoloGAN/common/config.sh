#!/bin/bash
export ROOT="${BASH_SOURCE%/*}"
echo "${ROOT}"
echo "Loading common function file"
source "${ROOT}/functions.sh"

JobFlavour=espresso
memory=2600
MaxRuntime=$((12*60*60))

energiesEgamma="64 128 256 512 1024 2048 4096 8192 16384 32768 65536 131072 262144 524288 1048576 2097152 4194304"
#energiesEgamma="64 128 256 512 1024 262144"
energiesPion="256 512 1024 2048 4096 8192 16384 32768 65536 131072 262144 524288 1048576 2097152 4194304"
#energiesPion="1024"
energiesOtherHadrons="1024 2048 4096 8192 16384 32768 65536 131072 262144 524288 1048576 2097152 4194304"
#energiesPion="131072 262144 524288 1048576 2097152 4194304"
TotalBatchesEgamma=(1 1 1 1 1 1 1 1 1 1 1 1 2 4 8 8 8)
#TotalBatchesEgamma=(1 1 1 1 1 2)
#TotalBatchesEgamma=(1 1 10 10 10 10 10 10 10 10 10 10 20 40 80 80 80)
TotalBatchesPion=(1 1 1 1 1 1 1 1 1 2 4 8 16 16 16)
#TotalBatchesPion=(1)
TotalBatchesOtherHadrons=(1 1 1 1 1 1 1 2 4 8 16 16 16)
#TotalBatchesPion=(2 4 8 16 16 16)
etasSeedsEgamma="20 100 130 135 140 145 155 200 270 315 410"
etasSeedsPion="20 100 120 140 160 200 250 300 330 420"
rangeEgamma="Low12 High12" #rangeEgamma="Low12 High12" #rangeEgamma="UltraLow12 High12"
rangePion="All"

etasAll=$(eval echo "{0..495..5}")
etas=$etasAll

etasSeeds=("${etasSeedsEgamma}" "${etasSeedsEgamma}" "${etasSeedsPion}")

################################################################################## Options for studies ###################################################
pids="211 11 22"
etaSelection=all

pids="22"
etaSelection=all
#etas="20"

#etaSelection=noSeed

#pids="2212"
#etaSelection=all
#etas=$(eval echo "{0..495..5}")

if [ "$PARTICLE_TYPE" = "pions" ] ; then
  pids="211"
  etaSelection=all 
  etas=$(eval echo "{0..205..5}")
fi 
#etas="20"

#etaSelection=false
#etas="35" # 100"

#pids="211"
#etaSelection=false
#etas="200"
#etas="80 85 240 245 250 255 260 265 270 275"
#rangeEgamma="UltraLow12" #"UltraLow12" "High12"

#pids="22"

binningFile=binning.xml
#binningName="nominal_v2.3.1" #"nominal_v1_highstat" #"nominal_v2.1" #"nominal_v1_highstat" #
#binningName="nominal_v2.4.0" #"nominal_v1_highstat" #"nominal_v2.1" #"nominal_v1_highstat" #
#binningName="nominal_v2.4.1" #"nominal_v1_highstat" #"nominal_v2.1" #"nominal_v1_highstat" #
binningName="caloChallengeHighStats"
#binningName="nominal_v2.3" #"nominal_v1_highstat" #"nominal_v2.1" #"nominal_v1_highstat" #
SetVoxelisationDir
