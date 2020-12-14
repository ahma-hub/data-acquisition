#!/usr/bin/python3
from typing import Any, Union
from scipy import signal
import matplotlib.pyplot as plt
plt.figure(dpi=300)
import scipy.fftpack as fourier
import numpy as np
import struct
import argparse
import sys, os
import ctypes
from oscilloscopes.utils import unpackData

samplingRate = 1.25e9

def autocorr(x):
    result = np.correlate(x, x, mode='full')
    return result[result.size // 2:]

def slidingMean(x, a):
    i = 0
    j = a
    dataLength = len(x)
    res = []
    while(j<dataLength):
        res.append(np.mean(x[i:j]))
        i += a
        j += a
    return res

def plot_SlidingMean(data, windowsLength):
    print("Means")
    mean = slidingMean(data, windowsLength)
    plt.ylabel('Power (V)')
    plt.xlabel('Samples')
    plt.plot(mean)

def plot_autocorr(data):
    print("Autocorrelation")
    plt.plot(autocorr(data))

def plot_fourier(data, samplingRate):
    print("Fourier")
    frequencies = fourier.fftfreq(len(data), 1/samplingRate)
    plt.plot(frequencies, np.abs(fourier.fft(data)))

def plot_spectrogram(data, samplingRate):
    print("Spectrogram")
    f, t, Sxx = signal.spectrogram(np.array(data), samplingRate, nperseg = 128)
    plt.pcolormesh(t*1e6, f, Sxx)
    plt.colorbar()
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [usec]')


def burst_index(traces, threshold=None, threshold_nr_burst=50):
    if threshold is None:
        max_value = np.amax(traces)
        threshold = max_value*0.9

    ind = []
    for i in range(traces.shape[0]):
        n = (len((np.abs(traces[i, :]) > threshold).nonzero()[0]))
        if n > threshold_nr_burst:
            ind.append(i)
    return ind


def remove_bursts(plaintexts, traces, index):
    p = np.delete(plaintexts, index, 0)
    t = np.delete(traces, index, 0)
    return p, t


def get_bursts(plaintexts, traces, index):
    p = plaintexts[index, :]
    t = traces[index, :]
    return p, t


def get_mean_var_traces(traces, plaintexts, byte=0):
    nr_classes = 256
    mean_traces = np.zeros((traces.shape[1],nr_classes))
    var_traces = np.zeros((traces.shape[1],nr_classes))

    for v in range(nr_classes):
        ind = np.nonzero(plaintexts[:, byte] == v)[0]
        mean_traces[:,v] = np.mean(traces[ind, :], axis=0)
        var_traces[:,v] = np.var(traces[ind, :], axis=0)

    return mean_traces,var_traces

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataFile', type=str, help='The file/folder of data')
    parser.add_argument('-c', action='store', type=str, dest='corrFile', help='Print the Pearson coefficient of the dataFile and the corrFile')
    parser.add_argument('-f', action='store_true', default=False, dest='fourier', help='Plot the fourier transformation of the data')
    parser.add_argument('-s', action='store_true', default=False, dest='spectrogram', help='Plot a spectrogram of the data')
    parser.add_argument('-m', action='store', type=int, default=None, dest='mean', help='Plot the mean smoothing of the data')
    parser.add_argument('-o', action='store', type=str, default="out.png", dest='out', help='Output PNG path')
    parser.add_argument('-d', action='store', type=str, default="p", dest='device', help='Devices: p(pico), i(infiniium)')
    parser.add_argument('--show', action='store_true', default=False, dest='show', help='Show plot(s)')
    args = parser.parse_args()
  
    data = unpackData(args.dataFile, args.device)

    if args.corrFile:
        data2 = unpackData(args.corrFile, args.device)
        print('c = %s'%str(np.corrcoef(data, data2)))
    elif args.fourier:
        plot_fourier(data, samplingRate)
    elif args.spectrogram:
        plot_spectrogram(data, samplingRate)
    elif args.mean:
        plot_SlidingMean(data, args.mean)
    else:
        plt.plot(data)
    plt.savefig(args.out)
    if args.show:
        plt.show()
