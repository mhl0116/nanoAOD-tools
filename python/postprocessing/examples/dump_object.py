import ROOT
import array
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Object 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class HHggtautauProducer(Module):
    def __init__(self, name="Photon", index="gHidx", n=0, newname="leadingPhoton"):
        self.name = name
        self.index = index
        self.n=n
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
            self.out.branch(branchname.replace(self.name, self.newname),  "F");   

        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):    
        objs = list(Collection(event, self.name))
        index = getattr(event, self.index)[self.n]

        for branchname in self.branches:
            value=-1
            if index>=0: 
                value=getattr(objs[index],branchname.replace(self.name+"_", ""))
            self.out.fillBranch(branchname.replace(self.name, self.newname),  value);   

        
        return True
    
dumpLeadingPhoton = lambda : HHggtautauProducer(name="Photon", index="gHidx", n=0, newname="leadingPhoton") 

 
