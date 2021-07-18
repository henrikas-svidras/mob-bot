import yaml
import os

def get_yaml(path):
    """Method that opens the yaml file.

    Args:
        path (str, optional): path to yaml file..
    """
    env_vars = None
    with open(path, 'r') as stream:
        env_vars = yaml.safe_load(stream)
    
    return env_vars

def update_yaml_file(path, value, key):
    """Method to update an existing yaml file.
    
    Args:
        path (str): path to the yaml file to update.
        value: the value to set.
        key (str): the key the value will be set to
    """ 
    print(path)
    data = get_yaml(path)
    if data is None:
        data = {} 
    data[key] = value
    with open(path, 'w') as stream:
        yaml.dump(data, stream, default_flow_style=False)
        
def smart_create_file(path):
    if os.path.isfile(path):
        return None
    else:
        basedir = os.path.dirname(path)
        if basedir:
            if not os.path.exists(basedir):
                os.makedirs(basedir)
        
        open(path, 'a').close()
        return None