#! /usr/bin/env python

import logging
import glob
import time
import os
import sys
import subprocess
import serial

from twisted.internet.serialport import SerialPort
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ProcessProtocol
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.python import filepath
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler
import psutil

log = logging
log.basicConfig(level=logging.ERROR)

DEFAULT_PATCH = os.path.join(os.path.dirname(__file__), 'soundcheck.pd')


class PuredataWatcher(ProcessProtocol):

    def connectionMade(self):
        log.info("Pure Data Launched with PID: %s" %
                self.transport.pid)
        if not main_controller.find_process(): # Double onfirm it's running
            log.error("Process checker says Pd isn't actually running")

    def outReceived(self, data):
        # log.info("Output from Pd: %s" % data)
        pass

    def errReceived(self, data):
        # log.warn("Error from Pd: %s" % data)
        pass

    def processExited(self, reason):
        log.info("Pure Data Quit: %s" % reason.value.message)

<<<<<<< HEAD
=======
class PuredataController(object):
    # Conroller using subprocess instead of twisted processprotocol
    
    def start(self, patch):
        proc = psutil.Popen(['pd', '-nogui', '-jack', '-rt', patch])
        return proc 
        
    def stop(self):
        pass
       
>>>>>>> 3187ae90ad45256686ad3d2c6265312b38f4871d

class ArduinoController(LineReceiver):

    def __init__(self):
        # check for locks? 
        #  /var/lock/ ..
        self.data = ""

    def connectionMade(self):
        log.info("Arudino Connected")
        self.transport.write("LED1\n")
        self.transport.write("LED1\n")
        self.transport.write("LED1\n")

    def connectionLost(self, reason):
        log.warning("Arduino serial connection lost: %s" % reason.value.message)
        # @TODO maybe raise SerialException instead and restart from main_controller?
        # When quitting the program arudino starts back up

    def lineReceived(self, line):
        # @TODO Try using JSON to communicate pin states from Arduino

        log.info(line)
        self.transport.write(line)

        if 'button 1' in line:
            if main_controller.find_process():
                log.debug('Trying to stop Pd')
                main_controller.stop_puredata()
            else:
                log.debug('Trying to launch Pd')
                main_controller.start_puredata()

        if 'button 2' in line:
            import pdb; pdb.set_trace()

    def dataReceived(self, data):
<<<<<<< HEAD
        if data in ['\n', '\r']: # If the end of the line
            log.debug("Line of serial data: %s" % self.data)
            if 'button 1' in self.data:
                log.info('Button pressed')
                if main_controller.pd_running():
                    main_controller.stop_puredata()
                else:
                    main_controller.start_puredata()
=======
        # log.debug("DATA: %s" % data)
        if data in ['\n', '\r']: # If the end of the line
            log.debug("Line of serial data: %s" % self.data)
            if 'button 1' in self.data:
                if main_controller.find_process():
                    log.debug('Trying to stop Pd')
                    main_controller.stop_puredata()
                else:
                    log.debug('Trying to launch Pd')
                    main_controller.start_puredata()
                main_controller.arduino.flushInput()
>>>>>>> 3187ae90ad45256686ad3d2c6265312b38f4871d
    	        self.data = ""
        else:
            self.data += data


class FileSystemWatcher(LoggingEventHandler):
    # Rename to specific purpose when we have one (Jackd log watcher)
    pass


class ConnectedDevicesWatcher(PatternMatchingEventHandler):
    def __init__(self, *args, **kwargs):
        super(ConnectedDevicesWatcher, self).__init__(*args, **kwargs)
        # Look for device already connected at startup
        ports = []
        log.debug("Looking for device matching '%s'" % self.patterns)
<<<<<<< HEAD
        ports = glob.glob(*self.patterns)
=======
        ports = glob.glob(self.patterns[0])
