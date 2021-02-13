import ROOT
import array
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Object 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class NewPair(Module):
    def __init__(self, name="Photon", index="gHidx", newname="selectedPhoton"):
        self.name = name
        self.index = index
        self.newname = newname
        
        ### ref link useful later on
        ### reduced JES uncertainties (see https://twiki.cern.ch/twiki/bin/viewauth/CMS/JECUncertaintySources#Run_2_reduced_set_of_uncertainty)
       
    def beginJob(self):
        pass
    
    def endJob(self):
        pass
    
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        
        self.branches=[]
        for b in inputTree.GetListOfBranches():
            if b.GetName().startswith(self.name+"_"):
                self.branches.append(b.GetName())
        print "remaking branches ---->", self.branches
        
        self.out = wrappedOutputTree
             
        for branchname in self.branches:
            self.out.branch(branchname.replace(self.name, self.newname),  "F", 2);   

        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):    
        objs = list(Collection(event, self.name))
        indices = getattr(event, self.index)
        
        
        for branchname in self.branches:
          value=[-1,-1]
          for i in range(len(indices)):
              index=indices[i]
              if index>=0: 
                  value[i]=getattr(objs[index],branchname.replace(self.name+"_", ""))
          self.out.fillBranch(branchname.replace(self.name, self.newname),  value);   

        
        return True
    
dumpSelectedPhotons   = lambda : NewPair(name="Photon",   index="gHidx",   newname="selectedPhoton") 
dumpSelectedMuons     = lambda : NewPair(name="Muon",     index="tauHidx", newname="selectedMuon") 
dumpSelectedElectrons = lambda : NewPair(name="Electron", index="tauHidx", newname="selectedElectron") 
dumpSelectedTaus      = lambda : NewPair(name="Tau",      index="tauHidx", newname="selectedTau") 
 
