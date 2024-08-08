import logging
from functools import wraps
from voxel.devices.camera.base import BaseCamera
from voxel.devices.camera.sdks.egrabber import *
from voxel.processes.downsample.gpu.gputools.downsample_2d import GPUToolsDownSample2D
from voxel.descriptors.deliminated_property import DeliminatedProperty
from acquire import DeviceKind, Runtime, SampleType, Trigger, TriggerEdge
import numpy as np

MAX_WIDTH_PX = 14192
MIN_WIDTH_PX = 64
STEP_WIDTH_PX = 16
MAX_HEIGHT_PX = 10640
MIN_HEIGHT_PX = 2
STEP_HEIGHT_PX = 2

BINNING = {
    1: 1,
    2: 2,
    4: 4,
    8: 8
}

PIXEL_TYPES = {
    'mono8': SampleType.U8,
    'mono10': SampleType.U10,
    'mono12': SampleType.U12,
    'mono14': SampleType.U14,
    'mono16': SampleType.U16,
}

LINE_INTERVALS_US = {
    'mono8': 15.00,
    'mono10': 15.00,
    'mono12': 15.00,
    'mono14': 20.21,
    'mono16': 45.44
}

TRIGGERS = {"mode": {
                "on": True,
                "off": False
            },
            "source": {
                "line0": 0
            },
            "polarity": {
                "risingedge": TriggerEdge.Rising,
                "fallingedge": TriggerEdge.Falling
            }
}


