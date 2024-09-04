from voxel.devices.nidaq import plot_waveforms, DAQWaveform, DAQWaveformConfig


def main():
    common = {
        "sampling_frequency_hz": 350e3,
        "period_time_ms": 10,
        "start_time_ms": 0,
        "end_time_ms": 5,
        "rest_time_ms": 0,
        "center_volts": 2.5,
        "amplitude_volts": 5,
        "frequency_hz": 1000
    }

    square_cfg = DAQWaveformConfig(**common)

    delayed_square_cfg = DAQWaveformConfig(**{**common, "start_time_ms": common["period_time_ms"] * 0.25})

    triangle_cfg = DAQWaveformConfig(**{**common, "end_time_ms": common["period_time_ms"] * 0.5})

    delayed_triangle_cfg = DAQWaveformConfig(
        **{**common, "start_time_ms": common["period_time_ms"] * 0.25, "end_time_ms": common["period_time_ms"] * 0.75}
    )

    sawtooth_cfg = DAQWaveformConfig(**{**common, "end_time_ms": common["period_time_ms"]})

    waves = {
        "Square": DAQWaveform.SQUARE.generate_waveform(square_cfg),
        "Delayed Square": DAQWaveform.SQUARE.generate_waveform(delayed_square_cfg),
        "triangle": DAQWaveform.TRIANGLE.generate_waveform(triangle_cfg, False),
        "sawtooth": DAQWaveform.TRIANGLE.generate_waveform(sawtooth_cfg, False)
    }

    plot_waveforms(waves, square_cfg, num_cycles=2)


if __name__ == "__main__":
    main()
