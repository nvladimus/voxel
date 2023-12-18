from pathlib import Path
from spim_core.config_base import Config
from ni import DAQ

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_ni.yaml")
config = Config(str(config_path))

ao_task = config.cfg['daq']['tasks']['ao_task']
do_task = config.cfg['daq']['tasks']['do_task']
co_task = config.cfg['daq']['tasks']['co_task']

daq = DAQ("Dev1")
daq.add_ao_task(ao_task)
daq.add_do_task(do_task)
daq.add_co_task(co_task)
daq.generate_ao_waveforms(ao_task, '488')
daq.generate_do_waveforms(do_task, '488')
daq.write_ao_waveforms()
daq.write_do_waveforms()
daq.plot_waveforms_to_pdf()
daq.close_all()