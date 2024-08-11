import logging
import numpy as np
import tifffile
from pathlib import Path
from voxel.devices.camera.base import VoxelCamera


class BackgroundCollection:

    def __init__(self, path: str):

        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._path = Path(path)
        self._frame_count_px_px = 1
        self._filename = None
        self._data_type = None

    @property
    def frame_count_px(self):
        return self._frame_count_px_px

    @frame_count_px.setter
    def frame_count_px(self, frame_count_px: int):
        self._frame_count_px_px = frame_count_px

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, data_type: np.unsignedinteger):
        self.log.info(f'setting data type to: {data_type}')
        self._data_type = data_type

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path: str):
        self._path = Path(path)
        self.log.info(f'setting path to: {path}')

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self._filename = filename.replace(".tiff","").replace(".tif", "") \
            if filename.endswith(".tiff") or filename.endswith(".tif") else f"{filename}"
        self.log.info(f'setting filename to: {filename}')

    #TODO: Change to device so routine set up can be more routine hehe
    def start(self, device: VoxelCamera):
        camera = device
        # store initial trigger mode
        initial_trigger = camera.trigger
        # turn trigger off
        new_trigger = initial_trigger
        new_trigger['mode'] = 'off'
        camera.trigger = new_trigger
        # prepare and start camera
        camera.prepare()
        camera.start()
        background_stack = np.zeros((self._frame_count_px_px, camera.roi_height_px, camera.roi_width_px), dtype=self._data_type)
        for frame in range(self._frame_count_px_px):
            background_stack[frame] = camera.grab_frame()
        # close writer and camera
        camera.stop()
        # reset the trigger
        camera.trigger = initial_trigger
        # average and save the image
        background_image = np.median(background_stack, axis=0)
        tifffile.imwrite(Path(self.path, f"{self.filename}.tiff"), background_image.astype(self._data_type))