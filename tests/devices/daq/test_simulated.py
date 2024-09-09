from pathlib import Path
from voxel.instrument.devices.daq.simulated import DAQ
from ruamel.yaml import YAML

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_simulated.yaml")
config = YAML().load(Path(config_path))

ao_task = config['daq']['tasks']['ao_task']
do_task = config['daq']['tasks']['do_task']
co_task = config['daq']['tasks']['co_task']

daq = DAQ("Dev1")
daq.add_task(ao_task, 'ao')
daq.add_task(do_task, 'do')
daq.add_task(co_task, 'co')
daq.generate_waveforms(ao_task, 'ao', '488')
daq.generate_waveforms(do_task, 'do',  '488')
daq.write_ao_waveforms()
daq.write_do_waveforms()
daq.plot_waveforms_to_pdf()
daq.close_all()