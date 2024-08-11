import numpy as np

from voxel.descriptors.deliminated_property import DeliminatedProperty
from voxel.devices.camera import VoxelCamera
from voxel.devices.camera.codes import (
    Binning, BinningLUT,
    PixelType, PixelTypeInfo, PixelTypeLUT,
    BitPackingMode, BitPackingModeLUT,
    TriggerSettings, TriggerMode, TriggerSource, TriggerPolarity, TriggerLUT,
    VoxelFrame, AcquisitionState,
)
from voxel.devices.camera.simulated.simulated_hardware import (
    SimulatedCameraHardware,
    MIN_WIDTH_PX,
    MAX_WIDTH_PX,
    STEP_WIDTH_PX,
    MIN_HEIGHT_PX,
    MAX_HEIGHT_PX,
    STEP_HEIGHT_PX,
    MIN_EXPOSURE_TIME_MS,
    MAX_EXPOSURE_TIME_MS,
    STEP_EXPOSURE_TIME_MS,
)
from voxel.devices.utils.geometry import Vec2D
from voxel.processes.gpu.gputools.downsample_2d import DownSample2D


class SimulatedCamera(VoxelCamera):

    def __init__(self, id: str, serial_number: str):
        super().__init__(id)
        self.serial_number = serial_number
        self.instance = SimulatedCameraHardware()

        # Property LUTs
        self.trigger_lut = TriggerLUT
        self.pixel_type_lut: PixelTypeLUT
        self.binning_lut: BinningLUT
        self.bit_packing_lut: BitPackingModeLUT

        self._generate_luts()

        # private properties
        self._binning: Binning = 1

        # cache properties
        self._trigger_cache = None
        self._pixel_type_cache = None
        self._bit_packing_mode_cache = None

        self.gpu_binning = DownSample2D(binning=self.binning)

        self.log.debug(f"simulated camera initialized with id: {id}, serial number: {serial_number}")
        self.log.debug(f"   simulated camera instance: {self.instance}")

    def _generate_luts(self):
        self.trigger_lut = TriggerLUT(
            mode={TriggerMode.ON: "On", TriggerMode.OFF: "Off"},
            source={TriggerSource.INTERNAL: "None", TriggerSource.EXTERNAL: "Line0"},
            polarity={TriggerPolarity.RISING: "RisingEdge", TriggerPolarity.FALLING: "FallingEdge"},
        )
        self.pixel_type_lut: PixelTypeLUT = {
            PixelType.MONO8: PixelTypeInfo(np.uint8, self.instance.line_interval_us_lut[np.uint8]),
            PixelType.MONO16: PixelTypeInfo(np.uint16, self.instance.line_interval_us_lut[np.uint16]),
        }
        self.binning_lut: BinningLUT = {
            1: 1,
            2: 2,
            4: 4
        }
        self.bit_packing_lut: BitPackingModeLUT = {
            BitPackingMode.LSB: "lsb",
            BitPackingMode.MSB: "msb",
            BitPackingMode.NONE: "none"
        }

    # TODO: Update DeliminatedProperty to use callables
    @DeliminatedProperty(
        minimum=MIN_WIDTH_PX,
        maximum=MAX_WIDTH_PX,
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
        self.log.debug(f'ROI width set to: {value} px')

    @property
    def roi_width_offset_px(self) -> int:
        return self.instance.roi_width_offset_px

    @property
    def sensor_width_px(self) -> int:
        return self.instance.sensor_width_px

    @DeliminatedProperty(
        minimum=MIN_HEIGHT_PX,
        maximum=MAX_HEIGHT_PX,
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
        self.log.debug(f'ROI height set to: {value} px')

    @property
    def roi_height_offset_px(self) -> int:
        return self.instance.roi_height_offset_px

    @property
    def sensor_height_px(self) -> int:
        return self.instance.sensor_height_px

    @property
    def binning(self) -> Binning:
        try:
            binning: Binning =  next(key for key, value in self.binning_lut.items() if value == self._binning)
        except KeyError:
            self.log.error(f"Invalid binning: {self._binning}")
            binning: Binning = 1
        return binning

    @binning.setter
    def binning(self, value: Binning) -> None:
        try:
            self._binning = self.binning_lut[value]
            self.gpu_binning = DownSample2D(binning=self.binning)
        except KeyError as e:
            self.log.error(f"Invalid binning: {e}")
            return

        self.log.debug(f"Binning set to: {value}")

    @property
    def image_size_px(self) -> Vec2D:
        return Vec2D(self.instance.roi_width_px, self.instance.roi_height_px) // self.binning

    @property
    def pixel_type(self) -> PixelType:
        self._pixel_type_cache = self._get_pixel_type()
        return self._pixel_type_cache

    def _get_pixel_type(self) -> PixelType:
        try:
            return next(key for key, value in self.pixel_type_lut.items() if value.repr == self.instance.pixel_type)
        except KeyError:
            self.log.error(f"Invalid pixel type: {self.instance.pixel_type}")
            return PixelType.MONO16

    @pixel_type.setter
    def pixel_type(self, pixel_type: PixelType) -> None:
        try:
            self.instance.pixel_type = self.pixel_type_lut[pixel_type]
        except KeyError as e:
            self.log.error(f"Invalid pixel type: {e}")
            return

        self.log.debug(f"Pixel type set to: {pixel_type.name}")

        # Invalidate the cached property
        self._pixel_type_cache = None

    @property
    def bit_packing_mode(self) -> BitPackingMode:
        self._bit_packing_mode_cache = self._get_bit_packing_mode()
        return self._bit_packing_mode_cache

    def _get_bit_packing_mode(self) -> BitPackingMode:
        try:
            return next(key for key, value in self.bit_packing_lut.items() if value == self.instance.bit_packing_mode)
        except KeyError:
            self.log.error(f"Invalid bit packing mode: {self.instance.bit_packing_mode}")
            return BitPackingMode.NONE

    @bit_packing_mode.setter
    def bit_packing_mode(self, bit_packing_mode: BitPackingMode) -> None:
        try:
            self.instance.bit_packing_mode = self.bit_packing_lut[bit_packing_mode]
        except KeyError as e:
            self.log.error(f"Invalid bit packing mode: {e}")
            return

        self.log.debug(f"Bit packing mode set to: {bit_packing_mode.name}")

        # Invalidate the cached property
        self._bit_packing_mode_cache = None

    @DeliminatedProperty(
        minimum=MIN_EXPOSURE_TIME_MS,
        maximum=MAX_EXPOSURE_TIME_MS,
        step=STEP_EXPOSURE_TIME_MS, unit="ms"
    )
    def exposure_time_ms(self) -> float:
        return self.instance.exposure_time_ms

    @exposure_time_ms.setter
    def exposure_time_ms(self, value: float) -> None:
        self.instance.exposure_time_ms = value
        self.log.debug(f'Exposure time set to: {value} ms')

    @property
    def line_interval_us(self) -> float:
        return self.pixel_type_lut[self.pixel_type].line_interval_us

    @property
    def frame_time_ms(self) -> float:
        return (self.line_interval_us * self.roi_height_px) / 1000 + self.exposure_time_ms

    @property
    def trigger(self) -> TriggerSettings:
        self._trigger_cache = self._get_trigger_mode()
        return self._trigger_cache

    @trigger.setter
    def trigger(self, trigger: TriggerSettings) -> None:
        try:
            self.instance.trigger_mode = self.trigger_lut.mode[trigger.mode]
            self.instance.trigger_source = self.trigger_lut.source[trigger.source]
            self.instance.trigger_activation = self.trigger_lut.polarity[trigger.polarity]
        except KeyError as e:
            self.log.error(f"Invalid trigger setting: {e}")
            return

        self.log.debug(f"Trigger set to: mode={trigger.mode.name}, "
                       f"source={trigger.source.name}, polarity={trigger.polarity.name}")

        # Invalidate the cached property
        self._trigger_cache = None

    def _get_trigger_mode(self):
        try:
            return TriggerSettings(
                mode=next(
                    key for key, value in self.trigger_lut.mode.items() if value == self.instance.trigger_mode),
                source=next(
                    key for key, value in self.trigger_lut.source.items() if value == self.instance.trigger_source),
                polarity=next(key for key, value in self.trigger_lut.polarity.items() if
                              value == self.instance.trigger_activation)
            )
        except StopIteration:
            self.log.error(f"Invalid trigger settings recieved from camera: mode={self.instance.trigger_mode}, "
                           f"source={self.instance.trigger_source}, activation={self.instance.trigger_activation}")
            return TriggerSettings(TriggerMode.OFF, TriggerSource.INTERNAL, TriggerPolarity.RISING)

    def prepare(self) -> None:
        pass

    def start(self, frame_count: int) -> None:
        self.instance.start_acquisition(frame_count)

    def stop(self) -> None:
        self.instance.stop_acquisition()

    def reset(self) -> None:
        self.stop()
        self._generate_luts()
        self._binning_cache = None
        self._pixel_type_cache = None
        self._bit_packing_mode_cache = None
        self._trigger_cache = None
        self.trigger = TriggerSettings(TriggerMode.OFF, TriggerSource.INTERNAL, TriggerPolarity.RISING)

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
        self.instance.close()
