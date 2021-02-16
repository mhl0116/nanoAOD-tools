#from WMCore.Configuration import Configuration
#from CRABClient.UserUtilities import config #getUsernameFromSiteDB
from CRABClient.UserUtilities import config as Configuration

version="__v5"

import os 
base = os.environ["CMSSW_BASE"]

config = Configuration()

config.section_("General")
config.General.requestName = 'skimNano-Hggselection'
config.General.transferLogs = True
 
config.General.workArea = base+'/..'

config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script_ggOnly.sh'
#config.JobType.scriptArgs= "foo"
# hadd nano will not be needed once nano tools are in cmssw
config.JobType.inputFiles = ['crab_script_ggOnly.py', '../scripts/haddnano.py', 'keep_and_drop.txt']
config.JobType.sendPythonFolder = True

config.JobType.allowUndistributedCMSSW = True #shouldn't be necessary

config.section_("Data")
#config.Data.inputDataset = '/DYJetsToLL_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM'
#config.Data.inputDBS = 'phys03'
#config.Data.inputDBS = 'global'


#need to run on local files
config.Data.userInputFiles = ['/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_1.root',
                              '/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_2.root',
                              '/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_3.root',
                              '/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_4.root',
                              '/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_5.root',
                              '/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_6.root',
                              '/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_7.root',
                              '/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_8.root',
                              '/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_9.root',
                              '/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_10.root',
                              '/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_11.root',
                              '/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/test_nanoaod_12.root',
                             ] #override

config.Data.outputPrimaryDataset = "HHggtautau_2018_private" #override

config.Data.splitting = 'FileBased'
#config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 15
config.Data.totalUnits = 10 #override

config.Data.outLFNDirBase = '/store/user/legianni/skimNano-Hggselection' # cannot getUsernameFromSiteDB
config.Data.publication = False
config.Data.outputDatasetTag = 'skimNano-Hggselection'+version


config.section_("Site")
config.Site.storageSite = "T2_US_UCSD"
config.Site.whitelist = ["T2_US_UCSD"] # i know where the files are!!!!

from CRABAPI.RawCommand import crabCommand

#from https://github.com/cmstas/HggAnalysisDev/tree/main/Skimming
import sys
sys.path.append(base+"/..//HggAnalysisDev/Skimming")
from sa import *
from allsamples import allsamples

counter=0

opds={}

for sample in allsamples:
  
    path=""
    
    if sample in mc16:
      config.JobType.scriptArgs=["arg=mc16"] #it seems this is not working without the = sign!!!
      path=mc16[sample]
      opd=sample.split("RunII")[0].split("private")[0]+"private_mc16"
    if sample in mc17:
      config.JobType.scriptArgs=["arg=mc17"]
      path=mc17[sample]
      opd=sample.split("RunII")[0].split("private")[0]+"private_mc17"
    if sample in mc18:
      config.JobType.scriptArgs=["arg=mc18"]
      path=mc18[sample]
      opd=sample.split("RunII")[0].split("private")[0]+"private_mc18"
    if sample in data16:
      config.JobType.scriptArgs=["arg=data16"]
      path=data16[sample]
      opd=sample.split("-")[0]+"_private_data16"
    if sample in data17:
      config.JobType.scriptArgs=["arg=data17"]
      path=data17[sample]
      opd=sample.split("-")[0]+"_private_data17"
    if sample in data18:
      config.JobType.scriptArgs=["arg=data18"]
      path=data18[sample]
      opd=sample.split("-")[0]+"_private_data18"

    if opd in opds:
      opds[opd]+=1
      opd=opd+"_"+str(opds[opd])
      
    else:
      opds[opd]=1
    print opd
    
    # output primary dataset is necessary when working with private input
    config.Data.outputPrimaryDataset=opd
    
    #get files - it works at ucsd
    files=os.listdir(path)
    for i in range(len(files)):
      files[i]=path.replace("/hadoop/cms", "")+"/"+files[i]
    
    
    config.Data.userInputFiles=files
    config.Data.totalUnits = len(files)
    
    config.General.requestName = 'skimNano-Hggselection'+sample[0:30].replace(".","")+"--"+str(counter)
    
    print "Submitting "+ sample, "nfiles ", len(files), "found at",  files[0:1], " extra ARG ", config.JobType.scriptArgs
    #print config
    crabCommand('submit', config = config, dryrun = False) ## dryrun = True for local test
    print "DONE"
    
    counter+=1
    
    #break

