"""File Transfer process in a separate class for Win/Linux compatibility."""
import os
import time
import logging
import sys
import threading
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from typing import List, Any, Iterable

class FileTransfer():

    def __init__(self, external_directory: str):
        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # check path for forward slashes
        if '\\' in external_directory or '/' not in external_directory:
            assert ValueError('external_directory string should only contain / not \\')
        self._external_directory = Path(external_directory)
        self._filename = None
        self._local_directory = None
        self._protocol = 'rsync'
        self.progress = 0
        self._output_file = None
        # print progress, delete files after transfer
        self._flags = ['--progress', '--remove-source-files', '--recursive']

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
    def local_directory(self, local_directory: str):
        if '\\' in local_directory or '/' not in local_directory:
            assert ValueError('external_directory string should only contain / not \\')
        # add a forward slash at end so directory name itself is not copied, contents only
        self._local_directory = Path(local_directory)
        self.log.info(f'setting local path to: {local_directory}')

    @property
    def external_directory(self):
        return self._external_directory

    @property
    def signal_progress_percent(self):
        self.log.info(f'{self.filename} transfer progress: {self.progress} [%]')
        return self.progress

    def start(self):
        if not os.path.isfile(self._local_directory / self._filename):
            raise FileNotFoundError(f"{self._local_directory / self._filename} does not exist.")
        file_extension = Path(self._filename).suffix
        self._log_filename = self._filename.replace(file_extension, '.txt')
        # do not move and transfer log file
        self._exclude = ["--exclude", self._log_filename]
        # open log file for writing to pipe into stdout
        self._log_file = open(f'{self._local_directory / self._log_filename}', 'w')
        self.log.info(f"transferring from {self._local_directory} to {self._external_directory}")
        # add a forward slash at end so local directory itself is not copied, contents only
        cmd_with_args = self._flatten([self._protocol,
                                       self._flags,
                                       self._exclude,
                                       f'{self._local_directory}/',
                                       self._external_directory])
        self.thread = threading.Thread(target=self._run,
                                       args=(list(cmd_with_args),))
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
            f = open(f'{self._local_directory / self._log_filename}', 'r+')
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
                    self.log.info(f'file transfer is {self.progress} % complete.')
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
        os.remove(f'{self._local_directory / self._log_filename}')
        self.log.info(f"transfer finished")

    def _flatten(self, lst: List[Any]) -> Iterable[Any]:
        """Flatten a list using generators comprehensions.
            Returns a flattened version of list lst.
        """
        for sublist in lst:
             if isinstance(sublist, list):
                 for item in sublist:
                     yield item
             else:
                 yield sublist