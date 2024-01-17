"""File Transfer process in a separate class for Win/Linux compatibility."""
import os
import time
import logging
import sys
import threading
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path

class FileTransfer():

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.filename = None
        self._local_drive = None
        self._external_drive = None
        self._protocol = None
        self.progress = None

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

    @external_drive.setter
    def external_drive(self, external_drive: Path or str):
        self.log.info(f'setting external path to: {external_drive}')
        self._external_drive = Path(external_drive)

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, protocol: str):
        self.log.info(f'setting transfer protocol to: {protocol}')
        self._protocol = protocol

    def get_progress(self):
        self.log.info(f'{self.filename} transfer progress: {self.progress} [%]')

    def start(self):
        if not os.path.isfile(self.local_drive.absolute() / self.filename):
            raise FileNotFoundError(f"{self.local_drive} does not exist.")
        # xcopy requires an asterisk to indicate source and destination are
        # files, not directories.
        # TODO: identify if xcopy src/dest are files or directories, and
        #   annotate them as such.
        # flags = f'/j /mov /log:{self.local_drive.absolute()}\\log.txt /njh /njs'
        self.log_name = self.filename.replace('ims', 'txt')
        flags = f'/j /mov /njh /njs /log:{self.local_drive.absolute()}\\{self.log_name}'
        cmd_with_args = f'{self.protocol} {self.local_drive.absolute()} {self.external_drive.absolute()} \
            {self.filename} {flags}'
        self.log.info(f"transferring from {self.local_drive} to {self.external_drive}")
        # self.cmd = subprocess.run(cmd_with_args, check=True)
        self.thread = threading.Thread(target=self._run, args=(cmd_with_args,))
        self.thread.start()

    def join(self):
        self.thread.join()

    def is_alive(self):
        return self.thread.is_alive()

    def _run(self, cmd_with_args: str):
        subprocess = Popen(cmd_with_args, stdout=PIPE, stderr=STDOUT)  # blocks.
        time.sleep(1)
        self.progress = 0
        while self.progress < 100:
            f = open(f'{self.local_drive.absolute()}\\{self.log_name}', 'r')
            line = f.readlines()[-1]
            f.close()
            del f
            try:
                self.progress = float(line.replace('%',''))
            except:
                self.progress = 0
            self.get_progress()
            time.sleep(1)
        # while subprocess.poll() == None:
        #     time.sleep(1)
        # with subprocess.stdout:
        #     try:
        #         for line in iter(subprocess.stdout.readline, b''):
        #             self.log.info(f'subprocess: {line.decode("utf-8").strip()}')       
        #     except CalledProcessError as e:
        #         self.log.info(f"{str(e)}")
        subprocess.kill()
        subprocess.wait()
        os.remove(f'{self.local_drive.absolute()}\\{self.log_name}')
        self.log.info(f"transfer finished")

