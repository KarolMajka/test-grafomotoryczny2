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

class InfoWindow(QMainWindow):
    mtbGui = None
    def __init__(self, parent=None, mtbGui=None):
        super(InfoWindow, self).__init__(parent)
        mtbGui=self.mtbGui
        self.createWindow()

    def createWindow(self):
        pass