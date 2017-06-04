#!/usr/bin/python

import sys, os, random
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QTextEdit, QFileDialog, QSizePolicy,\
    QVBoxLayout, QWidget, QColorDialog, QMdiSubWindow, QCheckBox, QSlider, QMenu, QPushButton
from PyQt5.QtGui import QIcon, QColor
from PyQt5 import QtCore
from PyQt5.Qt import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from Mtb import *
from MtbPlot import *
from InfoWindow import *


class PlotWindow(QWidget):
    mtbGui = None

    def __init__(self, width, height, mtbGui):
        #super().__init__()
        self.mtbGui = mtbGui
        self.createWindow(width, height)
        self.addPlot()
        self.setObjectName(self.mtbGui.mtb.nazwaPliku.toString())

    def createWindow(self, WindowWidth, WindowHeight):
        parent = None
        super(PlotWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(WindowWidth, WindowHeight)
        self.setMinimumSize(QSize(WindowWidth, WindowHeight))
        self.naciskCheckBox = QCheckBox('Nacisk', self)
        self.naciskCheckBox.stateChanged.connect(self.changeNacisk)

        self.linieCheckBox = QCheckBox('Linie', self)
        self.linieCheckBox.move(70, 0)
        self.linieCheckBox.stateChanged.connect(self.changeLinie)

        self.timerSlider = QSlider(Qt.Horizontal, self)
        self.timerSlider.move(130, 0)
        self.timerSlider.setMinimum(0)
        max = self.mtbGui.mtbPlot.momentPomiaruAll[-1:][0]
        self.timerSlider.setMaximum(max)
        self.timerSlider.setValue(max)
        self.timerSlider.valueChanged.connect(self.changeTimer)

        self.timerLabel = QLabel(str(max), self)
        self.timerLabel.move(220, 4)

        self.hideButton = QPushButton('Hide', self)
        self.hideButton.move(270, 0)
        self.hideButton.clicked.connect(self.hideClick)

        self.infoButton = QPushButton('Info', self)
        self.infoButton.move(335, 0)
        self.infoButton.clicked.connect(self.infoClick)
        #self.dialog = InfoWindow(self)

        self.main_widget = QWidget(self)
        self.main_widget.setFocus()
        self.l = QVBoxLayout(self.main_widget)
        self.main_widget.move(0, 20)
        self.main_widget.resize(WindowWidth, WindowHeight)
        #self.mouse
        #QMouseEvent(Type)

    def hideClick(self):
        self.setParent(None)

    def infoClick(self):
        InfoWindow(self, mtbGui=self.mtbGui).show()

    def contextMenuEvent(self, event):
        #QContextMenuEvent.x()
        #print(event.x())
        #event.x()
        #event.y()
        self.menu = QMenu(self)
        firstAction = self.menu.addAction('kolko')
        firstAction.triggered.connect(lambda: self.renameSlot('kolko'))
        self.menu.addAction(firstAction)
        self.menu.popup(QCursor.pos())
        # add other required actions
        #self.menu.popup(QtGui.QCursor.pos())
    def renameSlot(self, event):
        print(event)

    def addPlot(self):
        dc = MyDynamicMplCanvas(self, width=5, height=4, dpi=100, mtbPlot=self.mtbGui.mtbPlot)
        self.mtbGui.plot = dc
        self.l.addWidget(self.mtbGui.plot)

    def changeTimer(self):
        value = self.timerSlider.value()
        self.timerLabel.setText(str(value))
        self.mtbGui.plot.timer[1] = value
        self.mtbGui.plot.update_figure()

    def changeNacisk(self, state):
        if state == Qt.Checked:
            self.mtbGui.plot.nacisk = True
        else:
            self.mtbGui.plot.nacisk = False
        self.mtbGui.plot.update_figure()

    def changeLinie(self, state):
        if state == Qt.Checked:
            self.mtbGui.plot.pokaz_wszystkie_linie = True
        else:
            self.mtbGui.plot.pokaz_wszystkie_linie = False
        self.mtbGui.plot.update_figure()



class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    nacisk = False
    pokaz_wszystkie_linie = False
    mtbPlot = object

    def __init__(self, parent=None, width=5, height=4, dpi=100, mtbPlot=None):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)
        self.mtbPlot = mtbPlot
        #print(mtbPlot)
        self.timer = []
        self.timer.append(0)
        self.timer.append(self.mtbPlot.momentPomiaruAll[-1:][0])

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.compute_initial_figure()

    def compute_initial_figure(self):
        pass

def findElementIn(array, elem):
    for i in range(0, len(array)):
        if array[i] >= elem:
            return i
    return len(array)

class MyDynamicMplCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.update_figure()

    def update_figure(self):
        self.axes.clear()

        #timer obecnie nie wykorzystywany, ale można wykorzystac go do pokazania tylko czesci wyników
        #wystarczy tylko przekazac odpowiednie wartości, a reszta będzie już działac
        #timer = []
        #timer.append(0)
        #timer.append(self.mtbPlot.momentPomiaruAll[-1:][0])

        if self.pokaz_wszystkie_linie:
            index = findElementIn(self.mtbPlot.momentPomiaruAll, int(self.timer[0])), findElementIn(
                self.mtbPlot.momentPomiaruAll, int(self.timer[1]))
        else:
            index = findElementIn(self.mtbPlot.momentPomiaru, int(self.timer[0])), findElementIn(
                self.mtbPlot.momentPomiaru, int(self.timer[1]))
        lim = [min(min(self.mtbPlot.XAll), min(self.mtbPlot.YAll)), max(max(self.mtbPlot.XAll), max(self.mtbPlot.YAll))]
        self.axes.set_xlim(lim)
        self.axes.set_ylim(lim)

        if self.pokaz_wszystkie_linie and self.nacisk:

            self.axes.scatter(self.mtbPlot.XAll[index[0]:index[1]], self.mtbPlot.YAll[index[0]:index[1]],
                        c=self.mtbPlot.naciskKoloryAll[index[0]:index[1]],
                        s=self.mtbPlot.gruboscAll[index[0]:index[1]])
        elif not self.pokaz_wszystkie_linie and self.nacisk:
            self.axes.scatter(self.mtbPlot.X[index[0]:index[1]], self.mtbPlot.Y[index[0]:index[1]],
                        c=self.mtbPlot.naciskKolory[index[0]:index[1]],
                        s=np.linspace(0.5, 0.5, num=len(self.mtbPlot.X[index[0]:index[1]])))
        elif self.pokaz_wszystkie_linie and not self.nacisk:
            self.axes.scatter(self.mtbPlot.XAll[index[0]:index[1]], self.mtbPlot.YAll[index[0]:index[1]],
                        s=self.mtbPlot.gruboscAll[index[0]:index[1]])
        elif not self.pokaz_wszystkie_linie and not self.nacisk:
            self.axes.scatter(self.mtbPlot.X[index[0]:index[1]], self.mtbPlot.Y[index[0]:index[1]],
                        s=np.linspace(0.5, 0.5, num=len(self.mtbPlot.X[index[0]:index[1]])))

        self.draw()