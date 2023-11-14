import sys
from ruamel.yaml import YAML
from pathlib import Path

def load_device(driver, module, kwds):
    """Load in device based on config. Expecting driver, module, and kwds input"""
    __import__(driver)
    device_class = getattr(sys.modules[driver], module)
    for k, v in kwds.items():
        if str(v).split('.')[0] in dir(sys.modules[driver]):
            arg_class = getattr(sys.modules[driver], v.split('.')[0])
            kwds[k] = getattr(arg_class, '.'.join(v.split('.')[1:]))
    return device_class(**kwds)

def setup_device(device, driver, setup):
    """Setup device based on config
    :param device: device to be setup
    :param setup: dictionary of attributes, values to set according to config"""

    for property, value in setup.items():
        if str(value).split('.')[0] in dir(sys.modules[driver]):
            arg_class = getattr(sys.modules[driver], value.split('.')[0])
            value = getattr(arg_class, '.'.join(value.split('.')[1:]))
        else:
            value = eval(value) if '.' in str(value) else value

        setattr(device, property, value)

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_oxxius_laser.yaml")
cfg = YAML().load(stream=config_path)
lasers = {}
combiners = {}

for name, specs in cfg['channel_specs'].items():
    if 'type' in specs.keys() and specs['type'] == 'laser':
        # If type is laser, create laser class and use kw specified
        lasers[name] = load_device(specs['driver'], specs['module'], specs['kwds'])
        setup_device(lasers[name] ,specs['driver'], specs['setup'])
    elif 'type' in specs.keys() and specs['type'] == 'combiner':
        # If type is combiner, set up combiner then set up all lasers inside combiner
        combiners[name] = load_device(specs['driver'], specs['module'], specs['kwds'])
        setup_device(combiners[name], specs['driver'], specs['setup'])
        for nm in specs.keys():
            if nm.isdigit() and specs[nm]['type'] == 'laser':
                kwds = dict(specs[nm]['kwds'])
                kwds['combiner'] = combiners[name]# Add combiner to kwds
                lasers[name +'.'+ nm] = load_device(specs[nm]['driver'], specs[nm]['module'], kwds)
                setup_device(lasers[name +'.'+ nm], specs[nm]['driver'], specs[nm]['setup'])

print(lasers)
print(combiners)