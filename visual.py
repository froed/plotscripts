from particles import *

from subprocess import call

import thread
import threading

#
# Visualization
# 

ThreadList = []

def GraphViz(fileName, MainConstituent):
	diFileName = fileName + ".di"
	pngFileName = fileName + ".png"
	
	f = open(diFileName , 'w')
	f.write("digraph G {\n")
	f.write("graph [nodesep=0.01]\n") 
	
	RecurseParticle(f, MainConstituent, 0, "", 0)
	
	f.write("}\n")
	f.close()
	
	thread.start_new_thread( GraphVizCreate, (diFileName, pngFileName ))
	
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
	
def RecurseParticle(f, p, rec, last, index):
	
	particleName = GetParticleName( p.pdgId() )
	cs = abs(p.status())
	
	typeString = str(cs)
	colorString = "black"
	fillColorString = "white"
	styleString = ""
	
	if cs == 4:
		styleString = ", style=filled"
		fillColorString="deeppink"
	if 21 <= cs <= 29:
		hardest = True
		#typeString = "H"
		#colorString = "yellow"
		fillColorString="yellow"
		styleString = ", style=filled"
	elif 31 <= cs <= 39:
		fillColorString="green"
		styleString = ", style=filled"
	elif 41 <= cs <= 49:
		iSS = True
		#typeString = "ISS"
		#colorString = "red"
		fillColorString="red"
		styleString = ", style=filled"
	elif 51 <= cs <= 59:
		fSS = True
		#typeString = "FSS"
		#colorString = "blue"
		fillColorString="lightblue"
		styleString = ", style=filled"
	elif 61 <= cs <= 69:
		#typeString = "FSS"
		#colorString = "blue"
		fillColorString="brown"
		styleString = ", style=filled"
	elif 71 <= cs <= 79:
		#typeString = "FSS"
		#colorString = "blue"
		fillColorString="gray"
		styleString = ", style=filled"
	#else:
		#typeString = str(cs)
	
	particleQualifier = last + "H" + str(rec) + "I" + str(index)
	particleLabel = particleName
	
	attrib = styleString + ", color=" + colorString + ", fillcolor=" + fillColorString
	
	f.write(particleQualifier + "[label=\"" + particleLabel + "[" + typeString + "]" + "\"" + attrib + "];\n")
	if last <> "":
		f.write(last + " -> " + particleQualifier + ";\n")
	n = p.numberOfDaughters();
	for i in range(0,n):
		RecurseParticle(f, p.daughter(i), rec + 1, particleQualifier, i)