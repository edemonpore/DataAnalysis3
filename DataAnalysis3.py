# DataAnalysis3
# Latest: 1/2019

import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from localtools import ElementsData
from PyQt5 import QtWidgets, uic

Ui_DA = uic.loadUiType("DataAnalysis.ui")[0]

class DAApp(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_DA()
        self.ui.setupUi(self)

        # Signals to slots
        self.ui.actionOpen.triggered.connect(self.FileDialog)
        self.ui.actionExit.triggered.connect(self.close)

        # Set up plotting widgets
        self.ui.RawData.setBackground('w')
        self.rawdata = self.ui.RawData.addPlot()
        self.rawdata.setLabel('bottom', text='Time', units='s')
        self.rawdata.setLabel('left', text='Current', units='nA')
        self.rawdata.enableAutoRange(axis='x')
        self.rawdata.setDownsampling(ds=True, auto=True, mode='peak')
        self.ui.DFT.setBackground('w')
        self.dft = self.ui.DFT.addPlot()
        self.dft.setLabel('bottom', text='Frequency', units='Hz')
        self.dft.setLabel('left', text='Amplitude', units='')
        self.dft.enableAutoRange(axis='x')
        self.dft.setDownsampling(ds=True, auto=True, mode='peak')
        self.ui.FilteredData.setBackground('w')
        self.filtereddata = self.ui.FilteredData.addPlot()
        self.filtereddata.setLabel('bottom', text='Time', units='s')
        self.filtereddata.setLabel('left', text='Current', units='nA')
        self.filtereddata.enableAutoRange(axis='x')
        self.filtereddata.setDownsampling(ds=True, auto=True, mode='peak')

    #Open File Dialog
    def FileDialog(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self,
                                               'Open file',
                                               'C:\\Users\\User\\Desktop\\Demonpore\\Data',
                                               "Elements Header Files (*.edh)")[0]
        self.ED = ElementsData(self.filename)
        if self.ED:
            self.Plot()

    def Plot(self):

        # Execution timekeeping...
        self.start_time = time.time()

        # Set up parameters
        Fs = self.ED.Sampfrq*1000        #Samples per second
        Ts = 1.0 / Fs               #Sample time in seconds
        n = self.ED.Rows                 #Number of acquired data samples
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

        self.rawdata.plot(t, self.ED.current[:,i], linewidth=.05, pen='b')

        if str(os.path.splitext(self.datafilename)[1]) != '.abf':
            self.p1.addLine(y=self.baseline, pen='g')

        #Matplotlib plots
        plt.style.use('dark_background')
        #Raw data
        kwargs = {"color": (1,1,1), "linewidth": .3}
        plt.figure(1)
        plt.subplot(2,1,1)
        for i in range(1): #ED.Channels):
            plt.plot(t, self.ED.current[:,i], linewidth=.05)
        plt.title(os.path.split(self.ED.DataFileName)[1] + ': Raw Data')
        plt.ylabel('Current (nA)')
        plt.grid(True, which='both', axis='both', **kwargs)
        plt.subplot(2,1,2)
        plt.plot(t, self.ED.voltage, 'r', linewidth=.5)
        plt.ylabel('Potential (mV)')
        plt.xlabel('time (s)')
        plt.grid(True, which='both', axis='both', **kwargs)

        #Plot DFT
        plt.figure(2)
        for i in range(1): #ED.Channels):
            #plt.plot(frq, abs(Y[:,i]).real, linewidth=.3)
            plt.plot(frq, abs(Y).real, 'y', linewidth=1)
        plt.title(os.path.split(self.ED.DataFileName)[1] + ': DFT')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude')
        plt.grid(True, which='both', axis='both', **kwargs)

        # #Plot inverseDFT
        icurrent = np.fft.ifft(Y, n)
        a = abs(np.mean(icurrent)).real
        plt.figure(3)
        for i in range(1): #ED.Channels):
            plt.plot(t, self.ED.current[:,i], 'c', linewidth=.2, label="Raw Data")
            b = abs(np.mean(self.ED.current[:,i])).real
            scale = b/a
            print("mean of icurrent =", a)
            print("mean of ED.current =", b)
            scale = np.mean(self.ED.current[:,i].real) / np.mean(icurrent.real)
            print("Scale of FFT", i, "= ", scale)
        plt.plot(t, abs(icurrent).real*scale, 'g', linewidth=.2, label="Filtered Data")
        plt.title(os.path.split(self.ED.DataFileName)[1] + ': Inverse DFT')
        legend = plt.legend()
        for legobj in legend.legendHandles:
            legobj.set_linewidth(2.0)
        plt.xlabel('time (s)')
        plt.ylabel('Current (nA)')
        plt.grid(True, which='both', axis='both', **kwargs)

        print("Execution time: %s seconds" % (time.time() - self.start_time))
        plt.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DAApp()
    window.show()
    sys.exit(app.exec_())