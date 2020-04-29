import ROOT
import array
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Object 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class VBSWWHProducer(Module):
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
        self.out.branch("bbMass",  "F");
        self.out.branch("qqMass",  "F");
        self.out.branch("muonNumber",  "I");  
        self.out.branch("electronNumber",  "I");  
        self.out.branch("hJidx",  "I", 2);
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def mqq(self, jets):
        j1 = ROOT.TLorentzVector()
        j2 = ROOT.TLorentzVector()
        j1.SetPtEtaPhiM(jets[0].pt_nom, jets[0].eta, jets[0].phi, jets[0].mass_nom)
        j2.SetPtEtaPhiM(jets[1].pt_nom, jets[1].eta, jets[1].phi, jets[1].mass_nom)
        return (j1+j2).M()
        
    def analyze(self, event):
        
        """process event, return True (go to next module) or False (fail, go to next event)"""
        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        jets = list(Collection(event, "Jet"))
        
        if (len(filter(self.muSel,muons)) < 2 or len(filter(self.eSel,electrons))<2): return False        
        muonNumber = len(filter(self.muSel,muons))
        electronNumber = len(filter(self.eSel,electrons))
        
        muonfilter = lambda j : (j.muonIdx1==-1 or muons[j.muonIdx1].pfRelIso04_all>0.25 or not muons[j.muonIdx1].mediumId or muons[j.muonIdx1].corrected_pt<20) and (j.muonIdx2==-1 or muons[j.muonIdx2].iso>0.25 or not muons[j.muonIdx2].mediumId or muons[j.muonIdx2].corrected_pt<20)
        
        electronfilter = lambda j : (j.electronIdx1==-1 or electrons[j.electronIdx1].pfRelIso03_all>0.25 or abs(electrons[j.electronIdx1].dz) > 0.2 or abs(electrons[j.electronIdx1].dxy) > 0.05) and(j.electronIdx2==-1 or electrons[j.electronIdx2].pfRelIso03_all>0.25 or abs(electrons[j.electronIdx2].dz) > 0.2 or abs(electrons[j.electronIdx2].dxy) > 0.05)     

        jetFilter1      = lambda j : (j.jetId>0 and (j.pt>50 or j.puId>0  ) and abs(j.eta)<4.7 and (abs(j.eta)<2.5 or j.puId>6 or j.pt>50))
        jetFilter2      = lambda j : (j.jetId>0 and (j.pt>50 or j.puId>0  ) and abs(j.eta)<4.7 )
        #jetFilter2_2017 = lambda j : (j.jetId>0 and (j.pt>50 or j.puId17>0) and abs(j.eta)<4.7 )
        #jetFilter3_2017 = lambda j : (j.jetId>0 and (j.pt>50 or j.puId17>0) and abs(j.eta)<4.7 ) and (j.puId17 > 6 or abs(j.eta) < 2.6 or abs(j.eta) > 3.0 )
                
        jetsNolep = [j for j in jets if (muonfilter(j) or electronfilter(j))]   
        if len(jetsNolep) < 2: return False #N==4 jets expected but...    
        
        hJidx=[-1,-1]
        bbMass = 0
        
        jetsForHiggs = [x for x in jetsNolep if (jetFilter1(x) or jetFilter2(x)) and x.pt_nom>20 and abs(x.eta)<2.5]
        if (len(jetsForHiggs) >= 2): 
            hJets = sorted(jetsForHiggs ,key=lambda j : j.btagDeepFlavB, reverse=True)[0:2]
            hJidx[0] = jets.index(hJets[0])
            hJidx[1] = jets.index(hJets[1])

        bbMass = self.mqq(hJets)
         
        passAtLeastOne=False
        
        jetsNolepNobb=jetsNolep
        jetsNolepNobb.remove(hJets[0])
        jetsNolepNobb.remove(hJets[1])

        sortedJets=sorted(jetsNolepNobb,key=lambda j : j.pt_nom, reverse=True)
        jetsCriteria1=[j for j in sortedJets if jetFilter1(j)]
        jetsCriteria2=[j for j in sortedJets if jetFilter2(j)]
        if ( len(jetsCriteria1)>=2 and jetsCriteria1[0].pt_nom > 35 and jetsCriteria1[1].pt_nom > 25 and self.mqq(jetsCriteria1) > 250 ) : passAtLeastOne=True
        if ( len(jetsCriteria2)>=2 and jetsCriteria2[0].pt_nom > 35 and jetsCriteria2[1].pt_nom > 25 and self.mqq(jetsCriteria2) > 250 ) : passAtLeastOne=True
 
        qqMass = 0   
  
        if not passAtLeastOne : return False
              
        # decorrelated JER
        jerBinName = []
        if not self.data:
            etabins=[0,1.93,2.5,3.139]
            ptbins=[0,50]
            jerBinName = ["JEReta%spt%s"%(n,m) for n in range(len(etabins)) for m in range(len(ptbins))]
            
            for j in jetsNolep:
                binEta = len(etabins)-1
                binPt = len(ptbins)-1
                for n in range(len(etabins)-1) : 
                    if abs(j.eta) > etabins[n] and  abs(j.eta) < etabins[n+1] : binEta = n
                for m in range(len(ptbins)-1) :  
                    if j.pt > ptbins[m] and j.pt < ptbins[m+1] : binPt = m
                #print "test pteta ", abs(j.eta), " \t", j.pt, " \t", binEta, " \t", binPt, " \t", "JEReta%spt%s"%(binEta,binPt), " \t  ", jerBinName                
                for k in jerBinName : setattr(j, k, j.pt_nom if k == "JEReta%spt%s"%(binEta,binPt) else j.pt)

        self.out.fillBranch("bbMass",bbMass)
        self.out.fillBranch("qqMass",qqMass)
        self.out.fillBranch("muonNumber",muonNumber)
        self.out.fillBranch("electronNumber",electronNumber)
        self.out.fillBranch("hJidx",hJidx)   
        return True
    
    
    
VBSWWHModule2016 = lambda : VBSWWHProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2016") 
VBSWWHModule2017 = lambda : VBSWWHProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2017") 
VBSWWHModule2018 = lambda : VBSWWHProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = False, year="2018") 

VBSWWHModuleDATA18 = lambda : VBSWWHProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2018") 
VBSWWHModuleDATA17 = lambda : VBSWWHProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2017") 
VBSWWHModuleDATA16 = lambda : VBSWWHProducer(jetSelection= lambda j : j.pt > 15, muSelection= lambda mu : mu.pt > 9, eSelection= lambda e : e.pt > 9, data = True, year="2016") 
 
