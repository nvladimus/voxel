# build.py

from voxel.instrument.instrument import VoxelInstrument
from voxel.instrument.device.camera import SimulatedCamera
from voxel.instrument.device.lens import VoxelLens
from voxel.instrument.device.laser import SimulatedLaser
from voxel.instrument.device.filter import SimulatedFilter, SimulatedFilterWheel
from voxel.instrument.device.linear_axis import SimulatedLinearAxis, LinearAxisDimension
from voxel.instrument.writers import ImarisWriter
from voxel.instrument.transfers import RobocopyFileTransfer
from voxel.instrument.daq import VoxelNIDAQ, VoxelDAQTask, DAQTaskType

# Create DAQ
daq = VoxelNIDAQ(name="example_daq", conn="Dev1", simulated=True)
primary_ao_task = VoxelDAQTask(
    name="primary_ao_task",
    task_type=DAQTaskType.AO,
    sampling_frequency_hz=350000,
    period_time_ms=10,
    rest_time_ms=0,
    daq=daq,
)

# Create devices
camera = SimulatedCamera(name="simulated_camera_1", serial_number="12345", pixel_size_um=(3.5, 3.5))
camera.daq_task = primary_ao_task
camera.daq_channel = primary_ao_task.add_channel(
    name="camera_trigger",
    port="ao0",
    waveform_type="square",
    center_volts=2.5,
    amplitude_volts=2.5,
    cutoff_freq_hz=1000,
    start_time_ms=0,
    end_time_ms=5,
)

objective_40x = VoxelLens(name="objective_40x", magnification=40)

laser_488 = SimulatedLaser(name="laser_488", wavelength=488)
laser_488.daq_task = primary_ao_task
laser_488.daq_channel = primary_ao_task.add_channel(
    name="laser_488_modulation",
    port="ao1",
    waveform_type="triangle",
    center_volts=2.5,
    amplitude_volts=2.5,
    cutoff_freq_hz=1000,
    peak_point=0.5,
)

laser_561 = SimulatedLaser(name="laser_561", wavelength=561)
laser_561.daq_task = primary_ao_task
laser_561.daq_channel = primary_ao_task.add_channel(
    name="laser_561_modulation",
    port="ao2",
    waveform_type="sawtooth",
    center_volts=2.5,
    amplitude_volts=2.5,
    cutoff_freq_hz=1000,
    peak_point=1,
)

filterwheel = SimulatedFilterWheel(name="filterwheel", wheel_id=1)
filter_488 = SimulatedFilter(name="filter_488", wheel=filterwheel, position=1)
filter_561 = SimulatedFilter(name="filter_561", wheel=filterwheel, position=2)

x_axis = SimulatedLinearAxis(name="x-axis", dimension=LinearAxisDimension.X)
x_axis.daq_task = primary_ao_task
x_axis.daq_channel = primary_ao_task.add_channel(
    name="x_axis_control",
    port="ao3",
    waveform_type="square",
    center_volts=2.5,
    amplitude_volts=2.5,
    cutoff_freq_hz=1000,
    start_time_ms=0,
    end_time_ms=5,
)

y_axis = SimulatedLinearAxis(name="y-axis", dimension=LinearAxisDimension.Y)
z_axis = SimulatedLinearAxis(name="z-axis", dimension=LinearAxisDimension.Z)

# Create writers and file transfers
imaris_writer = ImarisWriter(name="imaris", path="E:\\")
robocopy_transfer = RobocopyFileTransfer(name="robocopy", external_path="Z:\\scratch\\adam.glaser", local_path="E:\\")

# Create channels
red_channel = {
    "camera": camera,
    "lens": objective_40x,
    "laser": laser_561,
    "filter": filter_561,
    "writer": imaris_writer,
    "file_transfer": robocopy_transfer,
}

green_channel = {
    "camera": camera,
    "lens": objective_40x,
    "laser": laser_488,
    "filter": filter_488,
    "writer": imaris_writer,
    "file_transfer": robocopy_transfer,
}

# Create the instrument
instrument = VoxelInstrument(
    name="Example Instrument",
    devices={
        "simulated_camera_1": camera,
        "objective_40x": objective_40x,
        "laser_488": laser_488,
        "laser_561": laser_561,
        "filter_488": filter_488,
        "filter_561": filter_561,
        "filterwheel": filterwheel,
        "x-axis": x_axis,
        "y-axis": y_axis,
        "z-axis": z_axis,
    },
    channels={"red": red_channel, "green": green_channel},
    writers={"imaris": imaris_writer},
    file_transfers={"robocopy": robocopy_transfer},
    daq=daq,
)

# Apply settings
camera.exposure_time_ms = 20.0
camera.pixel_type = 16
camera.roi_height_px = 512
camera.roi_width_px = 512
camera.bit_packing_mode = "msb"

imaris_writer.compression = "lz4shuffle"
imaris_writer.data_type = "uint16"

robocopy_transfer.verify_transfer = True
robocopy_transfer.max_retry = 3
robocopy_transfer.timeout_s = 60

# The instrument is now ready to use
print(f"Created instrument: {instrument.name}")
print(f"Number of devices: {len(instrument.devices)}")
print(f"Number of channels: {len(instrument.channels)}")
