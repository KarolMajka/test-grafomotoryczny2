#!/usr/bin/python

import colorsys
import numpy as np

class Plot(object):
    X = []
    Y = []
    naciskKolory = []
    momentPomiaru = []
    XAll = []
    YAll = []
    naciskKoloryAll = []
    gruboscAll = []
    momentPomiaruAll = []
    def __init__(self, X, Y, naciskKolory, XAll, YAll, naciskKoloryAll, gruboscAll, momentPomiaru, momentPomiaruAll):
        self.X = np.array(X)
        self.Y = np.array(Y)
        self.naciskKolory = np.array(naciskKolory)
        self.XAll = np.array(XAll)
        self.YAll = np.array(YAll)
        self.naciskKoloryAll = np.array(naciskKoloryAll)
        self.gruboscAll = np.array(gruboscAll)
        self.momentPomiaru = np.array(momentPomiaru)
        self.momentPomiaruAll = np.array(momentPomiaruAll)


def getColorForPlot(nacisk, minValue):
    # 0 - wysoki nacisk
    # 1/3 - niski nacisk
    # value przyjmuje wartosci 0-1023 (0 - niski nacisk, 1023 - wysoki nacisk)
    # Jeśli nacisk jest mniejszy niż minimalny dopuszczalny, to uznajemy, że nie rysował

    if minValue >= nacisk:
        return colorsys.hsv_to_rgb(0.0, 0.0, 0.0)
    nacisk /= 1024
    nacisk = 1 - nacisk
    nacisk /= 3
    return colorsys.hsv_to_rgb(nacisk, 1.0, 1.0)


def createPlotObjectsFromMtbObjects(mtbFiles):
    #X, Y, nacisk kolory, X(bez usuwania nacisku), Y(bez usuwania nacisku), nacisk kolory, grubosc kolory, moment pomiaru, moment pomiaru (bez usuwania nacisku)
    plot = [[],[],[],[],[],[],[], [], [],[],[]]
    plotObject = []
    minimalnyNacisk = 64
    for i in range(0, len(mtbFiles)):
        plot[0].append([])
        plot[1].append([])
        plot[2].append([])
        plot[3].append([])
        plot[4].append([])
        plot[5].append([])
        plot[6].append([])
        plot[7].append([])
        plot[8].append([])
        for j in range(0, len(mtbFiles[i].pakietyDanych)):
            if mtbFiles[i].pakietyDanych[j].nacisk > minimalnyNacisk:
                plot[0][i].append(mtbFiles[i].pakietyDanych[j].polozenieX)
                plot[1][i].append(mtbFiles[i].pakietyDanych[j].polozenieY)
                plot[2][i].append(getColorForPlot(mtbFiles[i].pakietyDanych[j].nacisk, minimalnyNacisk))
                plot[6][i].append(1)
                plot[7][i].append(mtbFiles[i].pakietyDanych[j].momentPomiaru)
            else:
                plot[6][i].append(0.03)
            plot[3][i].append(mtbFiles[i].pakietyDanych[j].polozenieX)
            plot[4][i].append(mtbFiles[i].pakietyDanych[j].polozenieY)
            plot[5][i].append(getColorForPlot(mtbFiles[i].pakietyDanych[j].nacisk, minimalnyNacisk))
            plot[8][i].append(mtbFiles[i].pakietyDanych[j].momentPomiaru)
        plotObject.append(Plot(plot[0][i], plot[1][i], plot[2][i], plot[3][i], plot[4][i], plot[5][i], plot[6][i], plot[7][i], plot[8][i]))
    return plotObject
