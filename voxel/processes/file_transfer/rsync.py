"""File Transfer process in a separate class for Win/Linux compatibility."""
import os
import time
import logging
import sys
import threading
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path

class FileTransfer():

    def __init__(self, external_drive):
        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._filename = None
        self._local_drive = None
        self._external_drive = external_drive
        self._protocol = 'rsync'
        self.progress = 0
        self._output_file = None
        self._flags = '--progress'

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self.log.info(f'setting filename to: {filename}')
        self._filename = filename

    @property
    def local_drive(self):
        return self._local_drive

    @local_drive.setter
    def local_drive(self, local_drive: Path or str):
        self.log.info(f'setting local path to: {local_drive}')
        self._local_drive = Path(local_drive)

    @property
    def external_drive(self):
        return self._external_drive

    @property
    def signal_progress_percent(self):
        self.log.info(f'{self.filename} transfer progress: {self.progress} [%]')
        return self.progress

    def start(self):
        if not os.path.isfile(self._local_drive / self._filename):
            raise FileNotFoundError(f"{self._local_drive / self._filename} does not exist.")
        file_extension = Path(self._filename).suffix
        self._log_filename = self._filename.replace(file_extension, '.txt')
        # open log file for writing to pipe into stdout
        self._log_file = open(f'{self._local_drive / self._log_filename}', 'w')
        self.log.info(f"transferring from {self._local_drive} to {self._external_drive}")
        # self.cmd = subprocess.run(cmd_with_args, check=True)
        self.thread = threading.Thread(target=self._run,
                                       args=([self._protocol,
                                              self._local_drive / self._filename,
                                              self._external_drive,
                                              self._flags],))
        self.thread.start()

    def wait_until_finished(self):
        self.thread.join()

    def is_alive(self):
        return self.thread.is_alive()

    def _run(self, cmd_with_args: list):
        subprocess = Popen(cmd_with_args, stdout=self._log_file)
        # close the handle to the stdout log file
        self._log_file.close()
        # pause for 1 sec for log file first line write
        time.sleep(1)
        self.progress = 0
        while self.progress < 100:
            # open the stdout file in a temporary handle with r+ mode
            f = open(f'{self._local_drive / self._log_filename}', 'r+')
            # read the last line
            line = f.readlines()[-1]
            # try to find if there is a % in the last line
            try:
                # grab the index of the % symbol
                index = line.find('%')
                # a location with % has been found
                if index != -1:
                    # grab the string of the % progress
                    value = line[index-4:index]
                    # strip and convert to float
                    self.progress = float(value.rstrip())
                # we must be at the last line of the file
                else:
                    # go back to beginning of file
                    f.seek(0)
                    # read line that must be 100% line
                    line = f.readlines()[-4]
                    # grab the index of the % symbol
                    index = line.find('%')
                    # grab the string of the % progress
                    value = line[index-4:index]
                    # strip and convert to float
                    self.progress = float(value.rstrip())
            # no lines in the file yet          
            except:
                self.progress = 0
            # close temporary stdout file handle
            f.close()
            # pause for 1 sec
            time.sleep(1)
        # cleanup the subprocess
        subprocess.kill()
        subprocess.wait()
        # remove the log file
        os.remove(f'{self._local_drive / self._log_filename}')
        self.log.info(f"transfer finished")