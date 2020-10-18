import ROOT
import array
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Object 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class HHggtautauProducer(Module):
    def __init__(self, jetSelection, muSelection, eSelection, data, year="2016"):
        self.jetSel = jetSelection
        self.muSel = muSelection
        self.eSel = eSelection
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
        self.out.branch("tautauMass",  "F");
        self.out.branch("ggMass",  "F");
        self.out.branch("muonNumber",  "I");  
        self.out.branch("electronNumber",  "I");  
        self.out.branch("tauNumber",  "I");  
        self.out.branch("tauHidx",  "I", 2);
        self.out.branch("Category",   "I");
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def invMass(self, jets):
        j1 = ROOT.TLorentzVector()
        j2 = ROOT.TLorentzVector()
        j1.SetPtEtaPhiM(jets[0].pt_nom, jets[0].eta, jets[0].phi, jets[0].mass_nom)
        j2.SetPtEtaPhiM(jets[1].pt_nom, jets[1].eta, jets[1].phi, jets[1].mass_nom)
        return (j1+j2).M()
        
    
    def elid(self, el, wp):
        if (wp == "80"):
            return el.mvaFall17V2Iso_WP80
        elif (wp == "90"):
            return el.mvaFall17V2Iso_WP90

    
    def analyze(self, event):
        
        """process event, return True (go to next module) or False (fail, go to next event)"""
        electrons = list(Collection(event, "Electron"))
        muons = list(Collection(event, "Muon"))
        #jets = list(Collection(event, "Jet"))        
        taus = list(Collection(event, "Tau"))
        
        tautauMass=-1
        ggMass=-1
        Category = -1
        
        tElectrons = [x for x in electrons if self.elid(x,"80") and x.pt > 25 and x.pfRelIso03_all < 0.12]      
        tMuons = [x for x in muons if x.pt > 25 and x.tightId >= 1 and x.pfRelIso04_all < 0.15 and abs(x.dxy) < 0.05 and abs(x.dz) < 0.2]
        lElectrons = [x for x in electrons if x.pt > 20 and self.elid(x,"90") and x.pfRelIso03_all < 0.15]
        lMuons = [x for x in muons if x.pt > 20 and x.pfRelIso04_all < 0.25 and abs(x.dxy) < 0.05 and abs(x.dz) < 0.2]
        

        if (len(tMuons)==1 and len(lElectrons+lMuons)==1):
            Category=1
        elif (len(tElectrons)==1 and len(lElectrons+lMuons)==1):
            Category=2
        elif(len(lElectrons+lMuons)==0):
            Category=3

        #if category==-1 return False              
        
        muonNumber = len(tMuons)
        electronNumber = len(tElectrons)
        
        tausForHiggs = [x for x in taus if (x.pt>20 and abs(x.eta)<2.4  and  x.idDecayModeNewDMs and x.idDeepTau2017v2p1VSe and x.idDeepTau2017v2p1VSjet and x.idDeepTau2017v2p1VSmu)]        
        
        tauNumber = len(tausForHiggs)
       
        hTaus = sorted(tausForHiggs ,key=lambda x : x.pt, reverse=True)[0:2]
                
        tauHidx=[-1,-1]
        
        if (Category==3 and len(hTaus)>1):
            tauHidx[0] = taus.index(hTaus[0])
            tauHidx[1] = taus.index(hTaus[1])
        elif (Category<3 and len(hTaus)):
            tauHidx[0] = taus.index(hTaus[0])
        
        #much more to do....

        self.out.fillBranch("tautauMass",tautauMass)
        self.out.fillBranch("ggMass",ggMass)
        self.out.fillBranch("muonNumber",muonNumber)
        self.out.fillBranch("electronNumber",electronNumber)
        self.out.fillBranch("tauNumber",tauNumber)
        self.out.fillBranch("tauHidx",tauHidx)   
        self.out.fillBranch("Category",  Category);
        return True
    
    
    
HHggtauatauModule2016 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2016") 
HHggtauatauModule2017 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2017") 
HHggtauatauModule2018 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2018") 

HHggtauatauModuleDATA18 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2018") 
HHggtauatauModuleDATA17 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2017") 
HHggtauatauModuleDATA16 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2016") 
