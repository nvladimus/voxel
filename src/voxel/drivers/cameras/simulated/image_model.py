import numpy as np
import tifffile

from voxel.core.instrument.drivers.camera import ROI


class ImageModel:
    def __init__(self, qe, gain, dark_noise, bitdepth, baseline, reference_image_path) -> None:
        self.raw_reference_image = tifffile.imread(reference_image_path)
        self.sensor_size_px = self.raw_reference_image.shape
        self.qe = qe
        self.gain = gain
        self.dark_noise = dark_noise
        self.bitdepth = bitdepth
        self.baseline = baseline

    def __repr__(self):
        return (
            f"ImageModel(qe={self.qe}, "
            f"gain={self.gain}, "
            f"dark_noise={self.dark_noise}, "
            f"bitdepth={self.bitdepth}, "
            f"baseline={self.baseline})"
        )

    def generate_frame(self, exposure_time, roi: ROI, pixel_type):
        # Scale the reference image based on exposure time and ROI
        scaled_image = self.raw_reference_image * (exposure_time / 0.1)
        roi_image = self._apply_roi(scaled_image, roi)

        # Add noise to the image
        noisy_image = self._add_camera_noise(roi_image)

        # Convert to the correct pixel type
        return noisy_image.astype(pixel_type)

    @staticmethod
    def _apply_roi(image, roi: ROI):
        # crop the center of the image
        start_h = roi.origin.y
        start_w = roi.origin.x
        return image[start_h : start_h + roi.size.x, start_w : start_w + roi.size.y]

    def _add_camera_noise(self, image):
        # Add shot noise
        photons = np.random.poisson(image)

        # Convert to electrons
        electrons = self.qe * photons

        # Add dark noise
        electrons_out = np.random.normal(scale=self.dark_noise, size=electrons.shape) + electrons

        # Convert to ADU and add baseline
        max_adu = 2**self.bitdepth - 1
        image_out = (electrons_out * self.gain).astype(int)
        image_out += self.baseline
        np.clip(image_out, 0, max_adu, out=image_out)

        return image_out