>>>>>>> 3187ae90ad45256686ad3d2c6265312b38f4871d
        if ports:
            self.open_device(ports[0])

    def on_created(self, event):
        log.info(event)
        if not main_controller.arduino:
            self.open_device(event.src_path)

    def on_deleted(self, event):
        log.info(event)
        if event.src_path == main_controller.arduino_port: # The arduino we want
            main_controller.arduino_port = None
            main_controller.arduino = None

    def on_any_event(self, event):
<<<<<<< HEAD
        pass
        # log.info(event)
=======
        # log.info(event)
        pass
>>>>>>> 3187ae90ad45256686ad3d2c6265312b38f4871d

    def open_device(self, port):
        log.info("Arduino found at: %s" % port)
        time.sleep(1)
        main_controller.arduino_port = port
        main_controller.start_arduino()


class JackWatcher(ProcessProtocol):
     pass


class DmesgWatcher(object):
    pass


class LogFileWatcher(object):
    pass


class SatelliteCCRMAController(object):

    def __init__(self, *args, **kwargs):
        self.puredata = None # Make empty Process instance instead?
        self.filewatcher = None # Make more specific
        self.arduino = None
        self.arduino_port = None

    def start(self):
        try:
            self.start_puredata()
            self.start_devicewatcher()
            # self.start_arduino()
            # self.start_filewatcher()
            reactor.run()

        except KeyboardInterrupt:
            log.debug("Keybord Interrupt")
            log.info("How can we close the Arduino gracefully with Ctrl+C ?")
            self.stop_puredata()
            self.find_process()
            import pdb; pdb.set_trace()

    def stop(self):
        reactor.stop()

    def start_arduino(self):
        if self.arduino_port: 
            port = self.arduino_port
<<<<<<< HEAD
            baudrate = 9600
            log.info("Opening Arduino on port: %s" % port)
	    main_controller.arduino = SerialPort(ArduinoController(), 
					         port, reactor, baudrate)
        # log.info("Opening Arduino on port: %s" % self.port)
        # self.arduino = SerialPort(ArduinoController(), self.port, reactor, self.baudrate)
=======
            baudrate = 4800 
            log.info("Opening Arduino on port: %s" % port)
            self.pulseDTR(port) 
	    self.arduino = SerialPort(ArduinoController(), 
	      		              port, reactor, baudrate,
                                      timeout=0.5)

    def pulseDTR(self, port):
        """ I have no idea whatsoever why this is needed in order to communicate
        at the maximum baud rate.
        """
        log.info('Pulsing serial control line...')
        ser = serial.Serial(port)
        ser.setDTR(1)
        time.sleep(0.5)
        ser.setDTR(0)
        ser.close()
>>>>>>> 3187ae90ad45256686ad3d2c6265312b38f4871d

    def start_filewatcher(self):
        path_to_watch = os.environ['HOME']
        self.filewatcher = Observer()
        self.filewatcher.schedule(FileSystemWatcher(), path=path_to_watch, recursive=False)
        log.info("Watching for file changes to: %s" % path_to_watch)
        self.filewatcher.start()

    def start_devicewatcher(self):
        self.devicewatcher = Observer()
<<<<<<< HEAD
        self.devicewatcher.schedule(ConnectedDevicesWatcher(patterns=['/dev/tty*']), path='/dev/')
=======
        patterns = ['/dev/ttyUSB*', '/dev/ttyACM*']
        self.devicewatcher.schedule(ConnectedDevicesWatcher(patterns=patterns), path='/dev/')
