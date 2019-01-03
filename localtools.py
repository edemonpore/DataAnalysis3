#Local tools library...
#12/2018

import os
import sys
import struct
import numpy as np

"""ElementsData Class Definition
Methods:
    __init__(self, filename)

Attributes:
    HeaderFileName  # Header file name acquired by "open file" dialog...
    DataFileName    # Derived data file name from selected ".edh" header file name
    Channels        # 1 or 4 Depending on which Elements PCA
    Range           # PCA potential range in nA
    Sampfrq         # Sample rate in KHz
    BandwidthDivisor# Integer divisor to derive actual bandwidth
    DAQStart        # Acquisition initialization mark
    Data            # Single multi-dimensional array
    current         # Data array with current values for acquired channel(s) in nA
    voltage         # 1D Data array with acquired potentials in mV
    Rows            # Acquired data points, each having current(s) and voltage
"""
class ElementsData:
    def __init__(self, filename):
        # Initialize Header Data
        self.HeaderFileName = filename
        with open(filename, 'r') as f:
            for line in f.readlines():
                text = line.split(": ")[0]
                if text == "Channels":
                    self.Channels = int(line.split(": ")[1])
                    print("Channels =", self.Channels)
                if text == "Range":
                    temp = line.split(": ")[1]
                    self.Range = float(temp.split(" ")[0])
                    print("Range =", self.Range, " nA")
                if text == "Sampling frequency (SR)":
                    temp = line.split(": ")[1]
                    self.Sampfrq = float(temp.split(" ")[0])
                    print("Sample Frequency =", self.Sampfrq, " KHz")
                if text == "Final Bandwidth":
                    temp = line.split("Final Bandwidth: SR/")[1]
                    self.BandwidthDivisor = int(temp.split(" ")[0])
                    print("Slew Rate (SR) Divisor =", self.BandwidthDivisor)
                if text == "Acquisition start time":
                    self.DAQStart = line.split(": ")[1]
                    print("Acquisition start:", self.DAQStart)

        # Initialize Raw Data
        databytes = 0
        self.DataFileName = filename.split(".edh")[0] + "_000.dat"
        with open(self.DataFileName, 'rb') as file: # Read binary
            databytes += os.path.getsize(self.DataFileName)

            print("Datasize in bytes =",databytes)
            columns = self.Channels + 1
            self.Rows = int(databytes // 4 // columns)

            # Use struct to unpack binary data into Data array
            formatstring = str(columns * 'f')
            buffersize = struct.calcsize(formatstring)
            #Read into python list for speed...
            test = []
            for i in range(self.Rows):
                test.append(struct.unpack(formatstring, file.read(buffersize)))
            #Store as numpy array for indexing versatility...
            self.Data = np.array(test)

            # Read Data from PCA (either 1 or 4-channel) into local arrays
            self.voltage = []
            self.current = np.empty(shape=(self.Rows, self.Channels), dtype=float)
            if self.Channels == 1 or self.Channels == 4:
                for i in range(self.Channels):
                    self.current[:,i] = self.Data[:,i]
                self.voltage = self.Data[:,self.Channels]
            else:
                print("Unrecognized patch clamp amplifier. Exiting...")
                exit()


#Plotly plot (fails with really large data sets)
import time
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
def goplotly():
    #Establish plotly credentials and/or settings
    plotly.tools.set_credentials_file(username='e@demonpore.com', api_key='7HOIUl4yTmgPyY5AA2aI')
    plotly.tools.set_config_file(world_readable=False, sharing='private')
    plotly.offline.init_notebook_mode(connected=True)

    # Plot raw data
    trace1 = go.Scattergl(x=t,
                      y=current,
                      line=dict(color=('rgb(0,63,127)'), width=1),
                      name='Current')
    trace2 = go.Scattergl(x=t,
                      y=voltage,
                      line=dict(color=('rgb(255,0,0)'), width=1),
                      name='Potential',
                      yaxis='y2')
    data = [trace1, trace2]
    # plot_url = py.plot(data, filename=filename + '_Data')
    plotly.offline.plot({"data": data,
                     "layout": go.Layout(title="Acquired Data:   " + os.path.split(filename)[1],
                                         xaxis=dict(title='Time (s)',
                                                    titlefont=dict(family='Courier New, monospace',
                                                                   size=16,
                                                                   color='rgb(55,55,55)')
                                                    ),
                                         yaxis=dict(title='Current (nA)',
                                                    titlefont=dict(family='Courier New, monospace',
                                                                   size=16,
                                                                   color='rgb(0,63,127)')
                                                    ),
                                         yaxis2=dict(title='Potential (mV)',
                                                     titlefont=dict(family='Courier New, monospace',
                                                                    size=16,
                                                                    color='rgb(255,0,0)'),
                                                     overlaying='y',
                                                     side='right'
                                                     )
                                         )
                     })

    time.sleep(1)  # Apparently necessary pause to get plotly to work with both url graphs

    # Plot DFT
    # plot_url = py.plot(data, filename=filename + '_DFT')
    plotly.offline.plot({"data": [go.Scattergl(x=frq, y=abs(Y).real,
                                           line=dict(color=('rgb(255,0,127)'),
                                                     width=1))],
                     "layout": go.Layout(title="DFT:   " + os.path.split(filename)[1],
                                         xaxis=dict(title='Spectrum (Hz)',
                                                    titlefont=dict(family='Courier New, monospace',
                                                                   size=16,
                                                                   color='rgb(55,55,55)')
                                                    ),
                                         yaxis=dict(title='Amplitude',
                                                    titlefont=dict(family='Courier New, monospace',
                                                                   size=16,
                                                                   color='rgb(55,55,55)')
                                                    )
                                         )
                     })

    time.sleep(1)

    # Set up inverse DFT
    icurrent = np.fft.ifft(Y, n)

    # Plot inverse DFT
    # plot_url = py.plot(data, filename=filename + ' Inverse DFT')
    plotly.offline.plot({"data": [go.Scattergl(x=t, y=icurrent.real,
                                           line=dict(color=('rgb(0,255,127)'),
                                                     width=1))],
                     "layout": go.Layout(title="Inverse DFT:   " + os.path.split(filename)[1],
                                         xaxis=dict(title='Time (s)',
                                                    titlefont=dict(family='Courier New, monospace',
                                                                   size=16,
                                                                   color='rgb(55,55,55)')
                                                    ),
                                         yaxis=dict(title='Current (nA)',
                                                    titlefont=dict(family='Courier New, monospace',
                                                                   size=16,
                                                                   color='rgb(55,55,55)')
                                                    )
                                         )
                     })