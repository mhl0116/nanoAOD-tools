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
    def __init__(self, hadtau1="Loose", hadtau2="Loose"):
        
        self.hadtau1 = hadtau1
        self.hadtau2 = hadtau2
        self.postfix = hadtau1+(hadtau2 if hadtau1!=hadtau2 else "")
       
    def beginJob(self):
        pass
    
    def endJob(self):
        pass
    
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("tautauMass"+self.postfix+"_SVFit",  "F");
      
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    
    def analyze(self, event):
                
        """process event, return True (go to next module) or False (fail, go to next event)"""
        electrons = list(Collection(event, "Electron"))
        muons = list(Collection(event, "Muon"))   
        taus = list(Collection(event, "Tau"))
        tauHidx = getattr(event, "tau"+self.postfix+"Hidx") 
        MET = Object(event, "MET")
        
        Category = getattr(event, "Category")
        Category_pairs = getattr(event, "Category_pairs"+self.postfix)
        
        category1=Category
        category2=0 #not sure exactly what is supposed to be given here
        
        tautauMass=-1
        
        covMET_XX=MET.covXX
        covMET_XY=MET.covXY
        covMET_YY=MET.covYY
        measuredMETx=MET.pt*math.cos(MET.phi) #add MET smearing soon
        measuredMETy=MET.pt*math.sin(MET.phi) #add MET smearing soon
        
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
    
        
        self.out.fillBranch("tautauMass"+self.postfix+"_SVFit",tautauMass)
        
        return True
    
#modules to be run after the tau selection
SVFitMassProducer_MediumMedium = lambda : SVFitMassProducer(hadtau1="Medium", hadtau2="Medium") 
SVFitMassProducer_LooseLoose = lambda : SVFitMassProducer(hadtau1="Loose", hadtau2="Loose") 
SVFitMassProducer_AllAll = lambda : SVFitMassProducer(hadtau1="All", hadtau2="All") 
SVFitMassProducer_LooseAll = lambda : SVFitMassProducer(hadtau1="Loose", hadtau2="All") 
