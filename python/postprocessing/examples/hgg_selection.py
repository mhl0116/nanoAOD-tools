import ROOT
import array
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Object 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

import ROOT
import array
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Object 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

class HggSelector(Module):
    def __init__(self, data, year="2016"):
        self.data = data
        self.year = year
        
        ### ref link useful later on
        ### reduced JES uncertainties (see https://twiki.cern.ch/twiki/bin/viewauth/CMS/JECUncertaintySources#Run_2_reduced_set_of_uncertainty)
       
    def beginJob(self):
        pass
    
    def endJob(self):
        pass
    
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("passedGoodPhotons","B")
        self.out.branch("passedHPhotons","B")
        self.out.branch("passedDigammaPair","B")
        self.out.branch("gHidx",  "I", 2);    
        self.out.branch("ggMass",  "F");        
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def useLowR9(self, photon, rho, isEB):
        if (isEB):        
            if ( (photon.sieie >= 0.015) ): 
                return False     
            if ( (photon.trkSumPtHollowConeDR03 >= 6.0) ): 
                return False     
            if ( (photon.photonIso - 0.16544*rho >= 4.0) ): 
                return False      
        else:
            if ( (photon.sieie >= 0.035) ): 
                return False;       
            if ( (photon.trkSumPtHollowConeDR03 >= 6.0) ): 
                return False      
            if ( (photon.photonIso - 0.13212*rho >= 4.0) ): 
                return False       

        # 0.16544 and 0.13212 are copied from flashggPreselectedDiPhotons_cfi.py
        return True

    
    def analyze(self, event):
        
        """process event, return True (go to next module) or False (fail, go to next event)"""

        photons = list(Collection(event, "Photon"))
        rho = getattr(event, "fixedGridRhoAll")
        
        v1 = ROOT.TLorentzVector()
        v2 = ROOT.TLorentzVector()
        
        passedGoodPhotons=False
        passedHPhotons=False
        passedDigammaPair=False
        
        gHidx=[-1,-1]
        ggMass=-1
        
        pho_EB_highR9 = lambda x : (abs(x.eta) < 1.5 and x.r9 > 0.85)
        pho_EE_highR9 = lambda x : (abs(x.eta) > 1.5 and x.r9 > 0.9)
        pho_EB_lowR9 = lambda x : (abs(x.eta) < 1.5 and x.r9 < 0.85 and x.r9 > 0.5 and self.useLowR9(x,rho,True))
        pho_EE_lowR9 = lambda x : (abs(x.eta) > 1.5 and x.r9 < 0.85 and x.r9 > 0.8 and self.useLowR9(x,rho,False))

        photonsGood = [ph for ph in photons if (ph.electronVeto>=0.5 and (pho_EB_highR9(ph) or pho_EE_highR9(ph) or pho_EB_lowR9(ph) or pho_EE_lowR9(ph)))]
        if (len(photonsGood)>1):
            passedGoodPhotons=True
        
        photonsForHiggs = [ph for ph in photonsGood if (ph.hoe<0.08 and abs(ph.eta)<2.5 and (abs(ph.eta)<1.442 or abs(ph.eta)>1.566)  and (ph.r9>0.8 or ph.chargedHadronIso<20 or ph.chargedHadronIso/ph.pt<0.3) )]
        photonsForHiggs=sorted(photonsForHiggs, key=lambda x : x.pt, reverse=True)
        if (len(photonsForHiggs)>1):
            passedHPhotons=True
        
        #digamma pair
        if (len(photonsForHiggs)>1 and photonsForHiggs[0].pt >35 and photonsForHiggs[1].pt>25 ):
            passedDigammaPair=True
            gHidx[0]=photons.index(photonsForHiggs[0])
            gHidx[1]=photons.index(photonsForHiggs[1])
            
        if (gHidx[0]>=0 and gHidx[1]>=0):
            v1.SetPtEtaPhiM(photons[gHidx[0]].pt,photons[gHidx[0]].eta,photons[gHidx[0]].phi,0)
            v2.SetPtEtaPhiM(photons[gHidx[1]].pt,photons[gHidx[1]].eta,photons[gHidx[1]].phi,0)
            ggMass=(v1+v2).M()

        self.out.fillBranch("ggMass",ggMass)      
        self.out.fillBranch("passedGoodPhotons",passedGoodPhotons)
        self.out.fillBranch("passedHPhotons",passedHPhotons)
        self.out.fillBranch("passedDigammaPair",passedDigammaPair)
        self.out.fillBranch("gHidx",gHidx)
        
        return True
    

HggModule2016 = lambda : HggSelector(data = False, year="2016") 
HggModule2017 = lambda : HggSelector(data = False, year="2017")     
HggModule2018 = lambda : HggSelector(data = False, year="2018")    

HggModuleData2016 = lambda : HggSelector(data = True, year="2016")       
HggModuleData2017 = lambda : HggSelector(data = True, year="2017")
HggModuleData2018 = lambda : HggSelector(data = True, year="2018") 
