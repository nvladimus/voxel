from abc import abstractmethod

# TODO should we have a base VoxelProcess?
# from ..base import VoxelDevice


class BaseFileTransfer:
    """
    Base class for all voxel file transfer processes.

    Process will transfer files with the following regex\n
    format:\n
    \n
    From -> \\local_path\\acquisition_name\\filename*\n
    To -> \\external_path\\acquisition_name\\filename*
    """

    def __init__(self, external_path: str, local_path: str):
        super().__init__(external_path, local_path)

    @property
    @abstractmethod
    def filename(self):
        """
        The base filename of files to be transferred.

        :return: The base filename
        :rtype: str
        """
        pass

    @filename.setter
    @abstractmethod
    def filename(self, value: str) -> None:
        """
        The base filename of files to be transferred.

        :param value: The base filename
        :type value: str
        """
        pass

    @property
    @abstractmethod
    def acquisition_name(self):
        """
        The base acquisition name of files to be transferred.

        :return: The base filename
        :rtype: str
        """
        pass

    @acquisition_name.setter
    @abstractmethod
    def acquisition_name(self, value: str) -> None:
        """
        The base acquisition name of files to be transferred.

        :param value: The base acquisition_name
        :type value: str
        """
        pass

    @property
    @abstractmethod
    def local_path(self):
        """
        The local path of files to be transferred.

        :return: The local path
        :rtype: str
        """
        pass

    @local_path.setter
    @abstractmethod
    def local_path(self, value: str) -> None:
        """
        The local path of files to be transferred.

        :param value: The local path
        :type value: str
        """
        pass

    @property
    @abstractmethod
    def external_path(self):
        """
        The external path of files to be transferred.

        :return: The external path
        :rtype: str
        """
        pass

    @external_path.setter
    @abstractmethod
    def external_path(self, value: str) -> None:
        """
        The external path of files to be transferred.

        :param value: The external path
        :type value: str
        """
        pass

    @property
    @abstractmethod
    def verify_transfer(self):
        """
        State of transfer process.

        :return: The transfer process state
        :rtype: str
        """
        pass

    @verify_transfer.setter
    @abstractmethod
    def verify_transfer(self, value: bool) -> None:
        """
        State of transfer process.

        :param value: The transfer process state
        :type value: bool
        """
        pass

    @property
    @abstractmethod
    def max_retry(self):
        """
        Number of times to retry the transfer process.

        :return: Number of retry attempts
        :rtype: int
        """
        pass

    @max_retry.setter
    @abstractmethod
    def max_retry(self, value: int) -> None:
        """
        Number of times to retry the transfer process.

        :param value: Number of retry attempts
        :type value: int
        """
        pass

    @property
    @abstractmethod
    def timeout_s(self):
        """
        Timeout for the transfer process.

        :return: Timeout in seconds
        :rtype: float
        """
        pass

    @timeout_s.setter
    @abstractmethod
    def timeout_s(self, value: float) -> None:
        """
        Timeout for the transfer process.

        :param value: Timeout in seconds
        :type value: float
        """
        pass

    @property
    @abstractmethod
    def signal_process_percent(self):
        """
        Get the progress of the transfer process.

        :return: Progress in percent
        :rtype: float
        """
        pass

    @abstractmethod
    def start(self):
        """
        Start the transfer process.
        """
        pass

    @abstractmethod
    def wait_until_finished(self):
        """
        Wait for the transfer process to finish.
        """
        pass

    @abstractmethod
    def is_alive(self):
        """
        Check if the transfer process is still running.
        """
        pass

    @abstractmethod
    def _run(self):
        """
        Internal function that runs the transfer process.
        """
        pass

    @abstractmethod
    def _verify_file(self, local_file_path: str, external_file_path: str):
        """
        Internal function that hash checks a transfered file.

        :return: State of transfered file
        :rtype: bool
        """
        pass
