<img src="logo.png" width="75" height="75">

# Voxel

Voxel is a general microscope control package designed to simplify the process of configuring
and controlling different microscopy systems. Voxel provides two key modules:

1. **Instrument**: `VoxelInstrument`

   Defining and controlling a collection of devices through a configuration YAML file.
   The instrument module is designed to be flexible and extensible supporting various device types each with their own
   base class.

   The devices are defined in `voxel.instrument.devices.<device-type>` and include:
    - camera: `VoxelCamera`
    - lens: `VoxelLens`
    - laser: `VoxelLaser`
    - filter: `VoxelFilterWheel`, `VoxelFilter`
    - linear_axis: `VoxelLinearAxis`
    - rotation_axis: `VoxelRotationAxis`
    - flip_mount: `VoxelFlipMount`
    - power_meter: `VoxelPowerMeter`

   A voxel compatible device driver is one that inherits from the appropriate base class and implements the
   required methods.

   In addition to the device classes, the instrument module also includes a `VoxelNIDAQ` class that abstracts the
   `nidaqmx` SDK and allows for `AO`, `DO`, and `CO` tasks for controlling supported devices such as AOTFs, cameras, and
   axes.

   Instruments can be defined as a collection of any set of devices through a configuraiton
   YAML file, typically named `instrument.yaml`. The configuration file is used to build the instrument object and
   instantiate the devices with the appropriate settings. Classes `InstrumentConfig` and `InstrumentFactory` handle the
   reading and parsing of the configuration file and the creation of the instrument object respectively.

   A complete list of available device drivers can be found in the [Device Drivers](#device-drivers) section.

2. **Acquisition**: `VoxelAcquisition`, `VoxelAcquisitionEngine`

   Performing imaging experiments with the defined instrument. This includes classes for writing data and concurrent
   transferring of data to external
   storage.

Voxel also provides additional utilities useful for performing imaging experiments including tools for performing
online processing of imaging data under the `voxel.kit` module.

## Device Drivers

Currently supported device types and models are listed below.

```yaml
Devices:
  Cameras:
    - eGrabber GenICam cameras
      - Vieworks VP-151MX tested
      - Vieworks VNP-604MX tested
    - Hamamatsu cameras
      - ORCA-Flash4.0 V3 tested
      - ORCA-Fusion BT tested
    - PCO cameras (untested)
    - Simulated camera
  Axes:
    - ASI
    - Simulated stage
  Lasers:
    - Coherent OBIS
    - Coherent Genesis
    - Vortran Stradus
    - Oxxius LBX and LCX
    - Cobolt
    - Simulated laser
  AOTF:
    - AAOpto
    - Simulated AOTF
  Filterwheel:
    - ASI FW-1000
    - Simulated filter wheel
  Flip mount:
    - Thorlabs MFF101
    - Simulated flip mount
  Power meter:
    - Thorlabs PM100D
    - Simulated power meter
  Rotation mount:
    - Thorlabs K10CR1
    - Simulated rotation mount
  Tunable lens:
    - ASI TGTLC
    - Optotune ELE41
    - Optotune ICC4C
    - Simulated tunable lens
  DAQ:
    - National Instruments
      - PCIe-6738 tested
    - Simulated DAQ
```

# File Handlers

```yaml
Writers:
  - ImarisWriter (.ims)
  - TIFFWriter (.tiff)
  - BDVWriter (.h5/.xml)
  - ACQUIRE (.zarr V2/V3)
File transfers:
  - Robocopy
  - Rsync
```

## Useful tools

```yaml
CPU processes:
  - Downsample 2D
  - Downsample 3D
  - Maximum projections (xy, xz, yz)
GPU processes:
  - Downsample 2D
  - Downsample 3D
  - Rank-ordered downsample 3D
```

## Documentation

    *(coming soon)*

## Installation

### Prerequisites

- **Python>=3.7** (tested)
  (Recommended to install via
  [Anaconda](https://www.anaconda.com/products/individual) or
  [Miniconda](https://docs.conda.io/en/latest/miniconda.html))
- **eGrabber** (Windows and Linux)
  To control the Vieworks VP-151MX camera you will need
  [eGrabber for CoaxLink and GigELink](https://www.euresys.com/en/Support/Download-area?Series=105d06c5-6ad9-42ff-b7ce-622585ce607f)
  installed for your particular system. Note that, to download the eGrabber SDK, you will first need to make
  an account. After downloading and installing eGrabber, you will need to install the eGrabber python package (stored as
  a wheel file). For more info installing the Python wheel file, see
  the [notes from Euresys](https://documentation.euresys.com/Products/COAXLINK/COAXLINK/en-us/Content/04_eGrabber/programmers-guide/Python.htm).

  Generally, the process should be as simple as finding the wheel package in the
  eGrabber subfolder and invoking:
    ````
    pip install egrabber-xx.xx.x.xx-py2.py3-none-any.whl
    ````
- **DCAM** (Windows only)
  To control Hamamatsu cameras you will need
  [DCAM API](https://dcam-api.com/) installed for your particular system.
- **Coherent HOPS** (Windows only)
  To control Coherent Genesis series lasers, you will need to install
  Coherent HOPS. *(instructions coming soon)*

### Installation Steps

1. Create a virtual environment and activate it:
   On Windows:
    ```bash
    conda create -n voxel
    conda activate voxel
    ```

2. Clone the repository:
    ```bash
    git clone https://github.com/AllenNeuralDynamics/voxel.git
    ```

3. To use the software, in the root directory, run:
    ```bash
    pip install -e .
    ```

4. To develop the code, run:
    ```bash
    pip install -e .[dev]
    ```

## Usage

1. Instantiating a single device:

   Individual device can be instantiated by importing the appropriate driver
   class with the expected arguments. For example a camera object for a Vieworks
   VP-151MX can be invoked as:
    ```python
    from voxel.instrument.devices.camera import VieworksCamera

    camera = VieworksCamera(id='123456')
    ```
   Camera properties can then be queried and set by accessing attributes of the
   camera object:
    ```python
    camera.exposure_time ms = 10.0
    camera.pixel_type = 'mono16'
    camera.bit_packing_mode = 'lsb'
    camera.binning = 1
    camera.width_px = 14192
    camera.height_px = 10640
    camera.trigger = {'mode': 'on', 'source': 'line0', 'polarity': 'risingedge'}
    ```
   The camera can then be operated with:
    ```python
    camera.prepare() # this function arms and creates the camera buffer
    camera.start()
    image = camera.grab_frame()
    camera.stop()
    camera.close()
    ```

2. Voxel facilitates defining entire instruments through a YAML file:

    ```yaml
    instrument:
    devices:
        vp-151mx camera:
        type: camera
        driver: voxel.devices.camera.simulated
        module: SimulatedCamera
        init:
            id: 123456
        settings:
            exposure_time_ms: 10.0
            pixel_type: mono16
            height_offest_px: 0
            height_px: 2048
            width_offset_px: 0
            width_px: 2048
            trigger:
            mode: off
            polarity: rising
            source: external
        488 nm laser:
        type: laser
        driver: voxel.devices.lasers.simulated
        module: SimulatedLaser
        init:
            id: COM1
        x axis stage:
        type: scanning_stage
        driver: voxel.devices.stage.simulated
        module: Stage
        init:
            hardware_axis: x
            instrument_axis: z
        settings:
            speed_mm_s: 1.0
    ```
   An instrument can be invoked by loading the YAML file with and the loaded devices
   can be accessed with. The above example uses all simulated device classes.
    ```python
    from voxel.instrument.instrument import Instrument

    instrument = Instrument(config_path='example.yaml')
    instrument.cameras['vp-151mx camera']
    instrument.lasers['488 nm laser']
    instrument.scanning_stages['x axis stage']
    ```

3. Experimental workflows may then be scripted by using the full instrument object
   and the contained device objects as needed:

   *(example coming soon)*

## Support and Contribution

If you encounter any problems or would like to contribute to the project,
please submit an [Issue](https://github.com/AllenNeuralDynamics/voxel/issues)
on GitHub.

### Branching Strategy

This repository uses the following branching strategy:

- `main`: Contains production-ready code. Updated only for releases and hotfixes.
- `develop`: Default branch. Contains the latest development changes.
- `feature/*`: Used for developing new features. Branch off from and merge back into `develop`.
- `hotfix/*`: Used for critical bug fixes. Branch off from `main`, and merge to both `main` and `develop`.

Contributors should typically branch off from and create pull requests to `develop`.

Refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for more details.

### License

Voxel is licensed under the MIT License. For more details, see
the [LICENSE](LICENSE) file.
