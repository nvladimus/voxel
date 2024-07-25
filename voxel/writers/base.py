import logging
from abc import abstractmethod
from multiprocessing import Event, Queue, Value
from pathlib import Path
from typing import Optional

import numpy


class BaseWriter:
    """
    Base class for all voxel writers.

    :param path: Path for the data writer
    :type path: str
    """

    def __init__(self, path: str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._path = Path(path)
        self._channel = None
        self._filename = None
        self._acquisition_name = None
        self._data_type = None
        self._compression = None
        self._row_count_px = None
        self._column_count_px = None
        self._frame_count_px_px = None
        self._shm_name = None
        self._x_voxel_size_um = None
        self._y_voxel_size_um = None
        self._z_voxel_size_um = None
        self._x_position_mm = None
        self._y_position_mm = None
        self._z_position_mm = None
        self._channel = None
        self._process = None
        # share values to update inside process
        self._progress = Value("d", 0.0)
        # share queue for passing logs out of process
        self._log_queue = Queue()
        # Flow control attributes to synchronize inter-process communication.
        self.done_reading = Event()
        self.done_reading.set()  # Set after processing all data in shared mem.
        self.deallocating = Event()

    @property
    def x_voxel_size_um(self):
        """Get x voxel size of the writer.

        :return: Voxel size in the x dimension in microns
        :rtype: float
        """

        return self._x_voxel_size_um

    @x_voxel_size_um.setter
    def x_voxel_size_um(self, x_voxel_size_um: float):
        """Set the x voxel size of the writer.

        :param value: Voxel size in the x dimension in microns
        :type value: float
        """

        self.log.info(f"setting x voxel size to: {x_voxel_size_um} [um]")
        self._x_voxel_size_um = x_voxel_size_um

    @property
    def y_voxel_size_um(self):
        """Get y voxel size of the writer.

        :return: Voxel size in the y dimension in microns
        :rtype: float
        """

        return self._y_voxel_size_um

    @y_voxel_size_um.setter
    def y_voxel_size_um(self, y_voxel_size_um: float):
        """Set the x voxel size of the writer.

        :param value: Voxel size in the y dimension in microns
        :type value: float
        """

        self.log.info(f"setting y voxel size to: {y_voxel_size_um} [um]")
        self._y_voxel_size_um = y_voxel_size_um

    @property
    def z_voxel_size_um(self):
        """Get z voxel size of the writer.

        :return: Voxel size in the z dimension in microns
        :rtype: float
        """

        return self._z_voxel_size_um

    @z_voxel_size_um.setter
    def z_voxel_size_um(self, z_voxel_size_um: float):
        """Set the z voxel size of the writer.

        :param value: Voxel size in the z dimension in microns
        :type value: float
        """

        self.log.info(f"setting z voxel size to: {z_voxel_size_um} [um]")
        self._z_voxel_size_um = z_voxel_size_um

    @property
    def x_position_mm(self):
        """Get x position of the writer.

        :return: Position in the x dimension in mm
        :rtype: float
        """

        return self._x_position_mm

    @x_position_mm.setter
    def x_position_mm(self, x_position_mm: float):
        """Set the x position of the writer.

        :param value: Position in the x dimension in mm
        :type value: float
        """

        self.log.info(f"setting x position to: {x_position_mm} [mm]")
        self._x_position_mm = x_position_mm

    @property
    def y_position_mm(self):
        """Get y position of the writer.

        :return: Position in the y dimension in mm
        :rtype: float
        """

        return self._y_position_mm

    @y_position_mm.setter
    def y_position_mm(self, y_position_mm: float):
        """Set the y position of the writer.

        :param value: Position in the x dimension in mm
        :type value: float
        """

        self.log.info(f"setting y position to: {y_position_mm} [mm]")
        self._y_position_mm = y_position_mm

    @property
    def z_position_mm(self):
        """Get z position of the writer.

        :return: Position in the z dimension in mm
        :rtype: float
        """

        return self._z_position_mm

    @z_position_mm.setter
    def z_position_mm(self, z_position_mm: float):
        """Set the z position of the writer.

        :param value: Position in the z dimension in mm
        :type value: float
        """

        self.log.info(f"setting z position to: {z_position_mm} [mm]")
        self._z_position_mm = z_position_mm

    @property
    @abstractmethod
    def theta_deg(self) -> float:
        """Get theta value of the writer.

        :return: Theta value in deg
        :rtype: float
        """

        pass

    @theta_deg.setter
    @abstractmethod
    def theta_deg(self, value: float) -> None:
        """Set the theta value of the writer.

        :param value: Theta value in deg
        :type value: float
        """

        pass

    @property
    @abstractmethod
    def frame_count_px(self) -> int:
        """Get the number of frames in the writer.

        :return: Frame number in pixels
        :rtype: int
        """

        pass

    @frame_count_px.setter
    @abstractmethod
    def frame_count_px(self, value: int) -> None:
        """Set the number of frames in the writer.

        :param value: Frame number in pixels
        :type value: int
        """

        pass

    @property
    def column_count_px(self):
        """Get the number of columns in the writer.

        :return: Column number in pixels
        :rtype: int
        """

        return self._column_count_px

    @column_count_px.setter
    def column_count_px(self, column_count_px: int):
        """Set the number of columns in the writer.

        :param value: Column number in pixels
        :type value: int
        """

        self.log.info(f"setting column count to: {column_count_px} [px]")
        self._column_count_px = column_count_px

    @property
    def row_count_px(self):
        """Get the number of rows in the writer.

        :return: Row number in pixels
        :rtype: int
        """

        return self._row_count_px

    @row_count_px.setter
    def row_count_px(self, row_count_px: int):
        """Set the number of rows in the writer.

        :param value: Row number in pixels
        :type value: int
        """

        self.log.info(f"setting row count to: {row_count_px} [px]")
        self._row_count_px = row_count_px

    @property
    @abstractmethod
    def chunk_count_px(self) -> int:
        """Get the chunk count in pixels

        :return: Chunk count in pixels
        :rtype: int
        """

        pass

    @property
    @abstractmethod
    def compression(self) -> str:
        """Get the compression codec of the writer.

        :return: Compression codec
        :rtype: str
        """

        pass

    @compression.setter
    @abstractmethod
    def compression(self, value: str) -> None:
        """Set the compression codec of the writer.

        :param value: Compression codec
        :type value: str
        """

        pass

    @property
    def data_type(self):
        """Get the data type of the writer.

        :return: Data type
        :rtype: numpy.unsignedinteger
        """

        return self._data_type

    @data_type.setter
    def data_type(self, data_type: numpy.unsignedinteger):
        """Set the data type of the writer.

        :param value: Data type
        :type value: numpy.unsignedinteger
        """

        self.log.info(f"setting data type to: {data_type}")
        self._data_type = data_type

    @property
    def path(self):
        """Get the path of the writer.

        :return: Path
        :rtype: Path
        """

        return self._path

    @property
    def acquisition_name(self):
        """
        The base acquisition name of the writer.

        :return: The base acquisition name
        :rtype: str
        """

        return self._acquisition_name

    @acquisition_name.setter
    def acquisition_name(self, acquisition_name: str):
        """
        The base acquisition name of writer.

        :param value: The base acquisition name
        :type value: str
        """

        self._acquisition_name = Path(acquisition_name)
        self.log.info(f"setting acquisition name to: {acquisition_name}")

    @property
    @abstractmethod
    def filename(self) -> str:
        """
        The base filename of file writer.

        :return: The base filename
        :rtype: str
        """

        pass

    @filename.setter
    @abstractmethod
    def filename(self, value: str) -> None:
        """
        The base filename of file writer.

        :param value: The base filename
        :type value: str
        """

        pass

    @property
    def channel(self):
        """
        The channel of the writer.

        :return: Channel
        :rtype: str
        """

        return self._channel

    @channel.setter
    def channel(self, channel: str):
        """
        The channel of the writer.

        :param value: Channel
        :type value: str
        """

        self.log.info(f"setting channel name to: {channel}")
        self._channel = channel

    @property
    @abstractmethod
    def color(self) -> Optional[str]:
        """
        The color of the writer.

        :return: Color
        :rtype: str
        """
        pass

    @color.setter
    @abstractmethod
    def color(self, value: str) -> Optional[None]:
        """
        The color of the writer.

        :param value: Color
        :type value: str
        """
        pass

    @property
    def shm_name(self):
        """
        The shared memory address (string) from the c array.

        :return: Shared memory address
        :rtype: str
        """

        return str(self._shm_name[:]).split("\x00")[0]

    @shm_name.setter
    def shm_name(self, name: str):
        """
        The shared memory address (string) from the c array.

        :param value: Shared memory address
        :type: str
        """

        for i, c in enumerate(name):
            self._shm_name[i] = c
        self._shm_name[len(name)] = "\x00"  # Null terminate the string.
        self.log.info(f"setting shared memory to: {name}")

    @property
    def signal_progress_percent(self):
        """Get the progress of the writer.

        :return: Progress in percent
        :rtype: float
        """
        # convert to %
        state = {"Progress [%]": self._progress.value * 100}
        self.log.info(f"Progress [%]: {self._progress.value*100}")
        return state

    def get_logs(self):
        """
        Get logs from the writer run process.
        """
        while not self._log_queue.empty():
            self.log.info(self._log_queue.get())

    def start(self):
        """
        Start the writer.
        """
        self.log.info(f"{self._filename}: starting writer.")
        self._process.start()

    def wait_to_finish(self):
        """
        Wait for the writer to finish.
        """

        self.log.info(f"{self._filename}: waiting to finish.")
        self._process.join()
        # log the finished writer %
        self.signal_progress_percent

    @abstractmethod
    def delete_files(self):
        """
        Delete all files generated by the writer.
        """
        pass

    @abstractmethod
    def prepare(self):
        """
        Prepare the writer.
        """
        pass

    @abstractmethod
    def _run(self):
        """
        Internal run function of the writer.
        """
        pass
