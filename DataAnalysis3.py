# DataAnalysis3
# Latest: 1/2019

import os
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
ED = ElementsData(filename)

# Set up parameters
Fs = ED.Sampfrq*1000
Ts = 1.0 / Fs
n = len(ED.current)
t = np.arange(0, n/Fs, Ts)
k = np.arange(n)
T = n/Fs
frq = k/T
frq = frq[range(n//2)]

if ED.Channels == 1:
    Y = np.fft.fft(ED.current)/n
    Y = Y[range(n//2)]
else:
    Y = np.array((range(n//2), 4))
    for i in range(ED.Channels):
        np.append(Y[i], np.fft.fft(ED.current[...,i]), axis=i)
    exit()
# Isolate DC and 60 Cycle components
DCOffset = Y[0]
ACNoise = 0

# General loop through data to either filter or isolate artifacts
for i in range(n // 2):
    if (frq[i] >= 58 and frq[i] <= 65):
        if abs(Y[i]) >= ACNoise:
            ACNoise = abs(Y[i])
            ACFreq = frq[i]
        Y[i] = 0  # Kill 60 cycle noise
    #Kill other noise sources above threshold
"""    threshold = .03
    if abs(Y[i]).real >= threshold:
#       print("{:.2f}".format(frq[i]),"",abs(Y[i]).real)
       Y[i] = threshold
"""

print("\nDC Offset = {:.2f}".format(DCOffset.real), "nA")
print("60 Hz noise amplitude = {:.4f}".format(ACNoise.real),
      " Centered at {:.2f}".format(ACFreq), "Hz")

#Matplotlib plots
plt.style.use('dark_background')
#Raw data
kwargs = {"color": (1,1,1), "linewidth": .3}
plt.figure(1)
plt.subplot(2,1,1)
plt.plot(t, current, 'b', linewidth=.01)
plt.title(os.path.split(filename)[1] + ': Raw Data')
plt.ylabel('Current (nA)')
plt.grid(True, which='both', axis='both', **kwargs)
plt.subplot(2,1,2)
plt.plot(t, voltage, 'r', linewidth=.01)
plt.ylabel('Potential (mV)')
plt.xlabel('time (s)')
plt.grid(True, which='both', axis='both', **kwargs)

#Plot DFT
plt.figure(2)
plt.plot(frq, abs(Y).real, 'g', linewidth=.3)
plt.title(os.path.split(filename)[1] + ': DFT')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid(True, which='both', axis='both', **kwargs)

# Set up inverse DFT
icurrent = np.fft.ifft(Y, n)

#Plot inverseDFT
plt.figure(3)
plt.plot(t, abs(icurrent).real, 'c', linewidth=.01)
plt.title(os.path.split(filename)[1] + ': Inverse DFT')
plt.xlabel('time (s)')
plt.ylabel('Current (nA)')
plt.grid(True, which='both', axis='both', **kwargs)

plt.show()

#lt.goplotly()
