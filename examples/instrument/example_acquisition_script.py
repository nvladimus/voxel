import numpy as np
from colorama import Fore, Style, init
from matplotlib import pyplot as plt

from voxel.acquisition import AcquisitionConfig, AcquisitionFactory
from voxel.acquisition.acquisition import VoxelAcquisition
from voxel.acquisition.model.scan_plan import ScanPath, ParametricScanPathGenerator, StartCorner, \
    Direction, Pattern, SpiralScanPathGenerator
from voxel.utils.geometry.vec import Vec3D
from voxel.utils.logging import setup_logging

ACQUISITION_CONFIG_YAML = './example_acquisition.yaml'

init(autoreset=True)  # Initialize colorama


def main():
    setup_logging(log_level='DEBUG')

    acq_config = AcquisitionConfig.from_yaml(ACQUISITION_CONFIG_YAML)
    acq: VoxelAcquisition = AcquisitionFactory(acq_config).create_acquisition()

    print_acquisition_info(acq)

    acq.volume.min_corner = Vec3D(0, 0, 0)
    acq.volume.max_corner = Vec3D(150, 150, 100)
    print_acquisition_info(acq)

    # Demonstrate different scan path strategies
    parametric_generator = ParametricScanPathGenerator(
        start_corner=StartCorner.TOP_LEFT,
        direction=Direction.ROW_WISE,
        pattern=Pattern.RASTER
    )
    spiral_generator = SpiralScanPathGenerator()

    print("Parametric Scan Path:")
    acq.scan_path_generator = parametric_generator
    print_acquisition_info(acq)
    # plot_scan_path(acq.scan_path, "Parametric Scan Path")

    print("\nSpiral Scan Path:")
    acq.scan_path_generator = spiral_generator
    print_acquisition_info(acq)
    # plot_scan_path(acq.scan_path, "Spiral Scan Path")

    acq.save_tiles()

    acq.instrument.close()


def print_acquisition_info(acq: VoxelAcquisition):
    tiles = [tile for tile_set in acq.tiles for tile in tile_set.values()]
    print(f"{len(tiles)} tiles generated")
    print(f"ScanPath: {acq.scan_path}")
    print(f"Volume: {acq.volume}")
    print()


def plot_scan_path(scan_path: ScanPath, title: str):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_title(title)

    x, y = zip(*scan_path)

    # Create a colormap based on the order of tiles
    colors = plt.cm.viridis(np.linspace(0, 1, len(scan_path)))

    # Plot tiles
    scatter = ax.scatter(x, y, c=range(len(scan_path)), cmap='viridis', s=100)

    # Add colorbar
    plt.colorbar(scatter, label='Scan Order')

    # Plot arrows to show the path direction
    for i in range(len(scan_path) - 1):
        ax.annotate('', xy=scan_path[i + 1], xytext=scan_path[i],
                    arrowprops=dict(arrowstyle='->', color=colors[i], lw=1.5),
                    va='center', ha='center')

    # Highlight start and end points
    ax.plot(x[0], y[0], 'go', markersize=15, label='Start')
    ax.plot(x[-1], y[-1], 'ro', markersize=15, label='End')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend()

    # Invert y-axis to match the typical image coordinate system
    ax.invert_yaxis()

    plt.tight_layout()

    plt.show()


def colorama_visualize_scan_plan(scan_plan: ScanPath, highlight_start: bool = True) -> str:
    """
    Visualize the scan plan with colored output and optional start point highlighting.

    :param scan_plan: List of coordinates representing the scan path
    :param highlight_start: Whether to highlight the start point in green
    :return: String representation of the visualized scan plan
    """
    visualized_plan = ''
    max_i = max(t[0] for t in scan_plan) + 1
    max_j = max(t[1] for t in scan_plan) + 1
    grid = [[' ' for _ in range(max_j)] for _ in range(max_i)]

    for order, (i, j) in enumerate(scan_plan):
        if order == 0 and highlight_start:
            grid[i][j] = f"{Fore.GREEN}{str(order).zfill(2)}{Style.RESET_ALL}"
        else:
            intensity = int(255 * order / len(scan_plan))
            grid[i][j] = f"\033[38;2;{intensity};0;{255 - intensity}m{str(order).zfill(2)}{Style.RESET_ALL}"

    for row in grid:
        visualized_plan += ' '.join(row) + '\n'

    return visualized_plan


if __name__ == "__main__":
    main()
