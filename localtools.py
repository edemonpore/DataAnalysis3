#Local tools library...
#12/2018

# Tkinter file open dialog
from tkinter import *
from tkinter import filedialog
def opendata():
    root = Tk()
    root.withdraw()
    root.update()
    filename = filedialog.askopenfilename(initialdir="C:\\Users\\User\\Desktop\\Demonpore\\Data",
                                      title="Select Data File",
                                      filetypes=(("Elements Data", "*.dat"), ("all files", "*.*")))
    root.destroy()
    if filename:
        return filename
    else:
        print('No file to open. Exiting.')
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