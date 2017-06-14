#!/usr/bin/python

import sys, os, random
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication,\
    QTextEdit, QFileDialog, QSizePolicy, QVBoxLayout, QWidget, QMdiSubWindow, QScrollArea, QTableWidget, QTableWidgetItem
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
        self.mtbGui = mtbGui
        self.createWindow()

    def createWindow(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(3)

        self.tableWidget.setItem(0, 0, QTableWidgetItem("nacisk"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("predkosc"))
        self.tableWidget.setItem(0, 2, QTableWidgetItem("inne parametry"))

        self.tableWidget.setParent(self)
        pass