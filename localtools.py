#Local tools library...
#12/2018

# Elements Data Class Definition
import sys
import struct
import numpy as np
class ElementsData:
    def __init__(self, filename):
        # Initialize Header Data
        self.HeaderFileName = filename
        with open(filename, 'r') as f:
            for line in f.readlines():
                text = line.split(": ")[0]
                if text == "Channels":
                    self.Channels = int(line.split(": ")[1])
                if text == "Range":
                    temp = line.split(": ")[1]
                    self.Range = float(temp.split(" ")[0])
                if text == "Sampling frequency (SR)":
                    temp = line.split(": ")[1]
                    self.Sampfrq = float(temp.split(" ")[0])
                if text == "Final Bandwidth":
                    temp = line.split("Final Bandwidth: SR/")[1]
                    self.BandwidthDivisor = int(temp.split(" ")[0])
                if text == "Acquisition start time":
                    self.DAQStart = line.split(": ")[1]
        # Initialize Raw Data
        self.DataFileName = filename.strip('.edh') + "_000.dat"
        with open(self.DataFileName, 'rb') as file:
            rawdata = file.read()
            datasize = sys.getsizeof(rawdata)
            columns = self.Channels + 1  #Current channels + voltage
            rows = int(datasize / (4 * columns))

            # struct games...
            formatstring = str(rows)+ (columns * 'f')  # Values packed as floats
            #print(formatstring)
            buffersize = struct.calcsize(formatstring)
            #print('buffersize = ', buffersize)
            values = struct.unpack(formatstring, rawdata[0:int(buffersize)])
            print(values[0])

            self.current = np.zeros(4, dtype=float)
            self.voltage = []
            for i in range(len(values)):
                if (i + 1) % 5 == 0:
                    np.append(self.current, [values[i - 4], values[i - 3], values[i - 2], values[i - 1]], axis=0)
                    self.voltage.append(values[i])
                    print(i,"  current=",self.current, "voltage=",self.voltage)

            print('Rows: ', i)

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