#! /usr/bin/env python

import logging
import glob
import time
import os
import sys
import subprocess

from twisted.internet.serialport import SerialPort
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ProcessProtocol
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.python import filepath
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import psutil

log = logging
log.basicConfig(level=logging.DEBUG)

DEFAULT_PATCH = os.path.join(os.path.dirname(__file__), 'soundcheck.pd')


class PuredataWatcher(ProcessProtocol):

    def connectionMade(self):
        log.info("Puredata Launched / Connected to stdin. PID: %s" %
                self.transport.pid)
        if not main_controller.find_process(): # Double onfirm it's running
            log.error("Process checker says Pd isn't actually running")

    def outReceived(self, data):
        log.info("Output from Pd: %s" % data)

    def errReceived(self, data):
        log.warn("Error from Pd: %s" % data)

    def processExited(self, reason):
        log.info("Pd Process Exited. Reason: %s" % reason)

    def processEnded(self, reason):
        log.info("Pd Process Ended. Reason: %s" % reason)


class ArduinoController(LineReceiver):

    def __init__(self):
        self.data = ""

    def connectionMade(self):
        log.info("Arudino Connected")

    def connectionLost(self, reason):
        log.warning("Arduino serial connection lost: %s" % reason)
        log.info("How can we make a graceful exit with Ctrl+C ?")
        main_controller.start_arduino()
        # @TODO maybe raise SerialException instead and restart from main_controller?
        # When quitting the program arudino starts back up

    def lineReceived(self, line):
        # @TODO Try using JSON to communicate pin states from Arduino

        log.info(line)
        self.transport.write(line)

        if 'button 1' in line:
            if main_controller.pd_running():
                main_controller.stop_puredata()
            else:
                main_controller.start_puredata()

        if 'button 2' in line:
            import ipdb; ipdb.set_trace()

    def dataReceived(self, data):
        self.data += data
        if 'button 1' in self.data:
            if main_controller.pd_running():
                main_controller.stop_puredata()
            else:
                main_controller.start_puredata()
	    log.debug(self.data)
	    self.data = ""
        pass


class FileSystemWatcher(LoggingEventHandler):
    # Rename to specific purpose when we have one (Jackd log watcher)
    '''
    def on_any_event(self, event):
        log.info(event)

    def on_modified(self, event):
        log.info(event)
    '''
    pass


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

    def start(self):
        try:
            self.start_filewatcher()
            self.start_puredata()
            self.start_arduino()
            reactor.run()

        except KeyboardInterrupt:
            log.debug("Keybord Interrupt")
            self.stop_puredata()
            self.find_process()
            import ipdb; ipdb.set_trace()

    def stop(self):
        reactor.stop()

    def start_arduino(self):
        self.port = self.get_arduino_port()
        self.baudrate = 9600
        log.info("Opening Arduino on port: %s" % self.port)
        self.arduino = SerialPort(ArduinoController(), self.port, reactor, self.baudrate)

    def start_filewatcher(self):
        path_to_watch = os.environ['HOME']
        self.filewatcher = Observer()
        self.filewatcher.schedule(FileSystemWatcher(), path=path_to_watch, recursive=False)
        log.info("Watching for file changes to: %s" % path_to_watch)
        self.filewatcher.start()

    def start_puredata(self, *args):
        # @TODO Raise system volume to where it was (or 100%)
        if not self.pd_running():
            # @TODO use ENV variables to load patches ($PATCH1, $PATCH2, etc)
            # Mac OS X: export PD=/Applications/Pd-extended.app/Contents/Resources/bin/pd
            # Linux: export PD=pd
            pd_binary = os.environ.get('PD') or 'pd'
            patch = os.environ.get('PATCH1') or DEFAULT_PATCH
            cmd = [pd_binary, '-nogui', patch]
            log.info("Loading PD patch: '%s'" % ' '.join(cmd))
            self.puredata = reactor.spawnProcess(PuredataWatcher(), cmd[0], cmd, env=os.environ)
        return self.puredata

    def stop_puredata(self):
        # @TODO Lower system volume to zero
        # OR send message to Pd patch lowering the vol? would depend on patch.
        if self.pd_running():
            log.info("Killing PD patch")
            try:
                self.puredata.signalProcess('TERM') # How to avoid "defunct" state in 'ps' output?
                #self.puredata.signalProcess('KILL')
                # psutil.Process(self.puredata.transport.pid).wait(0)
                # Try and kill everything Pd:
                #[p.wait() for p in self.find_process()] # this works
                return True
            except OSError:
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
        procs = self.find_process(process_name)
        for proc in procs:
            proc.terminate()
            # proc.wait(3)
            # proc.kill()
            log.debug("Killed %s" % proc)
        # subprocess.call(['killall', process_name])

    def get_arduino_port(self, pattern='/dev/ttyUSB*'):
        ''' Wait for Arduino to be connected and return it's port. '''
        # Could use watchdog here as well, wait for changes to /dev/
        # Or monitor dmesg or kern.log ?
        ports = []
        log.debug("Looking for USB device matching '%s'" % pattern)
        while not ports:
            ports = glob.glob(pattern)
            time.sleep(1)
        log.info("Arduino found at: %s" % ports[0])
        return ports[0]


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

