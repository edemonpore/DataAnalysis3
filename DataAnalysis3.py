# DataAnalysis2
# Latest: 12/2018

import os
import sys
import numpy as np
import struct
import matplotlib.pyplot as plt
import localtools as lt

filename = lt.opendata()
file = open(filename, 'rb')

rawdata = file.read()
datasize = sys.getsizeof(rawdata)
rows = int(datasize/8)

# struct games...
formatstring = str(rows)+'ff' #Values are stored as floats, 2 per line
buffersize = struct.calcsize(formatstring)
values = struct.unpack(formatstring, rawdata[0:int(buffersize)])

current1 = []
current2 = []
current3 = []
current4 = []
voltage = []
for i in range(len(values)):
    if i % 2 == 0:
        current.append(values[i])
    else:
        voltage.append(values[i])
if len(current)-len(voltage):
    voltage.append(values[i-1])
print('Rows: ', i)

# Set up parameters
Fs = 1250.0
Ts = 1.0 / Fs
n = len(current)
t = np.arange(0, n/Fs, Ts)
k = np.arange(n)
T = n/Fs
frq = k/T
frq = frq[range(n//2)]

Y = np.fft.fft(current)/n
Y = Y[range(n//2)]

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