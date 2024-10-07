import importlib
import platform
from typing import Dict, Any

from voxel.utils.logging import get_logger
from voxel.factory.instrument_config import InstrumentConfig, InstanceSpec
from voxel.instrument.channel import VoxelChannel
from voxel.instrument.drivers import VoxelDevice
from voxel.instrument.file_transfers import VoxelFileTransfer
from voxel.instrument.instrument import VoxelInstrument
from voxel.instrument.nidaq import VoxelNIDAQ
from voxel.instrument.nidaq.simulated import SimulatedNIDAQ
from voxel.instrument.nidaq.task import DAQTask, DAQTaskType
from voxel.instrument.writers import VoxelWriter


class InstrumentFactory:
    def __init__(self, config: InstrumentConfig):
        self.log = get_logger(self.__class__.__name__)
        self._config = config

    def create_instrument(self):
        devices = self.create_devices()
        writers = self.create_writers()
        file_transfers = self.create_file_transfers()
        daq = self.create_daq(self._config.devices, devices)
        channels = self.create_channels(devices, writers, file_transfers)

        module = importlib.import_module(self._config.module)
        cls = getattr(module, self._config.class_name)
        assert issubclass(cls, VoxelInstrument), f"Class {cls} is not a VoxelInstrument"
        kwds = self._config.instrument_kwds or {}

        return cls(
            name=self._config.name,
            config=self._config,
            devices=devices,
            writers=writers,
            file_transfers=file_transfers,
            channels=channels,
            daq=daq,
            **kwds,
        )

    def create_devices(self) -> Dict[str, VoxelDevice]:
        return self._create_multiple_instances(self._config.devices)

    def create_writers(self) -> Dict[str, VoxelWriter]:
        return self._create_multiple_instances(self._config.writers)

    def create_file_transfers(self) -> Dict[str, VoxelFileTransfer]:
        return self._create_multiple_instances(self._config.file_transfers)

    def create_daq(self, device_specs, devices) -> VoxelNIDAQ:
        """
        Create a DAQ instance and add DAQ tasks and channels to the devices.
        :param device_specs: Device specifications from the configuration file
        :param devices: Dictionary of devices created by the factory
        :return: VoxelNIDAQ instance
        :rtype: VoxelNIDAQ
        Note: Side effect: Adds daq_task and daq_channel attributes to the devices
        """
        daq_specs = self._config.daq
        name = f"{self._config.name}_daq"
        simulated = daq_specs.simulated
        conn = daq_specs.conn
        this_platform = platform.system().lower()
        match this_platform:
            case "windows" | "linux":
                daq = VoxelNIDAQ(name=name, conn=conn, simulated=simulated)
            case "darwin":
                if not simulated:
                    raise ValueError(
                        f"Nidaq not supported on {this_platform}, set simulated=True in the yaml config"
                    )
                daq = SimulatedNIDAQ(name=name, conn=conn)
            case _:
                raise ValueError(f"Unsupported platform: {this_platform}")
        tasks = {}
        for task_name, task_specs in daq_specs.tasks.items():
            tasks[task_name] = DAQTask(
                name=task_name,
                task_type=DAQTaskType(task_specs.task_type),
                sampling_frequency_hz=task_specs.sampling_frequency_hz,
                period_time_ms=task_specs.period_time_ms,
                rest_time_ms=task_specs.rest_time_ms,
                daq=daq,
            )
        # create daq channels
        for instance_name, device_spec in device_specs.items():
            if device_spec.daq_channel:
                device = devices[instance_name]
                daq_channel_specs = device_spec.daq_channel
                task = tasks[daq_channel_specs["task"]]
                channel_kwds = {
                    k: v for k, v in daq_channel_specs.items() if k != "task"
                }
                channel_kwds["name"] = device.name
                channel = task.add_channel(**channel_kwds)
                device.daq_task = task
                device.daq_channel = channel

        return daq

    def create_channels(
        self, devices, writers, file_transfers
    ) -> Dict[str, VoxelChannel]:
        """
        Create a channel instance and return the channel name and instance.
        :param devices: Dictionary of devices created by the factory
        :param writers: Dictionary of writers created by the factory
        :param file_transfers: Dictionary of file transfers created by the factory
        :return: VoxelChannel instance
        :rtype: VoxelChannel
        """
        channels = {}
        for channel_name, channel_spec in self._config.channels.items():
            channels[channel_name] = VoxelChannel(
                name=channel_name,
                camera=devices[channel_spec.camera],
                lens=devices[channel_spec.lens],
                laser=devices[channel_spec.laser],
                emmision_filter=devices[channel_spec.filter_],
                writer=writers[channel_spec.writer],
                file_transfer=file_transfers[channel_spec.file_transfer],
            )
        return channels

    def _create_multiple_instances(self, specs) -> Dict[str, Any]:
        register = {}
        for instance_name in specs:
            register[instance_name] = self._create_instance(
                instance_name, specs, register
            )
        return register

    def _create_instance(
        self,
        instance_name: str,
        instances_spec: Dict[str, InstanceSpec],
        register: Dict[str, Any],
    ):
        if instance_name not in register:
            instance_spec = instances_spec[instance_name]
            module = importlib.import_module(instance_spec.module)
            instance_class = getattr(module, instance_spec.class_name)

            # Prepare keyword arguments
            kwargs = instance_spec.kwds.copy()

            # Recursively create and replace instance dependencies
            for key, value in kwargs.items():
                if isinstance(value, str) and value in instances_spec:
                    kwargs[key] = self._create_instance(value, instances_spec, register)

            # Add 'name' to kwargs if not present
            if "name" not in kwargs:
                kwargs["name"] = instance_name

            # Initialize the instance
            try:
                instance = instance_class(**kwargs)
                register[instance_name] = instance
                self.log.debug(f"Successfully created instance: {instance_name}")
            except Exception as e:
                self.log.error(f"Error creating instance {instance_name}: {str(e)}")
                raise

        return register[instance_name]
