from particles import *

from subprocess import call

import thread
import threading

#
# Visualization
# 

ThreadList = []

def GraphViz(fileName, MainConstituent,  isr_jets, fsr_jets, Ws, Bs, Hs):
	if MainConstituent is None:
		print "Warning in " + fileName + ": MainConstituent is None."
		return 
	diFileName = fileName + ".di"
	pngFileName = fileName + ".png"
	
	f = open(diFileName , 'w')
	f.write("digraph G {\n")
	f.write("graph [nodesep=0.01]\n") 
	
	RecurseParticle(f, MainConstituent, 0, "", 0,  isr_jets, fsr_jets, Ws, Bs, Hs)
	
	f.write("}\n")
	f.close()
	
	#thread.start_new_thread( GraphVizCreate, (diFileName, pngFileName ))
	
	GraphVizCreate (diFileName, pngFileName )
	
	#thread = threading.Thread(None, GraphVizCreate (diFileName, pngFileName ))
	
	#thread.start()
	
	#global ThreadList
	#ThreadList.append(thread)

#def GraphViz_WaitForThreads():
	#print "Waiting for visualization threads to end...",
	#global ThreadList
	#for thread in ThreadList:
		#thread.join()
	#print " done."

def GraphVizCreate(diFileName, pngFileName):
	call(["twopi", diFileName ,"-Tpng","-o",pngFileName ])	
	
def CreateColorChannelFromIndex(index,parity=1):
	color = index * (256-25)
	color = color % 256
	if parity == -1:
		color = 255 - color
	colorString = hex(color)
	result = colorString[2:]
	if len(result) == 1:
		result = "0" + result

	#print str(index) + " (" + str(parity) + ")" + ": " + result
	return result
	
def CreateColorFromParams(jetType,numJet):
	if jetType == "FSR":
		return "00" + CreateColorChannelFromIndex(numJet) + CreateColorChannelFromIndex(numJet,-1)
	elif jetType == "ISR":
		return "FF" + CreateColorChannelFromIndex(numJet) + "00"
	else:
		raise Exception("unknown jet type: '" + jetType + "'")
	
def RecurseParticle(f, p, rec, last, index, isr_jets, fsr_jets, Ws, Bs, Hs, isWDaughter=False, isBDaughter=False, isHDaughter=False):
	
	particleName = GetParticleName( p.pdgId() )
	cs = abs(p.status())
	
	typeString = str(cs)
	colorString = "black"
	
	textColorString = "black"
	
	fillColorString = "white"
	styleString = ""
	
	if cs == 4:
		styleString = ", style=filled"
		fillColorString="deeppink"
	elif 21 <= cs <= 29:
		hardest = True
		fillColorString="yellow"
		styleString = ", style=filled"
	elif 31 <= cs <= 39:
		fillColorString="green"
		styleString = ", style=filled"
	elif 41 <= cs <= 49:
		iSS = True
		#fillColorString="red"
		#styleString = ", style=filled"
	elif 51 <= cs <= 59:
		fSS = True
		#fillColorString="lightblue"
		#styleString = ", style=filled"
	elif 61 <= cs <= 69:
		fillColorString="brown"
		styleString = ", style=filled"
	elif 71 <= cs <= 79:
		fillColorString="gray"
		styleString = ", style=filled"
	
	particleQualifier = last + "H" + str(rec) + "I" + str(index)
	particleLabel = particleName
	particleLabelFinal = particleLabel + "[" + typeString + "]"

			
	if isWDaughter or isBDaughter or isHDaughter :
		colorString = "black"
		textColorString = "black"
		if isWDaughter:
			fillColorString = "red"
			#particleLabelFinal = "<W>"
		if isBDaughter:
			fillColorString = "orange"
			#particleLabelFinal = "<B>"
		if isHDaughter:
			fillColorString = "deeppink"
			#particleLabelFinal = "<H>"
		styleString = ", style=filled"
	
	else:
		
		for w in Ws:
			if p == w:
				isWDaughter = True
				
		for b in Bs:
			if p == b:
				isBDaughter = True
			
		for h in Hs:
			if p == h:
				isHDaughter = True

		if not (isWDaughter or isBDaughter or isHDaughter):

			for numJet, jet in enumerate(isr_jets):

				nDaughters = jet.numberOfDaughters()
				for i in range(0,nDaughters):
					currentCandidate = jet.daughter(i)
					if currentCandidate == p:
						if p.pdgId() <> currentCandidate.pdgId():
							print str(p.pdgId()) + "-" + str(currentCandidate.pdgId())
						#particleLabelFinal = str(numJet)
						colorString = "red"
						textColorString = "black"
						fillColorString='"#'+CreateColorFromParams("ISR",numJet)+'"'
						styleString = ", style=filled"
						
			for numJet, jet in enumerate(fsr_jets):
				nDaughters = jet.numberOfDaughters()
				for i in range(0,nDaughters):
					currentCandidate = jet.daughter(i)
					if currentCandidate == p:
						if p.pdgId() <> currentCandidate.pdgId():
							print str(p.pdgId()) + "-" + str(currentCandidate.pdgId())
						#particleLabelFinal = str(numJet)
						colorString = "blue"
						textColorString = "black"
						fillColorString='"#'+CreateColorFromParams("FSR",numJet)+'"'
						styleString = ", style=filled"
	
	attrib = styleString + ", color=" + colorString + ", fillcolor=" + fillColorString + ", fontcolor=" + textColorString
	
	f.write(particleQualifier + "[label=\"" + particleLabelFinal + "\"" + attrib + "];\n")
	if last <> "":
		f.write(last + " -> " + particleQualifier + ";\n")
	n = p.numberOfDaughters();
	for i in range(0,n):
		RecurseParticle(f, p.daughter(i), rec + 1, particleQualifier, i,  isr_jets, fsr_jets, Ws, Bs, Hs, isWDaughter, isBDaughter, isHDaughter)
