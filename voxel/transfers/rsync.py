import os
import time
import logging
import threading
import shutil
import sys
from imohash import hashfile
from subprocess import Popen
from pathlib import Path
from typing import List, Any, Iterable

class FileTransfer():

    def __init__(self, external_directory: str, local_directory: str):
        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._external_directory = Path(external_directory)
        self._local_directory = Path(local_directory)
        if self._external_directory == self._local_directory:
            raise ValueError('External directory and local directory cannot be the same')
        self._filename = None
        self._protocol = 'rsync'
        self._verify_transfer = False
        self._num_tries = 1
        self._timeout_s = 60
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
    def local_directory(self, local_directory: str):
        self._local_directory = Path(local_directory)
        self.log.info(f'setting local path to: {local_directory}')

    @property
    def external_directory(self):
        return self._external_directory

    @external_directory.setter
    def external_directory(self, external_directory: str):
        self._external_directory = str(external_directory)
        self.log.info(f'setting local path to: {external_directory}')

    @property
    def verify_transfer(self):
        return self._verify_transfer

    @verify_transfer.setter
    def verify_transfer(self, verify_transfer: bool):
        self._verify_transfer = verify_transfer
        self.log.info(f'setting verify transfer to: {verify_transfer}')

    @property
    def max_retry(self):
        return self._max_retry

    @max_retry.setter
    def max_retry(self, max_retry: int):
        self._max_retry = max_retry
        self.log.info(f'setting max retry to: {max_retry}')

    @property
    def timeout_s(self):
        return self._timeout_s

    @timeout_s.setter
    def timeout_s(self, timeout_s: float):
        self._timeout_s = timeout_s
        self.log.info(f'setting timeout to: {timeout_s}')

    @property
    def signal_progress_percent(self):
        state = {}
        state['Transfer Progress [%]'] = self.progress
        self.log.info(f'{self._filename} transfer progress: {self.progress:.2f} [%]')
        return state

    def _verify_file(self, local_file_path: str, external_file_path: str):
        # verifying large files with a full checksum is too time consuming
        # verifying based on file size alone is not thorough
        # use imohash library to perform hasing on small subset of file
        # imohash defaults to reading 16K bits (i.e. 1<<14) from beginning, middle, and end
        local_hash = hashfile(local_file_path, sample_size=1<<14)
        external_hash = hashfile(external_file_path, sample_size=1<<14)
        if local_hash == external_hash:
            self.log.info(f'{local_file_path} and {external_file_path} hashes match')
            return True
        else:
            self.log.info(f'hash mismatch for {local_file_path} and {external_file_path}')
            self.log.info(f'{local_file_path} hash = {local_hash}')
            self.log.info(f'{external_file_path} hash = {external_hash}')
            return False
        
    def start(self):
        self.log.info(f"transferring from {self._local_directory} to {self._external_directory}")
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def wait_until_finished(self):
        self.thread.join()

    def is_alive(self):
        return self.thread.is_alive()

    def _run(self):
        transfer_complete = False
        retry_num = 0
        # loop over number of attempts in the event that a file transfer fails
        while transfer_complete == False and retry_num <= self._max_retry-1:
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
            # if file list is empty, transfer must be complete
            if not sorted_file_list:
                transfer_complete = True
            # if not, try to initiate transfer again
            else:
                self.log.info(f'starting file transfer attempt {retry_num+1}/{self._max_retry}')
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
                    log_path = Path(self._local_directory, f"{self._filename}.txt")
                    self._log_file = open(log_path, 'w')
                    self.log.info(f"transferring {file_path} from {self._local_directory} to {self._external_directory}")
                    # generate rsync command with args
                    if sys.platform == "win32":
                        # if windows, rsync expects absolute paths with driver letters to use
                        # /cygdrive/drive-letter and / not \
                        # example: /cygdrive/c/test/filename.extension
                        file_path = file_path.replace('\\', '/').replace(':', '')
                        file_path = '/cygdrive/' + file_path
                        external_dir = external_dir.replace('\\', '/').replace(':', '')
                        external_dir = '/cygdrive/' + external_dir + '/' + filename
                        cmd_with_args = self._flatten([self._protocol,
                                        self._flags,
                                        file_path,
                                        external_dir])
                    elif sys.platform == 'darwin' or 'linux' or 'linux2':
                        # linux or darwin, paths defined as below
                        cmd_with_args = self._flatten([self._protocol,
                                        self._flags,
                                        file_path,
                                        Path(external_dir, filename)])
                    subprocess = Popen(cmd_with_args, stdout=self._log_file)
                    self._log_file.close()
                    time.sleep(0.01)
                    # lets monitor the progress of the individual file if size > 1 GB
                    if file_size_mb > 1024:
                        # wait for subprocess to start otherwise log file won't exist yet
                        time.sleep(1.0)
                        file_progress = 0
                        previous_progress = 0
                        stuck_time_s = 0
                        while file_progress < 100:
                            start_time_s = time.time()
                            # open the stdout file in a temporary handle with r+ mode
                            f = open(log_path, 'r+')
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
                            end_time_s = time.time()
                            # keep track of how long stuck at same progress
                            if self.progress == previous_progress:
                                stuck_time_s += (end_time_s - start_time_s)
                                # break if exceeds timeout
                                if stuck_time_s >+ self._timeout_s:
                                    break
                            previous_progress = self.progress
                            self.log.info(f'file transfer is {self.progress:.2f} % complete.')
                            # close temporary stdout file handle
                            f.close()
                            # pause for 1 sec
                            time.sleep(0.001)
                    else:
                        subprocess.wait()
                        self.progress = (total_transferred_mb + file_size_mb) / total_size_mb * 100
                        self.log.info(f'file transfer is {self.progress:.2f} % complete.')
                    # clean up and remove the temporary log file
                    os.remove(log_path)
                    # update the total transfered amount
                    total_transferred_mb += file_size_mb
                    # self.log.info(f'file transfer is {self.progress:.2f} % complete.')         
                # clean up the local subdirs and files
                for file in delete_list:
                    # f is a relative path, convert to absolute
                    local_file_path = os.path.join(self._local_directory.absolute(), file)
                    external_file_path = os.path.join(self._external_directory.absolute(), file)
                    # .zarr is directory but os.path.isdir will return False
                    if os.path.isdir(local_file_path) or ".zarr" in local_dir:
                        # TODO how to hash check zarr -> directory instead of file?
                        shutil.rmtree(local_file_path)
                    elif os.path.isfile(local_file_path):
                        # verify transfer with hashlib
                        if self._verify_transfer:
                            # if hash is verified delete file
                            if self._verify_file(local_file_path, external_file_path):
                                # remove local file
                                os.remove(local_file_path)
                            # if has fails, external file is corrupt
                            else:
                                # remove external file, try again
                                os.remove(external_file_path)
                                pass
                    else:
                        raise ValueError(f'{local_file_path} is not a file or directory.')
                self.log.info(f"transfer finished")
                subprocess.kill()
                retry_num += 1

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
