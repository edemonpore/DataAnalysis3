#Local tools library...
#12/2018

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
        self.DataFileName = filename.strip('.edh') + "_000.dat"
        with open(self.DataFileName, 'rb') as file:
            rawdata = file.read()
            datasize = sys.getsizeof(rawdata)
            columns = self.Channels + 1  #Current channels + voltage
            self.Rows = int(datasize // (4 * columns))
            print("Acquired data points =", self.Rows)

            # struct games...
            formatstring = str(self.Rows)+(columns*'f')
            #print(formatstring)
            buffersize = struct.calcsize(formatstring)
            #print('buffersize = ', buffersize)
            values = struct.unpack(formatstring, rawdata[0:int(buffersize)])

            self.voltage = []
            #Single channel read
            if self.Channels == 1:
                self.current = []
                for i in range(len(values)):
                    if i % 2 == 0:
                        self.current.append(values[i])
                        if values[i+1]:
                            self.voltage.append(values[i+1])
            # 4-channel read
            elif self.Channels == 4:
                self.current = np.empty(shape=(self.Rows,4))
                for i in range(self.Rows):
                    a = np.array([values[i], values[i+1], values[i+2], values[i+3]])
                    self.current[i] = a
                    self.voltage.append(values[i+4])
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