class Camera(BaseCamera):

    def __init__(self, id: str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.id = str(id)  # convert to string incase serial # is entered as int
        self.runtime = Runtime()
        self.acquire_api = self.runtime.get_configuration()
        self._latest_frame = None

        device_manager = self.runtime.device_manager()
        for device in device_manager.devices():
            if (device.kind == DeviceKind.Camera) and \
                (self.id in device.name):
                self.acquire_api.video[0].camera.identifier = device_manager.select(DeviceKind.Camera, device.name)
                self.acquire_api = self.runtime.set_configuration(self.acquire_api)
                self._device_name = device.name
        
        if not self.acquire_api:
            self.log.error(f"no grabber found for S/N: {self.id}")
            raise ValueError(f"no grabber found for S/N: {self.id}")

        # initialize binning as 1
        self._binning = 1

    @DeliminatedProperty(minimum=float('-inf'), maximum=float('inf'))
    def exposure_time_ms(self):
        # us to ms conversion
        return self.acquire_api.video[0].camera.settings.exposure_time_us / 1000

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float):
        # Note: round ms to nearest us
        self.acquire_api.video[0].camera.settings.exposure_time_us = exposure_time_ms * 1000
        self.acquire_api = self.runtime.set_configuration(self.acquire_api)
        self.log.info(f"exposure time set to: {exposure_time_ms} ms")

    @DeliminatedProperty(minimum=float('-inf'), maximum=float('inf'))
    def width_px(self):
        return self.acquire_api.video[0].camera.settings.shape[0]
    
    @width_px.setter
    def width_px(self, value: int):
        # round value
        value = round(value / STEP_WIDTH_PX) * STEP_WIDTH_PX
        # reset offset to (0,0)
        height_offset_px = self.acquire_api.video[0].camera.settings.offset[1]
        height_px = self.acquire_api.video[0].camera.settings.shape[1]
        self.acquire_api.video[0].camera.settings.offset = (0, height_offset_px)
        centered_offset_px = round((MAX_WIDTH_PX / 2 - value / 2) / STEP_WIDTH_PX) * STEP_WIDTH_PX
        self.acquire_api.video[0].camera.settings.shape = (value, height_px)
        self.acquire_api = self.runtime.set_configuration(self.acquire_api)
        self.acquire_api.video[0].camera.settings.offset = (centered_offset_px, height_offset_px)
        self.acquire_api = self.runtime.set_configuration(self.acquire_api)
        self.log.info(f"width set to: {value} px")

    @property
    def width_offset_px(self):
        return self.acquire_api.video[0].camera.settings.offset[0]
    
    @DeliminatedProperty(minimum=float('-inf'), maximum=float('inf'))
    def height_px(self):
        return self.acquire_api.video[0].camera.settings.shape[1]

    @height_px.setter
    def height_px(self, value: int):
        # round value
        value = round(value / STEP_HEIGHT_PX) * STEP_HEIGHT_PX
        # reset offset to (0,0)
        width_offset_px = self.acquire_api.video[0].camera.settings.offset[0]
        width_px = self.acquire_api.video[0].camera.settings.shape[0]
        self.acquire_api.video[0].camera.settings.offset = (width_offset_px, 0)
        centered_offset_px = round((MAX_HEIGHT_PX / 2 - value / 2) / STEP_HEIGHT_PX) * STEP_HEIGHT_PX
        self.acquire_api.video[0].camera.settings.shape = (width_px, value)
        self.acquire_api = self.runtime.set_configuration(self.acquire_api)
        self.acquire_api.video[0].camera.settings.offset = (width_offset_px, centered_offset_px)
        self.acquire_api = self.runtime.set_configuration(self.acquire_api)
        self.log.info(f"height set to: {value} px")

    @property
    def height_offset_px(self):
        return self.acquire_api.video[0].camera.settings.offset[1]

    @property
    def pixel_type(self):
        pixel_type = self.acquire_api.video[0].camera.settings.pixel_type
        # invert the dictionary and find the abstracted key to output
        return next(key for key, value in PIXEL_TYPES.items() if value == pixel_type)

    @pixel_type.setter
    def pixel_type(self, pixel_type_bits: str):
        valid = list(PIXEL_TYPES.keys())
        if pixel_type_bits not in valid:
            raise ValueError("pixel_type_bits must be one of %r." % valid)
        # note: for the Vieworks VP-151MX camera, the pixel type also controls line interval
        self.acquire_api.video[0].camera.settings.pixel_type = PIXEL_TYPES[pixel_type_bits]
        self.acquire_api = self.runtime.set_configuration(self.acquire_api)
        self.log.info(f"pixel type set to: {pixel_type_bits}")

    @property
    def line_interval_us(self):
        pixel_type = self.pixel_type
        return LINE_INTERVALS_US[pixel_type]

    @property
    def frame_time_ms(self):
        return (self.line_interval_us * self.height_px)/1000 + self.exposure_time_ms

    @property
    def trigger(self):
        mode = self.acquire_api.video[0].camera.settings.input_triggers.exposure.enable
        source = self.acquire_api.video[0].camera.settings.input_triggers.exposure.line
        polarity = self.acquire_api.video[0].camera.settings.input_triggers.exposure.edge
        return {"mode": next(key for key, value in TRIGGERS['mode'].items() if value == mode),
                "source": next(key for key, value in TRIGGERS['source'].items() if value == source),
                "polarity": next(key for key, value in TRIGGERS['polarity'].items() if value == polarity)}

    @trigger.setter
    def trigger(self, trigger: dict):
        mode = trigger['mode']
        source = trigger['source']
        polarity = trigger['polarity']
        valid_mode = list(TRIGGERS['mode'].keys())
        if mode not in valid_mode:
            raise ValueError("mode must be one of %r." % valid_mode)
        valid_source = list(TRIGGERS['source'].keys())
        if source not in valid_source:
            raise ValueError("source must be one of %r." % valid_source)
        valid_polarity = list(TRIGGERS['polarity'].keys())
        if polarity not in valid_polarity:
            raise ValueError("polarity must be one of %r." % valid_polarity)
        self.acquire_api.video[0].camera.settings.input_triggers.exposure = Trigger(
            enable = TRIGGERS['mode'][mode],
            line = TRIGGERS['source'][source],
            edge = "Rising" if TRIGGERS['polarity'][polarity] == TriggerEdge.Rising else "Falling",
            kind = "Input",
        )
        self.acquire_api = self.runtime.set_configuration(self.acquire_api)

    @property
    def binning(self):
        return self._binning

    @binning.setter
    def binning(self, binning: int):
        valid_binning = list(BINNING.keys())
        if binning not in valid_binning:
            raise ValueError("binning must be one of %r." % valid_binning)
        self._binning = binning
        if binning > 1:
            self.gpu_binning = GPUToolsDownSample2D(binning=int(self._binning))

    @property
    def sensor_width_px(self):
        return MAX_WIDTH_PX

    @property
    def sensor_height_px(self):
        return MAX_HEIGHT_PX

    def prepare(self):
        pass

    def start(self, frame_count: int = 2**64 - 1):
        self.acquire_api.video[0].max_frame_count = frame_count
        self.runtime.start()

    def stop(self):
        self.runtime.stop()

    def abort(self):
        self.runtime.abort()

    def close(self):
        del self.runtime

    def reset(self):
        del self.runtime, self.acquire_api
        self.runtime = Runtime()
        self.acquire_api = self.runtime.get_configuration()
        device_manager = self.runtime.device_manager()
        self.acquire_api.video[0].camera.identifier = device_manager.select_one_of(DeviceKind.Camera, self._device_name)
                
    def grab_frame(self):

        if available_data := self.runtime.get_available_data(0):
            packet = available_data.__enter__()
            f = next(packet.frames())
            image = f.data().squeeze().copy()
        if self._binning > 1:
            image = np.copy(self.gpu_binning.run(image))
        self._latest_frame = np.copy(image)
        return image

    @property
    def latest_frame(self):
        return self._latest_frame
