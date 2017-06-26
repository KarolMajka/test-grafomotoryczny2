import sys

from PyQt5.QtCore import Qt, QLineF, QRectF
from PyQt5.QtWidgets import (QLabel, QApplication, QFileDialog, QMainWindow, QWidget, QHBoxLayout, QAction, QScrollArea,
                             QVBoxLayout, QSlider, QCheckBox)
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPainterPath, QBrush

from Mtb import loadMtbFileStructure, Mtb, PakietDanych
# from MtbPlot import getColorForPlot

import matplotlib.pyplot as plt

from itertools import tee

def pairwise(iterable):
    """s -> (s0, s1), (s1, s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

from colorsys import hsv_to_rgb

def getColorForPlot(press, minPress, maxPress):
    diffPress = maxPress - minPress
    press = (press - minPress) / diffPress # [0, 1]
    press = -1/3 * press + 1/3 # 0 -> 1/3 (zielony), 1 -> 0 (czerwony)
    return hsv_to_rgb(press, 1.0, 1.0)

def intersect(group1, group2):
    minX1, minY1, maxX1, maxY1 = group1[0:4]
    minX2, minY2, maxX2, maxY2 = group2[0:4]
    if maxX1 < minX2 or maxX2 < minX1 or maxY1 < minY2 or maxY2 < minY1:
        return False
    else:
        return True

def join(groups, i, j):
    group1 = groups[i]
    group2 = groups[j]
    minX1, minY1, maxX1, maxY1 = group1[0:4]
    minX2, minY2, maxX2, maxY2 = group2[0:4]
    minX = min(minX1, minX2)
    minY = min(minY1, minY2)
    maxX = max(maxX1, maxX2)
    maxY = max(maxY1, maxY2)
    deltaX = maxX - minX
    deltaY = maxY - minY
    packages = group1[6] + group2[6]
    group = [minX, minY, maxX, maxY, deltaX, deltaY, packages]
    return [group] + [grp for idx, grp in enumerate(groups) if idx != i and idx != j]

import numpy as np

def polyfit(x, y, degree):
    results = {}
    coeffs = np.polyfit(x, y, degree)
    results['polynomial'] = coeffs.tolist()
    p = np.poly1d(coeffs)
    yhat = p(x)
    ybar = np.sum(y) / len(y)
    ssreg = np.sum((yhat - ybar) ** 2)
    sstot = np.sum((y - ybar) ** 2)
    results['determination'] = ssreg / sstot
    return results

class PlotWidget(QLabel):
    def __init__(self, mtb, antialiasing=True, margin=0.01, sf=25, minVisiblePress=64, endTime=None):
        super().__init__()
        packages = mtb.pakietyDanych
        minX = min([package.polozenieX for package in packages])
        minY = min([package.polozenieY for package in packages])
        maxX = max([package.polozenieX for package in packages])
        maxY = max([package.polozenieY for package in packages])
        minPress = min([package.nacisk for package in packages])
        maxPress = max([package.nacisk for package in packages])
        diffX = maxX - minX
        diffY = maxY - minY
        w = int(round(diffX * (1 + 2 * margin) / sf))
        h = int(round(diffY * (1 + 2 * margin) / sf))
        for package in packages:
            package.polozenieX = (package.polozenieX - minX) / diffX # [0, 1]
            package.polozenieY = (package.polozenieY - minY) / diffY # [0, 1]
        # print(min([package.polozenieX for package in packages]))
        # print(min([package.polozenieY for package in packages]))
        # print(max([package.polozenieX for package in packages]))
        # print(max([package.polozenieY for package in packages]))
        for package in packages:
            package.polozenieX = (package.polozenieX * (1 - 2 * margin) + margin) * w
            package.polozenieY = (package.polozenieY * (1 - 2 * margin) + margin) * h
        # print(w * margin, (1 - margin) * w)
        # print(h * margin, (1 - margin) * h)
        # print(min([package.polozenieX for package in packages]))
        # print(min([package.polozenieY for package in packages]))
        # print(max([package.polozenieX for package in packages]))
        # print(max([package.polozenieY for package in packages]))
        mtb.pakietyDanych = packages
        self.mtb = mtb
        self.pixmap_w, self.pixmap_h = w, h
        pixmap = QPixmap(w, h)
        self.pixmap = pixmap
        self.antialiasing = antialiasing
        self.minVisiblePress = minVisiblePress
        if endTime is None:
            self.duration = packages[-1].momentPomiaru
            self.endTime = self.duration
        else:
            self.endTime = endTime
        self.showPressure = True
        self.group_points()
        self.repaint_pixmap()
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignCenter)

    def draw_line(self, painter, x1, y1, press1, x2, y2, press2):
        minVisiblePress = self.minVisiblePress
        showPressure = self.showPressure
        color1 = getColorForPlot((press1 + press2) / 2, minVisiblePress, 1024)
        # color2 = getColorForPlot(press2, minVisiblePress, 1024)
        line = QLineF(x1, y1, x2, y2)
        if showPressure:
            painter.setPen(QColor(color1[0] * 255, color1[1] * 255, color1[2] * 255))
        painter.drawLine(line)

    def group_points(self):
        groups = []
        group = []
        packages = self.mtb.pakietyDanych
        if len(packages) > 1:
            minVisiblePress = self.minVisiblePress
            for package1, package2 in pairwise(packages):
                if len(group) == 0:
                    group = group + [package1]
                press1 = package1.nacisk
                press2 = package2.nacisk
                if press1 >= minVisiblePress and press2 >= minVisiblePress:
                    group = group + [package2]
                else:
                    if len(group) > 1:
                        groups = groups + [group]
                    group = []
        groups1 = []
        for group in groups:
            minX = min([package.polozenieX for package in group])
            minY = min([package.polozenieY for package in group])
            maxX = max([package.polozenieX for package in group])
            maxY = max([package.polozenieY for package in group])
            diffX = maxX - minX
            diffY = maxY - minY
            groups1 = groups1 + [[minX, minY, maxX, maxY, diffX, diffY, group]]

        groups1_1 = groups1
        another_repetition_needed = True
        while another_repetition_needed:
            another_repetition_needed = False
            for i in range(len(groups1_1)):
                for j in range(i + 1, len(groups1_1)):
                    if intersect(groups1_1[i], groups1_1[j]):
                        groups1_1 = join(groups1_1, i, j)
                        another_repetition_needed = True
                        break
                if another_repetition_needed:
                    break

        w, h = self.pixmap_w, self.pixmap_h

        groups2 = []
        for group in groups1_1:
            minX, minY, maxX, maxY, diffX, diffY = group[0:6]
            if diffX > w / 100 or diffY > h / 100:
                groups2 = groups2 + [group]

        groups3 = []
        r = 0.8
        for group in groups2:
            minX, minY, maxX, maxY, diffX, diffY = group[0:6]
            if diffX / diffY > r and diffY / diffX > r:
                groups3 = groups3 + [group]

        groups4 = groups3
        m = 0.05
        n = 0.05
        for group in groups4:
            minX, minY, maxX, maxY, diffX, diffY = group[0:6]
            minX -= m * diffX
            minY -= n * diffY
            maxX += m * diffX
            maxY += n * diffY
            minX, minY = max(minX, 0), max(minY, 0)
            maxX, maxY = min(maxX, w), min(maxY, h)
            diffX = maxX - minX
            diffY = maxY - minY
            group[0:6] = minX, minY, maxX, maxY, diffX, diffY

        from math import sqrt, atan2, pi

        groups5 = []
        for group in sorted(groups4, key=lambda group: group[0]):
            minX, minY, maxX, maxY, diffX, diffY = group[0:6]
            packages4 = self.get_packages_in_rectangle(minX, minY, maxX, maxY)
            avgX = (minX + maxX) / 2
            avgY = (minY + maxY) / 2
            xyt = [(pkg.polozenieX - avgX, pkg.polozenieY - avgY, pkg.momentPomiaru) for pkg in packages4]
            sqrt_atan2_t = [[sqrt(x * x + y * y), atan2(y, x), t] for x, y, t in xyt]
            c = 0
            for a, b in pairwise(sqrt_atan2_t):
                d = (b[1] + c) - a[1]
                if abs(d) > pi:
                    c = c - d
                b[1] = b[1] + c
            # plt.plot([t for sqrt, atan2, t in sqrt_atan2_t], [sqrt for sqrt, atan2, t in sqrt_atan2_t])
            # plt.plot([t for sqrt, atan2, t in sqrt_atan2_t], [atan2 for sqrt, atan2, t in sqrt_atan2_t])
            # plt.show()
            sqrt_atan2_t_np = np.array(sqrt_atan2_t)
            res = polyfit(sqrt_atan2_t_np[:, 2], sqrt_atan2_t_np[:, 1], 1)
            print(" res['determination'] = " + str(res['determination']))
            xyt_np = np.array(xyt)
            res2 = polyfit(xyt_np[:, 0], xyt_np[:, 1], 1)
            print("res2['determination'] = " + str(res2['determination']))
            print("res/res2 = " + str(res['determination'] / res2['determination']))
            if res['determination'] / res2['determination'] > 10:
                groups5 = groups5 + [group]

        '''
        groups3 = sorted(groups2, key=lambda group: group[0])
        groups4 = []
        prevGroup = groups3[0]
        for group in groups3[1:]:
            if group[0] - prevGroup[0] < w / 20:
                prevGroup[1] = min(prevGroup[1], group[1])
                prevGroup[2] = max(prevGroup[2], group[2])
                prevGroup[3] = max(prevGroup[3], group[3])
                prevGroup[4] = prevGroup[2] - prevGroup[0]
                prevGroup[5] = prevGroup[3] - prevGroup[1]
            else:
                groups4 = groups4 + [prevGroup]
                prevGroup = group
        groups4 = groups4 + [prevGroup]
        groups5 = []
        for group in groups4:
            if group[5] < h * 0.5:
                pass
            else:
                groups5 = groups5 + [group]
        groups6 = []
        m = 0.2
        n = 0.4
        for group in groups2:
            minX, minY, maxX, maxY, diffX, diffY = group[0:6]
            minX -= m * diffX
            minY -= n * diffY
            minX, minY = max(minX, 0), max(minY, 0)
            maxX += m * diffX
            maxY += n * diffY
            maxX, maxY = min(maxX, w), min(maxY, h)
            diffX = maxX - minX
            diffY = maxY - minY
            groups6 = groups6 + [[minX, minY, maxX, maxY, diffX, diffY] + group[6:]]
        '''

        self.groups = groups5
        print(len(self.groups))

    def get_packages_in_rectangle(self, minX, minY, maxX, maxY):
        packages = self.mtb.pakietyDanych
        res = [pkg for pkg in packages if minX <= pkg.polozenieX <= maxX and minY <= pkg.polozenieY <= maxY and pkg.nacisk >= self.minVisiblePress]
        res.sort(key=lambda pkg: pkg.momentPomiaru)  # just to be sure
        return res

    def repaint_pixmap(self):
        """"""
        pixmap = self.pixmap
        pixmap.fill(QColor(255, 255, 255))
        packages = self.mtb.pakietyDanych
        if len(packages) > 1:
            minVisiblePress = self.minVisiblePress
            painter = QPainter()
            painter.begin(pixmap)
            painter.setPen(QColor(0, 0, 0))
            antialiasing = self.antialiasing
            painter.setRenderHint(QPainter.Antialiasing, antialiasing)
            for package1, package2 in pairwise(packages):
                press1 = package1.nacisk
                press2 = package2.nacisk
                deltaPress = press2 - press1
                x1, y1 = package1.polozenieX, package1.polozenieY
                x2, y2 = package2.polozenieX, package2.polozenieY
                deltaX, deltaY = x2 - x1, y2 - y1
                time1 = package1.momentPomiaru
                time2 = package2.momentPomiaru
                deltaTime = time2 - time1
                endTime = self.endTime
                if time1 >= endTime:
                    break
                elif time2 >= endTime:
                    a = (endTime - time1) / deltaTime
                    deltaX, deltaY, deltaPress = deltaX * a, deltaY * a, deltaPress * a
                    x2 = x1 + deltaX
                    y2 = y1 + deltaY
                    press2 = press1 + deltaPress
                if press1 >= minVisiblePress and press2 >= minVisiblePress:
                    pass # draw a line
                elif press1 < minVisiblePress < press2:
                    # deltaPress > 0
                    a = (minVisiblePress - press1) / deltaPress
                    x1 = x1 + deltaX * a
                    y1 = y1 + deltaY * a
                    press1 = minVisiblePress
                elif press2 < minVisiblePress < press1:
                    # deltaPress < 0
                    deltaPress = -deltaPress
                    # deltaPress > 0
                    a = (minVisiblePress - press2) / deltaPress
                    x2 = x2 - deltaX * a
                    y2 = y2 - deltaY * a
                    press2 = minVisiblePress
                else:
                    continue # don't draw a line
                self.draw_line(painter, x1, y1, press1, x2, y2, press2)
        """
        self.pixmap.fill(QColor(255, 255, 255))
        packages = self.mtb.pakietyDanych
        if len(packages) > 1:
            path = QPainterPath()
            path.moveTo(packages[0].polozenieX, packages[0].polozenieY)
            for package in packages[1:]:
                path.lineTo(package.polozenieX, package.polozenieY)
            painter = QPainter()
            painter.begin(self.pixmap)
            painter.setPen(QColor(0, 0, 0))
            painter.setRenderHint(QPainter.Antialiasing, self.antialiasing)
            painter.drawPath(path)
            painter.end()
        """
        groups = self.groups
        painter.setPen(QColor(0, 0, 0))
        for group in groups:
            minX, minY, maxX, maxY, diffX, diffY = group[0:6]
            assert(diffX == maxX - minX)
            assert(diffY == maxY - minY)
            rect = QRectF(minX, minY, diffX, diffY)
            painter.drawRect(rect)
            # print(minX, minY, maxX, maxY)
        painter.end()
        self.setPixmap(pixmap)

    def setEndTime(self, endTime):
        self.endTime = endTime
        self.repaint_pixmap()
        # self.update()
    def setShowPressure(self, showPressure):
        self.showPressure = showPressure
        self.repaint_pixmap()

class MainWindow(QMainWindow):
    def __init__(self, pw=None):
        super().__init__()
        layout = QHBoxLayout()
        if pw is not None:
            layout.addWidget(pw)
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        widget = QWidget()
        widget.setLayout(layout)
        scrollArea.setWidget(widget)
        self.setCentralWidget(scrollArea)
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        openButton = QAction('Open', self)
        openButton.setShortcut('Ctrl+N')
        openButton.setStatusTip('Open mtb file')
        openButton.triggered.connect(self.tryOpen)
        fileMenu.addAction(openButton)
        self.layout = layout
        self.widget = widget
        self.scrollArea = scrollArea

    def tryOpen(self):
        filename = QFileDialog.getOpenFileName(caption="Wybierz plik...", filter="MTB files (*.mtb)")[0]
        layout = self.layout
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        checkbox = QCheckBox('Nacisk')
        checkbox.setChecked(True)
        scrollbar = QSlider(Qt.Horizontal)
        mtb = loadMtbFileStructure(filename)
        scrollbar.setMinimum(0)
        scrollbar.setMaximum(mtb.pakietyDanych[-1].momentPomiaru)
        scrollbar.setValue(mtb.pakietyDanych[-1].momentPomiaru)
        pw = PlotWidget(mtb)
        checkbox.stateChanged.connect(pw.setShowPressure)
        scrollbar.valueChanged.connect(pw.setEndTime)
        vbox.addWidget(checkbox)
        vbox.addWidget(scrollbar)
        vbox.addWidget(pw)
        widget = QWidget()
        widget.setLayout(vbox)
        widget.setMaximumSize(widget.sizeHint())
        layout.addWidget(widget)

def main():
    # print(QPainter.setPen.__doc__)
    app = QApplication(sys.argv)
    # filename = QFileDialog.getOpenFileName(caption="Wybierz plik...", filter="MTB files (*.mtb)")[0]
    # filename = r'C:\Users\Aleksander\PycharmProjects\test-grafomotoryczny2\test-grafomotoryczny-dane\dane\33100000000 (M)\01_33100000000_10MLLP.mtb'
    d = 128
    a = PakietDanych(0, 0, 0, 0, 0, 0)
    b = PakietDanych(10, 2500, 2500, d, 0, 0)
    c = PakietDanych(20, 0, 2500, 0, 0, 0)
    mtb = Mtb('', '', '', [a, b, c])
    # mtb = loadMtbFileStructure(filename)
    # mtb.pakietyDanych = mtb.pakietyDanych[1:100]
    # pw = PlotWidget(mtb)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
