import inspect
import numpy as np
from pathlib import Path


class BaseWriter():

    @property
    def signal_progress_percent(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def x_voxel_size_um(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @x_voxel_size_um.setter
    def x_voxel_size_um(self, x_voxel_size_um: float):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def y_voxel_size_um(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @y_voxel_size_um.setter
    def y_voxel_size_um(self, y_voxel_size_um: float):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def z_voxel_size_um(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @z_voxel_size_um.setter
    def z_voxel_size_um(self, z_voxel_size_um: float):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def x_position_mm(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @x_position_mm.setter
    def x_position_mm(self, x_position_mm: float):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def y_position_mm(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @y_position_mm.setter
    def y_position_mm(self, y_position_mm: float):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def z_position_mm(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @z_position_mm.setter
    def z_position_mm(self, z_position_mm: float):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def theta_deg(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @theta_deg.setter
    def theta_deg(self, theta_deg: float):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass
        
    @property
    def frame_count_px(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @frame_count_px.setter
    def frame_count_px(self, frame_count_px: int):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def column_count_px(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @column_count_px.setter
    def column_count_px(self, column_count_px: int):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def row_count_px(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @row_count_px.setter
    def row_count_px(self, row_count_px: int):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def chunk_count_px(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def compression(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @compression.setter
    def compression(self, compression: str):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def shuffle(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @shuffle.setter
    def shuffle(self, shuffle: str):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def compression_level(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @compression_level.setter
    def compression_level(self, compression_level: int):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def downsample_method(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @downsample_method.setter
    def downsample_method(self, downsample_method: str):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass
        
    @property
    def data_type(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @data_type.setter
    def data_type(self, data_type: np.unsignedinteger):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def path(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def filename(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @filename.setter
    def filename(self, filename: str):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def channel(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @channel.setter
    def channel(self, channel: str):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def color(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @color.setter
    def color(self, color: str):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def shm_name(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @shm_name.setter
    def shm_name(self, name: str):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass
        
    def prepare(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def start(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def _run(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def wait_to_finish(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass