from pathlib import Path

import numpy as np
from tifffile import tifffile

from acquisition.acquisition import VoxelAcquisition
from acquisition.routines.base import VoxelRoutine


class BackgroundCollection(VoxelRoutine):
    """
    This class is used to collect background images from the camera for the purpose of background subtraction.
    :param acq: The acquisition object.
    :param channel: The channel to collect the background images for.
    :param num_frames: The number of frames to collect.
    :param folder: The folder to save the background images to.
    :param filename: The filename to save the background images to.
    :type acq: VoxelAcquisition
    :type channel: str
    :type num_frames: int
    :type folder: str
    :type filename: str
    """

    def __init__(self, acq: VoxelAcquisition, channel: str, num_frames: int, folder: str, filename: str):
        super().__init__(acq)
        self._channel = self.acq.instrument.channels[channel]
        self._data_type = self._channel.camera.pixel_type.dtype
        self._num_frames = num_frames
        self._path = Path(folder, self.acq.name, f"{filename}")

    # TODO: Take care of camera trigger settings
    def run(self):
        """
        This method collects background images from the camera.
        """
        self.log.info("Collecting background images")
        camera = self._channel.camera

        camera.prepare()
        camera.start(frame_count=-1)
        background_stack = np.zeros(shape=(self._num_frames, camera.frame_height_px, camera.frame_width_px),
                                    dtype=camera.pixel_type.dtype)
        for frame in range(self._num_frames):
            background_stack[frame] = camera.grab_frame()

        camera.stop()
        background_image = np.mean(background_stack, axis=0)
        tifffile.imwrite(f"{self._path}_background.tiff"), background_image.astype(self._data_type)
