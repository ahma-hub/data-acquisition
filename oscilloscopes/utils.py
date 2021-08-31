import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import struct
import numpy as np
import ctypes

def plotBigFile(dataFile, graphFile):
    CHUNK_SIZE = 1e6
    dataFileHandler = open(dataFile, 'r')
    x = []
    y = []
    i = 0
    while True:
        d = dataFileHandler.read(4)
        if not d:
            break
        s = struct.unpack('i', d)
        #x.append(i/float(sampleRate))
        x.append(i)
        y.append(s)
        if len(y) >= CHUNK_SIZE:
            plt.plot(x, y, color="blue")
            x = []
            y = []
        i += 1
    plt.plot(x, y, color="blue")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (mV)")
    plt.savefig(graphFile)
    dataFileHandler.close()


def unpackData(dataFile, device):
    dataFileHandler = open(dataFile, mode="br")
    MAX_VALUE = 32512.
    return np.fromfile(dataFile, np.dtype('int16'))/MAX_VALUE