from typing import TypeAlias, Dict, Optional, Tuple

from utils.descriptors.deliminated_property import deliminated_property
from utils.descriptors.enumerated_property import enumerated_property
from utils.geometry.vec import Vec2D
from voxel.instrument.devices.camera import VoxelCamera
from voxel.instrument.devices.camera.definitions import VoxelFrame, AcquisitionState
from voxel.kit.downsample.gpu.gputools.downsample_2d import GPUToolsDownSample2D
from .definitions import (
    Binning, PixelType,
    TriggerSettings, TriggerMode, TriggerSource, TriggerPolarity,
)
from .image_model import ImageModel
from .simulated_hardware import (
    SimulatedCameraHardware,
    MIN_WIDTH_PX,
    STEP_WIDTH_PX,
    MIN_HEIGHT_PX,
    STEP_HEIGHT_PX,
    MIN_EXPOSURE_TIME_MS,
    MAX_EXPOSURE_TIME_MS,
    STEP_EXPOSURE_TIME_MS,
)

PixelTypeLUT: TypeAlias = Dict[PixelType, str]
BinningLUT: TypeAlias = Dict[Binning, str]
TriggerModeLUT: TypeAlias = Dict[TriggerMode, str]
TriggerSourceLUT: TypeAlias = Dict[TriggerSource, str]
TriggerPolarityLUT: TypeAlias = Dict[TriggerPolarity, str]


