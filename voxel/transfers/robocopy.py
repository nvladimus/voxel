"""File Transfer process in a separate class for Win/Linux compatibility."""
import os
import time
import logging
import sys
import threading
import glob
import shutil
from subprocess import Popen, PIPE, STDOUT, DEVNULL
from pathlib import Path

class FileTransfer():

    def __init__(self, external_directory: str, local_directory: str):
        super().__init__()
        # check path for forward slashes
        if '\\' in external_directory or '/' not in external_directory:
            assert ValueError('external_directory string should only contain / not \\')
        self._external_directory = Path(external_directory)
        self._local_directory = Path(local_directory)
        if self._external_directory == self._local_directory:
            raise ValueError('External directory and local directory cannot be the same')
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._filename = ''
        self._protocol = 'robocopy'
        self.progress = 0

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
    def local_directory(self, local_directory: str or Path):
        if '\\' in str(local_directory) or '/' not in str(local_directory):
            assert ValueError('external_directory string should only contain / not \\')
        # add a forward slash at end so directory name itself is not copied, contents only
        self._local_directory = Path(local_directory)
        self.log.info(f'setting local path to: {local_directory}')

    @property
    def external_directory(self):
        return self._external_directory

    @external_directory.setter
    def external_directory(self, external_directory: str or Path):
        if '\\' in str(external_directory) or '/' not in str(external_directory):
            assert ValueError('external_directory string should only contain / not \\')
        # add a forward slash at end so directory name itself is not copied, contents only
        self._external_directory = Path(external_directory)
        self.log.info(f'setting local path to: {external_directory}')

    @property
    def signal_progress_percent(self):
        state = {}
        state['Transfer Progress [%]'] = self.progress
        self.log.info(f'{self._filename} transfer progress: {self.progress:.2f} [%]')
        return state

    def start(self):
        self.log.info(f"transferring from {self._local_directory} to {self._external_directory}")
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def wait_until_finished(self):
        self.thread.join()

    def is_alive(self):
        return self.thread.is_alive()

    def _run(self):
        # generate a list of subdirs and files in the parent local dir to delete at the end
        delete_list = []
        for name in os.listdir(self._local_directory.absolute()):
            if self.filename in name:
                delete_list.append(name)
        # generate a list of files to copy
        # path is the entire experiment path
        # subdirs is any tile specific subdir i.e. zarr store
        # files are any tile specific files
        file_list = dict()
        for path, subdirs, files in os.walk(self._local_directory.absolute()):
            for name in files:
                # check and only add if filename matches tranfer's filename
                if self.filename in name:
                    file_list[os.path.join(path, name)] = os.path.getsize(os.path.join(path, name))/1024**2
        total_size_mb = sum(file_list.values())
        # sort the file list based on the file sizes and create a list for transfers
        sorted_file_list = dict(sorted(file_list.items(), key = lambda item: item[1]))
        total_transferred_mb = 0
        for file_path, file_size_mb in sorted_file_list.items():
            # transfer just one file and iterate
            # split filename and path
            [local_dir, filename] = os.path.split(file_path)
            # specify external directory
            # need to change directories to str because they are Path objects
            external_dir = local_dir.replace(str(self._local_directory), str(self._external_directory))
            # robocopy flags
            # /j unbuffered copy for transfer speed stability
            # /mov deletes local files after transfer
            # /if move only the specified filename
            # /njh no job header in log file
            # /njs no job summary in log file
            log_path = Path(f'{self._local_directory.absolute()}/{self._filename}.txt')
            cmd_with_args = f'{self._protocol} {local_dir} {external_dir} \
                /j /if {filename} /njh /njs /log:{log_path}'
            # stdout to PIPE will cause malloc errors on exist
            # no stdout will print subprocess to python
            # stdout to DEVNULL will supresss subprocess output
            subprocess = Popen(cmd_with_args, stdout=DEVNULL)
            time.sleep(0.01)
            # lets monitor the progress of the individual file if size > 1 GB
            if file_size_mb > 1024:
                file_progress = 0
                while file_progress < 100:
                    # open log file
                    f = open(f'{log_path}', 'r')
                    # read the last line
                    line = f.readlines()[-1]
                    # close the log file
                    f.close()
                    # try to find if there is a % in the last line
                    try:
                        # conver the string to a float
                        file_progress = float(line.replace('%',''))
                    # line did not contain %
                    except:
                        file_progress = 0
                    # sum to transferred amount to track progress
                    self.progress = (total_transferred_mb +
                                    file_size_mb * file_progress / 100) / total_size_mb * 100
                    # pause for 1 sec
                    time.sleep(0.1)
            else:
                subprocess.wait()
                self.progress = (total_transferred_mb + file_size_mb) / total_size_mb * 100
            # clean up and remove the temporary log file
            os.remove(log_path)
            # update the total transfered amount
            total_transferred_mb += file_size_mb
            self.log.info(f'file transfer is {self.progress:.2f} % complete.')
        # clean up the local subdirs and files
        for f in delete_list:
            # f is a relative path, convert to absolute
            f = os.path.join(self._local_directory.absolute(), f)
            # .zarr is directory but os.path.isdir will return False
            if os.path.isdir(f) or ".zarr" in f:
                shutil.rmtree(os.path.join(self._local_directory.absolute(), f))
            elif os.path.isfile(f):
                os.remove(os.path.join(self._local_directory.absolute(), f))
            else:
                raise ValueError(f'{f} is not a file or directory.')
        self.log.info(f"transfer finished")
        subprocess.kill()