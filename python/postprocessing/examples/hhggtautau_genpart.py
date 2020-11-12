import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import sys
import copy

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #deltaR, matching etc..



'''statusFlags_bits={0 : "isPrompt", 
1 : "isDecayedLeptonHadron", 
2 : "isTauDecayProduct", 
3 : "isPromptTauDecayProduct", 
4 : "isDirectTauDecayProduct", 
5 : "isDirectPromptTauDecayProduct", 
6 : "isDirectHadronDecayProduct", 
7 : "isHardProcess", 
8 : "fromHardProcess", 
9 : "isHardProcessTauDecayProduct", 
10 : "isDirectHardProcessTauDecayProduct", 
11 : "fromHardProcessBeforeFSR", 
12 : "isFirstCopy", 
13 : "isLastCopy", 
14 : "isLastCopyBeforeFSR" }'''


class HHggtautauGenLevel(Module):

    def __init__(self, isMC, era):
        self.era = era
        self.isMC = isMC
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        
        ## Gen information
        self.out.branch("GenHPhoton1_index", "I");
        self.out.branch("GenHPhoton2_index", "I");
        
        self.out.branch("GenHTauPlus_index", "I");
        self.out.branch("GenHTauMinus_index", "I");
        
        self.out.branch("GenHTauPlus_isHadronic", "B");
        self.out.branch("GenHTauMinus_isHadronic", "B");
        
        self.out.branch("GenHTauPlus_isEle", "B");
        self.out.branch("GenHTauMinus_isEle", "B");
        
        self.out.branch("GenHTauPlus_isMu", "B");
        self.out.branch("GenHTauMinus_isMu", "B");
        
        self.out.branch("GenHadTauPlus_index", "I");
        self.out.branch("GenHadTauMinus_index", "I");

        self.out.branch("GenMuTauPlus_index", "I");
        self.out.branch("GenMuTauMinus_index", "I");

        self.out.branch("GenEleTauPlus_index", "I");
        self.out.branch("GenEleTauMinus_index", "I");
        
        self.out.branch("GenDiphoton_pt", "F");
        self.out.branch("GenDiphoton_eta", "F");
        self.out.branch("GenDiphoton_phi", "F");
        self.out.branch("GenDiphoton_mass", "F");
        self.out.branch("GenDiphoton_dEta", "F");
        self.out.branch("GenDiphoton_dPhi", "F");
        self.out.branch("GenDiphoton_dR", "F");        
                
        self.out.branch("GenDitau_pt", "F");
        self.out.branch("GenDitau_eta", "F");
        self.out.branch("GenDitau_phi", "F");
        self.out.branch("GenDitau_mass", "F");
        self.out.branch("GenDitau_dEta", "F");
        self.out.branch("GenDitau_dPhi", "F");
        self.out.branch("GenDitau_dR", "F");
        
        self.out.branch("GenDitauvis_pt", "F");
        self.out.branch("GenDitauvis_eta", "F");
        self.out.branch("GenDitauvis_phi", "F");
        self.out.branch("GenDitauvis_mass", "F");
        self.out.branch("GenDitauvis_dEta", "F");
        self.out.branch("GenDitauvis_dPhi", "F");
        self.out.branch("GenDitauvis_dR", "F");



    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass    


    def isLastCopyBeforeFSR(self, status):
        if ((status>>14)&1): return True
        else: return False
    
    def isLastCopy(self, status):
        if ((status>>13)&1): return True
        else: return False
    
    def isFirstCopy(self, status):
        if ((status>>12)&1): return True
        else: return False
    
    def isTauDecayProduct(self, status):
        if ((status>>2)&1): return True
        else: return False
    
    def isPromptTauDecayProduct(self, status):
        if ((status>>3)&1): return True
        else: return False
    
    def isDirectTauDecayProduct(self, status):
        if ((status>>4)&1): return True
        else: return False
    
    def isDirectPromptTauDecayProduct(self, status):
        if ((status>>5)&1): return True
        else: return False
    
    def fromH(self, genparticles, genP, origin):
        if (genP.genPartIdxMother > -1):
            if (genparticles[genP.genPartIdxMother].pdgId==25 and genP.pdgId==origin):
                return True
            ##else:
                ##return self.fromH(genparticles, genparticles[genP.genPartIdxMother], origin)
        return False
    
    
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        if self.isMC:
            
            GenHPhoton1_index=-999
            GenHPhoton2_index=-999
            GenHTauPlus_index=-999
            GenHTauMinus_index=-999

            GenHadTauPlus_index=-999
            GenHadTauMinus_index=-999
            GenMuTauPlus_index=-999
            GenMuTauMinus_index=-999
            GenEleTauPlus_index=-999
            GenEleTauMinus_index=-999
        
            GenHTauPlus_isHadronic=False
            GenHTauMinus_isHadronic=False

            GenHTauPlus_isEle=False
            GenHTauMinus_isEle=False

            GenHTauPlus_isMu=False
            GenHTauMinus_isMu=False    
            
            #print GenHTauPlus_index,GenHTauMinus_index,GenHPhoton1_index,GenHPhoton2_index
            #print GenHTauPlus_isHadronic,GenHadTauPlus_index
            #print GenHTauPlus_isMu,GenMuTauPlus_index
            #print GenHTauPlus_isEle,GenEleTauPlus_index
            #print GenHTauMinus_isHadronic,GenHadTauMinus_index
            #print GenHTauMinus_isMu,GenMuTauMinus_index
            #print GenHTauMinus_isEle,GenEleTauMinus_index
         
            
            
            genParticles = list(Collection(event, "GenPart"))
            genVisTau = list(Collection(event, "GenVisTau"))
            
            genHtausPlus=None
            genHtausMinus=None
            genHphotons=[]
            
            genEleTauPlus=[]
            genEleTauMinus=[]
            genMuTauPlus=[]
            genMuTauMinus=[]
            genHadTauPlus=[]
            genHadTauMinus=[]
            
            
            for genP in genParticles:
                if((genP.pdgId==15) and self.isLastCopy(genP.statusFlags) and genP.status==2 and self.fromH(genParticles, genP,15)):
                    genHtausPlus=genP
                if((genP.pdgId==-15) and self.isLastCopy(genP.statusFlags) and genP.status==2 and self.fromH(genParticles, genP,-15)):
                    genHtausMinus=genP
                if((genP.pdgId==13) and self.isTauDecayProduct(genP.statusFlags) and (abs(genParticles[genP.genPartIdxMother].pdgId)==15)):
                    genMuTauPlus.append(genP)
                if((genP.pdgId==-13) and self.isTauDecayProduct(genP.statusFlags) and (abs(genParticles[genP.genPartIdxMother].pdgId)==15)):
                    genMuTauMinus.append(genP)
                if((genP.pdgId==11) and self.isTauDecayProduct(genP.statusFlags) and (abs(genParticles[genP.genPartIdxMother].pdgId)==15) ):
                    genEleTauPlus.append(genP)
                if((genP.pdgId==-11) and self.isTauDecayProduct(genP.statusFlags) and (abs(genParticles[genP.genPartIdxMother].pdgId)==15)):
                    genEleTauMinus.append(genP)
                if(genP.pdgId==22 and self.isLastCopy(genP.statusFlags) and genP.status==1 and self.fromH(genParticles, genP,22)):
                    genHphotons.append(genP)
            
                    
            for genVT in genVisTau:
                if(genVT.charge==-1):
                    genHadTauPlus.append(genVT)
                else:
                    genHadTauMinus.append(genVT)
                    
            print genHphotons
            print genHtausPlus,genHtausMinus
            print genEleTauPlus,genEleTauMinus,genMuTauPlus,genMuTauMinus,genHadTauPlus,genHadTauMinus

            genHphotons.sort(key=lambda x:x.pt, reverse=True)
  
            
            if len (genHphotons) > 0:        
                GenHPhoton1_index=genParticles.index(genHphotons[0])
                if len (genHphotons) > 1:
                    GenHPhoton2_index=genParticles.index(genHphotons[1])
            
            if (genHtausPlus!=None):
                GenHTauPlus_index=genParticles.index(genHtausPlus)
            if (genHtausMinus!=None):
                GenHTauMinus_index=genParticles.index(genHtausMinus)

            if(GenHTauPlus_index>0 and GenHTauMinus_index>0):                   
                
                
                if (len(genHadTauMinus)==1 and len(genMuTauMinus)==0 and len(genEleTauMinus)==0):
                    #hadronic tau minus
                    GenHTauMinus_isHadronic=True
                    GenHadTauMinus_index=genVisTau.index(genHadTauMinus[0])
                    
                elif (len(genHadTauMinus)==0 and len(genMuTauMinus)==1 and len(genEleTauMinus)==0):
                    #muon minus
                    GenHTauMinus_isMu=True
                    GenMuTauMinus_index=genParticles.index(genMuTauMinus[0])
                    
                elif (len(genHadTauMinus)==0 and len(genMuTauMinus)==0 and len(genEleTauMinus)==1):
                    #ele minus
                    GenHTauMinus_isEle=True
                    GenEleTauMinus_index=genParticles.index(genEleTauMinus[0])
                    
                else:
                    
                    dRmin=999
                    for j in genHadTauMinus:
                        dR=deltaR(j,genHtausMinus)
                        if (dR<dRmin):
                            dRmin=dR
                            #hadronic
                            GenHTauMinus_isHadronic=True
                            GenHadTauMinus_index=genVisTau.index(genHadTauMinus[0])
                            GenHTauMinus_isMu=False
                            GenMuTauMinus_index=-999
                            GenHTauMinus_isEle=False
                            GenEleTauMinus_index=-999

                    for j in genMuTauMinus:
                        dR=deltaR(j,genHtausMinus)
                        if (dR<dRmin):
                            dRmin=dR
                            #muon
                            GenHTauMinus_isHadronic=False
                            GenHadTauMinus_index=-999
                            GenHTauMinus_isMu=True
                            GenMuTauMinus_index=-genParticles.index(genMuTauMinus[0])
                            GenHTauMinus_isEle=False
                            GenEleTauMinus_index=-999
                            
                    for j in genEleTauMinus:
                        dR=deltaR(j,genHtausMinus)
                        if (dR<dRmin):
                            dRmin=dR
                            #ele
                            GenHTauMinus_isHadronic=False
                            GenHadTauMinus_index=-999
                            GenHTauMinus_isMu=False
                            GenMuTauMinus_index=-999
                            GenHTauMinus_isEle=True
                            GenEleTauMinus_index=-genParticles.index(genEleTauMinus[0])
                            
                if (len(genHadTauPlus)==1 and len(genMuTauPlus)==0 and len(genEleTauPlus)==0):
                    #hadronic tau minus
                    GenHTauPlus_isHadronic=True
                    GenHadTauPlus_index=genVisTau.index(genHadTauPlus[0])
                    
                elif (len(genHadTauPlus)==0 and len(genMuTauPlus)==1 and len(genEleTauPlus)==0):
                    #muon minus
                    GenHTauPlus_isMu=True
                    GenMuTauPlus_index=genParticles.index(genMuTauPlus[0])
                    
                elif (len(genHadTauPlus)==0 and len(genMuTauPlus)==0 and len(genEleTauPlus)==1):
                    #ele minus
                    GenHTauPlus_isEle=True
                    GenEleTauPlus_index=genParticles.index(genEleTauPlus[0])
                    
                else:
                    
                    dRmin=999
                    for j in genHadTauPlus:
                        dR=deltaR(j,genHtausPlus)
                        if (dR<dRmin):
                            dRmin=dR
                            #hadronic
                            GenHTauPlus_isHadronic=True
                            GenHadTauPlus_index=genVisTau.index(genHadTauPlus[0])
                            GenHTauPlus_isMu=False
                            GenMuTauPlus_index=-999
                            GenHTauPlus_isEle=False
                            GenEleTauPlus_index=-999
                            
                    for j in genMuTauPlus:
                        dR=deltaR(j,genHtausPlus)
                        if (dR<dRmin):
                            dRmin=dR
                            #muon
                            GenHTauPlus_isHadronic=False
                            GenHadTauPlus_index=-999
                            GenHTauPlus_isMu=True
                            GenMuTauPlus_index=-genParticles.index(genMuTauPlus[0])
                            GenHTauPlus_isEle=False
                            GenEleTauPlus_index=-999
                            
                    for j in genEleTauPlus:
                        dR=deltaR(j,genHtausPlus)
                        if (dR<dRmin):
                            dRmin=dR
                            #ele
                            GenHTauPlus_isHadronic=False
                            GenHadTauPlus_index=-999
                            GenHTauPlus_isMu=False
                            GenMuTauPlus_index=-999
                            GenHTauPlus_isEle=True
                            GenEleTauPlus_index=-genParticles.index(genEleTauPlus[0])
                            
            print GenHTauPlus_index,GenHTauMinus_index,GenHPhoton1_index,GenHPhoton2_index
            print GenHTauPlus_isHadronic,GenHadTauPlus_index
            print GenHTauPlus_isMu,GenMuTauPlus_index
            print GenHTauPlus_isEle,GenHadTauPlus_index
            print GenHTauMinus_isHadronic,GenHadTauMinus_index
            print GenHTauMinus_isMu,GenMuTauMinus_index
            print GenHTauMinus_isEle,GenEleTauMinus_index
            
            self.out.fillBranch("GenHTauPlus_index",GenHTauPlus_index)
            self.out.fillBranch("GenHTauMinus_index",GenHTauMinus_index)
            self.out.fillBranch("GenHPhoton1_index",GenHPhoton1_index)
            self.out.fillBranch("GenHPhoton2_index",GenHPhoton2_index)
            
            self.out.fillBranch("GenHTauPlus_isMu",GenHTauPlus_isMu)
            self.out.fillBranch("GenHTauPlus_isEle",GenHTauPlus_isEle)
            self.out.fillBranch("GenHTauPlus_isHadronic",GenHTauPlus_isHadronic)
            self.out.fillBranch("GenHTauMinus_isMu",GenHTauMinus_isMu)
            self.out.fillBranch("GenHTauMinus_isEle",GenHTauMinus_isEle)
            self.out.fillBranch("GenHTauMinus_isHadronic",GenHTauMinus_isHadronic)
            
            self.out.fillBranch("GenHadTauPlus_index",GenHadTauPlus_index)
            self.out.fillBranch("GenEleTauPlus_index",GenEleTauPlus_index)
            self.out.fillBranch("GenMuTauPlus_index",GenMuTauPlus_index)
            self.out.fillBranch("GenMuTauMinus_index",GenMuTauMinus_index)
            self.out.fillBranch("GenEleTauMinus_index",GenEleTauMinus_index)
            self.out.fillBranch("GenHadTauMinus_index",GenHadTauMinus_index)
            
                    
            if(GenHTauPlus_index>0 and GenHTauMinus_index>0 and GenHPhoton1_index>0 and GenHPhoton2_index>0):     
                genP1 = ROOT.TLorentzVector()
                genP2 = ROOT.TLorentzVector()
 
                genP1.SetPtEtaPhiM(genHphotons[0].pt,genHphotons[0].eta,genHphotons[0].phi,0)
                genP2.SetPtEtaPhiM(genHphotons[1].pt,genHphotons[1].eta,genHphotons[1].phi,0)
                self.out.fillBranch("GenDiphoton_pt",(genP1+genP2).Pt())
                self.out.fillBranch("GenDiphoton_eta",(genP1+genP2).Eta())
                self.out.fillBranch("GenDiphoton_phi",(genP1+genP2).Phi())
                self.out.fillBranch("GenDiphoton_mass",(genP1+genP2).M())
                self.out.fillBranch("GenDiphoton_dEta",abs(genHphotons[0].eta-genHphotons[1].eta))
                self.out.fillBranch("GenDiphoton_dR", deltaR(genHphotons[0],genHphotons[1]))
                self.out.fillBranch("GenDiphoton_dPhi", deltaPhi(genHphotons[0],genHphotons[1]))     
                
                genP1.SetPtEtaPhiM(genHtausPlus.pt,genHtausPlus.eta,genHtausPlus.phi,1.777)
                genP2.SetPtEtaPhiM(genHtausMinus.pt,genHtausMinus.eta,genHtausMinus.phi,1.777)
                self.out.fillBranch("GenDitau_pt",(genP1+genP2).Pt())
                self.out.fillBranch("GenDitau_eta",(genP1+genP2).Eta())
                self.out.fillBranch("GenDitau_phi",(genP1+genP2).Phi())
                self.out.fillBranch("GenDitau_mass",(genP1+genP2).M())
                self.out.fillBranch("GenDitau_dEta",abs(genHtausPlus.eta-genHtausMinus.eta))
                self.out.fillBranch("GenDitau_dR", deltaR(genHtausPlus,genHtausMinus))
                self.out.fillBranch("GenDitau_dPhi", deltaPhi(genHtausPlus,genHtausMinus))  
                
                if ((GenHTauPlus_isHadronic or GenHTauPlus_isMu or GenHTauPlus_isEle) and (GenHTauMinus_isMu or GenHTauMinus_isEle or GenHTauMinus_isHadronic)):
                    if GenHTauPlus_isHadronic:
                        p=genVisTau[GenHadTauPlus_index]
                        genP1.SetPtEtaPhiM(p.pt,p.eta,p.phi,p.mass)
                    elif GenHTauPlus_isMu:
                        p=genParticles[GenMuTauPlus_index]
                        genP1.SetPtEtaPhiM(p.pt,p.eta,p.phi,0.105)
                    elif GenHTauPlus_isEle:
                        p=genParticles[GenEleTauPlus_index]
                        genP1.SetPtEtaPhiM(p.pt,p.eta,p.phi,0.511/1000.)
                    if GenHTauMinus_isHadronic:
                        pp=genVisTau[GenHadTauMinus_index]
                        genP2.SetPtEtaPhiM(pp.pt,pp.eta,pp.phi,pp.mass)
                    elif GenHTauMinus_isMu:
                        pp=genParticles[GenMuTauMinus_index]
                        genP2.SetPtEtaPhiM(pp.pt,pp.eta,pp.phi,0.105)
                    elif GenHTauMinus_isEle:
                        pp=genParticles[GenEleTauMinus_index]
                        genP2.SetPtEtaPhiM(pp.pt,pp.eta,pp.phi,0.511/1000.)
                    
                    self.out.fillBranch("GenDitauvis_pt",(genP1+genP2).Pt())
                    self.out.fillBranch("GenDitauvis_eta",(genP1+genP2).Eta())
                    self.out.fillBranch("GenDitauvis_phi",(genP1+genP2).Phi())
                    self.out.fillBranch("GenDitauvis_mass",(genP1+genP2).M())
                    self.out.fillBranch("GenDitauvis_dEta",abs(p.eta-pp.eta))
                    self.out.fillBranch("GenDitauvis_dR", deltaR(p,pp))
                    self.out.fillBranch("GenDitauvis_dPhi", deltaPhi(p,pp))  
                else:
                    self.out.fillBranch("GenDitauvis_pt",-999)
                    self.out.fillBranch("GenDitauvis_eta",-999)
                    self.out.fillBranch("GenDitauvis_phi",-999)
                    self.out.fillBranch("GenDitauvis_mass",-999)
                    self.out.fillBranch("GenDitauvis_dEta",-999)
                    self.out.fillBranch("GenDitauvis_dR",-999)
                    self.out.fillBranch("GenDitauvis_dPhi",-999)
                
            else:
                self.out.fillBranch("GenDiphoton_pt",-999)
                self.out.fillBranch("GenDiphoton_eta",-999)
                self.out.fillBranch("GenDiphoton_phi",-999)
                self.out.fillBranch("GenDiphoton_mass",-999)
                self.out.fillBranch("GenDiphoton_dEta",-999)
                self.out.fillBranch("GenDiphoton_dR",-999)
                self.out.fillBranch("GenDiphoton_dPhi",-999)
                
                self.out.fillBranch("GenDitau_pt",-999)
                self.out.fillBranch("GenDitau_eta",-999)
                self.out.fillBranch("GenDitau_phi",-999)
                self.out.fillBranch("GenDitau_mass",-999)
                self.out.fillBranch("GenDitau_dEta",-999)
                self.out.fillBranch("GenDitau_dR",-999)
                self.out.fillBranch("GenDitau_dPhi",-999)
                
                self.out.fillBranch("GenDitauvis_pt",-999)
                self.out.fillBranch("GenDitauvis_eta",-999)
                self.out.fillBranch("GenDitauvis_phi",-999)
                self.out.fillBranch("GenDitauvis_mass",-999)
                self.out.fillBranch("GenDitauvis_dEta",-999)
                self.out.fillBranch("GenDitauvis_dR",-999)
                self.out.fillBranch("GenDitauvis_dPhi",-999)

                

        return True
                

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

HHggtautauGenLevelModule = lambda : HHggtautauGenLevel(True, "X") 




