import importlib
import platform
from typing import Any

from ruamel.yaml import YAML

from pydantic import BaseModel, Field, field_validator

from voxel.instrument.daq import VoxelDAQ
from voxel.utils.logging import get_logger
from voxel.instrument.channel import VoxelChannel
from voxel.instrument.device.drivers import VoxelDevice
from voxel.instrument.transfers import VoxelFileTransfer
from voxel.instrument.instrument import VoxelInstrument
from voxel.instrument.daq import VoxelNIDAQ
from voxel.instrument.daq.simulated import SimulatedNIDAQ
from voxel.instrument.daq.task import VoxelDAQTask, DAQTaskType
from voxel.instrument.writers import VoxelWriter


class DAQTaskSpecs(BaseModel):
    task_type: str
    sampling_frequency_hz: int
    period_time_ms: float
    rest_time_ms: float


class DAQSpecs(BaseModel):
    conn: str
    tasks: dict[str, DAQTaskSpecs]
    simulated: bool = False


class DeviceSpec(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: dict[str, Any] = {}
    daq_channel: dict[str, Any] | None = None


class WriterSpec(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: dict[str, Any] = {}


class FileTransferSpec(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: dict[str, Any] = {}


class ChannelSpec(BaseModel):
    camera: str
    lens: str
    laser: str
    writer: str
    filter_: str = Field(None, alias="filter")
    writer: str
    file_transfer: str


type InstanceSpec = DeviceSpec | WriterSpec | FileTransferSpec


class InstrumentConfigError(Exception):
    pass


class InstrumentConfig(BaseModel):
    """Instrument configuration class."""

    name: str
    description: str | None = None
    module: str = "voxel.instrument.instrument"
    class_name: str = Field("VoxelInstrument", alias="class")
    daq: DAQSpecs
    devices: dict[str, DeviceSpec]
    writers: dict[str, WriterSpec] = {}
    file_transfers: dict[str, FileTransferSpec] = Field({}, alias="transfers")
    channels: dict[str, ChannelSpec] = {}
    settings: dict[str, dict[str, Any]] = {}

    @classmethod
    @field_validator("name")
    def sanitize_name(cls, v):
        return v.lower().replace(" ", "_")

    @classmethod
    @field_validator("settings")
    def validate_devices_in_settings(cls, v, info):
        devices = info.data.get("devices", {})
        for device_name in v:
            if device_name not in devices:
                raise ValueError(
                    f"Device {device_name} in settings not found in devices"
                )
        return v

    @classmethod
    @field_validator("channels")
    def validate_channel_items(cls, v, info):
        items = (
            info.data.get("devices", {})
            | info.data.get("writers", {})
            | info.data.get("transfers", {})
        )
        for channel_name, channel in v.items():
            for item_name in [
                "camera",
                "lens",
                "laser",
                "writer",
                "filter",
                "transfer",
            ]:
                if channel[item_name] not in items:
                    raise ValueError(
                        f"Item {channel[item_name]} in channel {channel_name} not found in devices, "
                        f"writers or transfers"
                    )

    @classmethod
    def from_yaml(cls, config_file: str) -> 'InstrumentConfig':
        try:
            yaml = YAML(typ="safe", pure=True)
            with open(config_file, "r") as f:
                config_data = yaml.load(f)
            return cls(**config_data)
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")

    def __post_init__(self, **data):
        super().__init__(**data)
        self.log = get_logger(self.__class__.__name__)

    def __repr__(self):
        return f"InstrumentConfig(name={self.name}, devices={len(self.devices)})"



class InstrumentFactory:
    def __init__(self, config: InstrumentConfig) -> None:
        self.log = get_logger(self.__class__.__name__)
        self._config = config

    def create_instrument(self) -> VoxelInstrument:
        devices = self.create_devices()
        writers = self.create_writers()
        file_transfers = self.create_file_transfers()
        daq = self.create_daq(self._config.devices, devices)
        channels = self.create_channels(devices, writers, file_transfers)

        module = importlib.import_module(self._config.module)
        cls = getattr(module, self._config.class_name)
        assert issubclass(cls, VoxelInstrument), f"Class {cls} is not a VoxelInstrument"

        return cls(
            name=self._config.name,
            build_settings=self._config.settings,
            devices=devices,
            writers=writers,
            file_transfers=file_transfers,
            channels=channels,
            daq=daq,
        )

    def create_devices(self) -> dict[str, VoxelDevice]:
        return self._create_multiple_instances(self._config.devices)

    def create_writers(self) -> dict[str, VoxelWriter]:
        return self._create_multiple_instances(self._config.writers)

    def create_file_transfers(self) -> dict[str, VoxelFileTransfer]:
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
            tasks[task_name] = VoxelDAQTask(
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
    ) -> dict[str, VoxelChannel]:
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

    def _create_multiple_instances[T](self, specs: dict[str, T]) -> dict[str, T]:
        register = {}
        for instance_name in specs:
            register[instance_name] = self._create_instance(
                instance_name, specs, register
            )
        return register

    def _create_instance[T](
        self,
        instance_name: str,
        instances_spec: dict[str, InstanceSpec],
        register: dict[str, T],
    ) -> T:
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


def validate_instrument(instrument: VoxelInstrument, inst_config: InstrumentConfig):
    print(f"Testing Instrument: {instrument.name}...")

    # Test general device creation
    assert len(instrument.devices) == len(inst_config.devices), "Not all devices were created"

    # Test specific device types
    print("\nTesting Cameras:")
    for camera in instrument.cameras.values():
        print(f"  Camera: {camera}")
        assert camera.name in inst_config.devices, f"Camera {camera.name} not in config"

    print("\nTesting Lasers:")
    for laser in instrument.lasers.values():
        print(f"  Laser: {laser}")
        assert laser.name in inst_config.devices, f"Laser {laser.name} not in config"

    # Test DAQ and tasks
    print("\nTesting DAQ and Tasks:")
    daq = instrument.daq
    assert isinstance(daq, VoxelDAQ), "DAQ is not a VoxelNIDAQ"
    print(f"  DAQ: {daq}")

    for task_name, task_specs in inst_config.daq.tasks.items():
        task = daq.tasks.get(task_name)
        assert task is not None, f"DAQ Task {task_name} not found"
        print(f"  DAQ Task: {task}")

        assert task.task_type == task_specs.task_type, f"Mismatch in task type for {task_name}"
        assert (
            task.sampling_frequency_hz == task_specs.sampling_frequency_hz
        ), f"Mismatch in sampling frequency for {task_name}"
        assert task.period_time_ms == task_specs.period_time_ms, f"Mismatch in period time for {task_name}"
        assert task.rest_time_ms == task_specs.rest_time_ms, f"Mismatch in rest time for {task_name}"

    # Test DAQ channels
    print("\nTesting DAQ Channels:")
    for device_name, device_spec in inst_config.devices.items():
        if device_spec.daq_channel:
            device = instrument.devices.get(device_name)
            assert device is not None, f"Device {device_name} not found"
            assert hasattr(device, "daq_task"), f"Device {device_name} missing daq_task attribute"
            assert hasattr(device, "daq_channel"), f"Device {device_name} missing daq_channel attribute"
            print(f"  Device {device_name} DAQ channel: {device.daq_channel}")

    # Test writers
    print("\nTesting Writers:")
    for writer_name in inst_config.writers:
        assert writer_name in instrument.writers, f"Writer {writer_name} not created"
        print(f"  Writer: {instrument.writers[writer_name]}")

    # Test file transfers
    print("\nTesting File Transfers:")
    for transfer_name in inst_config.file_transfers:
        assert transfer_name in instrument.file_transfers, f"File transfer {transfer_name} not created"
        print(f"  File Transfer: {instrument.file_transfers[transfer_name]}")

    print("\nAll tests passed successfully!")
