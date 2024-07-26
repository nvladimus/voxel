import logging
from multiprocessing import Event, Process
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path

import numpy as np
import tifffile
from fast_histogram import histogram1d


class HistogramProjection:
    """
    Voxel driver for performing histogram projections along the x, y, and z axes.

    :param path: Path for the histogram projection process
    :type path: str
    """

    def __init__(self, path: str):

        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._path = Path(path)
        self._column_count_px = None
        self._row_count_px = None
        self._frame_count_px_px = None
        self._x_bin_count_px = None
        self._y_bin_count_px = None
        self._z_bin_count_px = None
        self._x_bins = None
        self._y_bins = None
        self._z_bins = None
        self._filename = None
        self._acquisition_name = Path()
        self._data_type = None
        self.new_image = Event()
        self.new_image.clear()

    @property
    def column_count_px(self) -> int:
        """Get the number of columns in the writer.

        :return: Column number in pixels
        :rtype: int
        """

        return self._column_count_px

    @column_count_px.setter
    def column_count_px(self, column_count_px: int) -> None:
        """Set the number of columns in the writer.

        :param column_count_px: Column number in pixels
        :type column_count_px: int
        """

        self.log.info(f"setting column count to: {column_count_px} [px]")
        self._column_count_px = column_count_px

    @property
    def row_count_px(self) -> int:
        """Get the number of rows in the writer.

        :return: Row number in pixels
        :rtype: int
        """

        return self._row_count_px

    @row_count_px.setter
    def row_count_px(self, row_count_px: int) -> None:
        """Set the number of rows in the writer.

        :param row_count_px: Row number in pixels
        :type row_count_px: int
        """

        self.log.info(f"setting row count to: {row_count_px} [px]")
        self._row_count_px = row_count_px

    @property
    def frame_count_px(self) -> int:
        """Get the number of frames in the writer.

        :return: Frame number in pixels
        :rtype: int
        """

        return self._frame_count_px

    @frame_count_px.setter
    def frame_count_px(self, frame_count_px: int) -> None:
        """Set the number of frames in the writer.

        :param frame_count_px: Frame number in pixels
        :type frame_count_px: int
        """

        self.log.info(f"setting frame count to: {frame_count_px} [px]")
        self._frame_count_px_px = frame_count_px

    @property
    def x_bin_count_px(self):
        """Get the number the x size of bins in pixels.

        :return: X size of bins in pixels
        :rtype: int
        """

        return self._x_bin_count_px

    @x_bin_count_px.setter
    def x_bin_count_px(self, x_bin_count_px: int):
        """Set the number the x size of bins in pixels.

        :param x_bin_count_px: X size of bins in pixels
        :type x_bin_count_px: int
        """

        self.log.info(f'setting x projection count to: {x_bin_count_px} [px]')
        self._x_bin_count_px = x_bin_count_px

    @property
    def y_bin_count_px(self):
        """Get the number the y size of bins in pixels.

        :return: Y size of bins in pixels
        :rtype: int
        """

        return self._y_bin_count_px

    @y_bin_count_px.setter
    def y_bin_count_px(self, y_bin_count_px: int):
        """Set the number the y size of bins in pixels.

        :param y_bin_count_px: Y size of bins in pixels
        :type y_bin_count_px: int
        """

        self.log.info(f'setting y rojection count to: {y_bin_count_px} [px]')
        self._y_bin_count_px = y_bin_count_px

    @property
    def z_bin_count_px(self):
        """Get the number the z size of bins in pixels.

        :return: Z size of bins in pixels
        :rtype: int
        """

        return self._z_bin_count_px

    @z_bin_count_px.setter
    def z_bin_count_px(self, z_bin_count_px: int):
        """Set the number the z size of bins in pixels.

        :param z_bin_count_px: Z size of bins in pixels
        :type z_bin_count_px: int
        """

        self.log.info(f'setting z projection count to: {z_bin_count_px} [px]')
        self._z_bin_count_px = z_bin_count_px

    @property
    def x_bins(self):
        """Get the number of intensity bins for the x direction.

        :return: Number of intensity bins for the x direction
        :rtype: int
        """

        return self._x_bins

    @x_bins.setter
    def x_bins(self, x_bins: int):
        """Set the number of intensity bins for the x direction.

        :param x_bin_count_px: Number of intensity bins for the x direction
        :type x_bin_count_px: int
        """

        self.log.info(f'setting x bin count to: {x_bins} [px]')
        self._x_bins = x_bins

    @property
    def y_bins(self):
        """Get the number of intensity bins for the y direction.

        :return: Number of intensity bins for the y direction
        :rtype: int
        """

        return self._y_bins

    @y_bins.setter
    def y_bins(self, y_bins: int):
        """Set the number of intensity bins for the y direction.

        :param y_bin_count_px: Number of intensity bins for the y direction
        :type y_bin_count_px: int
        """

        self.log.info(f'setting x bin count to: {y_bins} [px]')
        self._y_bins = y_bins

    @property
    def z_bins(self):
        """Get the number of intensity bins for the z direction.

        :return: Number of intensity bins for the z direction
        :rtype: int
        """

        return self._z_bins

    @z_bins.setter
    def z_bins(self, z_bins: int):
        """Set the number of intensity bins for the z direction.

        :param z_bin_count_px: Number of intensity bins for the z direction
        :type z_bin_count_px: int
        """

        self.log.info(f'setting x bin count to: {z_bins} [px]')
        self._z_bins = z_bins

    @property
    def data_type(self):
        """Get the data type of the writer.

        :return: Data type
        :rtype: numpy.unsignedinteger
        """

        return self._data_type

    @data_type.setter
    def data_type(self, data_type: np.unsignedinteger):
        """Set the data type of the writer.

        :param data_type: Data type
        :type data_type: numpy.unsignedinteger
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
    def filename(self) -> str:
        """
        The base filename of file writer.

        :return: The base filename
        :rtype: str
        """

        return self._filename

    @filename.setter
    def filename(self, filename: str) -> None:
        """
        The base filename of file writer.

        :param filename: The base filename
        :type filename: str
        """

        self._filename = (
            filename.replace(".tiff", "").replace(".tif", "")
            if filename.endswith(".tiff") or filename.endswith(".tif")
            else f"{filename}"
        )
        self.log.info(f"setting filename to: {filename}")

    def prepare(self, shm_name):
        """
        Prepare the max projection process.

        :param shm_name: Shared memory name
        :type shm_name: multiprocessing.shared_memory.SharedMemory
        """

        self._process = Process(target=self._run)
        self.shm_shape = (self._row_count_px, self._column_count_px)
        # create attributes to open shared memory in run function
        self.shm = SharedMemory(shm_name, create=False)
        self.latest_img = np.ndarray(
            self.shm_shape, self._data_type, buffer=self.shm.buf
        )
 
    def start(self):
        """
        Start the writer.
        """
        self.log.info(f"{self._filename}: starting max projection process.")
        self._process.start()

    def _run(self):
        """_summary_

        :raises ValueError: _description_
        :raises ValueError: _description_
        :raises ValueError: _description_
        """        
        # check if projection counts were set
        # if not, set to max possible values based on tile
        if self._x_bin_count_px is None:
            x_projection = False
        else:
            x_projection = True
            if self._x_bin_count_px < 0 or self._x_bin_count_px > self._column_count_px:
                raise ValueError(f'x projection must be > 0 and < {self._column_count_px}')
            x_index_list = np.arange(0, self._column_count_px, self._x_bin_count_px)
            if self._column_count_px not in x_index_list:
                x_index_list = np.append(x_index_list, self._column_count_px)
            self.histogram_x = np.zeros((self._x_bins, len(x_index_list)-1), dtype='float32')
        if self._y_bin_count_px is None:
            y_projection = False
        else:
            y_projection = True
            if self._y_bin_count_px < 0 or self._y_bin_count_px > self._row_count_px:
                raise ValueError(f'y projection must be > 0 and < {self._row_count_px}')
            y_index_list = np.arange(0, self._row_count_px, self._y_bin_count_px)
            if self._row_count_px not in y_index_list:
                y_index_list = np.append(y_index_list, self._row_count_px)
            self.histogram_y = np.zeros((self._y_bins, len(y_index_list)-1), dtype='float32')
        if self._z_bin_count_px is None:
            z_projection = False
        else:
            z_projection = True
            if self._z_bin_count_px < 0 or self._z_bin_count_px > self._frame_count_px_px:
                raise ValueError(f'z projection must be > 0 and < {self._frame_count_px}')
            z_index_list = np.arange(0, self._frame_count_px_px, self._z_bin_count_px)
            if self._frame_count_px_px not in z_index_list:
                z_index_list = np.append(z_index_list, self._frame_count_px_px)
            self.histogram_z = np.zeros((self._z_bins, len(z_index_list)-1), dtype='float32')

        frame_index = 0
        z_chunk_number = 0

        while frame_index < self._frame_count_px_px:
            # max project latest image
            if self.new_image.is_set():
                self.latest_img = np.ndarray(self.shm_shape, self._data_type, buffer=self.shm.buf)
                if z_projection:
                    # if this projection thickness is complete or end of stack
                    chunk_index = frame_index % self._z_bin_count_px
                    if chunk_index == self._z_bin_count_px - 1 or frame_index == self._frame_count_px_px - 1:
                        self.histogram_z[:, z_chunk_number] = histogram1d(self.latest_img,
                                                                          bins=self._z_bins, range=[0, self._max_value])
                        z_chunk_number += 1
                if x_projection:
                    for i in range(0, len(x_index_list)-1):
                        self.histogram_x[:, i] = histogram1d(self.latest_img[:, x_index_list[i]:x_index_list[i+1]],
                                                             bins=self._x_bins, range=[0, self._max_value])
                if y_projection:
                    for i in range(0, len(y_index_list)-1):
                        self.histogram_y[:, i] = histogram1d(self.latest_img[y_index_list[i]:y_index_list[i+1], :],
                                                             bins=self._y_bins, range=[0, self._max_value])
                frame_index += 1
                self.new_image.clear()
        # save projections
        self.log.info(f'saving {self.filename}_histogram_x.tiff')
        tifffile.imwrite(Path(self._processath, self._acquisition_name, f"{self.filename}_histogram_x.tiff"), self.histogram_x)
        self.log.info(f'saving {self.filename}_histogram_y.tiff')
        tifffile.imwrite(Path(self._processath, self._acquisition_name, f"{self.filename}_histogram_y.tiff"), self.histogram_y)
        self.log.info(f'saving {self.filename}_histogram_z.tiff')
        tifffile.imwrite(Path(self._processath, self._acquisition_name, f"{self.filename}_histogram_z.tiff"), self.histogram_z)

    def wait_to_finish(self):
        """
        Wait for the writer to finish.
        """

        self.log.info(f"max projection {self.filename}: waiting to finish.")
        self._process.join()
