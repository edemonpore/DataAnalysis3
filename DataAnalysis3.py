"""DataAnalysis3
Plots raw data, DFT and filtered result
EYafuso
Latest: 2/2019
"""

import os
import sys
import time
import numpy as np
import pyqtgraph
from localtools import ElementsData
from PyQt5 import QtWidgets, uic

class DAApp(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_DA = uic.loadUiType("DataAnalysis.ui")[0]
        self.ui = Ui_DA()
        self.ui.setupUi(self)

        # Signals to slots
        self.ui.actionOpen.triggered.connect(self.FileDialog)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.pbPrevious.clicked.connect(lambda: self.nextData(-1))
        self.ui.pbNext.clicked.connect(lambda: self.nextData(1))

        # Set up plotting widgets
        self.rawdata = self.ui.RawData.addPlot()
        self.dft = self.ui.DFT.addPlot()
        self.filtereddata = self.ui.FilteredData.addPlot()
        self.show()

    def nextData(self, n):
        self.ED.index += n
        print("index =",self.ED.index)
        print("max =", self.ED.maxindex)
        self.ED.OpenDataFile()
        self.Plot()

    #Open File Dialog
    def FileDialog(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self,
                                               'Open file',
                                               'C:\\Users\\User\\Desktop\\Demonpore\\Data',
                                               "Elements Header Files (*.edh)")[0]
        self.ED = ElementsData(self.filename)
        if self.ED:
            self.setWindowTitle(os.path.split(self.ED.DataFileName)[1])
            self.Plot()

    def Plot(self):
        #Clear plots
        self.rawdata.clear()
        self.dft.clear()
        self.filtereddata.clear()

        # Execution timekeeping...
        self.start_time = time.time()

        # Set up parameters
        Fs = self.ED.Sampfrq*1000   #Samples per second
        Ts = 1.0 / Fs               #Sample time in seconds
        n = self.ED.Rows            #Number of acquired data samples
        t = np.arange(0, n/Fs, Ts)  #Metered time axis
        k = np.arange(n)
        T = n/Fs
        frq = k/T
        frq = frq[range(n//2)]

        Y = np.fft.fft(self.ED.current[:,0])/n
        Y = Y[range(n//2)]

        """
        # for when using more than one PCA channel...
        Y = np.empty(shape=(ED.Rows, ED.Channels), dtype=float)
        for i in range(ED.Channels):
            Y[:,i] = np.fft.fft(ED.current[:,i])/n
            Y[:,i] = Y[:,i][range(n//2)]
        """

        # Isolate DC and 60 Cycle components
        DCOffset = Y[0]
        ACNoise = 0
        ACFreq = 0

        # General loop through data to either filter or isolate artifacts
        threshold = .5
        for i in range(n // 2):
            if (frq[i] >= 58 and frq[i] <= 62):
                if abs(Y[i]) >= ACNoise:
                    ACNoise = abs(Y[i])
                    ACFreq = frq[i]
                    Y[i] = 0  # Kill 60 cycle noise
            #Kill other noise sources above threshold
            if abs(Y[i]).real >= threshold:
                Y[i] = threshold

        print("\nDC Offset = {:.2f}".format(DCOffset.real), "nA")
        print("60 Hz noise amplitude = {:.4f}".format(ACNoise.real),
              " Centered at {:.2f}".format(ACFreq), "Hz")

        #self.rawdata.plot(t[2:][:-2], self.ED.current[2:][:-2], linewidth=.05, pen='b')

        #PyQtGraph plots

        #Raw Data and Set Potential
        self.rawdata.addLegend()
        for i in range(1): #ED.Channels):
            self.rawdata.plot(t, self.ED.current[:,i], pen='c', linewidth=.05, name='Current')
        self.rawdata.plot(t, self.ED.voltage, pen='r', linewidth=.5, name='Potential (mV)')
        self.rawdata.showGrid(x=True, y=True, alpha=.8)
        self.rawdata.setLabel('left', 'Current', 'nA')
        self.rawdata.setLabel('bottom', 'Time (s)')

        #Plot DFT
        self.dft.plot(frq, abs(Y).real, pen='y', linewidth=1)
        self.dft.showGrid(x=True, y=True, alpha=.8)
        self.dft.setLabel('left', 'Amplitude')
        self.dft.setLabel('bottom', 'Frequency (Hz)')

        #Plot inverseDFT
        icurrent = np.fft.ifft(Y, n)
        a = abs(np.mean(icurrent)).real
        self.filtereddata.addLegend()
        for i in range(1): #ED.Channels):
            self.filtereddata.plot(t, self.ED.current[:,i], pen='c', linewidth=.2, name="Raw Data")
            b = abs(np.mean(self.ED.current[:,i])).real
            scale = b/a
            print("mean of icurrent =", a)
            print("mean of ED.current =", b)
            scale = np.mean(self.ED.current[:,i].real) / np.mean(icurrent.real)
            print("Scale of FFT", i, "= ", scale)
        self.filtereddata.plot(t, abs(icurrent).real*scale, pen='g', linewidth=.2, name="Filtered Data")
        self.filtereddata.showGrid(x=True, y=True, alpha=.8)
        self.filtereddata.setLabel('left', 'Current', 'nA')
        self.filtereddata.setLabel('bottom', 'Time (s)')

        print("Execution time: %s seconds" % (time.time() - self.start_time))
        self.rawdata.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DAApp()
    sys.exit(app.exec_())