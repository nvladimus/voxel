# Voxel Camera
`VoxelCamera` is an abstract base class that defines the inteface for cameras compatible with a VoxelInstrument.  

## Methods

### `prepare()`
Prepare the camera for data acquisition. This method should be called before starting the acquisition.  
Typically, this method will perform some initialization tasks, such as **buffer allocation** etc.  

### `start(frame_count: int)`
Start the acquisition of `frame_count` frames. By default, the camera will acquire an infinite number of frames.  

### `stop()`
Stop the acquisition.

### `grab_frame() -> VoxelFrame`
Grab a single frame from the camera. This method is blocking.  
Note: `VoxelFrame: TypeAlias = np.ndarray`.

### `reset()`
Reset the camera to its initial state....  

### `close()`
Close the camera. Called when the camera is no longer needed.  
Perform cleanup tasks, such as releasing resources.  

### `log_metadata()`
Log metadata about the camera....

## Properties

### 1. `sensor_size_px: Vec2D`, `sensor_width_px: int`, `sensor_height_px: int` 

The size of the camera sensor in pixels.  
- **Read-only**

### 2. `roi_width_px: int`, `roi_height_px: int`, `roi_width_offset_px: int`, `roi_height_offset_px: int`

Describes the size and position of the region of interest (ROI) on the sensor.  
- **Read-write**
- **Deliminated Property**

### 3. `binning: Binning`

The binning factor of the camera. Note: binning_y = binning_x.

- **Read-write**
- **Enumerated Property**

```python
class Binning(IntEnum):
    X1 = 1
    X2 = 2
    X4 = 4
    X8 = 8
```

### 4. `image_size_px: Vec2D`, `image_width_px: int`, `image_height_px: int`  

The size of the image that will be acquired by the camera. Describes the frame shape.  
- **Read-only**

### 5. `exposure_time_ms: int`

The exposure time of the camera in milliseconds.
- **Read-write**
- **Deliminated Property**

### 6. `frame_time_ms: int`

The time it takes to acquire a single frame in milliseconds.  
- **Read-only**

### 7. `acquisition_state: AcquisitionState`

The current state of the camera acquisition.
- **Read-only**

```python
@dataclass
class AcquisitionState:
    frame_index: int
    input_buffer_size: int
    output_buffer_size: int
    dropped_frames: int
    frame_rate_fps: float
    data_rate_mbs: float
```

### 8. `pixel_type: PixelType`

The pixel type of the camera.
- **Read-write**
- **Enumerated Property**

```python
class PixelType(IntEnum):
    MONO8 = 8
    MONO10 = 10
    MONO12 = 12
    MONO14 = 14
    MONO16 = 16
```

## Others
1. Line Interval
2. Bitpacking mode
3. Trigger settings
4. Sensor mode
5. Readout mode
6. Readout direction
7. Sensor temperature c.
8. 
