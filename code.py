import csv, re, math, sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

class Main(QtGui.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setGeometry(50, 50, 1000, 680)
        self.setWindowTitle("Krzysztof Dziadowiec, Michal Trojanowski - INDUSTRIAL ROBOTS")

        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.set_graph_view()
        self.transpose()

    def set_graph_view(self):
        self.tabWidget = QtGui.QTabWidget(self)
        self.central_widget.addWidget(self.tabWidget)
      
        self.pw2 = pg.PlotWidget(            
            title="[Displacement - Time] Diagram")
        self.tabWidget.insertTab(0, self.pw2, "Graph 1")
        self.pw2.showGrid(True, True, 0.5)
        self.pw2.addLegend()
        self.pw2.setLabel(
            axis='bottom', 
            text='Time [s]',
            units=None,
            unitPrefix=None,
            color='#FFFF00')
        self.pw2.setLabel(
            axis='left', 
            text='Distance [mm]', 
            color='#FFFF00')
        self.pw2.setLabel(
            axis='right', 
            text=None)

        self.pw = pg.PlotWidget(
            title="Summary Diagram")
        self.tabWidget.insertTab(1, self.pw, "Graph 2")
        self.pw.showGrid(True, True, 0.5)
        self.pw.addLegend()
        self.pw.setLabel(
            axis='bottom', 
            text='X axis [mm]', 
            color='#FFFF00')
        self.pw.setLabel(
            axis='left', 
            text='Y axis [mm]', 
            color='#FFFF00')
        self.pw.setLabel(
            axis='right', 
            text=None)

    def transpose(self):
        # Algorithm to recalculate voltages into distance in [mm]
        raw_x = []
        raw_y = []
        with open("GR03.txt") as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            for line in tsvreader:
                raw_x.append(10*float(line[:1][0])/1.43)
                raw_y.append(10*float(line[1:][0]))

        # Creation of time matrix
        time = []
        t = range(68031)
        for k in t:
            time.append(0.002*(k+1))
        with open("time.txt", 'w') as f:
            for k in time:
                f.write(str(k) + "\n")

        # Algorithm to read data from 'time.txt' file     
        time = []
        with open("time.txt") as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            for line in tsvreader:
                time.append(float(re.sub(r",", '.', line[:1][0])))

        # Algorithm to find 20 X-axis and 20 Y-axis cycles and calculate average for each of them
        av_ls_y = []
        av_ls_x = []
        averages_y = []
        averages_x = []
        av_y = 0
        av_x = 0
        i = 0
        ii = 0
        m = 0

        for k in raw_y:
            if k < -20:
                av_ls_y.append(k)
                av_ls_x.append(raw_x[m])
            else:
                if av_ls_y != []:
                    for j in av_ls_y:
                        i += 1
                        av_y += j
                    averages_y.append(av_y/i)

                if av_ls_x != []:
                    for j in av_ls_x:
                        ii += 1
                        av_x += j
                    averages_x.append(av_x/ii)

                av_ls_x = []
                av_ls_y = []
                i = 0
                ii = 0
                av_y = 0
                av_x = 0
            m += 1

        ver_mov_av_x = averages_x[::2]
        hor_mov_av_x = averages_x[1::2]
        ver_mov_av_y = averages_y[::2]
        hor_mov_av_y = averages_y[1::2]

        # Algorithm to calculate overall average for x-coordinate measurements after X-axis motion
        a = 0
        for k in ver_mov_av_x:
            a += k
        ver_avx = a/20

        # Algorithm to calculate overall average for x-coordinate measurements after Y-axis motion
        a = 0
        for k in hor_mov_av_x:
            a += k
        hor_avx = a/20

        # Algorithm to calculate overall average for y-coordinate measurements after X-axis motion
        a = 0
        for k in ver_mov_av_y:
            a += k
        ver_avy = a/20

        # Algorithm to calculate overall average for y-coordinate measurements after Y-axis motion
        a = 0
        for k in hor_mov_av_y:
            a += k
        hor_avy = a/20

        # Algorithm to calculate vector length for every X-axis cycle
        lenghts_ver = []
        for i in range(20):
            lenghts_ver.append(math.sqrt((ver_mov_av_x[i]-ver_avx)**2 + (ver_mov_av_y[i]-ver_avy)**2))
        
        # Algorithm to calculate average vector length for all X-axis cycles
        s = 0
        for k in lenghts_ver:
            s += k
        average_len_ver = s/20

        # Algorithm to calculate vector length for every Y-axis cycle
        lenghts_hor = []
        for i in range(20):
            lenghts_hor.append(math.sqrt((hor_mov_av_x[i]-hor_avx)**2 + (hor_mov_av_y[i]-hor_avy)**2))
        
        # Algorithm to calculate average vector length for all Y-axis cycles
        s = 0
        for k in lenghts_hor:
            s += k
        average_len_hor = s/20

        # Algorithm to calculate RP for X-axis cycles        
        l = 0
        for i in range(20):
            l += ((lenghts_ver[i] - average_len_ver)**2)
        ver_S = math.sqrt(l/(20-1))
        ver_RP = average_len_ver + 3*ver_S

        # Algorithm to calculate RP for Y-axis cycles 
        l = 0
        for i in range(20):
            l += ((lenghts_hor[i] - average_len_hor)**2)
        hor_S = math.sqrt(l/(20-1))
        hor_RP = average_len_hor + 3*hor_S
        
        # Algorithm to calculate RP for non-extreme X-axis cycles 
        l = 0
        for i in range(19):
            l += ((lenghts_ver[i+1] - average_len_ver)**2)
        ver_S = math.sqrt(l/(19-1))
        ver_RP2 = average_len_ver + 3*ver_S

        # Algorithm to calculate RP for non-extreme Y-axis cycles
        l = 0
        for i in range(19):
            l += ((lenghts_hor[i+1] - average_len_hor)**2)
        hor_S = math.sqrt(l/(19-1))
        hor_RP2 = average_len_hor + 3*hor_S
        
        #Creating plots -------------------------------

        self.pw2.plot(
            x=time, 
            y=raw_y, 
            name='Y axis', 
            pen='b')

        self.pw2.plot(
            x=time, 
            y=raw_x, 
            name='X axis', 
            pen='y')
        
        xx = []
        yx = []
        for i in range(101):
            xx.append(ver_avx+0.02*math.sin(math.radians((i+1)*3.6)))
            yx.append(ver_avy+0.02*math.cos(math.radians((i+1)*3.6)))

        xy = []
        yy = []
        for i in range(101):
            xy.append(hor_avx+0.02*math.sin(math.radians((i+1)*3.6)))
            yy.append(hor_avy+0.02*math.cos(math.radians((i+1)*3.6)))

        x_RP_ver = []
        y_RP_ver = []
        for i in range(101):
            x_RP_ver.append(ver_avx+ver_RP*math.sin(math.radians((i+1)*3.6)))
            y_RP_ver.append(ver_avy+ver_RP*math.cos(math.radians((i+1)*3.6)))

        x_RP_hor = []
        y_RP_hor = []
        for i in range(101):
            x_RP_hor.append(hor_avx+hor_RP*math.sin(math.radians((i+1)*3.6)))
            y_RP_hor.append(hor_avy+hor_RP*math.cos(math.radians((i+1)*3.6)))

        x_RP2_ver = []
        y_RP2_ver = []
        for i in range(101):
            x_RP2_ver.append(ver_avx+ver_RP2*math.sin(math.radians((i+1)*3.6)))
            y_RP2_ver.append(ver_avy+ver_RP2*math.cos(math.radians((i+1)*3.6)))

        x_RP2_hor = []
        y_RP2_hor = []
        for i in range(101):
            x_RP2_hor.append(hor_avx+hor_RP2*math.sin(math.radians((i+1)*3.6)))
            y_RP2_hor.append(hor_avy+hor_RP2*math.cos(math.radians((i+1)*3.6)))

        self.pw.plot(
            x=xx, 
            y=yx,
            name='0.02 mm radius', 
            pen='r')

        self.pw.plot(
            x=x_RP_ver, 
            y=y_RP_ver,
            name='RP for X-axis cycles', 
            pen='m')

        self.pw.plot(
            x=x_RP2_ver, 
            y=y_RP2_ver,
            name='RP for non-extreme X-axis cycles', 
            pen=pg.mkPen(
                color='m', 
                style=QtCore.Qt.DotLine))

        self.pw.plot(
            x=[ver_avx], 
            y=[ver_avy], 
            symbol='+',
            symbolPen='r',
            symbolBrush=None,
            symbolSize=7,
            name='Average point for X-axis cycles', 
            pen=None)

        self.pw.plot(
            x=ver_mov_av_x, 
            y=ver_mov_av_y, 
            symbol='t',
            symbolPen='y',
            symbolBrush=None,
            symbolSize=7,
            name='Average point for every of 20 X-axis cycles', 
            pen=None)

        self.pw.plot(
            x=xy, 
            y=yy,
            name='0.02 mm radius', 
            pen='g')

        self.pw.plot(
            x=x_RP_hor, 
            y=y_RP_hor,
            name='RP for Y-axis cycles', 
            pen='w')

        self.pw.plot(
            x=x_RP2_hor, 
            y=y_RP2_hor,
            name='RP for non-extreme Y-axis cycles', 
            pen=pg.mkPen(
                color='w', 
                style=QtCore.Qt.DotLine))

        self.pw.plot(
            x=[hor_avx], 
            y=[hor_avy], 
            symbol='+',
            symbolPen='g',
            symbolBrush=None,
            symbolSize=7,
            name='Average point for Y-axis cycles', 
            pen=None)

        self.pw.plot(
            x=hor_mov_av_x, 
            y=hor_mov_av_y, 
            symbol='t',
            symbolPen='b',
            symbolBrush=None,
            symbolSize=7,
            name='Average point for every of 20 Y-axis cycles', 
            pen=None)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    os._exit(app.exec_())