class SimulatedCamera(VoxelCamera):

    def __init__(self, serial_number: str, name: str = "", image_model: Optional[ImageModel] = None,
                 pixel_size_um: Tuple[float, float] = (5.5, 5.5)):
        super().__init__(name, pixel_size_um)
        self.log.info(f"Initializing simulated camera with id: {name}, serial number: {serial_number}")
        self.serial_number = serial_number
        self.instance = SimulatedCameraHardware(image_model)

        # Property LUTs
        self._pixel_type_lut: PixelTypeLUT = {
            PixelType.MONO8: 'MONO8',
            PixelType.MONO12: 'MONO12',
            PixelType.MONO14: 'MONO14',
            PixelType.MONO16: 'MONO16',
        }
        self._binning_lut: BinningLUT = {
            Binning.X1: "1x1",
            Binning.X2: "2x2",
            Binning.X4: "4x4",
            Binning.X8: "8x8",
        }
        self._trigger_mode_lut: TriggerModeLUT = {TriggerMode(mode): mode for mode in TriggerMode}
        self._trigger_source_lut: TriggerSourceLUT = {TriggerSource(source): source for source in TriggerSource}
        self._trigger_polarity_lut: TriggerPolarityLUT = {TriggerPolarity(polarity): polarity for polarity in
                                                          TriggerPolarity}

        # private properties
        self._binning: Binning = Binning.X1
        self._trigger_settings: Optional[TriggerSettings] = None

        self.gpu_binning = GPUToolsDownSample2D(binning=self._binning)

        self.log.info(f"simulated camera initialized with id: {name}, serial number: {serial_number}")

    def __repr__(self):
        return (
            f"Serial Number:        {self.serial_number}\n"
            f"Sensor Size:          {self.sensor_size_px}\n"
            f"Roi Size:             ({self.roi_width_px}, {self.roi_height_px})\n"
            f"Roi Offset:           ({self.roi_width_offset_px}, {self.roi_height_offset_px})\n"
            f"Binning:              {self.binning}\n"
            f"Image Size:           {self.frame_size_px}\n"
            f"Exposure Time:        {self.exposure_time_ms} ms\n"
            f"Line Interval:        {self.line_interval_us} us\n"
            f"Frame Time:           {self.frame_time_ms} ms\n"
            f"Pixel Type:           {self.pixel_type}\n"
            f"Trigger Settings:     {self.trigger_settings}\n"
            f"Image Model:          {self.instance.image_model}\n"
            # f"LUTs:________________________________________________________________________________\n"
            # f"Binning LUT:          {self._binning_lut}\n"
            # f"Pixel Type LUT:       {self._pixel_type_lut}\n"
            # f"Trigger Mode LUT:     {self._trigger_mode_lut}\n"
            # f"Trigger Source LUT:   {self._trigger_source_lut}\n"
            # f"Trigger Polarity LUT: {self._trigger_polarity_lut}\n"
        )

    # Sensor size properties

    @property
    def sensor_size_px(self) -> Vec2D:
        return Vec2D(self.instance.sensor_width_px, self.instance.sensor_height_px)

    @property
    def sensor_width_px(self) -> int:
        return self.sensor_size_px.x

    @property
    def sensor_height_px(self) -> int:
        return self.sensor_size_px.y

    # ROI properties

    @deliminated_property(
        minimum=MIN_WIDTH_PX,
        maximum=lambda self: self.sensor_width_px,
        step=STEP_WIDTH_PX, unit="px"
    )
    def roi_width_px(self) -> int:
        return self.instance.roi_width_px

    @roi_width_px.setter
    def roi_width_px(self, value: int) -> None:
        self.instance.roi_width_px = value
        centered_offset_px = (
                round((self.instance.sensor_width_px / 2 - value / 2) / self.instance.roi_step_width_px)
                * self.instance.roi_step_width_px
        )
        self.instance.roi_width_offset_px = centered_offset_px
        self.log.info(f'ROI width set to: {value} px')

    @deliminated_property(
        minimum=0,
        maximum=lambda self: self.sensor_width_px,
        step=STEP_WIDTH_PX, unit="px"
    )
    def roi_width_offset_px(self) -> int:
        return self.instance.roi_width_offset_px

    @roi_width_offset_px.setter
    def roi_width_offset_px(self, value: int) -> None:
        self.instance.roi_width_offset_px = value
        self.log.info(f'ROI width offset set to: {value} px')

    @deliminated_property(
        minimum=MIN_HEIGHT_PX,
        maximum=lambda self: self.sensor_height_px,
        step=STEP_HEIGHT_PX, unit="px"
    )
    def roi_height_px(self) -> int:
        return self.instance.roi_height_px

    @roi_height_px.setter
    def roi_height_px(self, value: int) -> None:
        self.instance.roi_height_px = value
        centered_offset_px = (
                round((self.instance.sensor_height_px / 2 - value / 2) / self.instance.roi_step_height_px)
                * self.instance.roi_step_height_px
        )
        self.instance.roi_height_offset_px = centered_offset_px
        self.log.info(f'ROI height set to: {value} px')

    @deliminated_property(
        minimum=0,
        maximum=lambda self: self.sensor_height_px,
        step=STEP_HEIGHT_PX, unit="px"
    )
    def roi_height_offset_px(self) -> int:
        return self.instance.roi_height_offset_px

    @roi_height_offset_px.setter
    def roi_height_offset_px(self, value: int) -> None:
        self.instance.roi_height_offset_px = value
        self.log.info(f'ROI height offset set to: {value} px')

    # Image Format properties

    @enumerated_property(Binning, lambda self: list(self._binning_lut))
    def binning(self) -> Binning:
        try:
            binning: Binning = next(key for key in self._binning_lut.keys() if key == self._binning)
        except StopIteration:
            self.log.error(f"Invalid binning: {self._binning}")
            binning: Binning = Binning.X1
        return binning

    @binning.setter
    def binning(self, binning: Binning) -> None:
        try:
            self._binning = self._binning_lut[binning]
            self.gpu_binning = GPUToolsDownSample2D(binning=self.binning)
        except KeyError as e:
            self.log.error(f"Invalid binning: {e}")
            return

        self.log.info(f"Binning set to: {binning}")

    @enumerated_property(PixelType, lambda self: list(self._pixel_type_lut))
    def pixel_type(self) -> PixelType:
        try:
            return next(key for key in self._pixel_type_lut.keys() if key == self.instance.pixel_type)
        except StopIteration:
            self.instance.pixel_type = self._pixel_type_lut[PixelType.MONO8]
            return PixelType.MONO8

    @pixel_type.setter
    def pixel_type(self, pixel_type: PixelType) -> None:
        try:
            self.instance.pixel_type = self._pixel_type_lut[pixel_type]
        except KeyError as e:
            self.log.error(f"Invalid pixel type: {e}")
            return

        self.log.info(f"Pixel type set to: {pixel_type.name}")

    @property
    def frame_size_px(self) -> Vec2D:
        return Vec2D(self.roi_width_px, self.roi_height_px) // self.binning

    @property
    def frame_width_px(self) -> int:
        return self.frame_size_px.x

    @property
    def frame_height_px(self) -> int:
        return self.frame_size_px.y

    @property
    def frame_size_mb(self) -> int:
        return self.frame_size_px.x * self.frame_size_px.y * self.pixel_type.bytes_per_pixel / 1e6

    @deliminated_property(
        minimum=MIN_EXPOSURE_TIME_MS,
        maximum=MAX_EXPOSURE_TIME_MS,
        step=STEP_EXPOSURE_TIME_MS, unit="ms"
    )
    def exposure_time_ms(self) -> float:
        return self.instance.exposure_time_ms

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float) -> None:
        self.instance.exposure_time_ms = exposure_time_ms
        self.log.info(f'Exposure time set to: {exposure_time_ms} ms')

    @property
    def line_interval_us(self) -> float:
        return self.instance.line_interval_us_lut[self.pixel_type]

    @property
    def frame_time_ms(self) -> float:
        return (self.line_interval_us * self.roi_height_px) / 1000 + self.exposure_time_ms

    @property
    def trigger_settings(self) -> TriggerSettings:
        if not self._trigger_settings:
            try:
                self._trigger_settings = TriggerSettings(
                    mode=next(k for k in self._trigger_mode_lut.keys() if k == self.instance.trigger_mode),
                    source=next(k for k in self._trigger_source_lut.keys() if k == self.instance.trigger_source),
                    polarity=next(k for k in self._trigger_polarity_lut.keys() if k == self.instance.trigger_activation)
                )
            except StopIteration:
                self.log.error(f"Invalid trigger settings recieved from camera: mode={self.instance.trigger_mode}, "
                               f"source={self.instance.trigger_source}, polarity={self.instance.trigger_activation}")
                self._trigger_settings = TriggerSettings(TriggerMode.OFF, TriggerSource.INTERNAL,
                                                         TriggerPolarity.RISINGEDGE)
        return self._trigger_settings

    @trigger_settings.setter
    def trigger_settings(self, trigger: TriggerSettings) -> None:
        try:
            self.instance.trigger_mode = self._trigger_mode_lut[trigger.mode]
            self.instance.trigger_source = self._trigger_source_lut[trigger.source]
            self.instance.trigger_activation = self._trigger_polarity_lut[trigger.polarity]
            self._trigger_settings = trigger
        except KeyError as e:
            self.log.error(f"Invalid trigger setting: {e}")
            return

        self.log.info(f"Trigger set to: mode={trigger.mode.name}, "
                      f"source={trigger.source.name}, polarity={trigger.polarity.name}")

    @property
    def sensor_temperature_c(self) -> float:
        return self.instance.sensor_temperature_c

    @property
    def mainboard_temperature_c(self) -> float:
        return self.instance.mainboard_temperature_c

    def prepare(self) -> None:
        pass

    def start(self, frame_count: int) -> None:
        self.instance.start_acquisition(frame_count)

    def stop(self) -> None:
        self.instance.stop_acquisition()

    def reset(self) -> None:
        self.stop()
        self._binning = Binning.X1
        self.trigger_settings = TriggerSettings(TriggerMode.OFF, TriggerSource.INTERNAL, TriggerPolarity.RISINGEDGE)

    def grab_frame(self) -> VoxelFrame:
        frame, timestamp, frame_count = self.instance.grab_frame()
        return frame if self.binning == 1 else self.gpu_binning.run(frame)

    @property
    def acquisition_state(self) -> AcquisitionState:
        return AcquisitionState(
            frame_index=self.instance.frame_index,
            input_buffer_size=self.instance.frame_buffer.qsize(),
            output_buffer_size=self.instance.frame_buffer.qsize(),
            dropped_frames=self.instance.dropped_frames,
            data_rate_mbs=self.instance.frame_rate * self.roi_width_px * self.roi_height_px * (
                16 if self.pixel_type == PixelType.MONO16 else 8) / 8 / 1e6,
            frame_rate_fps=self.instance.frame_rate
        )

    def log_metadata(self) -> None:
        pass

    def close(self):
        self.instance.close() if self.instance else None
