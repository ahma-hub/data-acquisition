"""
 # File: generate_traces_pico.py 
 # Project: data-acquisition
 # Last Modified: 2021-8-2
 # Created Date: 2021-8-2
 # Copyright (c) 2021
 # Author: AHMA project (Univ Rennes, CNRS, Inria, IRISA)
 # Modified By: Duy-Phuc Pham (duy-phuc.pham@irisa.fr)
 
"""

#!/usr/bin/python3
import paramiko
import oscilloscopes.picoscope as ps
import ctypes
import os
import random
import argparse
from threading import Thread
from tqdm import trange
import time

class PicoBlock(Thread):
    def __init__(self, handle, dataFile, timebase, triggerChan=None, noOfPreTriggerSamples=0, verbose=False):
        Thread.__init__(self)
        self.handle = handle
        self.timebase = timebase
        self.dataFile = dataFile
        self.triggerChan = triggerChan
        self.noOfPreTriggerSamples = noOfPreTriggerSamples
        self.verbose = verbose
        self.ready = False

    def run(self):
        ps.pico_block(handle, "A", self.dataFile, nbSamples, self.timebase, verbose, self.triggerChan, self.noOfPreTriggerSamples)
        self.ready = True

def randomString(stringLength=16):
    """Generate a random hex-string of fixed length """
    # """Generate a random string of fixed length """
    # letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    # return ''.join(random.choice(letters) for i in range(stringLength))
    return ''.join(chr(random.randrange(256)).encode("ISO-8859-1").hex() for i in range(stringLength))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cmdFile', type=str, help="Path to a file containing the commands to launch." )
    parser.add_argument('-c', action='store', type=int, default=10, dest='count',
                        help='Number of traces')
    parser.add_argument('-d', action='store', type=str, default='./data', dest='dirpath',
                        help='Absolute path of directory to store data')
    parser.add_argument('-n', action='store', type=int, default=5000000, dest='nbSamples',
                        help='Number of samples to capture')
    parser.add_argument('--timebase', action='store', type=int, default=5, dest='timebase',
                        help='Picoscope timebase. freq=5e9/2**timebase if timebase<5; freq=156250000/(timebase-4) if timebase>=5')
    parser.add_argument('-p', action='store', type=int, default=0, dest='noOfPreTriggerSamples',
                       help='Number of pre-triggered samples')
    parser.add_argument('-pre', action='store',  type=str, dest='prefix',
                        default='', help='Output file prefix')
    parser.add_argument('-t', action='store', type=str, default=None, dest='triggerChan',
                       help='Set trigger channel')
    parser.add_argument('-v', action='store_true', default=False, dest='verbose', help='Print very useful informations')
    parser.add_argument('-w', action='store', type=str, default="/home/pi/wrapper", 
            dest='wrapperPath', help='path of the wrapper program that will trigger the oscilloscope on the pi')
    args = parser.parse_args()
    timebase = args.timebase
    prefix = args.prefix
    verbose = args.verbose
    nbSamples = args.nbSamples
    noOfPreTriggerSamples = args.noOfPreTriggerSamples
    wrapperPath = args.wrapperPath

    #parse command file
    cmdLines = []
    f = open(args.cmdFile)
    for l in f:
        if len(l) > 1:
            cmdLines.append(l.strip("\n").split(","))

    #initialize ssh connection with the target device
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('192.168.1.177', username='pi')
    ssh_transp = ssh.get_transport()

    #initialize the picoscope
    handle = ctypes.c_int16()
    ps.pico_init(handle)
    if timebase < 5:
        freq = 5e9/2**timebase
    else:
        freq = float(156250000)/(timebase-4)
    print("Sampling frequency: {}hz".format(freq))
    timeout = int(float(nbSamples)/freq*1e6) #measurement time in us

    #measurements
    for i in trange(args.count):
        for line in cmdLines:
            pre, cmd, tag = line
            dataFile = os.path.join(args.dirpath, "{}{}-{}.dat".format(prefix, tag, randomString(16)))
            if verbose:
                print("\n")
                print("pre-command: " + pre)
                print("command: " + cmd)
                print("dataFile: " + dataFile)
            p = PicoBlock(handle, dataFile, timebase, args.triggerChan, noOfPreTriggerSamples, verbose)
            p.start()
            end = time.time() + float(timeout)/1e6
            #launch the pre-command
            if pre:
                chan = ssh_transp.open_session()
                chan.exec_command(pre)
                while not chan.exit_status_ready():
                    time.sleep(0.01)
                chan.close()
            #launch command
            chan = ssh_transp.open_session()
            print('{} "{}" {}'.format(wrapperPath, cmd, timeout))
            chan.exec_command('{} "{}" {}'.format(wrapperPath, cmd, timeout))
            while True:  # monitoring process
                if chan.exit_status_ready() or time.time() >= end:  # If completed or timeout
                    break
            while not p.ready: # wait for the picoscope to finish transferring data
                time.sleep(0.01)
                pass
            chan.close()
            p.join()
    ps.pico_close(handle)
    ssh.close()