>>>>>>> 3187ae90ad45256686ad3d2c6265312b38f4871d
        self.devicewatcher.start()

    def start_puredata(self, *args):
        # self.unmute_audio()
        # @TODO Raise system volume to where it was (or 100%)
        if not self.find_process():
            # @TODO use ENV variables to load patches ($PATCH1, $PATCH2, etc)
            # Mac OS X: export PD=/Applications/Pd-extended.app/Contents/Resources/bin/pd
            # Linux: export PD=pd
            pd_binary = os.environ.get('PD') or 'pd'
            patch = os.environ.get('PATCH1') or DEFAULT_PATCH
            cmd = [pd_binary, '-nogui', '-jack', '-rt', patch]
            log.info("Loading PD patch: '%s'" % ' '.join(cmd))
            self.puredata = reactor.spawnProcess(PuredataWatcher(), cmd[0], cmd, env=os.environ)
        return self.puredata

    def stop_puredata(self):
        # @TODO Lower system volume to zero
        # OR send message to Pd patch lowering the vol? would depend on patch.
        # self.mute_audio()
        try:
            log.info("Killing all PD patches")
            self.killall()
            # [p.wait() for p in self.find_process()] # this works
            '''
            if self.pd_running():
                self.puredata.signalProcess('TERM') # How to avoid "defunct" state in 'ps' output?
                self.puredata.signalProcess('KILL')
                # psutil.Process(self.puredata.transport.pid).wait(0)
            return True
            '''
        except OSError, psutil.error.NoSuchProcess:
            pass
        return False

    def pd_running(self):
        if self.puredata:
            try:
                self.puredata.reapProcess()
            except TypeError:
                # Fails sometimes when called twice
                pass
            if self.puredata.status < 0:
                return True
        return False

    @property
    def pd_binary_name(self):
        return os.path.split(os.environ.get('PD', 'pd'))[-1]

    def find_process(self, process_name=None):
        # Maybe look for PD running, rather than spawning from twisted
        # there's a chance we could loose sight of PD and it keeps running
        # even if the reactor stopped.
        # @TODO Still says Pd is running sometimes when it's not (after Ctl+C)
        process_name = process_name or self.pd_binary_name

        procs = [p for p in psutil.process_iter() if p.name==process_name]
        if procs:
            log.debug('Found processes: %s' % procs)
            return procs

        log.debug("No process named '%s' found" % process_name)
        return []

    def killall(self, process_name=None):
        process_name = process_name or self.pd_binary_name

        log.info("Killing any instances of '%s'" % process_name)
        while self.find_process(process_name):
		procs = self.find_process(process_name)
		for proc in procs:
		    try:
			proc.terminate()
			proc.wait(1)
			proc.kill()
			log.debug("Killed %s" % proc)
		    except psutil.error.NoSuchProcess:
			pass
		# subprocess.call(['killall', process_name])

    def get_arduino_port(self, pattern='/dev/ttyUSB*'):
        ''' See if Arduino is already connected and return it's port. '''
        ports = []
        log.debug("Looking for device matching '%s'" % pattern)
        ports = glob.glob(pattern)
        if ports:
            time.sleep(1)
            log.info("Arduino found at: %s" % ports[0])
            return ports[0]

    @property
    def audio_devices(self):
        # amixer scontrols (list devices)
        # -stdin will let you pipe in multiple commands
        return ["DAC2 Analog",
                "DAC2 Digital Coarse",
                #"Headset",
                "Master",]
 
    def volumes(self, direction='down'):
        if direction == 'down':
            return [10, 0, 'mute']
        elif direction == 'up':
            return ['unmute', 10, '0db', 50]

    def mute_audio(self):
        for device in self.audio_devices:
           for vol in self.volumes('down'):
                subprocess.call(
                    ['amixer', 'set', device, str(vol)])

    def unmute_audio(self):
        for device in self.audio_devices:
           for vol in self.volumes('up'):
                subprocess.call(
                    ['amixer', 'set', device, str(vol)])

main_controller = SatelliteCCRMAController()
def main():
    main_controller.start()

if __name__ == '__main__':
    main()



'''
# Don't know if these are is necessary

def add_service(transport):
    if transport not in running_services:
        running_services.append(transport)
        return True
    return False

def remove_service(transport):
    if transport in running_services:
        running_services.pop(running_services.index(transport))
        return True
    return True

def service_running(transport):
    if transport in running_services:
        return True
    return False


running_services = []

add_service(self.transport)
remove_service(self.transport)
'''

'''
# Twisted notes:

# self.transport.loseConnection()
# twisted.internet.error.ConnectionDone
# twisted.internet.error.ConnectionLost
# self.makeConnection(self.transport)
'''



