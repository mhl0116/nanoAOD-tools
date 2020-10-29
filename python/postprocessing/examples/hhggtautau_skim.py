import ROOT
import array
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Object 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

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
        self.out.branch("tautauMassLoose",  "F");
        self.out.branch("tautauMassAll",  "F");
        self.out.branch("ggMass",  "F");
        self.out.branch("muonNumber",  "I");  
        self.out.branch("electronNumber",  "I");  
        self.out.branch("tauNumber",  "I");  
        
        self.out.branch("passedGoodPhotons","B")
        self.out.branch("passedHPhotons","B")
        self.out.branch("passedDigammaPair","B")
        self.out.branch("gHidx",  "I", 2);        
        
        self.out.branch("tauHidx",  "I", 2);
        self.out.branch("tauLooseHidx",  "I", 2);
        self.out.branch("tauAllHidx",  "I", 2);
        
        self.out.branch("Category",   "I");
        self.out.branch("Category_lveto",   "I");
        self.out.branch("Category_tausel",   "I");
        self.out.branch("Category_pairs",   "I");
        
        self.out.branch("Category_LooseTausel",   "I");
        self.out.branch("Category_LoosePairs",   "I");
        self.out.branch("Category_AllPairs",   "I");
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def invMass(self, jets):
        j1 = ROOT.TLorentzVector()
        j2 = ROOT.TLorentzVector()
        j1.SetPtEtaPhiM(jets[0].pt_nom, jets[0].eta, jets[0].phi, jets[0].mass_nom)
        j2.SetPtEtaPhiM(jets[1].pt_nom, jets[1].eta, jets[1].phi, jets[1].mass_nom)
        return (j1+j2).M()
        
    
    def elid(self, el, wp, noiso=False):
        if (wp == "80"):
            return el.mvaFall17V2Iso_WP80
        elif (wp == "90"):
            return el.mvaFall17V2Iso_WP90
        elif (wp == "80" and noiso==True):
            return el.mvaFall17V2noIso_WP80
        elif (wp == "90" and noiso==True):
            return el.mvaFall17V2noIso_WP90
        
        
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
        
        electrons = list(Collection(event, "Electron"))
        muons = list(Collection(event, "Muon"))
        #jets = list(Collection(event, "Jet"))        
        taus = list(Collection(event, "Tau"))
        photons = list(Collection(event, "Photon"))
        
        rho = getattr(event, "fixedGridRhoAll")
        print rho
        
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
            
        tautauMass=-1
        tautauMassLoose=-1
        tautauMassAll=-1
        Category = -1
        Category_lveto = -1
        Category_tausel = -1
        Category_pairs = -1
        
        Category_LooseTausel = -1
        Category_LoosePairs = -1
        Category_AllPairs = -1
        
        #FOR SIGNAL
        tElectrons = [x for x in electrons if self.elid(x,"80") and x.pt > 25 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.5 ]   
        #tElectrons = [x for x in electrons if self.elid(x,"80") and x.pt > 25 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.1 ] 
        #2.1 must be due to the trigger, we don't need it
        
        #FOR SIGNAL        
        tMuons = [x for x in muons if x.pt > 20 and x.tightId >= 1 and x.pfRelIso04_all < 0.15 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.4 ]
        #tMuons = [x for x in muons if x.pt > 20 and x.tightId >= 1 and x.pfRelIso04_all < 0.15 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.1 ]
        #2.1 must be due to the trigger, we don't need it
        
        #FOR VETOS
        lElectrons = [x for x in electrons if x.pt > 10 and (self.elid(x,"90") or (x.pfRelIso03_all < 0.3 and self.elid(x,"90", True)))  and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.5 ]
        lMuons = [x for x in muons if x.pt > 10 and x.pfRelIso04_all < 0.3 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.4]
        

        if (len(tMuons)==1):
            Category=1
        elif (len(tElectrons)==1):
            Category=2
        else:
            Category=3
            
        if (len(tMuons)==1 and len(lMuons+lElectrons)==1):
            Category_lveto=1
        elif (len(tElectrons)==1 and len(lMuons+lElectrons)==1):
            Category_lveto=2
        elif (len(lMuons+lElectrons)==0):
            Category_lveto=3

        tausForHiggs=[]
        tausForHiggsLoose=[]
        
        if Category==1:
            #muonic decay
            tausForHiggsLoose = [x for x in taus if (x.pt>20 and 
                                                abs(x.eta)<2.3  and  
                                                x.idDecayModeNewDMs and 
                                                x.idDeepTau2017v2p1VSe>=4 and #VLoose
                                                x.idDeepTau2017v2p1VSjet>=8 and #Loose - use to be medium in bbtt
                                                x.idDeepTau2017v2p1VSmu>=8 and #Tight
                                                abs(x.dz) < 0.2)]       
        
        elif Category==2:
            #electron decay
            tausForHiggsLoose = [x for x in taus if (x.pt>20 and 
                                                abs(x.eta)<2.3  and  
                                                x.idDecayModeNewDMs and 
                                                x.idDeepTau2017v2p1VSe>=32 and #Tight
                                                x.idDeepTau2017v2p1VSjet>=8 and #Loose - use to be medium in bbtt
                                                x.idDeepTau2017v2p1VSmu>=8 and #Tight
                                                abs(x.dz) < 0.2)] 
            
            
            
        elif Category==3:
            tausForHiggsLoose = [x for x in taus if (x.pt>20 and 
                                                abs(x.eta)<2.3  and                        #2.1  due to the trigger, we don't need it
                                                x.idDecayModeNewDMs and 
                                                x.idDeepTau2017v2p1VSe>=2 and #VVLoose
                                                x.idDeepTau2017v2p1VSjet>=8 and #Loose - use to be medium in bbtt
                                                x.idDeepTau2017v2p1VSmu>=1 and #VLoose
                                                abs(x.dz) < 0.2)]
            
        tausForHiggs=[x for x in tausForHiggsLoose if x.idDeepTau2017v2p1VSjet>=16]
            
            
            
        
        if (Category_lveto==1 and len(tausForHiggsLoose)>0):
            Category_LooseTausel=1
        elif (Category_lveto==2 and len(tausForHiggsLoose)>0):
            Category_LooseTausel=2
        elif (Category_lveto==3 and len(tausForHiggsLoose)>1):
            Category_LooseTausel=3
            
        if (Category_lveto==1 and len(tausForHiggs)>0):
            Category_tausel=1
        elif (Category_lveto==2 and len(tausForHiggs)>0):
            Category_tausel=2
        elif (Category_lveto==3 and len(tausForHiggs)>1):
            Category_tausel=3

        #Tau_idDeepTau2017v2p1VSe	UChar_t	byDeepTau2017v2p1VSe ID working points (deepTau2017v2p1): bitmask 1 = VVVLoose, 2 = VVLoose, 4 = VLoose, 8 = Loose, 16 = Medium, 32 = Tight, 64 = VTight, 128 = VVTight
        #Tau_idDeepTau2017v2p1VSjet	UChar_t	byDeepTau2017v2p1VSjet ID working points (deepTau2017v2p1): bitmask 1 = VVVLoose, 2 = VVLoose, 4 = VLoose, 8 = Loose, 16 = Medium, 32 = Tight, 64 = VTight, 128 = VVTight
        #Tau_idDeepTau2017v2p1VSmu	UChar_t	byDeepTau2017v2p1VSmu ID working points (deepTau2017v2p1): bitmask 1 = VLoose, 2 = Loose, 4 = Medium, 8 = Tight
         
                
        #if category==-1 return False              
        
        muonNumber = len(tMuons)
        electronNumber = len(tElectrons)        
        tauNumber = len(tausForHiggs)
       
        
        #if len(tausForHiggs)>1:
        #    tausForHiggs=sorted(tausForHiggs, key=lambda x : x.chargedIso, reverse=True)
        #
        # SKIP SORTING FOR NOW
                
        tauHidx=[-1,-1]
        tauLooseHidx=[-1,-1]
        tauAllHidx=[-1,-1]
        
        #Original selections
        if (Category_tausel==1 and len(tausForHiggs)):
            tauHidx[0] = muons.index(tMuons[0])
            charge = tMuons[0].charge
            for j in range(len(tausForHiggs)):
                if (charge!=tausForHiggs[j].charge):
                    tauHidx[1] = taus.index(tausForHiggs[j])
                    
        elif (Category_tausel==2 and len(tausForHiggs)):
            tauHidx[0] = electrons.index(tElectrons[0])
            charge = tElectrons[0].charge
            for j in range(len(tausForHiggs)):
                if (charge!=tausForHiggs[j].charge):
                    tauHidx[1] = taus.index(tausForHiggs[j])
        
        elif (Category_tausel==3):
            tauLooseHidx[0] = taus.index(tausForHiggs[0])
            charge=tausForHiggs[0].charge
            for j in range(1,len(tausForHiggs)):
                if (charge!=tausForHiggs[j].charge):
                    tauLooseHidx[1] = taus.index(tausForHiggs[j])
        
        #Loose selections
        if (Category_LooseTausel==1 and len(tausForHiggsLoose)):
            tauLooseHidx[0] = muons.index(tMuons[0])
            charge = tMuons[0].charge
            for j in range(len(tausForHiggsLoose)):
                if (charge!=tausForHiggsLoose[j].charge):
                    tauLooseHidx[1] = taus.index(tausForHiggsLoose[j])
                    
        elif (Category_LooseTausel==2 and len(tausForHiggsLoose)):
            tauLooseHidx[0] = electrons.index(tElectrons[0])
            charge = tElectrons[0].charge
            for j in range(len(tausForHiggsLoose)):
                if (charge!=tausForHiggsLoose[j].charge):
                    tauLooseHidx[1] = taus.index(tausForHiggsLoose[j])
        
        elif (Category_LooseTausel==3):
            tauLooseHidx[0] = taus.index(tausForHiggsLoose[0])
            charge=tausForHiggsLoose[0].charge
            for j in range(1,len(tausForHiggsLoose)):
                if (charge!=tausForHiggsLoose[j].charge):
                    tauLooseHidx[1] = taus.index(tausForHiggsLoose[j])
                    
        #EVEN LOOSER selections
        if (Category_lveto==1 and len(taus)):
            tauAllHidx[0] = muons.index(tMuons[0])
            charge = tMuons[0].charge
            for j in range(len(taus)):
                if (charge!=taus[j].charge and deltaR(tMuons[0], taus[j])>0.2):
                    tauAllHidx[1] = j
                    
        elif (Category_lveto==2 and len(taus)):
            tauAllHidx[0] = electrons.index(tElectrons[0])
            charge = tElectrons[0].charge
            for j in range(len(taus)):
                if (charge!=taus[j].charge and deltaR(tElectrons[0], taus[j])>0.2):
                    tauAllHidx[1] = j
        
        elif (Category_lveto==3 and len(taus)>1):
            tauAllHidx[0] = 0
            charge=taus[0].charge
            for j in range(1,len(taus)):
                if (charge!=taus[j].charge):
                    tauAllHidx[1] = j
            
        
        
        if (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_tausel==3):
            Category_pairs=3
            v1.SetPtEtaPhiM(taus[tauHidx[0]].pt,taus[tauHidx[0]].eta,taus[tauHidx[0]].phi,taus[tauHidx[0]].mass)
            v2.SetPtEtaPhiM(taus[tauHidx[1]].pt,taus[tauHidx[1]].eta,taus[tauHidx[1]].phi,taus[tauHidx[1]].mass)
            tautauMass=(v1+v2).M()
        elif (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_tausel==2):
            Category_pairs=2
            v1.SetPtEtaPhiM(electrons[tauHidx[0]].pt,electrons[tauHidx[0]].eta,electrons[tauHidx[0]].phi,0.511/1000.)
            v2.SetPtEtaPhiM(taus[tauHidx[1]].pt,taus[tauHidx[1]].eta,taus[tauHidx[1]].phi,taus[tauHidx[1]].mass)
            tautauMass=(v1+v2).M()
        elif (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_tausel==1):
            Category_pairs=1
            v1.SetPtEtaPhiM(muons[tauHidx[0]].pt,muons[tauHidx[0]].eta,muons[tauHidx[0]].phi,0.1056)
            v2.SetPtEtaPhiM(taus[tauHidx[1]].pt,taus[tauHidx[1]].eta,taus[tauHidx[1]].phi,taus[tauHidx[1]].mass)
            tautauMass=(v1+v2).M()
            
        if (tauLooseHidx[0]>=0 and tauLooseHidx[1]>=0 and Category_LooseTausel==3):
            Category_LoosePairs=3
            v1.SetPtEtaPhiM(taus[tauLooseHidx[0]].pt,taus[tauLooseHidx[0]].eta,taus[tauLooseHidx[0]].phi,taus[tauLooseHidx[0]].mass)
            v2.SetPtEtaPhiM(taus[tauLooseHidx[1]].pt,taus[tauLooseHidx[1]].eta,taus[tauLooseHidx[1]].phi,taus[tauLooseHidx[1]].mass)
            tautauMassLoose=(v1+v2).M()
        elif (tauLooseHidx[0]>=0 and tauLooseHidx[1]>=0 and Category_LooseTausel==2):
            Category_LoosePairs=2
            v1.SetPtEtaPhiM(electrons[tauLooseHidx[0]].pt,electrons[tauLooseHidx[0]].eta,electrons[tauLooseHidx[0]].phi,0.511/1000.)
            v2.SetPtEtaPhiM(taus[tauLooseHidx[1]].pt,taus[tauLooseHidx[1]].eta,taus[tauLooseHidx[1]].phi,taus[tauLooseHidx[1]].mass)
            tautauMassLoose=(v1+v2).M()
        elif (tauLooseHidx[0]>=0 and tauLooseHidx[1]>=0 and Category_LooseTausel==1):
            Category_LoosePairs=1
            v1.SetPtEtaPhiM(muons[tauLooseHidx[0]].pt,muons[tauLooseHidx[0]].eta,muons[tauLooseHidx[0]].phi,0.1056)
            v2.SetPtEtaPhiM(taus[tauLooseHidx[1]].pt,taus[tauLooseHidx[1]].eta,taus[tauLooseHidx[1]].phi,taus[tauLooseHidx[1]].mass)
            tautauMassLoose=(v1+v2).M()
            
        if (tauAllHidx[0]>=0 and tauAllHidx[1]>=0 and Category_lveto==3):
            Category_AllPairs=3
            v1.SetPtEtaPhiM(taus[tauAllHidx[0]].pt,taus[tauAllHidx[0]].eta,taus[tauAllHidx[0]].phi,taus[tauAllHidx[0]].mass)
            v2.SetPtEtaPhiM(taus[tauAllHidx[1]].pt,taus[tauAllHidx[1]].eta,taus[tauAllHidx[1]].phi,taus[tauAllHidx[1]].mass)
            tautauMassAll=(v1+v2).M()
        elif (tauAllHidx[0]>=0 and tauAllHidx[1]>=0 and Category_lveto==2):
            Category_AllPairs=2
            v1.SetPtEtaPhiM(electrons[tauAllHidx[0]].pt,electrons[tauAllHidx[0]].eta,electrons[tauAllHidx[0]].phi,0.511/1000.)
            v2.SetPtEtaPhiM(taus[tauAllHidx[1]].pt,taus[tauAllHidx[1]].eta,taus[tauAllHidx[1]].phi,taus[tauAllHidx[1]].mass)
            tautauMassAll=(v1+v2).M()
        elif (tauAllHidx[0]>=0 and tauAllHidx[1]>=0 and Category_lveto==1):
            Category_AllPairs=1
            v1.SetPtEtaPhiM(muons[tauAllHidx[0]].pt,muons[tauAllHidx[0]].eta,muons[tauAllHidx[0]].phi,0.1056)
            v2.SetPtEtaPhiM(taus[tauAllHidx[1]].pt,taus[tauAllHidx[1]].eta,taus[tauAllHidx[1]].phi,taus[tauAllHidx[1]].mass)
            tautauMassAll=(v1+v2).M()
            

        self.out.fillBranch("tautauMass",tautauMass)
        self.out.fillBranch("tautauMassLoose",tautauMassLoose)
        self.out.fillBranch("tautauMassAll",tautauMassAll)
        
        self.out.fillBranch("ggMass",ggMass)
        self.out.fillBranch("muonNumber",muonNumber)
        self.out.fillBranch("electronNumber",electronNumber)
        self.out.fillBranch("tauNumber",tauNumber)
        
        self.out.fillBranch("passedGoodPhotons",passedGoodPhotons)
        self.out.fillBranch("passedHPhotons",passedHPhotons)
        self.out.fillBranch("passedDigammaPair",passedDigammaPair)
        self.out.fillBranch("gHidx",gHidx)
        
        self.out.fillBranch("tauHidx",tauHidx)   
        self.out.fillBranch("Category",  Category);
        self.out.fillBranch("Category_lveto",  Category_lveto);
        self.out.fillBranch("Category_tausel",  Category_tausel);
        self.out.fillBranch("Category_pairs",  Category_pairs);
        self.out.fillBranch("Category_LooseTausel",  Category_LooseTausel);
        self.out.fillBranch("Category_LoosePairs",  Category_LoosePairs);
        self.out.fillBranch("Category_AllPairs",  Category_AllPairs);
        
        return True
    
    
    
HHggtauatauModule2016 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2016") 
HHggtauatauModule2017 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2017") 
HHggtauatauModule2018 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2018") 

HHggtauatauModuleDATA18 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2018") 
HHggtauatauModuleDATA17 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2017") 
HHggtauatauModuleDATA16 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2016") 
