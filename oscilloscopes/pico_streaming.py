#!/usr/bin/python3

import pico as ps
import argparse
import ctypes
import time
from utils import *
import logging

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('channel', type=str, help='Channel <A,B,C,D>')
    parser.add_argument('-t', action='store',default=None, dest='trigger', type=str, help='Channel <AUX>')
    parser.add_argument('duration', type=int, help='Duration of the capture in seconds')
    parser.add_argument('sampleRate', type=int, help='Sample rate in Hz')
    parser.add_argument('-b', action='store', default=100000, type=int, dest='bufferLength', help='Define the size of the buffer used by the picoscope (default 100000)')
    parser.add_argument('-g', action='store', type=str, dest='graphFile', help='File name to save the plot (.svg .png)')
    parser.add_argument('-d', action='store', default="picoscope.dat", type=str, dest='dataFile', help='File name to save the data')
    parser.add_argument('-v', action='store_true', default=False, dest='verbose', help='Print very useful informations')
    args = parser.parse_args()
    duration = args.duration
    sampleRate = args.sampleRate
    channel = args.channel
    trigger = args.trigger
    graphFile = args.graphFile
    dataFile = args.dataFile
    bufferLth = args.bufferLength
    verbose = args.verbose
    logger = logging.getLogger("anon-sca")  # Centralized log
    handle = ctypes.c_int16()
    ps.pico_init(handle)
    begin = time.time()
    ps.pico_streaming(handle, channel, duration, sampleRate, bufferLth, dataFile, verbose, trigger)
    end = time.time()
    logger.info("Capture time: {:.2f}s".format(end - begin))
    ps.pico_close(handle)
    if graphFile:
        plotBigFile(dataFile, graphFile)
