#Script to extract histograms from the Root Tree, that is produced by Pythia8 in CMSSW
#Usage: TODO

from DataFormats.FWLite import Events, Handle
from math import pi
import sys 
from glob import glob
import os

import ROOT
from ROOT import TH1F, TFile, TTree, TString, gSystem

# sibling modules
import config
import visual
from particles import *
from runparams import *
from argparser import *
from histogram import *

#-------------------------------------------------#
#First use FW Lite from CMSSW
#-------------------- FW Lite --------------------#
cmsswbase = TString.getenv("CMSSW_BASE")

print 'Loading FW Lite setup.\n'
gSystem.Load("libFWCoreFWLite.so")
ROOT.AutoLibraryLoader.enable()
gSystem.Load("libDataFormatsFWLite.so")
gSystem.Load("libDataFormatsPatCandidates.so")
#-------------------------------------------------#


class ExtractHistos(object):
	def run(self, runParams):
			
		outputFileObject = TFile(runParams.outputFile,"RECREATE")
			
		for currentCutIndex, currentCut in enumerate(config.pTCuts):
		
			events = Events (runParams.inputFileList)
			
			currentCutString = str(currentCut) #variable for names of histograms
			#Definition of the Histogram
			#Jet Histogram
			njets = Histogram (outputFileObject, "HnJets"+currentCutString, "Number of Jets "+currentCutString, 15, -0.5, 14.5)
			pt = Histogram(outputFileObject, "Hpt"+currentCutString,"Gen-Jet pt "+currentCutString,100,0,300)
			phi = Histogram(outputFileObject, "Hphi"+currentCutString,"Gen-Jet Phi "+currentCutString,50,-pi,pi)
			theta = Histogram(outputFileObject, "Htheta"+currentCutString,"Gen-Jet Theta "+currentCutString,50,0,pi)
			energy = Histogram(outputFileObject, "Henergy"+currentCutString,"Gen-Jet Energy "+currentCutString,100,0,600)
			firstjetpt = Histogram(outputFileObject, "HfirstJetpt"+currentCutString,"Pt of hardest Gen-Jet "+currentCutString, 100,0,300)
			firstjeteta = Histogram(outputFileObject, "H1sJeteta"+currentCutString,"Eta of hardest Gen-Jet "+currentCutString,50,-5,5)
			secondjetpt = Histogram(outputFileObject, "HsecondJetpt"+currentCutString,"Pt of 2nd hardest Gen-Jet "+currentCutString, 100,0,300)
			isrjetpt = Histogram(outputFileObject, "Hisrjetpt"+currentCutString, "Pt of ISR-Jets "+currentCutString,100,0,300)
			fsrjetpt = Histogram(outputFileObject, "Hfsrjetpt"+currentCutString, "Pt of FSR-Jets "+currentCutString,100,0,300)
			nIsrJets = Histogram(outputFileObject, "HnIsrJets"+currentCutString,"Number of ISR Jets per Event "+currentCutString, 15, -0.5, 14.5)
			nFsrJets = Histogram(outputFileObject, "HnFsrJets"+currentCutString,"Number of FSR Jets per Event "+currentCutString, 15, -0.5, 14.5)
			
			# create handle outside of loop
			# Handle and lable are pointing at the Branch you want
			handle  = Handle ('std::vector<reco::GenJet>')
			label = ("ak5GenJets")
			infohandle = Handle ('<GenEventInfoProduct>')
			
			#ROOT.gROOT.SetStyle('Plain') # white background
			#Loop through all Events and Fill the Histogram
			print 'Filling new jet histograms with ptcut: '+currentCutString+'GeV'
			enumber = 0
			print "handle_label",handle, label
			print "Total Events: " + str(events.size())
			if not config.useDebugOutput:
				sys.stdout.write("[                    ]\r[")
				sys.stdout.flush()
			percentage20 = 0 
			for currentEventIndex, currentEvent in enumerate(events):
			
				if config.useDebugOutput:
					print "Event #" + str(currentEventIndex)
				else:
					percentageNow = 20. * currentEventIndex / events.size()
					if percentageNow >= percentage20+1:
						percentage20 = percentage20 + 1 
						sys.stdout.write('.')
						sys.stdout.flush()	
				if currentEventIndex <> 1:
					continue
				currentEvent.getByLabel (label, handle)
				GenJets = handle.product()
				currentEvent.getByLabel ("generator", infohandle)
				Infos = infohandle.product()
				nJets = 0
				firstJetpt = 0
				secondJetpt = 0
				firstJeteta = 0
				nISRJets = 0
				nFSRJets = 0
				eventweight = Infos.weight()
				
				thisEventHasBeenDiGraphed = False
					
				for currentJetIndex, currentJet in enumerate(GenJets):
					if currentJet.pt() >= currentCut and abs(currentJet.eta()) <= config.etaCut:
						nJets = nJets + 1
						pt.fill(eventweight,currentJet.pt())
						phi.fill(eventweight,currentJet.phi())
						theta.fill(eventweight,currentJet.theta())
						energy.fill(eventweight,currentJet.energy())
						
						# ISR/FSR implementation		
						jetMother = currentJet.getJetConstituents()
						
						hardest = False
						iSS = False
						fSS = False
								
						particle = jetMother[0]
								
						while(True):
							oldParticle = particle
							try:
								cs = abs(particle.status())
								if config.useDebugOutput:
									print ( GetParticleName( particle.pdgId() ) ),
									print cs,
								
								if 21 <= cs <= 29:
									hardest = True
									if config.useDebugOutput:
										print ( "[H]" ),
								if 41 <= cs <= 49:
									iSS = True
									if config.useDebugOutput:
										print ( "[IS]" ),
								if 51 <= cs <= 59:
									fSS = True
									if config.useDebugOutput:
										print ( "[FS]" ),
								if config.useDebugOutput:
									print (" <- "),
								particle = particle.mother()
								particle.mother() # this shall throw
							except ReferenceError:
								if config.useDebugOutput:
									print "."
								
								if config.useVisualization and not thisEventHasBeenDiGraphed:
									visual.GraphViz(currentEventIndex, oldParticle)
									thisEventHasBeenDiGraphed = True
									
								break
							#break
						if not hardest and not fSS and iSS:
							isrjetpt.fill(eventweight,currentJet.pt())
							nISRJets = nISRJets + 1
							if config.useDebugOutput:
								print ( "[ISR++]" ) 
						if hardest and fSS:
							fsrjetpt.fill(eventweight,currentJet.pt())
							nFSRJets = nFSRJets + 1
							if config.useDebugOutput: 
								print ( "[FSR++]" )
						if currentJet.pt() >= firstJetpt and currentJet.pt() >= secondJetpt:
							secondJetpt = firstJetpt
							firstJetpt = currentJet.pt()
							firstJeteta = currentJet.eta()
						elif currentJet.pt() >= secondJetpt and currentJet.pt() <= firstJetpt:
							secondJetpt = currentJet.pt()
							enumber=enumber+1
						firstjetpt.fill(eventweight,firstJetpt)
						secondjetpt.fill(eventweight,secondJetpt)
						firstjeteta.fill(eventweight,firstJeteta)
				njets.fill(eventweight,nJets)
				nIsrJets.fill(eventweight,min(15,nISRJets))
				nFsrJets.fill(eventweight,min(15,nFSRJets))
				
			#write all histograms in the output file. After they are wrote, they are getting deleted (s. write() method)
			pt.write()
			phi.write()
			theta.write()
			energy.write()
			firstjetpt.write()
			secondjetpt.write()
			firstjeteta.write()
			njets.write()
			isrjetpt.write()
			fsrjetpt.write()
			nIsrJets.write()
			nFsrJets.write()
			#delete all variables, that are used again in the next loop
			del handle
			del label
			del infohandle
			del events
			sys.stdout.write('.\n')
			sys.stdout.flush()


if __name__ == '__main__': 
	argParser = ArgParser(sys.argv)
	extractHistos = ExtractHistos()
	extractHistos.run(argParser.runParams)
    