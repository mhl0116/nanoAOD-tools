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

class HHggtautauLepSelector(Module):
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
        self.out.branch("Categoryb",   "I");
        self.out.branch("Category_lvetob",   "I");
        self.out.branch("taulepHidx","I", 2);
        self.out.branch("Jet_Filter",  "O", 1, "nJet");
        self.out.branch("Tau_Filter",  "O", 1, "nTau");

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass       
    
    def elid(self, el, wp, noiso=False):
        if (wp == "80"):
            return el.mvaFall17V2Iso_WP80
        elif (wp == "90"):
            return el.mvaFall17V2Iso_WP90
        elif (wp == "80" and noiso==True):
            return el.mvaFall17V2noIso_WP80
        elif (wp == "90" and noiso==True):
            return el.mvaFall17V2noIso_WP90
        
    def analyze(self, event):

        electrons = list(Collection(event, "Electron"))
        muons = list(Collection(event, "Muon"))
        jets = list(Collection(event, "Jet"))        
        photons = list(Collection(event, "Photon"))
        taus = list(Collection(event, "Tau"))
        gHidx = getattr(event, "gHidx")
        
        
        Category = -1
        Category_lveto = -1
        taulepHidx=[-1,-1]
        
        hphotonFilter = lambda j : ((deltaR(j,photons[gHidx[0]])>0.2 if gHidx[0]>=0 else 1) and (deltaR(j,photons[gHidx[1]])>0.2 if gHidx[1]>=0 else 1))
        hphotonFilter4 = lambda j : ((deltaR(j,photons[gHidx[0]])>0.4 if gHidx[0]>0 else 1) and (deltaR(j,photons[gHidx[1]])>0.4 if gHidx[1]>0 else 1))

        #FOR SIGNAL        
        tElectrons = [x for x in electrons if self.elid(x,"80") and x.pt > 25 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.5 and hphotonFilter(x)]       
        tMuons = [x for x in muons if x.pt > 20 and x.tightId >= 1 and x.pfRelIso04_all < 0.15 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.4 and hphotonFilter(x)]

        #FOR VETOS
        lElectrons = [x for x in electrons if x.pt > 10 and (self.elid(x,"90") or (x.pfRelIso03_all < 0.3 and self.elid(x,"90", True)))  and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.5 and hphotonFilter(x) ] #electron ecal cracks?
        #lMuons = [x for x in muons if x.pt > 10 and x.pfRelIso04_all < 0.3 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.4 and hphotonFilter(x) ]
        lMuons = [x for x in muons if x.pt > 10 and x.pfRelIso03_all < 0.3 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.4 and hphotonFilter(x) ]
        #spotted one difference pfRelIso03_allpfRelIso03_all pfRelIso04_all
        
             
        tElectrons=lElectrons
        tMuons=lMuons
 
        # these should be use for jet counting (for mva etc.)
        jetFilterFlags = [True]*len(jets)
        tauFilterFlags = [True]*len(taus)
    
        for i in range(len(jets)):
            if (hphotonFilter4(jets[i])==0):
                jetFilterFlags[i]=False
                
        for i in range(len(taus)):
            if (hphotonFilter(taus[i])==0):
              tauFilterFlags[i]=False
            for lepton in lElectrons+lMuons:
              if deltaR(lepton, taus[i])<0.2:
                tauFilterFlags[i]=False
            
    
        for lepton in lElectrons+lMuons:
            jetInd = lepton.jetIdx
            if jetInd >= 0:
                jetFilterFlags[jetInd] = False
    
        #dilepton categories first
        for i in range(len(lMuons)):
            if lMuons[i].pt>10:
                for j in range(i+1,len(lMuons)):
                    if (lMuons[j].pt>10 and lMuons[i].charge*lMuons[j].charge==-1):
                        Category=4
                for j in range(0,len(lElectrons)):
                    if (lElectrons[j].pt>10 and lMuons[i].charge*lElectrons[j].charge==-1):
                        Category=6
    
        for i in range(len(lElectrons)):
            if lElectrons[i].pt>10:
                for j in range(i+1,len(lElectrons)):
                    if (lElectrons[j].pt>10 and lElectrons[i].charge*lElectrons[j].charge==-1):
                        Category=5
    
        #leptons of opposite charges not found (pt >20, loose ID, iso)
        if Category<0: 
            if (len(lMuons)==1):
                Category=1
            elif (len(lElectrons)==1):
                Category=2
            elif(len(lMuons+lElectrons)==0):
                Category=3

        #leptons vetos
        if (Category==1 and len(lMuons+lElectrons)==1):
            Category_lveto=1
        elif (Category==2 and len(lMuons+lElectrons)==1):
            Category_lveto=2
        elif (Category==3):
            Category_lveto=3
        elif(Category==4 and len(lMuons+lElectrons)==2):
            Category_lveto=4
        elif(Category==5 and len(lMuons+lElectrons)==2):
            Category_lveto=5
        elif(Category==6 and len(lMuons+lElectrons)==2):
            Category_lveto=6

        ### the lepton only categories dont need any tau ID
        ### and once we are here we are sure the pairs are formed in an unique way beacause of pairs+lep veto.
        if (Category_lveto==4):
            taulepHidx[0]=muons.index(lMuons[0])
            taulepHidx[1]=muons.index(lMuons[1])
        elif (Category_lveto==5):
            taulepHidx[0]=electrons.index(lElectrons[0])
            taulepHidx[1]=electrons.index(lElectrons[1])
        elif (Category_lveto==6):
            taulepHidx[0]=electrons.index(lElectrons[0])
            taulepHidx[1]=muons.index(lMuons[0])
        #one index is filled when the tau PAIR is lep+had
        elif (Category_lveto==2):
            taulepHidx[0]=electrons.index(tElectrons[0])
        elif (Category_lveto==1):
            taulepHidx[0]=muons.index(tMuons[0])


        self.out.fillBranch("taulepHidx",  taulepHidx);
        self.out.fillBranch("Categoryb",  Category);
        self.out.fillBranch("Category_lvetob",  Category_lveto);
        self.out.fillBranch("Jet_Filter",jetFilterFlags)
        self.out.fillBranch("Tau_Filter",tauFilterFlags)
        
        return True



HHggtautaulep2016 = lambda : HHggtautauLepSelector(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2016")
HHggtautaulep2017 = lambda : HHggtautauLepSelector(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2017")
HHggtautaulep2018 = lambda : HHggtautauLepSelector(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2018")

HHggtautaulepDATA18 = lambda : HHggtautauLepSelector(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2018")
HHggtautaulepDATA17 = lambda : HHggtautauLepSelector(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2017")
HHggtautaulepDATA16 = lambda : HHggtautauLepSelector(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2016")





 
