import sys, os
import time
import itertools
import numpy

import argparse

from metis.Sample import DirectorySample
from metis.CondorTask import CondorTask
from metis.StatsParser import StatsParser

from samples import *

print mc17
print mc16 
print mc18


exec_path = "exec_postproc.sh"
tar_path = "../rel2.tar.gz"
hadoop_path = ""


loca="/hadoop/cms/store/user/hmei/nanoaod_runII/HHggtautau/HHggtautau_Era2018_private_v2_20201005/"


a={


#"HHggtautau":"HHggtautau_Era2018_private_v2_20201005/"    ,
"DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8_18" : "DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2_MINIAODSIM_v0.6_20201021/",
"DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_18" : "DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"DiPhotonJetsBox_M40_80-Sherpa_18" : "DiPhotonJetsBox_M40_80-Sherpa_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"DiPhotonJetsBox_MGG-80toInf_13TeV-Sherpa_18" : "DiPhotonJetsBox_MGG-80toInf_13TeV-Sherpa_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"GJets_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8_18" : "GJets_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18MiniAOD-4cores5k_102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"GJets_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_18" : "GJets_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"GJets_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_18" : "GJets_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"GJets_HT-40To100_TuneCP5_13TeV-madgraphMLM-pythia8_18" : "GJets_HT-40To100_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"GJets_HT-600ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_18" : "GJets_HT-600ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v2_MINIAODSIM_v0.6_20201021/",
"THQ_ctcvcp_HToGG_M125_TuneCP5_13TeV-madgraph-pythia8_18" : "THQ_ctcvcp_HToGG_M125_TuneCP5_13TeV-madgraph-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"TTGG_0Jets_TuneCP5_13TeV_amcatnlo_madspin_pythia8_18" : "TTGG_0Jets_TuneCP5_13TeV_amcatnlo_madspin_pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2_MINIAODSIM_v0.6_20201021/",
"TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_18" : "TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8_18" : "TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v2_MINIAODSIM_v0.6_20201021/",
"TTJets_TuneCP5_13TeV-madgraphMLM-pythia8_18" : "TTJets_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_18" : "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_18_2" : "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18MiniAOD-NZSFlatPU28to62_102X_upgrade2018_realistic_v15_ext1-v1_MINIAODSIM_v0.6_20201021/",
"TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_18" : "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_18" : "TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v2_MINIAODSIM_v0.6_20201021/",
"TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_18" : "TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v2_MINIAODSIM_v0.6_20201021/",
"VBFHToGG_M125_13TeV_amcatnlo_pythia8_18" : "VBFHToGG_M125_13TeV_amcatnlo_pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_18" : "VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"WGToLNuG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_18" : "WGToLNuG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v1_MINIAODSIM_v0.6_20201021/",
"WGToLNuG_TuneCP5_13TeV-madgraphMLM-pythia8_18" : "WGToLNuG_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"WW_TuneCP5_13TeV-pythia8_18" : "WW_TuneCP5_13TeV-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2_MINIAODSIM_v0.6_20201021/",
"WZ_TuneCP5_13TeV-pythia8_18" : "WZ_TuneCP5_13TeV-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v3_MINIAODSIM_v0.6_20201021/",
"ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_18" : "ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v2_MINIAODSIM_v0.2_20201021/",
"ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_18_2" : "ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v2_MINIAODSIM_v0.3_20201021/",
"ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_18_3" : "ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v2_MINIAODSIM_v0.6_20201021/",
"ZZ_TuneCP5_13TeV-pythia8_18" : "ZZ_TuneCP5_13TeV-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2_MINIAODSIM_v0.6_20201021/",
"ggZH_HToGG_ZToLL_M125_TuneCP5_13TeV-powheg-pythia8_18" : "ggZH_HToGG_ZToLL_M125_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",
"tZq_ll_4f_ckm_NLO_TuneCP5_13TeV-madgraph-pythia8_18" : "tZq_ll_4f_ckm_NLO_TuneCP5_13TeV-madgraph-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v2_MINIAODSIM_v0.6_20201021/",
"ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_18" : "ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_MINIAODSIM_v0.6_20201021/",

    
"DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8_17" : "DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_17" : "DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_17" : "DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14_ext1-v1_MINIAODSIM_v0.6_20201021/",
"DiPhotonJetsBox1BJet_MGG-80toInf_13TeV-Sherpa_17" : "DiPhotonJetsBox1BJet_MGG-80toInf_13TeV-Sherpa_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"DiPhotonJetsBox2BJets_MGG-80toInf_13TeV-Sherpa_17" : "DiPhotonJetsBox2BJets_MGG-80toInf_13TeV-Sherpa_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"DiPhotonJetsBox_M40_80-Sherpa_17" : "DiPhotonJetsBox_M40_80-Sherpa_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_MINIAODSIM_v0.6_20201021/",
"DiPhotonJetsBox_MGG-80toInf_13TeV-Sherpa_17" : "DiPhotonJetsBox_MGG-80toInf_13TeV-Sherpa_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_MINIAODSIM_v0.6_20201021/",
"DiPhotonJets_MGG-80toInf_13TeV_amcatnloFXFX_pythia8_17" : "DiPhotonJets_MGG-80toInf_13TeV_amcatnloFXFX_pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"GJets_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8_17" : "GJets_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"GJets_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_17" : "GJets_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"GJets_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_17" : "GJets_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"GJets_HT-40To100_TuneCP5_13TeV-madgraphMLM-pythia8_17" : "GJets_HT-40To100_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_MINIAODSIM_v0.6_20201021/",
"GJets_HT-600ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_17" : "GJets_HT-600ToInf_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_MINIAODSIM_v0.6_20201021/",
"GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_17" : "GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_MINIAODSIM_v0.6_20201021/",
"QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8_17" : "QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"QCD_Pt-30toInf_DoubleEMEnriched_MGG-40to80_TuneCP5_13TeV_Pythia8_17" : "QCD_Pt-30toInf_DoubleEMEnriched_MGG-40to80_TuneCP5_13TeV_Pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8_17" : "QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"THQ_ctcvcp_HToGG_M125_13TeV-madgraph-pythia8_TuneCP5_17" : "THQ_ctcvcp_HToGG_M125_13TeV-madgraph-pythia8_TuneCP5_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"THW_ctcvcp_HToGG_M125_13TeV-madgraph-pythia8_TuneCP5_17" : "THW_ctcvcp_HToGG_M125_13TeV-madgraph-pythia8_TuneCP5_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"TTGG_0Jets_TuneCP5_13TeV_amcatnlo_madspin_pythia8_17" : "TTGG_0Jets_TuneCP5_13TeV_amcatnlo_madspin_pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_MINIAODSIM_v0.6_20201021/",
"TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_17" : "TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_17_2" : "TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1_MINIAODSIM_v0.6_20201021/",
"TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8_17" : "TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_17" : "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_17" : "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_17" : "TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_17_2" : "TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_MINIAODSIM_v0.6_20201021/",
"TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_17" : "TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_17_2" : "TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_MINIAODSIM_v0.6_20201021/",
"VBFHToGG_M125_13TeV_amcatnlo_pythia8_17" : "VBFHToGG_M125_13TeV_amcatnlo_pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_17" : "VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"WGToLNuG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_17" : "WGToLNuG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v3_MINIAODSIM_v0.6_20201021/",
"WGToLNuG_TuneCP5_13TeV-madgraphMLM-pythia8_17" : "WGToLNuG_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"WW_TuneCP5_13TeV-pythia8_17" : "WW_TuneCP5_13TeV-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"WZ_TuneCP5_13TeV-pythia8_17" : "WZ_TuneCP5_13TeV-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
"ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_17" : "ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v3_MINIAODSIM_v0.6_20201021/",
"ZZ_TuneCP5_13TeV-pythia8_17" : "ZZ_TuneCP5_13TeV-pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v2_MINIAODSIM_v0.6_20201021/",
"ggZH_HToGG_ZToLL_M125_13TeV_powheg_pythia8_17" : "ggZH_HToGG_ZToLL_M125_13TeV_powheg_pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_MINIAODSIM_v0.6_20201021/",
"ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_17" : "ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1_MINIAODSIM_v0.6_20201021/",
    
}

