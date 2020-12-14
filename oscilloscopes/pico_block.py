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
    parser.add_argument('nbSamples', type=int, help='Number of samples to capture')
    parser.add_argument('-t', action='store',default=None, dest='trigger', type=str, help='Channel <AUX>')
    parser.add_argument('-p', action='store',default=0, dest='noOfPreTriggerSamples', type=int, help='Number of pre-triggered samples')
    parser.add_argument('-g', action='store', type=str, dest='graphFile', help='File name to save the plot (.svg .png)')
    parser.add_argument('-d', action='store', default="picoscope.dat", type=str, dest='dataFile', help='File name to save the data')
    parser.add_argument('-v', action='store_true', default=False, dest='verbose', help='Print very useful informations')
    args = parser.parse_args()
    channel = args.channel
    nbSamples = args.nbSamples
    trigger = args.trigger
    noOfPreTriggerSamples = args.noOfPreTriggerSamples
    graphFile = args.graphFile
    dataFile = args.dataFile
    verbose = args.verbose
    logger = logging.getLogger("anon-sca") # Centralized log
    handle = ctypes.c_int16()
    ps.pico_init(handle)
    begin = time.time()
    ps.pico_block(handle, channel, dataFile, nbSamples, verbose, trigger, noOfPreTriggerSamples)
    end = time.time()
    logger.info("Capture time: {:.2f}s".format(end - begin))
    ps.pico_close(handle)
    if graphFile:
        plotBigFile(dataFile, graphFile)
