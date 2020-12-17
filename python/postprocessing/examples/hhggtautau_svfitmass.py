import ROOT
import array
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Object 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

import math

import os
base = os.getenv("CMSSW_BASE")
arch = os.getenv("SCRAM_ARCH")

ROOT.gROOT.ProcessLine(".L %s/lib/%s/libTauAnalysisSVfitTF.so"%(base, arch))
ROOT.gROOT.ProcessLine(".L %s/lib/%s/libTauAnalysisClassicSVfit.so"%(base, arch))
ROOT.gROOT.ProcessLine(".L %s/src/PhysicsTools/NanoAODTools/python/postprocessing/helpers//SVFitFunc.cc+"%base)

class SVFitMassProducer(Module):
    def __init__(self):

        pass
        ### ref link useful later on
        ### reduced JES uncertainties (see https://twiki.cern.ch/twiki/bin/viewauth/CMS/JECUncertaintySources#Run_2_reduced_set_of_uncertainty)
       
    def beginJob(self):
        pass
    
    def endJob(self):
        pass
    
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("tautauMass_SVFit",  "F");
        self.out.branch("tautauMassLoose_SVFit",  "F");
        self.out.branch("tautauMassAll_SVFit",  "F");
        
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    
    def analyze(self, event):
                
        """process event, return True (go to next module) or False (fail, go to next event)"""
        electrons = list(Collection(event, "Electron"))
        muons = list(Collection(event, "Muon"))   
        taus = list(Collection(event, "Tau"))
        tauHidx = getattr(event, "tauHidx") 
        tauLooseHidx = getattr(event, "tauLooseHidx")
        tauAllHidx = getattr(event, "tauAllHidx") 
        MET = Object(event, "MET")
        
        Category = getattr(event, "Category")
        Category_pairs = getattr(event, "Category_pairs")
        Category_LoosePairs = getattr(event, "Category_LoosePairs")
        Category_AllPairs = getattr(event, "Category_AllPairs")
        
        category1=Category
        category2=0
        
        tautauMass=-1
        tautauMassLoose=-1
        tautauMassAll=-1
        
        covMET_XX=MET.covXX
        covMET_XY=MET.covXY
        covMET_YY=MET.covYY
        measuredMETx=MET.pt*math.cos(MET.phi)
        measuredMETy=MET.pt*math.sin(MET.phi)
        
        index1=tauHidx[0]
        index2=tauHidx[1]
        
        if Category_pairs==3:
            tau1_pt, tau1_eta, tau1_phi, tau1_mass=taus[index1].pt,taus[index1].eta,taus[index1].phi,taus[index1].mass
            tau2_pt, tau2_eta, tau2_phi, tau2_mass=taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass
            tauDecay_mode1=taus[index1].decayMode
            tauDecay_mode2=taus[index2].decayMode
            tauDecay_mode1,tauDecay_mode2
        elif Category_pairs==2:
            tau1_pt, tau1_eta, tau1_phi, tau1_mass=electrons[index1].pt,electrons[index1].eta,electrons[index1].phi,0.51100e-3
            tau2_pt, tau2_eta, tau2_phi, tau2_mass=taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass
            tauDecay_mode1=1
            tauDecay_mode2=taus[index2].decayMode
        elif Category_pairs==1:
            tau1_pt, tau1_eta, tau1_phi, tau1_mass=muons[index1].pt,muons[index1].eta,muons[index1].phi,0.10566
            tau2_pt, tau2_eta, tau2_phi, tau2_mass=taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass
            tauDecay_mode1=1
            tauDecay_mode2=taus[index2].decayMode
            
        if Category_pairs in [1,2,3]:
            tautauMass=ROOT.SVfit_mass( measuredMETx, measuredMETy, covMET_XX, covMET_XY, covMET_YY, tauDecay_mode1, tauDecay_mode2, category1, category2, 
                            tau1_pt, tau1_eta, tau1_phi, tau1_mass, tau2_pt, tau2_eta, tau2_phi, tau2_mass )
        
        
        index1=tauLooseHidx[0]
        index2=tauLooseHidx[1]
        
        if Category_LoosePairs==3:
            tau1_pt, tau1_eta, tau1_phi, tau1_mass=taus[index1].pt,taus[index1].eta,taus[index1].phi,taus[index1].mass
            tau2_pt, tau2_eta, tau2_phi, tau2_mass=taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass
            tauDecay_mode1=taus[index1].decayMode
            tauDecay_mode2=taus[index2].decayMode
        elif Category_LoosePairs==2:
            tau1_pt, tau1_eta, tau1_phi, tau1_mass=electrons[index1].pt,electrons[index1].eta,electrons[index1].phi,0.51100e-3
            tau2_pt, tau2_eta, tau2_phi, tau2_mass=taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass
            tauDecay_mode1=1
            tauDecay_mode2=taus[index2].decayMode
        elif Category_LoosePairs==1:
            tau1_pt, tau1_eta, tau1_phi, tau1_mass=muons[index1].pt,muons[index1].eta,muons[index1].phi,0.10566
            tau2_pt, tau2_eta, tau2_phi, tau2_mass=taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass
            tauDecay_mode1=1
            tauDecay_mode2=taus[index2].decayMode
                
        if Category_LoosePairs in [1,2,3]:
            tautauMassLoose=ROOT.SVfit_mass( measuredMETx, measuredMETy, covMET_XX, covMET_XY, covMET_YY, tauDecay_mode1, tauDecay_mode2, category1, category2, 
                            tau1_pt, tau1_eta, tau1_phi, tau1_mass, tau2_pt, tau2_eta, tau2_phi, tau2_mass )
            
            
        index1=tauAllHidx[0]
        index2=tauAllHidx[1]
        
        if Category_AllPairs==3:
            tau1_pt, tau1_eta, tau1_phi, tau1_mass=taus[index1].pt,taus[index1].eta,taus[index1].phi,taus[index1].mass
            tau2_pt, tau2_eta, tau2_phi, tau2_mass=taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass
            tauDecay_mode1=taus[index1].decayMode
            tauDecay_mode2=taus[index2].decayMode
        elif Category_AllPairs==2:
            tau1_pt, tau1_eta, tau1_phi, tau1_mass=electrons[index1].pt,electrons[index1].eta,electrons[index1].phi,0.51100e-3
            tau2_pt, tau2_eta, tau2_phi, tau2_mass=taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass
            tauDecay_mode1=1
            tauDecay_mode2=taus[index2].decayMode
        elif Category_AllPairs==1:
            tau1_pt, tau1_eta, tau1_phi, tau1_mass=muons[index1].pt,muons[index1].eta,muons[index1].phi,0.10566
            tau2_pt, tau2_eta, tau2_phi, tau2_mass=taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass
            tauDecay_mode1=1
            tauDecay_mode2=taus[index2].decayMode
            
        if Category_AllPairs in [1,2,3]:
            tautauMassAll=ROOT.SVfit_mass( measuredMETx, measuredMETy, covMET_XX, covMET_XY, covMET_YY, tauDecay_mode1, tauDecay_mode2, category1, category2, 
                            tau1_pt, tau1_eta, tau1_phi, tau1_mass, tau2_pt, tau2_eta, tau2_phi, tau2_mass )
        
        
        self.out.fillBranch("tautauMass_SVFit",tautauMass)
        self.out.fillBranch("tautauMassLoose_SVFit",tautauMassLoose)
        self.out.fillBranch("tautauMassAll_SVFit",tautauMassAll)

        
        return True
    


SVFitMassProducer_all = lambda : SVFitMassProducer() 
