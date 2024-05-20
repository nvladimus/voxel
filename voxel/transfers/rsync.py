"""File Transfer process in a separate class for Win/Linux compatibility."""
import os
import time
import logging
import sys
import threading
import shutil
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from typing import List, Any, Iterable

class FileTransfer():

    def __init__(self, external_directory: str, local_directory: str):
        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # check path for forward slashes
        if '\\' in external_directory or '/' not in external_directory:
            assert ValueError('external_directory string should only contain / not \\')
        self._external_directory = str(external_directory)
        self._local_directory = Path(local_directory)
        if self._external_directory == self._local_directory:
            raise ValueError('External directory and local directory cannot be the same')
        self._filename = None
        self._protocol = 'rsync'
        self.progress = 0
        self._output_file = None
        # print progress, delete files after transfer
        # check version of rsync
        # tested with v2.6.9
        # --info=progress2 is not available for rsync v2.x.x
        # self._flags = ['--progress', '--remove-source-files', '--recursive']
        # tested with v3.2.7
        # --progress outputs progress which is piped to log file
        # --recursive transfers all files in directory sequentially
        # --info=progress2 outputs % progress for all files not sequentially for each file
        self._flags = ['--progress', '--recursive', '--info=progress2']

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
        self._external_directory = str(external_directory)
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
            # make external directory tree if needed
            if not os.path.isdir(external_dir):
                os.makedirs(external_dir)
            # setup log file
            log_path = Path(f'{self._local_directory.absolute()}/{self._filename}.txt')
            self._log_file = open(log_path, 'w')
            self.log.info(f"transferring {file_path} from {self._local_directory} to {self._external_directory}")
            # generate rsync command with args
            cmd_with_args = self._flatten([self._protocol,
                                           self._flags,
                                           file_path,
                                           Path(external_dir) / Path(filename)])
            subprocess = Popen(cmd_with_args, stdout=self._log_file)
            self._log_file.close()
            time.sleep(0.01)
            # lets monitor the progress of the individual file if size > 1 GB
            if file_size_mb > 1024:
                file_progress = 0
                while file_progress < 100:
                    # open the stdout file in a temporary handle with r+ mode
                    f = open(f'{self._local_directory / self._log_file}', 'r+')
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
                            file_progress = float(value.rstrip())
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
                            file_progress = float(value.rstrip())
                    # no lines in the file yet          
                    except:
                        file_progress = 0
                    # sum to transferred amount to track progress
                    self.progress = (total_transferred_mb +
                                    file_size_mb * file_progress / 100) / total_size_mb * 100
                    # close temporary stdout file handle
                    f.close()
                    # pause for 1 sec
                    time.sleep(0.001)
            else:
                subprocess.wait()
                self.progress = (total_transferred_mb + file_size_mb) / total_size_mb * 100
            # clean up and remove the temporary log file
            os.remove(log_path)
            # update the total transfered amount
            total_transferred_mb += file_size_mb
            # self.log.info(f'file transfer is {self.progress:.2f} % complete.')         
        # clean up the local subdirs and files
        for f in delete_list:
            self.log.info(f"deleting {f}")
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