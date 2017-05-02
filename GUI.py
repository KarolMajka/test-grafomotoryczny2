#!/usr/bin/python

import sys, os, random
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication,\
    QTextEdit, QFileDialog, QSizePolicy, QVBoxLayout, QWidget, QMdiSubWindow, QScrollArea
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from Mtb import *
from MtbPlot import *
from PlotGUI import *

def GUILoop():
    app = QApplication(sys.argv)
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    mainWindow = MainWindow(width, height)
    sys.exit(app.exec_())

class MainWindow(QMainWindow):
    mtbGui = None
    width = 1
    height = 1
    mtbFiles = []

    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.initUI()

    def exit(self):
        #print('exit')
        pass


    def tryOpen(self):
        fileName = self.openFileNameDialog()
        if fileName.endswith('.mtb') and os.path.isfile(fileName):
            mtbGui = self.addMtbFile(fileName)
            self.open(mtbGui)

    def open(self, mtbGui):
        self.showPlot(mtbGui)
        self.updateRecentMenu()

    def showPlot(self, mtbGui):
        width = self.width - 60
        height = self.height - 150

        if isinstance(mtbGui, PlotWindow):
            if mtbGui.parent() != None:
                return
            mtbGui.setParent(self.l.parent())
            widget = mtbGui
        else:
            widget = PlotWindow(width, height, mtbGui)
            self.mtbFiles.append(widget)
        #self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, width, (height)*(self.l.count()+1)))
        self.l.addWidget(widget)

    def openFileFromList(self, identifier):
        for mtbFile in self.mtbFiles:
            if mtbFile.mtbGui.mtb.nazwaPliku.toString() == identifier:
                self.open(mtbFile)
                return None
        return "cos nie pyklo"

    def addMtbFile(self, fileName):
        #head, tail = os.path.split(fileName)
        mtbGui = self.loadMtbGUIFile(fileName)
        for mtbFile in self.mtbFiles:
            if mtbFile.mtbGui.mtb.nazwaPliku.toString() == mtbGui.mtb.nazwaPliku.toString():
                return mtbFile
        return mtbGui

    def loadMtbGUIFile(self, fileName):
        mtb = loadMtbFileStructure(fileName)
        mtbPlot = createPlotObjectsFromMtbObjects([mtb])[0]
        return MtbGUI(mtb, mtbPlot)


    def initUI(self):
        self.setGeometry(0, 0, self.width, self.height)
        self.setWindowTitle('Test grafomotoryczny')

        mainMenu = self.menuBar()

        #on mac neccesary
        mainMenu.setNativeMenuBar(False)

        fileMenu = mainMenu.addMenu('File')
        #toolsMenu = mainMenu.addMenu('Tools')
        self.recentMenu = mainMenu.addMenu('Recent')
        self.recentMenu.setEnabled(False)

        openButton = QAction('Open', self)
        openButton.setShortcut('Ctrl+N')
        openButton.setStatusTip('Open mtb file')
        openButton.triggered.connect(self.tryOpen)
        fileMenu.addAction(openButton)

        self.main_widget = QWidget(self)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.l = QVBoxLayout(self.main_widget)
        self.scrollArea = QScrollArea(self.main_widget)
        self.l.addWidget(self.scrollArea)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, self.width-30, self.height-150))
        #self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.l = QHBoxLayout(self.scrollAreaWidgetContents)

        #self.addToToolsMenu(toolsMenu)

        self.show()

    def updateToolsMenu(self):
        self.pokazWszystkieLinieButton.setChecked(self.mtbGui.plot.pokaz_wszystkie_linie)
        self.naciskButton.setChecked(self.mtbGui.plot.nacisk)

    def updateRecentMenu(self):
        self.recentMenu.setEnabled(True)
        self.recentMenu.clear()
        self.mapper = QtCore.QSignalMapper(self)
        for mtbFile in self.mtbFiles:
            name = mtbFile.mtbGui.mtb.nazwaPliku.toString()
            mtbButton = QAction(name, self)
            self.mapper.setMapping(mtbButton, name)
            mtbButton.triggered.connect(self.mapper.map)
            self.recentMenu.addAction(mtbButton)
        self.mapper.mapped['QString'].connect(self.openFileFromList)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open mtb file', "", "All Files (*);;Mtb Files (*.mtb)", options=options)
        return fileName

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                               "All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                 "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)

class MtbGUI(object):
    mtb = object
    mtbPlot = object
    plot = None

    def __init__(self, mtb, mtbPlot):
        self.mtb = mtb
        self.mtbPlot = mtbPlot


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
        timer = []
        timer.append(0)
        timer.append(self.mtbPlot.momentPomiaruAll[-1:][0])

        if self.pokaz_wszystkie_linie:
            index = findElementIn(self.mtbPlot.momentPomiaruAll, int(timer[0])), findElementIn(
                self.mtbPlot.momentPomiaruAll, int(timer[1]))
        else:
            index = findElementIn(self.mtbPlot.momentPomiaru, int(timer[0])), findElementIn(
                self.mtbPlot.momentPomiaru, int(timer[1]))

        self.axes.set_xlim([min(self.mtbPlot.XAll), max(self.mtbPlot.XAll)])
        self.axes.set_ylim([min(self.mtbPlot.YAll), max(self.mtbPlot.YAll)])

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