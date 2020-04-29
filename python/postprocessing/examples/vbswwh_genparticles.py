import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import sys
import copy

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import * #deltaR, matching etc..

class VBSWWHGenLevel(Module):

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
        self.out.branch("GenBQuark1_index", "I");
        self.out.branch("GenBQuark2_index", "I");
        
        self.out.branch("GenBJet1_index", "I");
        self.out.branch("GenBJet2_index", "I");
        
        self.out.branch("GenVBSJet1_index", "I");
        self.out.branch("GenVBSJet2_index", "I");
        
        self.out.branch("GenLep1_index", "I");
        self.out.branch("GenLep2_index", "I");
        
        self.out.branch("GenNeutrino1_index", "I");
        self.out.branch("GenNeutrino2_index", "I");
        
        self.out.branch("GenBB_pt", "F");
        self.out.branch("GenBB_eta", "F");
        self.out.branch("GenBB_phi", "F");
        self.out.branch("GenBB_mass", "F");
        self.out.branch("GenBB_dEta", "F");
        self.out.branch("GenBB_dPhi", "F");
        self.out.branch("GenBB_dR", "F");
                        
        self.out.branch("GenBJets_pt", "F");
        self.out.branch("GenBJets_eta", "F");
        self.out.branch("GenBJets_phi", "F");
        self.out.branch("GenBJets_mass", "F");     
        
        self.out.branch("GenVBSJets_pt", "F");
        self.out.branch("GenVBSJets_eta", "F");
        self.out.branch("GenVBSJets_phi", "F");
        self.out.branch("GenVBSJets_mass", "F");
        self.out.branch("GenVBSJets_dEta", "F");
        self.out.branch("GenVBSJets_dPhi", "F");
        self.out.branch("GenVBSJets_dR", "F");
        
        #self.out.branch("W1_pt","F")
        #self.out.branch("W1_eta","F")
        #self.out.branch("W1_phi","F")
        #self.out.branch("W1_mass","F")        
        #self.out.branch("W2_pt","F")
        #self.out.branch("W2_eta","F")
        #self.out.branch("W2_phi","F")
        #self.out.branch("W2_mass","F")
        
        self.out.branch("nGenStatus2bHad", "I");
        self.out.branch("nGenH","I")
        self.out.branch("nGenZ","I")          
        self.out.branch("nGenW","I")
        self.out.branch("nGenTop","I")
        self.out.branch("nGenWlep","I")
        self.out.branch("nGenWtau","I")


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    
    def statusFlags_dict(self, bit):
        Dict={0 : "isPrompt", 
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
              14 : "isLastCopyBeforeFSR" }
        return Dict[bit] 

    def isLastCopy(self, status):
        if ((status>>13)&1): return True
        else: return False
    
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        if self.isMC:
            genParticles = list(Collection(event, "GenPart"))
            genJets = list(Collection(event, "GenJet"))
            
            nGenStatus2bHad = 0
            nGenH = 0
            nGenZ = 0         
            nGenW = 0
            nGenTop = 0
            nGenWlep = 0   
            nGenWtau = 0               
            
            genP_index=0
            
            genBQuarks=[]
            genWleps=[]
            genWnus=[]
            
            for genP in genParticles:
                if ((abs(genP.pdgId)/100)%10==5 or (abs(genP.pdgId)/1000)%10==5):
                    if genP.status==2:                    
                        nGenStatus2bHad=nGenStatus2bHad+1
                if(abs(genP.pdgId)==6 and self.isLastCopy(genP.statusFlags)): 
                    nGenTop=nGenTop+1
                if(abs(genP.pdgId)==23 and self.isLastCopy(genP.statusFlags)):
                    nGenW+=1
                if(abs(genP.pdgId)==24 and self.isLastCopy(genP.statusFlags)):
                    nGenZ+=1
                if(abs(genP.pdgId)==25 and self.isLastCopy(genP.statusFlags)):
                    nGenH+=1
                if((abs(genP.pdgId)==13 or abs(genP.pdgId)==11) and genP.genPartIdxMother > -1 and (abs(genParticles[genP.genPartIdxMother].pdgId)==23)):
                    nGenWlep+=1
                    genWleps.append(genP)  
                if((abs(genP.pdgId)==14 or abs(genP.pdgId)==12) and genP.genPartIdxMother > -1 and (abs(genParticles[genP.genPartIdxMother].pdgId)==23)):
                    nGenWlep+=1
                    genWnus.append(genP)                 
                if((abs(genP.pdgId)==15) and genP.genPartIdxMother > -1 and (abs(genParticles[genP.genPartIdxMother].pdgId)==23)): #what to save for tau leptons??
                    nGenWtau+=1
                if (abs(genP.pdgId)==5 and genP.genPartIdxMother > -1 and abs(genParticles[genP.genPartIdxMother].pdgId)==25):
                    genBQuarks.append(genP)                    
                    
                genP_index+=1 #increase counter for indices
                
                
            self.out.fillBranch("nGenStatus2bHad",nGenStatus2bHad)
            self.out.fillBranch("nGenH",nGenH)
            self.out.fillBranch("nGenZ",nGenZ)
            self.out.fillBranch("nGenW",nGenW)
            self.out.fillBranch("nGenTop",nGenTop)            
            self.out.fillBranch("nGenWlep",nGenWlep)
            self.out.fillBranch("nGenWtau",nGenWtau)
            
            GenBQuark1_index=-999
            GenBQuark2_index=-999
            GenBJet1_index=-999
            GenBJet2_index=-999

            GenVBSJet1_index=-999
            GenVBSJet2_index=-999

            GenLep1_index=-999
            GenLep2_index=-999
            GenNeutrino1_index=-999
            GenNeutrino2_index=-999
                      
            genBQuarks.sort(key=lambda x:x.pt, reverse=True)
            genWleps.sort(key=lambda x:x.pt, reverse=True)
            genWnus.sort(key=lambda x:x.pt, reverse=True)
            
            if len (genWleps) > 0:        
                GenLep1_index=genParticles.index(genWleps[0])
                if len (genWleps) > 0:
                    GenLep2_index=genParticles.index(genWleps[1])
                    
            if len (genWnus) > 0:        
                GenNeutrino1_index=genParticles.index(genWnus[0])
                if len (genWnus) > 0:
                    GenNeutrino2_index=genParticles.index(genWnus[1])
                    
            if len (genBQuarks) > 0:        
                GenBQuark1_index=genParticles.index(genBQuarks[0])
                if len (genBQuarks) > 0:
                    GenBQuark2_index=genParticles.index(genBQuarks[1])

            genBQ1 = ROOT.TLorentzVector()
            genBQ2 = ROOT.TLorentzVector()
            genBJ1 = ROOT.TLorentzVector()
            genBJ2 = ROOT.TLorentzVector()
            genVBSJ1 = ROOT.TLorentzVector()
            genVBSJ2 = ROOT.TLorentzVector()
            
            if len (genBQuarks) > 1:
                genBQ1.SetPtEtaPhiM(genBQuarks[0].pt,genBQuarks[0].eta,genBQuarks[0].phi,4.2)
                genBQ2.SetPtEtaPhiM(genBQuarks[1].pt,genBQuarks[1].eta,genBQuarks[1].phi,4.2)
                self.out.fillBranch("GenBB_pt",(genBQ1+genBQ2).Pt())
                self.out.fillBranch("GenBB_eta",(genBQ1+genBQ2).Eta())
                self.out.fillBranch("GenBB_phi",(genBQ1+genBQ2).Phi())
                self.out.fillBranch("GenBB_mass",(genBQ1+genBQ2).M())
                self.out.fillBranch("GenBB_dEta",abs(genBQuarks[0].eta-genBQuarks[1].eta))
                self.out.fillBranch("GenBB_dR", deltaR(genBQuarks[0],genBQuarks[1]))
                self.out.fillBranch("GenBB_dPhi", deltaPhi(genBQuarks[0],genBQuarks[1]))                               
            else:
                self.out.fillBranch("GenBB_pt",-999)
                self.out.fillBranch("GenBB_eta",-999)
                self.out.fillBranch("GenBB_phi",-999)
                self.out.fillBranch("GenBB_mass",-999)
                self.out.fillBranch("GenBB_dEta",-999)
                self.out.fillBranch("GenBB_dR",-999)
                self.out.fillBranch("GenBB_dPhi",-999)

            ##Closest gen jet to b-parton:
            
            genjetsForHBB = [x for x in genJets if (1)]
            if len (genBQuarks) > 0:
                genjetsForHBB.sort(key=lambda x:deltaR(x,genBQuarks[0])) 
                GenBJet1_index=genJets.index(genjetsForHBB[0])
            if len (genBQuarks) > 1:
                genjetsForHBB.sort(key=lambda x:deltaR(x,genBQuarks[1])) 
                GenBJet2_index=genJets.index(genjetsForHBB[0]) if genJets.index(genjetsForHBB[0])!=GenBJet1_index else genJets.index(genjetsForHBB[1]) 

            self.out.fillBranch("GenBJet1_index",GenBJet1_index)
            self.out.fillBranch("GenBJet2_index",GenBJet2_index)
            
            if GenBJet2_index>-1:
                genBJ1.SetPtEtaPhiM(genJets[genjet_idx1].pt,genJets[genjet_idx1].eta,genJets[genjet_idx1].phi,genJets[genjet_idx1].mass) 
                genBJ2.SetPtEtaPhiM(genJets[genjet_idx2].pt,genJets[genjet_idx2].eta,genJets[genjet_idx2].phi,genJets[genjet_idx2].mass) 
                self.out.fillBranch("GenBJets_pt",(genBJ1+genBJ2).Pt())
                self.out.fillBranch("GenBJets_eta",(genBJ1+genBJ2).M())
                self.out.fillBranch("GenBJets_phi",(genBJ1+genBJ2).M())
                self.out.fillBranch("GenBJets_mass",(genBJ1+genBJ2).M())
            else:
                self.out.fillBranch("GenBJets_pt",-999)
                self.out.fillBranch("GenBJets_eta",-999)
                self.out.fillBranch("GenBJets_phi",-999)
                self.out.fillBranch("GenBJets_mass",-999)
                
            genjetsForVBF = [x for x in genJets if (x.partonFlavour>0 and x.partonFlavour<6 and genJets.index(x)!=GenBJet2_index and genJets.index(x)!=GenBJet1_index)]
            genjetsForVBF.sort(key=lambda x:x.pt,reverse=True)
            
            if len(genjetsForVBF)>1:                    
                GenVBSJet1_index=genJets.index(genjetsForVBF[0])
                GenVBSJet2_index=genJets.index(genjetsForVBF[1])
                genVBSJ1.SetPtEtaPhiM(genJets[GenVBSJet1_index].pt,genJets[GenVBSJet1_index].eta,genJets[GenVBSJet1_index].phi,genJets[GenVBSJet1_index].mass) 
                genVBSJ2.SetPtEtaPhiM(genJets[GenVBSJet2_index].pt,genJets[GenVBSJet2_index].eta,genJets[GenVBSJet2_index].phi,genJets[GenVBSJet2_index].mass) 
                self.out.fillBranch("GenVBSJets_pt",(genVBSJ1+genVBSJ2).Pt())
                self.out.fillBranch("GenVBSJets_eta",(genVBSJ1+genVBSJ2).M())
                self.out.fillBranch("GenVBSJets_phi",(genVBSJ1+genVBSJ2).M())
                self.out.fillBranch("GenVBSJets_mass",(genVBSJ1+genVBSJ2).M())
                self.out.fillBranch("GenVBSJets_dEta",abs(genjetsForVBF[0].eta-genjetsForVBF[1].eta))
                self.out.fillBranch("GenVBSJets_dR", deltaR(genjetsForVBF[0],genjetsForVBF[1]))
                self.out.fillBranch("GenVBSJets_dPhi", deltaPhi(genjetsForVBF[0],genjetsForVBF[1]))  
            else:
                self.out.fillBranch("GenVBSJets_pt",-999)
                self.out.fillBranch("GenVBSJets_eta",-999)
                self.out.fillBranch("GenVBSJets_phi",-999)
                self.out.fillBranch("GenVBSJets_mass",-999)
                self.out.fillBranch("GenVBSJets_dEta",-999)
                self.out.fillBranch("GenVBSJets_dR",-999)
                self.out.fillBranch("GenVBSJets_dPhi",-999) 
                

        return True
                

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

VBSWWHGenLevelModule = lambda : VBSWWHGenLevel(True, "X") 




