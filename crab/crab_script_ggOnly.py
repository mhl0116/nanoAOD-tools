#!/usr/bin/env python
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 

#this would take care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

from  PhysicsTools.NanoAODTools.postprocessing.examples.exampleModule import *

from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *
from  PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.muonScaleResProducer import *

#gamma stuff added by us
from PhysicsTools.NanoAODTools.postprocessing.modules.common.gammaSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.gammaWeightSFProducer import *
from  PhysicsTools.NanoAODTools.postprocessing.examples.hgg_selection import *

from  PhysicsTools.NanoAODTools.postprocessing.examples.dump_object import *
from  PhysicsTools.NanoAODTools.postprocessing.examples.dump_pair import *
#very basic selection which is covered then by the actual Hgg selection and crop at 1000 evts
selection='''Sum$(Photon_pt > 18 && abs(Photon_eta)<2.5) > 1'''

#work on a local file
# a modified nanoAOD which contians extra phton features -> to be merged soon to the central stuff
files=["/hadoop/cms/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_1.root"]

#2016 modules MC
#jetmetUncertainties2016, puAutoWeight_2016, muonScaleRes2016, PrefCorr2016
PrefCorr2016 = lambda : PrefCorr("L1prefiring_jetpt_2016BtoH.root", "L1prefiring_jetpt_2016BtoH", "L1prefiring_photonpt_2016BtoH.root", "L1prefiring_photonpt_2016BtoH")

#2017 modules MC
#jetmetUncertainties2017, puAutoWeight_2017, muonScaleRes2017, PrefireCorr2017
PrefireCorr2017 = lambda : PrefCorr('L1prefiring_jetpt_2017BtoF.root', 'L1prefiring_jetpt_2017BtoF', 'L1prefiring_photonpt_2017BtoF.root', 'L1prefiring_photonpt_2017BtoF')

#2018 modules MC
#jetmetUncertainties2018, puAutoWeight_2018, muonScaleRes2018

import sys
print sys.argv

if "mc16" in sys.argv[2]:
  p = PostProcessor(".", 
                    inputFiles(), #NOT IN LOCAL
                    selection.replace('\n',''),
                    branchsel="keep_and_drop.txt",
                    outputbranchsel="keep_and_drop.txt",
                    modules=[puAutoWeight_2018(),jetmetUncertainties2018(), muonScaleRes2018(), gammaSF(), HggModule2018(), gammaWeightSF(), dumpSelectedPhotons()],
                    provenance=True,
                    fwkJobReport=True, #NOT IN LOCAL
                    jsonInput=runsAndLumis() #NOT IN LOCAL
                    )
elif "mc17" in sys.argv[2]:
  p = PostProcessor(".", 
                    inputFiles(), #NOT IN LOCAL
                    selection.replace('\n',''),
                    branchsel="keep_and_drop.txt",
                    outputbranchsel="keep_and_drop.txt",
                    modules=[puAutoWeight_2017(),jetmetUncertainties2017(), muonScaleRes2017(), PrefireCorr2017(), gammaSF(), HggModule2017(), gammaWeightSF(), dumpSelectedPhotons()],
                    provenance=True,
                    fwkJobReport=True, #NOT IN LOCAL
                    jsonInput=runsAndLumis() #NOT IN LOCAL
                    )
elif "mc18" in sys.argv[2]:
  p = PostProcessor(".", 
                    inputFiles(), #NOT IN LOCAL
                    selection.replace('\n',''),
                    branchsel="keep_and_drop.txt",
                    outputbranchsel="keep_and_drop.txt",
                    modules=[puAutoWeight_2016(),jetmetUncertainties2016(), muonScaleRes2016(), PrefCorr2016(), gammaSF(), HggModule2018(), gammaWeightSF(), dumpSelectedPhotons()],
                    provenance=True,
                    fwkJobReport=True, #NOT IN LOCAL
                    jsonInput=runsAndLumis() #NOT IN LOCAL
                    )
elif "data16" in sys.argv[2]:
  p = PostProcessor(".", 
                    inputFiles(), #NOT IN LOCAL
                    selection.replace('\n',''),
                    branchsel="keep_and_drop.txt",
                    outputbranchsel="keep_and_drop.txt",
                    modules=[muonScaleRes2018(), HggModuleData2018(), dumpSelectedPhotons()],
                    provenance=True,
                    fwkJobReport=True, #NOT IN LOCAL
                    jsonInput=runsAndLumis() #NOT IN LOCAL
                    )
elif "data17" in sys.argv[2]:
  p = PostProcessor(".", 
                    inputFiles(), #NOT IN LOCAL
                    selection.replace('\n',''),
                    branchsel="keep_and_drop.txt",
                    outputbranchsel="keep_and_drop.txt",
                    modules=[muonScaleRes2017(), HggModuleData2017(), dumpSelectedPhotons()],
                    provenance=True,
                    fwkJobReport=True, #NOT IN LOCAL
                    jsonInput=runsAndLumis() #NOT IN LOCAL
                    )
elif "data18" in sys.argv[2]:
  p = PostProcessor(".", 
                    inputFiles(), #NOT IN LOCAL
                    selection.replace('\n',''),
                    branchsel="keep_and_drop.txt",
                    outputbranchsel="keep_and_drop.txt",
                    modules=[muonScaleRes2016(), HggModuleData2016(), dumpSelectedPhotons()],
                    provenance=True,
                    fwkJobReport=True, #NOT IN LOCAL
                    jsonInput=runsAndLumis() #NOT IN LOCAL
                    )
else:
  print "bo"

#NB the gammaWeightSF needs a gg selection as of now, while gammaSF is not related to a gg pair
# as a result HggModule2018() must be run before gammaWeightSF()

# keep and drop printout
print p.branchsel._ops
print p.outputbranchsel._ops

p.run()

print("DONE")

