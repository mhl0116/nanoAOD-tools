#include "TauAnalysis/ClassicSVfit/interface/ClassicSVfit.h"
#include "TauAnalysis/ClassicSVfit/interface/MeasuredTauLepton.h"
#include "TauAnalysis/ClassicSVfit/interface/svFitHistogramAdapter.h"
//#include "TauAnalysis/SVfitTF/interface/HadTauTFCrystalBall2.h"

#include "TauAnalysis/ClassicSVfit/interface/FastMTT.h"

using namespace classic_svFit;

double SVfit_mass(float measuredMETx, float measuredMETy, float covMET_XX, float covMET_XY, float covMET_YY,int tauDecay_mode1, int tauDecay_mode2, int category1, int category2, float tau1_pt,float  tau1_eta, float tau1_phi, float tau1_mass, float tau2_pt, float tau2_eta, float tau2_phi, float tau2_mass)
{
	double diTauSVfit_mass;

	TMatrixD covMET(2, 2);
	covMET[0][0] = covMET_XX;
	covMET[0][1] = covMET_XY;
	covMET[1][0] = covMET_XY;
	covMET[1][1] = covMET_YY;

	// define lepton four vectors
	std::vector<MeasuredTauLepton> measuredTauLeptons;
	if ( category1 == 1 ){
		measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToMuDecay, tau1_pt, tau1_eta, tau1_phi, 0.10566));
	}
	else if ( category1 == 2 ){
		measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToElecDecay, tau1_pt, tau1_eta, tau1_phi, 0.51100e-3));
	}
	else {
		measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToHadDecay, tau1_pt, tau1_eta, tau1_phi, tau1_mass, tauDecay_mode1));
	}

	measuredTauLeptons.push_back(MeasuredTauLepton(MeasuredTauLepton::kTauToHadDecay,  tau2_pt, tau2_eta, tau2_phi,  tau2_mass, tauDecay_mode2));

	//Run FastMTT
	FastMTT aFastMTTAlgo;
	aFastMTTAlgo.run(measuredTauLeptons, measuredMETx, measuredMETy, covMET);
	LorentzVector ttP4 = aFastMTTAlgo.getBestP4();
	diTauSVfit_mass = ttP4.M();

	return diTauSVfit_mass;
}
