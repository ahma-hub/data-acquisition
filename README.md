# Data acquisition interfaces
The current repository contains all the scripts needed to interact with data acquisition interfaces published in the paper: "Out of device malware analysis:leveraging IoT devices electromagnetic emanation".

# signal-processing
Compilation of tools to process side-channel data.

## generate\_traces\_pico.py
```
usage: generate_traces_pico.py [-h] [-c COUNT] [-d DIRPATH] [-n NBSAMPLES]
                               [--timebase TIMEBASE]
                               [-p NOOFPRETRIGGERSAMPLES] [-pre PREFIX]
                               [-t TRIGGERCHAN] [-v] [-w WRAPPERPATH]
                               cmdFile

positional arguments:
  cmdFile               Path to a file containing the commands to launch.

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT              Number of traces
  -d DIRPATH            Absolute path of directory to store data
  -n NBSAMPLES          Number of samples to capture
  --timebase TIMEBASE   Picoscope timebase. freq=5e9/2**timebase if
                        timebase<5; freq=156250000/(timebase-4) if timebase>=5
  -p NOOFPRETRIGGERSAMPLES
                        Number of pre-triggered samples
  -pre PREFIX           Output file prefix
  -t TRIGGERCHAN        Set trigger channel
  -v                    Print very useful informations
  -w WRAPPERPATH        path of the wrapper program that will trigger the
                        oscilloscope on the pi
```

### Command file
You now need to provide the list of commands you want to monitor in a cvs like file cmdFile.
The file must be of this form: pretrigger-command,command,tag

Every loop iteration will, for each line of the cmdFile, do the following:
1. Execute the pretrigger command on the device via ssh
2. Arm the oscilloscope
3. Trigger the oscilloscope and execute the monitored command
4. Record the data in a file tag-randomId.dat

Example of a command file:
```
sudo rmmod kisni,./keyemu/emu.sh A 10,keyemu
sudo insmod keysniffer/kisni-4.19.57-v7+.ko,./keyemu/emu.sh A 10,keyemu_kisni
```

### Wrapper path
To trigger the oscilloscope, we launch a [wrapper]() program on the device. This wrapper will simply send the trigger and launch the program we want to monitor for the according time. It is automatically called by generate\_traces\_pico.py. You just need to precise its path on the monitored device.