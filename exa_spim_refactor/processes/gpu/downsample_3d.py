import numpy
from gputools import OCLProgram, OCLArray, get_device

class DownSample3D:

    def __init__(self, binning: int = 2):
        # downscaling factor
        self._block_size = binning
        # opencl kernel
        self._kernel = """
        __kernel void downsample3d(__global short * input,
                                   __global short * output){
          int i = get_global_id(0);
          int j = get_global_id(1);
          int k = get_global_id(2);
          int Nx = get_global_size(0);
          int Ny = get_global_size(1);
          int Nz = get_global_size(2);
          int res = 0; 

          for (int m = 0; m < BLOCK; ++m) 
             for (int n = 0; n < BLOCK; ++n)
                for (int o = 0; o < BLOCK; ++o)
                    res+=input[BLOCK*Nx*Ny*(BLOCK*k+n)+BLOCK*Nx*(BLOCK*j+m)+BLOCK*i+n];
          output[Nx*Ny*k+Nx*j+i] = (short)(res/BLOCK/BLOCK/BLOCK);
        }
        """

        self._prog = OCLProgram(src_str=self._kernel,
                               build_options=['-D', f'BLOCK={self._block_size}'])

    def run(self, image: numpy.array):
            x_g = OCLArray.from_array(image)
            y_g = OCLArray.empty(tuple(s // self._block_size for s in image.shape), image.dtype)
            self._prog.run_kernel(f'downsample3d', y_g.shape[::-1],
                                 None, x_g.data, y_g.data)
            return y_g.get()