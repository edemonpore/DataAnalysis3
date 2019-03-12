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

        # Concatenate binary data files into full data file
        count = 0
        self.DataFileName = filename.split(".edh")[0] + "_FUll.dat"
        fin = filename.split(".edh")[0] + "_000.dat"
        if os.path.isfile(fin) and os.path.isfile(self.DataFileName):
            os.remove(self.DataFileName)
        with open(self.DataFileName, 'ab') as outfile:
            while (os.path.isfile(fin)):
                with open(fin, 'rb') as infile:  # Read binary
                    outfile.write(infile.read())
                break
               # count += 1
               # fin = filename.split(".edh")[0] + "_" + str('{:03d}'.format(int(count))) + ".dat"

        # Initialize Raw Data
        with open(self.DataFileName, 'rb') as file: # Read binary
            databytes = os.path.getsize(self.DataFileName)
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
