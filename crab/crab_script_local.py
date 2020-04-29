#!/usr/bin/env python
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

from  PhysicsTools.NanoAODTools.postprocessing.examples.exampleModule import *
from  PhysicsTools.NanoAODTools.postprocessing.examples.vbswwh_skim import *
from  PhysicsTools.NanoAODTools.postprocessing.examples.vbswwh_genparticles import *

from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *
from  PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.muonScaleResProducer import *


#p=PostProcessor(".",inputFiles(),"Jet_pt>200",modules=[exampleModuleConstr()],provenance=True,fwkJobReport=True,jsonInput=runsAndLumis())

selection='''(Sum$(Electron_pt > 18 && abs(Electron_eta)<2.5) >= 1  || Sum$(Muon_pt > 18 && abs(Muon_eta<2.4)) >= 1)&& Entry$ < 1000'''

files=["/scratch/lgiannini/FE7F7C99-F9B1-7F49-A767-193CCAFB4DF7.root"]


PrefireCorr2017 = lambda : PrefCorr('L1prefiring_jetpt_2017BtoF.root', 'L1prefiring_jetpt_2017BtoF', 'L1prefiring_photonpt_2017BtoF.root', 'L1prefiring_photonpt_2017BtoF')
jmeCorrections2017MC = createJMECorrector(True, "2017", "B", "Total", False, "AK4PFchs", False)


p=PostProcessor(".",files,       
                  selection.replace('\n',''),
                  branchsel="keep_and_drop.txt",
                  outputbranchsel="keep_and_drop.txt",
                  modules=[puAutoWeight_2017(),jmeCorrections2017MC(),muonScaleRes2017(),btagSFProducer("2017","deepjet"),PrefireCorr2017(), VBSWWHModule2017(), VBSWWHGenLevelModule()],
                  provenance=True)

print p.branchsel._ops
print p.outputbranchsel._ops
p.run()

print "DONE"


#RUN ON 
#dataset=/TTJets_SingleLeptFromT_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_ext_102X_mc2017_realistic_v7-v1/NANOAODSIM

#LOCAL STUFF VS CLUSTER

#selection='''(Sum$(Electron_pt > 20 && Electron_mvaFall17V2Iso_WP90) >= 2  ||
 #Sum$(Muon_pt > 20) >= 2 ||
 #Sum$(Electron_pt > 20 && Electron_mvaFall17V2Iso_WP80) >= 1   ||
 #Sum$(Muon_pt > 20 && Muon_tightId) >= 1 ||
 #(Sum$(Muon_pt > 20) == 0 && Sum$(Electron_pt > 20 && Electron_mvaFall17V2Iso_WP90) == 0 && MET_pt > 150 ) )
 #&&   ((Sum$((abs(Jet_eta)<2.5 && Jet_pt > 20 && Jet_jetId)) >= 2)||(Sum$((abs(FatJet_eta)<2.5 && FatJet_pt > 200 && FatJet_jetId)) >= 1))
#'''


#files=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/ZH_HToBB_ZToLL_M120_13TeV_powheg_pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/00000/1EAC53E9-235C-C64B-A681-FC5D3C249EE7.root"]

#p=PostProcessor(".",inputFiles(),selection.replace('\n',' '),"keep_and_drop.txt",modules=[muonScaleRes2018(),mhtVHbb(),vhbb2018_data(),kinfit()],provenance=True,fwkJobReport=True,jsonInput=runsAndLumis())
#p=PostProcessor(".",files,       selection.replace('\n',' '),"keep_and_drop.txt",modules=[muonScaleRes2018(),mhtVHbb(),vhbb2018_data(),kinfit()],provenance=True)



#more info

#p=PostProcessor(".",inputFiles(),selection.replace('\n',' '),"keep_and_drop.txt",[puAutoWeight_2017(),jmeCorrections2017MC(),jmeCorrections2017AK8MC(),muonScaleRes2017(),mhtVHbb(),btagSFProducer("2017","deepcsv"),PrefireCorr2017(),vhbb2017_vjets(),kinfit()],provenance=True,fwkJobReport=True,jsonInput=runsAndLumis())
#p=PostProcessor(".",inputFiles(),selection.replace('\n',' '),"keep_and_drop.txt",[puAutoWeight_2017(),jmeCorrections2017MC(),jmeCorrections2017AK8MC(),muonScaleRes2017(),mhtVHbb(),btagSFProducer("2017","deepcsv"),PrefireCorr2017(),vhbb2017(),kinfit()],provenance=True,fwkJobReport=True,jsonInput=runsAndLumis())
