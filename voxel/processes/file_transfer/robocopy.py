"""File Transfer process in a separate class for Win/Linux compatibility."""
import os
import time
import logging
import sys
import threading
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path

class FileTransfer():

    def __init__(self, external_directory):
        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._filename = None
        self._local_directory = None
        self._external_directory = external_directory
        self._protocol = 'robocopy'
        self.progress = None

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self.log.info(f'setting filename to: {filename}')
        self._filename = filename

    @property
    def local_directory(self):
        return self._local_directory

    @local_directory.setter
    def local_directory(self, local_directory: Path or str):
        self.log.info(f'setting local path to: {local_directory}')
        self._local_directory = Path(local_directory)

    @property
    def external_directory(self):
        return self._external_directory

    @property
    def signal_progress_percent(self):
        self.log.info(f'{self._filename} transfer progress: {self.progress} [%]')
        return self.progress

    def start(self):
        if not os.path.isfile(self._local_directory.absolute() / self._filename):
            raise FileNotFoundError(f"{self._local_directory} does not exist.")
        # xcopy requires an asterisk to indicate source and destination are
        # files, not directories.
        # TODO: identify if xcopy src/dest are files or directories, and
        #   annotate them as such.
        # flags = f'/j /mov /log:{self.local_directory.absolute()}\\log.txt /njh /njs'
        file_extension = Path(self._filename).suffix
        self._log_name = self._filename.replace(file_extension, 'txt')
        flags = f'/j /mov /njh /njs /log:{self._local_directory.absolute()}\\{self._log_name}'
        cmd_with_args = f'{self.protocol} {self._local_directory.absolute()} {self._external_directory.absolute()} \
            {self._filename} {flags}'
        self.log.info(f"transferring from {self._local_directory} to {self._external_directory}")
        # self.cmd = subprocess.run(cmd_with_args, check=True)
        self.thread = threading.Thread(target=self._run, args=(cmd_with_args,))
        self.thread.start()

    def wait_until_finished(self):
        self.thread.join()

    def is_alive(self):
        return self.thread.is_alive()

    def _run(self, cmd_with_args: str):
        subprocess = Popen(cmd_with_args, stdout=PIPE, stderr=STDOUT)
        # pause for 1 sec for log file first line write
        time.sleep(1)
        self.progress = 0
        while self.progress < 100:
            # open log file
            f = open(f'{self._local_directory.absolute()}\\{self.log_name}', 'r')
            # read the last line
            line = f.readlines()[-1]
            # close the log file
            f.close()
            # try to find if there is a % in the last line
            try:
                # conver the string to a float
                self.progress = float(line.replace('%',''))
            # line did not contain %
            except:
                self.progress = 0
            print(self.signal_progress_percent)
            # pause for 1 sec
            time.sleep(1)
        # cleanup the subprocess
        subprocess.kill()
        subprocess.wait()
        # remove the log file
        os.remove(f'{self._local_directory.absolute()}\\{self._log_name}')
        self.log.info(f"transfer finished")