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