#a={


#"HHggtautau":"HHggtautau_Era2018_private_v2_20201005/"  }

#a={ "HHggtautau":"HHggtautau_Era2018_private_v2_20201005",}

sample = DirectorySample(dataset = "HHggtautau_Era2018_private", location =loca )


for key in a:
    
    sample = DirectorySample(dataset = key, location ="/hadoop/cms/store/user/hmei/nanoaod_runII/HHggtautau/"+a[key] )

    files=[f.name for f in sample.get_files()]

    print "/hadoop/cms/store/user/hmei/nanoaod_runII/HHggtautau/"+a[key]
    print (a[key] in mc16)
    print (a[key] in mc17)
    print (a[key] in mc18)
    #quit()

    output_name="test_nanoaodSkim.root"
    job_tag="___v3"
    job_args="1"
    
    if a[key] in mc18:
        job_args="mc18"
    elif a[key] in mc17:
        job_args="mc17" 
    elif a[key] in mc16:
        job_args="mc16" 
    else:
        quit()
        
    task = CondorTask(
                sample = sample,
                open_dataset = False,
                flush = True,
                files_per_output = 10,
                #files_per_output = info["fpo"] if args.selection == 1 or args.selection == 3 else info["fpo"] * 3,
                output_name = output_name,
                tag = job_tag,
                cmssw_version = "CMSSW_10_2_22", # doesn't do anything
                arguments = job_args,
                executable = exec_path,
                tarfile = tar_path,
                #condor_submit_params = {"sites" : "T2_US_UCSD"},
            condor_submit_params = {"sites" : "T2_US_UCSD","container":"/cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel7-m20201010"}

                )



    attrs = vars(task)
    # now dump this in some way or another
    print(', '.join("%s: %s" % item for item in attrs.items()))

    task.process()

    total_summary = {}

    total_summary[task.get_sample().get_datasetname()] = task.get_task_summary()

    # Web dashboard
    StatsParser(data=total_summary, webdir="~/public_html/rnew/").do()
    os.system("chmod -R 755 ~/public_html/rnew/")
    
    print("Sleeping 1000 seconds ...")
    time.sleep(1000)

