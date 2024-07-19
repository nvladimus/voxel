"""File Transfer process in a separate class for Win/Linux compatibility."""
import os
import time
import logging
import threading
import shutil
from imohash import hashfile
from subprocess import Popen, DEVNULL
from pathlib import Path
from voxel.descriptors.deliminated_property import DeliminatedProperty

class FileTransfer():

    def __init__(self, external_path: str, local_path: str):
        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._external_path = Path(external_path)
        self._local_path = Path(local_path)
        if self._external_path == self._local_path:
            raise ValueError('External directory and local directory cannot be the same')
        self._progress = 0
        self._filename = None
        self._max_retry = 0
        self._acquisition_name = Path()
        self._protocol = 'robocopy'
        self._verify_transfer = False
        self._num_tries = 1
        self._timeout_s = 60

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self.log.info(f'setting filename to: {filename}')
        self._filename = filename

    @property
    def acquisition_name(self):
        return self._acquisition_name

    @acquisition_name.setter
    def acquisition_name(self, acquisition_name: str):
        self._acquisition_name = Path(acquisition_name)
        self.log.info(f'setting acquisition name to: {acquisition_name}')

    @property
    def local_path(self):
        return self._local_path

    @local_path.setter
    def local_path(self, local_path: str):
        self._local_path = Path(local_path)
        self.log.info(f'setting local path to: {local_path}')

    @property
    def external_path(self):
        return self._external_path

    @external_path.setter
    def external_path(self, external_path: str):
        self._external_path = Path(external_path)
        self.log.info(f'setting local path to: {external_path}')

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

    @DeliminatedProperty(minimum=0, maximum=100, unit='%')
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value: float):
        self._progress = value

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
        self.log.info(f"transferring from {self._local_path} to {self._external_path}")
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def wait_until_finished(self):
        self.thread.join()

    def is_alive(self):
        return self.thread.is_alive()

    def _run(self):
        
        local_directory = Path(self._local_path, self._acquisition_name)
        external_directory = Path(self._external_path, self._acquisition_name)
        
        transfer_complete = False
        retry_num = 0
        # loop over number of attempts in the event that a file transfer fails
        while transfer_complete == False and retry_num <= self._max_retry-1:
            # generate a list of subdirs and files in the parent local dir to delete at the end
            delete_list = []
            for name in os.listdir(local_directory.absolute()):
                if self.filename in name:
                    delete_list.append(name)
            # generate a list of files to copy
            # path is the entire experiment path
            # subdirs is any tile specific subdir i.e. zarr store
            # files are any tile specific files
            file_list = dict()
            for path, subdirs, files in os.walk(local_directory.absolute()):
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
                num_files = len(sorted_file_list)
                self.log.info(f'attempt {retry_num+1}/{self._max_retry}, tranferring {num_files} files.')
                for file_path, file_size_mb in sorted_file_list.items():
                    # transfer just one file and iterate
                    # split filename and path
                    [local_dir, filename] = os.path.split(file_path)
                    # specify external directory
                    # need to change directories to str because they are Path objects
                    external_dir = local_dir.replace(str(local_directory), str(external_directory))
                    # robocopy flags
                    # /j unbuffered copy for transfer speed stability
                    # /mov deletes local files after transfer
                    # /if move only the specified filename
                    # /njh no job header in log file
                    # /njs no job summary in log file
                    log_path = Path(local_directory, f"{self._filename}.txt")
                    cmd_with_args = f'{self._protocol} {local_dir} {external_dir} \
                        /j /if {filename} /njh /njs /log:{log_path}'
                    # stdout to PIPE will cause malloc errors on exist
                    # no stdout will print subprocess to python
                    # stdout to DEVNULL will supresss subprocess output
                    subprocess = Popen(cmd_with_args, stdout=DEVNULL)
                    # wait one second for process to start before monitoring log file for progress
                    time.sleep(1.0)
                    # lets monitor the progress of the individual file if size > 1 GB
                    if file_size_mb > 1024:
                        # wait for subprocess to start otherwise log file won't exist yet
                        time.sleep(1.0)
                        file_progress = 0
                        previous_progress = 0
                        stuck_time_s = 0
                        while file_progress < 100:
                            start_time_s = time.time()
                            # open log file
                            f = open(log_path, 'r')
                            # read the last line
                            line = f.readlines()[-1]
                            # close the log file
                            f.close()
                            # try to find if there is a % in the last line
                            try:
                                # convert the string to a float
                                file_progress = float(line.replace('%',''))
                            # line did not contain %
                            except:
                                file_progress = 0
                            # sum to transferred amount to track progress
                            self.progress = (total_transferred_mb +
                                            file_size_mb * file_progress / 100) / total_size_mb * 100
                            end_time_s = time.time()
                            # keep track of how long stuck at same progress
                            if self.progress == previous_progress:
                                stuck_time_s += (end_time_s - start_time_s)
                                self.log.info(stuck_time_s)
                                # break if exceeds timeout
                                if stuck_time_s >= self._timeout_s:
                                    self.log.info('timeout exceeded, restarting file transfer.')
                                    break
                            else:
                                stuck_time_s  = 0
                            previous_progress = self.progress
                            self.log.info(f'file transfer is {self.progress:.2f} % complete.')
                            # pause for 10 sec
                            time.sleep(10.0)
                    else:
                        subprocess.wait()
                        self.progress = (total_transferred_mb + file_size_mb) / total_size_mb * 100
                        self.log.info(f'file transfer is {self.progress:.2f} % complete.')
                    # wait for process to finish before cleaning log file
                    time.sleep(10.0)
                    # clean up and remove the temporary log file
                    os.remove(log_path)
                    # update the total transfered amount
                    total_transferred_mb += file_size_mb
                # clean up the local subdirs and files
                for file in delete_list:
                    # f is a relative path, convert to absolute
                    local_file_path = os.path.join(local_directory.absolute(), file)
                    external_file_path = os.path.join(external_directory.absolute(), file)
                    # .zarr is directory but os.path.isdir will return False
                    if os.path.isdir(local_file_path) or ".zarr" in local_dir:
                        # TODO how to hash check zarr -> directory instead of file?
                        shutil.rmtree(local_file_path)
                    elif os.path.isfile(local_file_path):
                        # verify transfer with hashlib
                        if self._verify_transfer:
                            # put in try except in case no external file found
                            try:
                                # if hash is verified delete file
                                if self._verify_file(local_file_path, external_file_path):
                                    # remove local file
                                    self.log.info(f'deleting {local_file_path}')
                                    os.remove(local_file_path)
                                # if has fails, external file is corrupt
                                else:
                                    # remove external file, try again
                                    self.log.info(f'hashes did not match, deleting {external_file_path}')
                                    os.remove(external_file_path)
                                    pass
                            except:
                                self.log.warning(f'no external file exists at {external_file_path}')
                        else:
                            # remove local file
                            self.log.info(f'deleting {local_file_path}')
                            os.remove(local_file_path)
                    else:
                        raise ValueError(f'{local_file_path} is not a file or directory.')
                self.log.info(f"transfer finished")
                subprocess.kill()
                retry_num += 1
