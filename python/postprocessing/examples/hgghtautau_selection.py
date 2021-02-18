import ROOT
import array
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Object 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

import os, math

base = os.getenv("CMSSW_BASE")
arch = os.getenv("SCRAM_ARCH")

ROOT.gROOT.ProcessLine(".L %s/lib/%s/libTauAnalysisSVfitTF.so"%(base, arch))
ROOT.gROOT.ProcessLine(".L %s/lib/%s/libTauAnalysisClassicSVfit.so"%(base, arch))
ROOT.gROOT.ProcessLine(".L %s/src/PhysicsTools/NanoAODTools/python/postprocessing/helpers//SVFitFunc.cc+"%base)


class HHggtautauProducer(Module):
    def __init__(self, jetSelection, muSelection, eSelection, data, year="2016", hadtau1="Loose", hadtau2="Loose"):
        self.jetSel = jetSelection
        self.muSel = muSelection
        self.eSel = eSelection
        self.data = data
        self.year = year
        self.hadtau1 = hadtau1
        self.hadtau2 = hadtau2
        self.postfix = hadtau1+(hadtau2 if hadtau1!=hadtau2 else "")
        
        ### ref link useful later on
        ### reduced JES uncertainties (see https://twiki.cern.ch/twiki/bin/viewauth/CMS/JECUncertaintySources#Run_2_reduced_set_of_uncertainty)
       
    def beginJob(self):
        pass
    
    def endJob(self):
        pass
    
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        
        self.out = wrappedOutputTree
                
        self.out.branch("pt_tautau"+self.postfix,  "F");   
        self.out.branch("eta_tautau"+self.postfix,  "F"); 
        self.out.branch("phi_tautau"+self.postfix,  "F"); 
        self.out.branch("m_tautau"+self.postfix,  "F"); 
        self.out.branch("dR_tautau"+self.postfix,  "F");
        
        self.out.branch("pt_tautauSVFit"+self.postfix,  "F");   
        self.out.branch("eta_tautauSVFit"+self.postfix,  "F"); 
        self.out.branch("phi_tautauSVFit"+self.postfix,  "F"); 
        self.out.branch("m_tautauSVFit"+self.postfix,  "F"); 
        self.out.branch("dR_tautauSVFit"+self.postfix,  "F");
        
        self.out.branch("dR_ggtautau"+self.postfix,  "F");
        self.out.branch("dPhi_ggtautau"+self.postfix,  "F");
        self.out.branch("dR_ggtautauSVFit"+self.postfix,  "F");
        self.out.branch("dPhi_ggtautauSVFit"+self.postfix,  "F");
        
        self.out.branch("selectedTau_ptSVFit",  "F", 2);   
        self.out.branch("selectedTau_etaSVFit",  "F", 2); 
        self.out.branch("selectedTau_phiSVFit",  "F", 2); 
        self.out.branch("selectedTau_mSVFit",  "F", 2);
        
        self.out.branch("selectedMuon_ptSVFit",  "F", 2);   
        self.out.branch("selectedMuon_etaSVFit",  "F", 2); 
        self.out.branch("selectedMuon_phiSVFit",  "F", 2); 
        self.out.branch("selectedMuon_mSVFit",  "F", 2); 
        
        self.out.branch("selectedElectron_ptSVFit",  "F", 2);   
        self.out.branch("selectedElectron_etaSVFit",  "F", 2); 
        self.out.branch("selectedElectron_phiSVFit",  "F", 2); 
        self.out.branch("selectedElectron_mSVFit",  "F", 2); 
        
        self.out.branch("tauHidx"+self.postfix,  "I", 2);
        self.out.branch("Category_tausel"+self.postfix,   "I");
        self.out.branch("Category_pairs"+self.postfix,   "I");
        
        self.out.branch("Jet_Filter"+self.postfix,  "O", 1, "nJet");    

        
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
   
    def analyze(self, event):
        
        """process event, return True (go to next module) or False (fail, go to next event)"""
        
        electrons = list(Collection(event, "Electron"))
        muons = list(Collection(event, "Muon"))
        jets = list(Collection(event, "Jet"))        
        taus = list(Collection(event, "Tau"))
        photons = list(Collection(event, "Photon"))
        MET = Object(event, "MET")
        
        gHidx = getattr(event, "gHidx")
        tauHidx = getattr(event, "taulepHidx")
        Category_lveto = getattr(event, "Category_lvetob")
        jetlepFilterFlags = getattr(event, "Jet_Filter")
        
        v1 = ROOT.TLorentzVector()
        v2 = ROOT.TLorentzVector()
        
        tautauMass=-1
        Category_tausel = -1
        Category_pairs = -1

        hphotonFilter = lambda j : ((deltaR(j,photons[gHidx[0]])>0.2 if gHidx[0]>=0 else 1) and (deltaR(j,photons[gHidx[1]])>0.2 if gHidx[1]>=0 else 1))
        
        jetFilterFlags = jetlepFilterFlags

        tausForHiggs=[]

        deepTauId_vsJet={"Medium":16, "Loose":8, "VLoose":4, "VVLoose":2, "VVVLoose":1}

        #if Category_lveto==1:
            ##muonic decay
            #tausForHiggs = [x for x in taus if (x.pt>20 and abs(x.eta)<2.3 and x.idDecayModeNewDMs and 
                                                #x.idDeepTau2017v2p1VSe>=4 and #VLoose
                                                #x.idDeepTau2017v2p1VSjet>=deepTauId_vsJet[self.hadtau1] and #choosing the WP for one tau
                                                #x.idDeepTau2017v2p1VSmu>=8 and #Tight
                                                #abs(x.dz) < 0.2 and hphotonFilter(x))]       
        
        #elif Category_lveto==2:
            ##electron decay
            #tausForHiggs = [x for x in taus if (x.pt>20 and  abs(x.eta)<2.3 and x.idDecayModeNewDMs and 
                                                #x.idDeepTau2017v2p1VSe>=32 and #Tight
                                                #x.idDeepTau2017v2p1VSjet>=deepTauId_vsJet[self.hadtau1] and #choosing the WP for one tau
                                                #x.idDeepTau2017v2p1VSmu>=8 and #Tight
                                                #abs(x.dz) < 0.2 and hphotonFilter(x))]           
            
            
        #elif Category_lveto==3:
            #tausForHiggs = [x for x in taus if (x.pt>20 and abs(x.eta)<2.3  and x.idDecayModeNewDMs and 
                                                #x.idDeepTau2017v2p1VSe>=2 and #VVLoose
                                                #(x.idDeepTau2017v2p1VSjet>=deepTauId_vsJet[self.hadtau1] or x.idDeepTau2017v2p1VSjet>=deepTauId_vsJet[self.hadtau2]) and #choosing the WP for both tau
                                                #x.idDeepTau2017v2p1VSmu>=1 and #VLoose
                                                #abs(x.dz) < 0.2 and hphotonFilter(x))]
                                                
        #one channel only selection
        tausForHiggs = [x for x in taus if (x.pt>20 and 
                                            abs(x.eta)<2.3  and 
                                            x.idDecayModeNewDMs and 
                                            x.idDeepTau2017v2p1VSe>=2 and #VVLoose
                                            (x.idDeepTau2017v2p1VSjet>=deepTauId_vsJet[self.hadtau1] or x.idDeepTau2017v2p1VSjet>=deepTauId_vsJet[self.hadtau2]) and #choosing the WP for both tau
                                            x.idDeepTau2017v2p1VSmu>=1 and #VLoose
                                            abs(x.dz) < 0.2 and 
                                            hphotonFilter(x))
                        ]
            
        
        if (Category_lveto==1 and len(tausForHiggs)>0):
            Category_tausel=1
        elif (Category_lveto==2 and len(tausForHiggs)>0):
            Category_tausel=2
        elif (Category_lveto==3 and len(tausForHiggs)>1):
            Category_tausel=3
        
        if (Category_tausel==1 and len(tausForHiggs)):
            tauToMuon = muons[tauHidx[0]] # assigned if running after lepton selection
            charge = tauToMuon.charge
            for j in range(len(tausForHiggs)):
                if (charge!=tausForHiggs[j].charge and deltaR(tausForHiggs[j],tauToMuon)>0.2):
                    tauHidx[1] = taus.index(tausForHiggs[j])
                    
        elif (Category_tausel==2 and len(tausForHiggs)):
            tauToEle = electrons[tauHidx[0]] # assigned if running after lepton selection
            charge = tauToEle.charge
            for j in range(len(tausForHiggs)):
                if (charge!=tausForHiggs[j].charge and deltaR(tausForHiggs[j],tauToEle)>0.2):
                    tauHidx[1] = taus.index(tausForHiggs[j])
        
        elif (Category_tausel==3):
            charge=0
            for tauCand in tausForHiggs:
                if (tauCand.idDeepTau2017v2p1VSjet>=deepTauId_vsJet[self.hadtau1]):
                    tauHidx[0] = taus.index(tauCand)
                    charge=tauCand.charge
            if (charge!=0):
                for tauCand in tausForHiggs:
                    if (charge*tauCand.charge<0 and tauCand.idDeepTau2017v2p1VSjet>=deepTauId_vsJet[self.hadtau2]):
                        tauHidx[1] = taus.index(tauCand)

        # visible mass etc for leptonic categories
        #add SVFit mass for categories 1,2,3
        tautauMassSVFit=-1
        covMET_XX=MET.covXX
        covMET_XY=MET.covXY
        covMET_YY=MET.covYY
        measuredMETx=MET.pt*math.cos(MET.phi)
        measuredMETy=MET.pt*math.sin(MET.phi)
        index1=tauHidx[0]
        index2=tauHidx[1]
        
        if (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_tausel==3):
            Category_pairs=3
            tautauMass=self.invMass(taus[tauHidx[0]],taus[tauHidx[1]])
            #print ROOT.SVfit_results( measuredMETx, measuredMETy, covMET_XX, covMET_XY, covMET_YY, 
            #                            taus[index1].decayMode, taus[index2].decayMode, Category_pairs, 0, 
            #                            taus[index1].pt,taus[index1].eta,taus[index1].phi,taus[index1].mass, 
            #                            taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass )
            
        elif (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_tausel==2):
            Category_pairs=2
            tautauMass=self.invMass(electrons[tauHidx[0]],taus[tauHidx[1]],0.511/1000.)
            #print ROOT.SVfit_results( measuredMETx, measuredMETy, covMET_XX, covMET_XY, covMET_YY, 
            #                            1, taus[index2].decayMode, Category_pairs, 0, 
            #                            electrons[index1].pt,electrons[index1].eta,electrons[index1].phi,0.51100e-3,
            #                            taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass)
            
        elif (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_tausel==1):
            Category_pairs=1
            tautauMass=self.invMass(muons[tauHidx[0]],taus[tauHidx[1]])
            #print ROOT.SVfit_results( measuredMETx, measuredMETy, covMET_XX, covMET_XY, covMET_YY, 
            #                            1, taus[index2].decayMode, Category_pairs, 0, 
            #                            muons[index1].pt,muons[index1].eta,muons[index1].phi,0.10566,
            #                            taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass )

        
        # visible mass etc for leptonic categories
        if (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_lveto==4):
            Category_tausel=4
            Category_pairs=4
            tautauMass=self.invMass(muons[tauHidx[0]],muons[tauHidx[1]])
            #print ROOT.SVfit_results( measuredMETx, measuredMETy, covMET_XX, covMET_XY, covMET_YY, 
                                        #1, taus[index2].decayMode, Category_pairs, 0, 
                                        #electrons[index1].pt,electrons[index1].eta,electrons[index1].phi,0.51100e-3,
                                        #taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass)

        elif (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_lveto==5):
            Category_tausel=5
            Category_pairs=5
            tautauMass=self.invMass(electrons[tauHidx[0]],electrons[tauHidx[1]],0.511/1000.,0.511/1000.)
            #print ROOT.SVfit_results( measuredMETx, measuredMETy, covMET_XX, covMET_XY, covMET_YY, 
                                        #1, taus[index2].decayMode, Category_pairs, 0, 
                                        #electrons[index1].pt,electrons[index1].eta,electrons[index1].phi,0.51100e-3,
                                        #taus[index2].pt,taus[index2].eta,taus[index2].phi,taus[index2].mass)

        elif (tauHidx[0]>=0 and tauHidx[1]>=0 and Category_lveto==6):
            Category_tausel=6
            Category_pairs=6
            tautauMass=self.invMass(electrons[tauHidx[0]],muons[tauHidx[1]],0.511/1000.)
            #print ROOT.SVfit_results( measuredMETx, measuredMETy, covMET_XX, covMET_XY, covMET_YY, 
                                        #1, taus[index2].decayMode, Category_pairs, 0, 
                                        #electrons[index1].pt,electrons[index1].eta,electrons[index1].phi,0.51100e-3,
                                        #muons[index2].pt,muons[index2].eta,muons[index2].phi,muons[index2].mass)

        for i in range(len(jets)):
            if (Category_pairs==3):
                if (deltaR(jets[i],taus[tauHidx[0]])<0.4):
                    jetFilterFlags[i]=False
                if (deltaR(jets[i],taus[tauHidx[1]])<0.4):
                    jetFilterFlags[i]=False
            elif (Category_pairs==2 or Category_pairs==1):
                if (deltaR(jets[i],taus[tauHidx[1]])<0.4):
                    jetFilterFlags[i]=False

        
        self.out.fillBranch("Jet_Filter"+self.postfix, jetFilterFlags)
        self.out.fillBranch("m_tautauSVFit"+self.postfix, tautauMassSVFit)   
        self.out.fillBranch("m_tautau"+self.postfix, tautauMass)   
        self.out.fillBranch("tauHidx"+self.postfix,  tauHidx)
        self.out.fillBranch("Category_tausel"+self.postfix, Category_tausel)
        self.out.fillBranch("Category_pairs"+self.postfix, Category_pairs)
        
        return True
    
    
    
HHggtautauModule2016LL = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2016", hadtau1="Loose", hadtau2="Loose") 
HHggtautauModule2017LL = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2017", hadtau1="Loose", hadtau2="Loose") 
HHggtautauModule2018LL = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2018", hadtau1="Loose", hadtau2="Loose") 

HHggtautauModule2016MM = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2016", hadtau1="Medium", hadtau2="Medium") 
HHggtautauModule2017MM = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2017", hadtau1="Medium", hadtau2="Medium") 
HHggtautauModule2018MM = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2018", hadtau1="Medium", hadtau2="Medium") 

HHggtautauModule2016LVVV = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2016", hadtau1="Loose", hadtau2="VVVLoose") 
HHggtautauModule2017LVVV = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2017", hadtau1="Loose", hadtau2="VVVLoose") 
HHggtautauModule2018LVVV = lambda : HHggtautauProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2018", hadtau1="Loose", hadtau2="VVVLoose") 

