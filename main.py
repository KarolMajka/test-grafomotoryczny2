#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button, RadioButtons
from tkinter import *
from ipywidgets import *
from IPython.display import display
from Mtb import *
from MtbPlot import *
from GUI import *

#----------------------------------------------------------------------------------------

def getAllMtbFilesFrom(folderName):
    mtbFiles = []
    for name in os.listdir(folderName):
        if name.endswith('.mtb') and os.path.isfile(folderName + '/' + name):
            mtbFile = loadMtbFileStructure(folderName + '/' + name)
            mtbFiles.append(mtbFile)
        elif os.path.isdir(folderName + '/' + name):
            mtbFiles += getAllMtbFilesFrom(folderName + '/' + name)
    return mtbFiles

#----------------------------------------------------------------------------------------



#mtbFiles = getAllMtbFilesFrom('./dane/33100000000 (M)')  # /33100000000 (M)
#print("created mtbFiles")
#plotObject = createPlotObjectsFromMtbObjects(mtbFiles)
#print("entering tkinter")
GUILoop()







#def findElementIn(array, elem):
#    for i in range(0, len(array)):
#        if array[i] >= elem:
#            return i
#    return len(array)
#
#
#def plotSelect(i):
#    i = int(i)
#
#    def plotConfiguration(Show_All_Lines, pokaz_nacisk, timer):
#        if Show_All_Lines:
#            index = findElementIn(plotObject[i].momentPomiaruAll, int(timer[0])), findElementIn(
#                plotObject[i].momentPomiaruAll, int(timer[1]))
#        else:
#            index = findElementIn(plotObject[i].momentPomiaru, int(timer[0])), findElementIn(
#                plotObject[i].momentPomiaru, int(timer[1]))
#        axes = plt.gca()
#        axes.set_xlim([min(plotObject[i].XAll), max(plotObject[i].XAll)])
#        axes.set_ylim([min(plotObject[i].YAll), max(plotObject[i].YAll)])
#
#        if Show_All_Lines and pokaz_nacisk:
#            plt.scatter(plotObject[i].XAll[index[0]:index[1]], plotObject[i].YAll[index[0]:index[1]],
#                        c=plotObject[i].naciskKoloryAll[index[0]:index[1]],
#                        s=plotObject[i].gruboscAll[index[0]:index[1]])
#        elif not Show_All_Lines and pokaz_nacisk:
#            plt.scatter(plotObject[i].X[index[0]:index[1]], plotObject[i].Y[index[0]:index[1]],
#                        c=plotObject[i].naciskKolory[index[0]:index[1]],
#                        s=np.linspace(0.5, 0.5, num=len(plotObject[i].X[index[0]:index[1]])))
#        elif Show_All_Lines and not pokaz_nacisk:
#            plt.scatter(plotObject[i].XAll[index[0]:index[1]], plotObject[i].YAll[index[0]:index[1]],
#                        s=plotObject[i].gruboscAll[index[0]:index[1]])
#        elif not Show_All_Lines and not pokaz_nacisk:
#            plt.scatter(plotObject[i].X[index[0]:index[1]], plotObject[i].Y[index[0]:index[1]],
#                        s=np.linspace(0.5, 0.5, num=len(plotObject[i].X[index[0]:index[1]])))
#        plt.show()
#
#    timerSlider = widgets.IntRangeSlider(min=0, max=plotObject[i].momentPomiaruAll[-1:][0], step=1,
#                                         value=[0, plotObject[i].momentPomiaruAll[-1:][0]])
#    interact(plotConfiguration, Show_All_Lines=False, pokaz_nacisk=False, timer=timerSlider)
#
#
#interact(plotSelect, i=np.linspace(0, len(mtbFiles) - 1, num=len(mtbFiles), dtype=int).tolist())