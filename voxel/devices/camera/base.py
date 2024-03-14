import inspect

class BaseCamera:

    @property
    def exposure_time_ms(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def roi(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @roi.setter
    def roi(self, roi: dict):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def pixel_type(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @pixel_type.setter
    def pixel_type(self, pixel_type_bits: str):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def bit_packing_mode(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @bit_packing_mode.setter
    def bit_packing_mode(self, bit_packing: str):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def line_interval_us(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @line_interval_us.setter
    def line_interval_us(self, line_interval_us: float):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def readout_mode(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @readout_mode.setter
    def readout_mode(self, readout_mode: str):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def trigger(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @trigger.setter
    def trigger(self, trigger: dict):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def binning(self): 
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @binning.setter
    def binning(self, binning: str): 
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def sensor_width_px(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def sensor_height_px(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def frame_time_ms(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def signal_mainboard_temperature_c(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def signal_sensor_temperature_c(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def reset(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def prepare(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def start(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def stop(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def close(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass
        
    def grab_frame(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def signal_acquisition_state(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def log_metadata(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass
    def abort(self):
        pass