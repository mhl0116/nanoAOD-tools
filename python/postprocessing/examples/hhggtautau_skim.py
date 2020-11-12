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
        
        self.out.branch("Jet_Filter",  "O", 1, "nJet");
        self.out.branch("Jet_FilterLoose",  "O", 1, "nJet");
        self.out.branch("Jet_FilterAll",  "O", 1, "nJet");
        
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def invMass(self, obj1, obj2, mass1=-1, mass2=-1):
        j1 = ROOT.TLorentzVector()
        j2 = ROOT.TLorentzVector()
        if (mass1==-1):
            j1.SetPtEtaPhiM(obj1.pt, obj1.eta, obj1.phi, obj1.mass)
        else:
            j1.SetPtEtaPhiM(obj1.pt, obj1.eta, obj1.phi, mass1)
        if (mass2==-1):
            j2.SetPtEtaPhiM(obj2.pt, obj2.eta, obj2.phi, obj2.mass)
        else:
            j2.SetPtEtaPhiM(obj2.pt, obj2.eta, obj2.phi, mass2)        
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
        jets = list(Collection(event, "Jet"))        
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
        
        hphotonFilter = lambda j : ((deltaR(j,photons[gHidx[0]])>0.4 if gHidx[0]>0 else 1) and (deltaR(j,photons[gHidx[1]])>0.4 if gHidx[1]>0 else 1))
        #print "h photon filtered"
        
        #FOR SIGNAL
        tElectrons = [x for x in electrons if self.elid(x,"80") and x.pt > 25 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.5 and hphotonFilter(x)]   
        #tElectrons = [x for x in electrons if self.elid(x,"80") and x.pt > 25 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.1 ] 
        #2.1 must be due to the trigger, we don't need it
        
        #FOR SIGNAL        
        tMuons = [x for x in muons if x.pt > 20 and x.tightId >= 1 and x.pfRelIso04_all < 0.15 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.4 and hphotonFilter(x)]
        #tMuons = [x for x in muons if x.pt > 20 and x.tightId >= 1 and x.pfRelIso04_all < 0.15 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.1 ]
        #2.1 must be due to the trigger, we don't need it
        
        #FOR VETOS
        lElectrons = [x for x in electrons if x.pt > 10 and (self.elid(x,"90") or (x.pfRelIso03_all < 0.3 and self.elid(x,"90", True)))  and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.5 and hphotonFilter(x) ] #electron ecal cracks?
        lMuons = [x for x in muons if x.pt > 10 and x.pfRelIso04_all < 0.3 and abs(x.dxy) < 0.045 and abs(x.dz) < 0.2 and abs(x.eta)<2.4 and hphotonFilter(x) ]
        
        # these should be use for jet counting (for mva etc.)
        jetFilterFlags = [True]*len(jets)
        
        for i in range(len(jets)):
            if (hphotonFilter(jets[i])==0):
                jetFilterFlags[i]=False
                
        for lepton in lElectrons+lMuons:
            jetInd = lepton.jetIdx
            if jetInd >= 0:
                jetFilterFlags[jetInd] = False
                
        #dilepton categories first
        for i in range(len(lMuons)):
            if lMuons[i].pt>20:
                for j in range(i+1,len(lMuons)):
                    if (lMuons[j].pt>20 and lMuons[i].charge*lMuons[j].charge==-1):
                        Category=4
                for j in range(0,len(lElectrons)):
                    if (lElectrons[j].pt>20 and lMuons[i].charge*lElectrons[j].charge==-1):
                        Category=6
                        
        for i in range(len(lElectrons)):
            if lElectrons[i].pt>20:
                for j in range(i+1,len(lElectrons)):
                    if (lElectrons[j].pt>20 and lElectrons[i].charge*lElectrons[j].charge==-1):
                        Category=5
        

        if Category<0: #leptons of opposite charges not found (pt >20, loose ID, iso)
            if (len(tMuons)==1):
                Category=1
            elif (len(tElectrons)==1):
                Category=2
            elif(len(lMuons+lElectrons)==0):
                Category=3

            
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
                                                abs(x.dz) < 0.2 and hphotonFilter(x))]       
        
        elif Category==2:
            #electron decay
            tausForHiggsLoose = [x for x in taus if (x.pt>20 and 
                                                abs(x.eta)<2.3  and  
                                                x.idDecayModeNewDMs and 
                                                x.idDeepTau2017v2p1VSe>=32 and #Tight
                                                x.idDeepTau2017v2p1VSjet>=8 and #Loose - use to be medium in bbtt
                                                x.idDeepTau2017v2p1VSmu>=8 and #Tight
                                                abs(x.dz) < 0.2 and hphotonFilter(x))] 
            
            
            
        elif Category==3:
            tausForHiggsLoose = [x for x in taus if (x.pt>20 and 
                                                abs(x.eta)<2.3  and                        #2.1  due to the trigger, we don't need it
                                                x.idDecayModeNewDMs and 
                                                x.idDeepTau2017v2p1VSe>=2 and #VVLoose
                                                x.idDeepTau2017v2p1VSjet>=8 and #Loose - use to be medium in bbtt
                                                x.idDeepTau2017v2p1VSmu>=1 and #VLoose
                                                abs(x.dz) < 0.2 and hphotonFilter(x))]
            
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

        muonNumber = len(tMuons)
        electronNumber = len(tElectrons)        
        tauNumber = len(tausForHiggs)
                
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
            tauHidx[0] = taus.index(tausForHiggs[0])
            charge=tausForHiggs[0].charge
            for j in range(1,len(tausForHiggs)):
                if (charge!=tausForHiggs[j].charge):
                    tauHidx[1] = taus.index(tausForHiggs[j])
        
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
                if (charge!=taus[j].charge and deltaR(tMuons[0], taus[j])>0.2 and hphotonFilter(taus[j])):
                    tauAllHidx[1] = j
                    
        elif (Category_lveto==2 and len(taus)):
            tauAllHidx[0] = electrons.index(tElectrons[0])
            charge = tElectrons[0].charge
            for j in range(len(taus)):
                if (charge!=taus[j].charge and deltaR(tElectrons[0], taus[j])>0.2 and hphotonFilter(taus[j])):
                    tauAllHidx[1] = j
        
        elif (Category_lveto==3 and len(taus)>1):
            charge="ddd"
            for k in range(0,len(taus)):
                if ( hphotonFilter(taus[k])):
                    tauAllHidx[0] = k
                    charge=taus[k].charge
                    break
            if (tauAllHidx[0]>=0):
                for j in range(tauAllHidx[0],len(taus)):
                    if ( charge!=taus[j].charge and hphotonFilter(taus[j]) ):
                        tauAllHidx[1] = j

        if (Category_lveto==3 and len(taus)>1):
            print "DEBUG", tauAllHidx[1],tauAllHidx[0] ,Category_lveto      
        ### the lepton only categories dont need any tau ID
        ### and once we are here we are sure the pairs are formed in an unique way beacause of pairs+lep veto.
        if (Category_lveto==4):
            Category_LooseTausel=4
            Category_tausel=4
            Category_AllPairs=4
            Category_LoosePairs=4
            Category_pairs=4
            tauHidx[0]=muons.index(lMuons[0])
            tauLooseHidx[0]=muons.index(lMuons[0])
            tauAllHidx[0]=muons.index(lMuons[0])
            tauHidx[1]=muons.index(lMuons[1])
            tauLooseHidx[1]=muons.index(lMuons[1])
            tauAllHidx[1]=muons.index(lMuons[1])
                            
        elif (Category_lveto==5):
            Category_LooseTausel=5
            Category_tausel=5
            Category_AllPairs=5
            Category_LoosePairs=5
            Category_pairs=5
            tauHidx[0]=electrons.index(lElectrons[0])
            tauLooseHidx[0]=electrons.index(lElectrons[0])
            tauAllHidx[0]=electrons.index(lElectrons[0])
            tauHidx[1]=electrons.index(lElectrons[1])
            tauLooseHidx[1]=electrons.index(lElectrons[1])
            tauAllHidx[1]=electrons.index(lElectrons[1])
                            
        elif (Category_lveto==6):
            Category_LooseTausel=6
            Category_tausel=6
            Category_AllPairs=6
            Category_LoosePairs=6
            Category_pairs=6
            tauHidx[0]=electrons.index(lElectrons[0])
            tauLooseHidx[0]=electrons.index(lElectrons[0])
            tauAllHidx[0]=electrons.index(lElectrons[0])
            tauHidx[1]=muons.index(lMuons[0])
            tauLooseHidx[1]=muons.index(lMuons[0])
            tauAllHidx[1]=muons.index(lMuons[0])
            
        
        # visible mass etc for leptonic categories
        if (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_tausel==3):
            Category_pairs=3
            tautauMass=self.invMass(taus[tauHidx[0]],taus[tauHidx[1]])
        elif (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_tausel==2):
            Category_pairs=2
            tautauMass=self.invMass(electrons[tauHidx[0]],taus[tauHidx[1]],0.511/1000.)
        elif (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_tausel==1):
            Category_pairs=1
            tautauMass=self.invMass(muons[tauHidx[0]],taus[tauHidx[1]])
            
        if (tauLooseHidx[0]>=0 and tauLooseHidx[1]>=0 and Category_LooseTausel==3):
            Category_LoosePairs=3
            tautauMassLoose=self.invMass(taus[tauLooseHidx[0]],taus[tauLooseHidx[1]])
        elif (tauLooseHidx[0]>=0 and tauLooseHidx[1]>=0 and Category_LooseTausel==2):
            Category_LoosePairs=2
            tautauMassLoose=self.invMass(electrons[tauLooseHidx[0]],taus[tauLooseHidx[1]], 0.511/1000.)
        elif (tauLooseHidx[0]>=0 and tauLooseHidx[1]>=0 and Category_LooseTausel==1):
            Category_LoosePairs=1
            tautauMassLoose=self.invMass(muons[tauLooseHidx[0]],taus[tauLooseHidx[1]])
            
        if (tauAllHidx[0]>=0 and tauAllHidx[1]>=0 and Category_lveto==3):
            Category_AllPairs=3
            tautauMassAll=self.invMass(taus[tauAllHidx[0]],taus[tauAllHidx[1]])
        elif (tauAllHidx[0]>=0 and tauAllHidx[1]>=0 and Category_lveto==2):
            Category_AllPairs=2
            tautauMassAll=self.invMass(electrons[tauAllHidx[0]],taus[tauAllHidx[1]],0.511/1000.)
        elif (tauAllHidx[0]>=0 and tauAllHidx[1]>=0 and Category_lveto==1):
            Category_AllPairs=1
            tautauMassAll=self.invMass(muons[tauAllHidx[0]],taus[tauAllHidx[1]])
        
        # visible mass etc for leptonic categories
        if (tauAllHidx[0]>=0 and tauAllHidx[1]>=0 and Category_lveto==4):
            tautauMassAll=self.invMass(muons[tauAllHidx[0]],muons[tauAllHidx[1]])
            tautauMass=tautauMassAll
            tautauMassLoose=tautauMassAll
        elif (tauAllHidx[0]>=0 and tauAllHidx[1]>=0 and Category_lveto==5):
            tautauMassAll=self.invMass(electrons[tauAllHidx[0]],electrons[tauAllHidx[1]],0.511/1000.,0.511/1000.)
            tautauMass=tautauMassAll
            tautauMassLoose=tautauMassAll
        elif (tauAllHidx[0]>=0 and tauAllHidx[1]>=0 and Category_lveto==6):
            tautauMassAll=self.invMass(electrons[tauAllHidx[0]],muons[tauAllHidx[1]],0.511/1000.)
            tautauMass=tautauMassAll
            tautauMassLoose=tautauMassAll
            
        jetFilterFlagsLoose=jetFilterFlags
        jetFilterFlagsAll=jetFilterFlags
        for i in range(len(jets)):
            if (Category_pairs==3):
                if (deltaR(jets[i],taus[tauHidx[0]])<0.4):
                    jetFilterFlags[i]=False
                if (deltaR(jets[i],taus[tauHidx[1]])<0.4):
                    jetFilterFlags[i]=False
            elif (Category_pairs==2 or Category_pairs==1):
                if (deltaR(jets[i],taus[tauHidx[1]])<0.4):
                    jetFilterFlags[i]=False
                    
            if (Category_LoosePairs==3):
                if (deltaR(jets[i],taus[tauLooseHidx[0]])<0.4):
                    jetFilterFlagsLoose[i]=False
                if (deltaR(jets[i],taus[tauLooseHidx[1]])<0.4):
                    jetFilterFlagsLoose[i]=False
            elif (Category_LoosePairs==2 or Category_LoosePairs==1):
                if (deltaR(jets[i],taus[tauLooseHidx[1]])<0.4):
                    jetFilterFlagsLoose[i]=False
                    
            if (Category_AllPairs==3):
                if (deltaR(jets[i],taus[tauAllHidx[0]])<0.4):
                    jetFilterFlagsAll[i]=False
                if (deltaR(jets[i],taus[tauAllHidx[1]])<0.4):
                    jetFilterFlagsAll[i]=False
            elif (Category_AllPairs==2 or Category_AllPairs==1):
                if (deltaR(jets[i],taus[tauAllHidx[1]])<0.4):
                    jetFilterFlagsAll[i]=False


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
        self.out.fillBranch("tauLooseHidx",  tauLooseHidx);
        self.out.fillBranch("tauAllHidx",  tauAllHidx);
        self.out.fillBranch("Category",  Category);
        self.out.fillBranch("Category_lveto",  Category_lveto);
        self.out.fillBranch("Category_tausel",  Category_tausel);
        self.out.fillBranch("Category_pairs",  Category_pairs);
        self.out.fillBranch("Category_LooseTausel",  Category_LooseTausel);
        self.out.fillBranch("Category_LoosePairs",  Category_LoosePairs);
        self.out.fillBranch("Category_AllPairs",  Category_AllPairs);
        
        self.out.fillBranch("Jet_Filter",jetFilterFlags)
        self.out.fillBranch("Jet_FilterLoose",jetFilterFlagsLoose)
        self.out.fillBranch("Jet_FilterAll",jetFilterFlagsAll)
        
        return True
    
    
    
HHggtauatauModule2016 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2016") 
HHggtauatauModule2017 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2017") 
HHggtauatauModule2018 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2018") 

HHggtauatauModuleDATA18 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2018") 
HHggtauatauModuleDATA17 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2017") 
HHggtauatauModuleDATA16 = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2016") 
