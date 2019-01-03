# DataAnalysis3
# Latest: 1/2019

import os
import time
import numpy as np
import matplotlib.pyplot as plt
from localtools import ElementsData
from tkinter import *
from tkinter import filedialog

root = Tk()
root.withdraw()
root.update()
filename = filedialog.askopenfilename(initialdir="C:\\Users\\User\\Desktop\\Demonpore\\Data",
                                  title="Select Elements Header File",
                                  filetypes=(("Elements Header", ".edh"), ("all files", "*.*")))
root.destroy()
start_time = time.time() # Execution timekeeping...

ED = ElementsData(filename)

# Set up parameters
Fs = ED.Sampfrq*1000        #Samples per second
Ts = 1.0 / Fs               #Sample time in seconds
n = ED.Rows                 #Number of acquired data samples
t = np.arange(0, n/Fs, Ts)  #Metered time axis
k = np.arange(n)
T = n/Fs
frq = k/T
frq = frq[range(n//2)]
Y = np.fft.fft(ED.current[:,0])/n
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
for i in range(n // 2):
    if (frq[i] >= 58 and frq[i] <= 63):
        if abs(Y[i]) >= ACNoise:
            ACNoise = abs(Y[i])
            ACFreq = frq[i]
            Y[i] = 0  # Kill 60 cycle noise
    #Kill other noise sources above threshold
#   threshold = .05
#    if abs(Y[i]).real >= threshold:
#       print("{:.2f}".format(frq[i]),"",abs(Y[i]).real)
#       Y[i] = threshold

print("\nDC Offset = {:.2f}".format(DCOffset.real), "nA")
print("60 Hz noise amplitude = {:.4f}".format(ACNoise.real),
      " Centered at {:.2f}".format(ACFreq), "Hz")

#Matplotlib plots
plt.style.use('dark_background')
#Raw data
kwargs = {"color": (1,1,1), "linewidth": .3}
plt.figure(1)
plt.subplot(2,1,1)
for i in range(1): #ED.Channels):
    plt.plot(t, ED.current[:,i], linewidth=.05)
plt.title(os.path.split(ED.DataFileName)[1] + ': Raw Data')
plt.ylabel('Current (nA)')
plt.grid(True, which='both', axis='both', **kwargs)
plt.subplot(2,1,2)
plt.plot(t, ED.voltage, 'r', linewidth=.5)
plt.ylabel('Potential (mV)')
plt.xlabel('time (s)')
plt.grid(True, which='both', axis='both', **kwargs)

#Plot DFT
plt.figure(2)
for i in range(1): #ED.Channels):
    #plt.plot(frq, abs(Y[:,i]).real, linewidth=.3)
    plt.plot(frq, abs(Y).real, 'y', linewidth=1)
plt.title(os.path.split(ED.DataFileName)[1] + ': DFT')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid(True, which='both', axis='both', **kwargs)

# #Plot inverseDFT
icurrent = np.fft.ifft(Y, n)
a = abs(np.mean(icurrent)).real
plt.figure(3)
for i in range(1): #ED.Channels):
    plt.plot(t, ED.current[:,i], 'c', linewidth=.03, label="Raw Data")
    b = abs(np.mean(ED.current[:,i])).real
    scale = b/a
    print("mean of icurrent =", a)
    print("mean of ED.current =", b)
    scale = np.mean(ED.current[:,i].real) / np.mean(icurrent.real)
    print("Scale of FFT", i, "= ", scale)
plt.plot(t, abs(icurrent).real*scale, 'g', linewidth=.2, label="Filtered Data")
plt.title(os.path.split(ED.DataFileName)[1] + ': Inverse DFT')
legend = plt.legend()
for legobj in legend.legendHandles:
    legobj.set_linewidth(2.0)
plt.xlabel('time (s)')
plt.ylabel('Current (nA)')
plt.grid(True, which='both', axis='both', **kwargs)

print("Execution time: %s seconds" % (time.time() - start_time))

plt.show()