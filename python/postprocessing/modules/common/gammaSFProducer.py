import ROOT
import os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module 

import json,array

class gammaSFProducer(Module):
    def __init__(self, sysnames=["MCScale", "MCScaleGain", "Material", "ShowerShape", "FNU", "MCSmear"]):
        #load helper modules if any
        #load data files
        self.sysnames=sysnames
        with open('%s/src/PhysicsTools/NanoAODTools/data/egamma/data_pho.txt' % os.environ['CMSSW_BASE'] ) as json_file:
            self.data = json.load(json_file)
        self.EGMCorrector=ROOT.EnergyScaleCorrection("PhysicsTools/NanoAODTools/data/egamma/ScalesSmearings/Run2018_Step2Closure_CoarseEtaR9Gain_v2")
        
    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        
        for sys in self.sysnames:
            for ud in ["Up", "Down"]:
                self.out.branch("Photon_pt_"+sys+ud, "F", lenVar="nPhoton")
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def getSFUpDown(self, sys, values):
        info=self.data[sys]
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
            return info["uncertainties"][j]
        else:
            return 0

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        photons = Collection(event, "Photon")
        run = getattr(event, "run") 
        
        pts=np.array([pho.pt for pho in photons])
        
        for sys in self.sysnames:
            if sys=="Material":
                sf_photons = np.array([ self.getSFUpDown("materialBinsMoriond17",[pho.eta,pho.r9]) for pho in photons])
                pt_up=pts*(1+sf_photons)
                pt_down=pts*(1-sf_photons)
                self.out.fillBranch("Photon_pt_"+sys+"Up", pt_up)
                self.out.fillBranch("Photon_pt_"+sys+"Down", pt_down)
            elif sys=="FNU":
                sf_photons = np.array([ self.getSFUpDown("FNUFBins",[pho.eta,pho.r9]) for pho in photons])
                pt_up=pts*(1+sf_photons)
                pt_down=pts*(1-sf_photons)
                self.out.fillBranch("Photon_pt_"+sys+"Up", pt_up)
                self.out.fillBranch("Photon_pt_"+sys+"Down", pt_down)
            elif sys=="ShowerShape":
                sf_photons = np.array([ self.getSFUpDown("showerShapeBins",[abs(pho.eta),pho.r9]) for pho in photons])
                pt_up=pts*(1+sf_photons)
                pt_down=pts*(1-sf_photons)
                self.out.fillBranch("Photon_pt_"+sys+"Up", pt_up)
                self.out.fillBranch("Photon_pt_"+sys+"Down", pt_down)
            elif sys=="MCScale":
                sf_photons = np.array([ self.EGMCorrector.scaleCorrUncert(run, pho.pt, abs(pho.eta), pho.r9, 1) for pho in photons])
                pt_up=pts*(1+sf_photons)
                pt_down=pts*(1-sf_photons)
                self.out.fillBranch("Photon_pt_"+sys+"Up", pt_up)
                self.out.fillBranch("Photon_pt_"+sys+"Down", pt_down)
            elif sys=="MCScaleGain":
                sf_photons = np.array([ self.EGMCorrector.scaleCorrUncert(run, pho.pt, abs(pho.eta), pho.r9, 1) for pho in photons])
                pt_up=pts*(1+sf_photons)
                pt_down=pts*(1-sf_photons)
                self.out.fillBranch("Photon_pt_"+sys+"Up", pt_up)
                self.out.fillBranch("Photon_pt_"+sys+"Down", pt_down)
            elif sys=="MCSmear":
                sf_photons = np.array([ self.EGMCorrector.smearingSigma(run, pho.pt, abs(pho.eta), pho.r9, 1, 1, 1) for pho in photons])
                pt_up=pts*(1+sf_photons)
                pt_down=pts*(1-sf_photons)
                self.out.fillBranch("Photon_pt_"+sys+"Up", pt_up)
                self.out.fillBranch("Photon_pt_"+sys+"Down", pt_down)
            else:
                print "ANOTHER TYPE"
                #need to read a text file in c++ probably
                #methods
                #auto shift_val = scaler_.scaleCorr(run_number_, y.et(), y.superCluster()->eta(), y.full5x5_r9(), gain, uncBitMask_);
                #auto shift_err = scaler_.scaleCorrUncert(run_number_, y.et(), y.superCluster()->eta(), y.full5x5_r9(), gain, uncBitMask_);
                #auto sigma = scaler_.smearingSigma(run_number_, y.et(), y.superCluster()->eta(), y.full5x5_r9(), gain, ((float)syst_shift.first), ((float)syst_shift.second));
        
        
        return True


gammaSF = lambda : gammaSFProducer(sysnames=["MCScale", "MCScaleGain", "Material", "ShowerShape", "FNU", "MCSmear"])
