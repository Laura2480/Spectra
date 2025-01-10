import yaml
from easydict import EasyDict as edict
import os
#project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
def update_config(config_file):
    #with open(os.path.join(project_dir,config_file)) as f:
    with open(config_file) as f:
        config = edict(yaml.load(f, Loader=yaml.FullLoader))
        return config
