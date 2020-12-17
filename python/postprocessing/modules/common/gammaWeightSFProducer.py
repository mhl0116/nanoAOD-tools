import ROOT
import os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module 

import json,array


class gammaWeightSFProducer(Module):
    
    def __init__(self, sysnames=["electronVeto", "presel", "looseMva"]):
        self.sysnames=sysnames
        with open('%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/photon/data.txt' % os.environ['CMSSW_BASE'] ) as json_file:
            self.data = json.load(json_file)
            
    def beginJob(self):
        pass
    
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for sys in self.sysnames:
            self.out.branch("evWeight_"+sys,  "F");
            for ud in ["Up", "Down"]:
                self.out.branch("evWeight_"+sys+ud,  "F");
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def getSFCentralUpDown(self, sys, values):
        
        info=self.data[sys+"Bins"]
        bins=info['bins']
        indexbin=-1
        
        for i in range(len(values)):
            var1=values[i]
            bins=info['bins'][i]            
            for j in range(max(indexbin,0),len(bins)):
                if var1<max(bins[j]) and var1>=min(bins[j]):
                    indexbin=j
                    break

        if indexbin>=0:
            return info["values"][j], info["uncertainties"][j]
        else:
            return 1,0


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        photons = list(Collection(event, "Photon"))
        gHidx = getattr(event, "gHidx") 
        weight={}
        for sys in self.sysnames:
            weight[sys]=1.
            for ud in ["Up", "Down"]:
                weight[sys+ud]=1.
        if gHidx[0]>=0 and gHidx[1]>=0:
            for sys in self.sysnames:
                photon1_SCeta=photons[gHidx[0]].isScEtaEB+2*photons[gHidx[0]].isScEtaEE
                photon1_r9=photons[gHidx[0]].r9
                photon2_SCeta=photons[gHidx[1]].isScEtaEB+2*photons[gHidx[1]].isScEtaEE
                photon2_r9=photons[gHidx[1]].r9
                SFCentralUpDown1=self.getSFCentralUpDown(sys, [photon1_SCeta,photon1_r9])
                SFCentralUpDown2=self.getSFCentralUpDown(sys, [photon2_SCeta,photon2_r9])
                weight[sys]=SFCentralUpDown1[0]*SFCentralUpDown2[0]
                weight[sys+"Up"]=(SFCentralUpDown1[0]+SFCentralUpDown1[1])*(SFCentralUpDown2[0]+SFCentralUpDown2[1])
                weight[sys+"Down"]=(SFCentralUpDown1[0]-SFCentralUpDown1[1])*(SFCentralUpDown2[0]-SFCentralUpDown2[1])
        
        for sys in self.sysnames:
            self.out.fillBranch("evWeight_"+sys,  weight[sys]);
            for ud in ["Up", "Down"]:
                self.out.fillBranch("evWeight_"+sys+ud,  weight[sys+ud]);
        
        return True
    
    
gammaWeightSF = lambda : gammaWeightSFProducer(sysnames=["electronVeto", "presel", "looseMva"])
