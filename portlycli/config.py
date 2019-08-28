import os
import configparser
from portlycli.models import Credentials
import portlycli.defaults as defaults

class Config(object):

    non_env_sections = ['paths', 'DEFAULT']
    portal_envs = []
    creds = dict()
    
    def __init__(self, ini):

        # Merge the user_provided options onto the default options
        envs = filter(lambda c: c not in self.non_env_sections, ini)

        self.portal_envs = list(envs)

        settings = filter(lambda c: c in self.non_env_sections, ini)

        for section in list(settings):
            for name, value in ini[section].items():
                setattr(self, name, value)        

        # turn the configured environments into named tuples 
        self.to_creds(ini)
        # print(self.downloads)

    def portals(self):
        return self.portal_envs

    def to_creds(self, ini):
        for env in self.portal_envs:
            section = ini[env]
            values = []
            for param in ['url', 'user', 'passwd']:
                if param in section:
                    values.append(section[param])
                else:
                    values.append(None)
            self.creds[env] = Credentials(*values)
            
    def get_owner_by_env(self, env):
        credentials = self.creds[env]
        return credentials.user


def find_file_in_syspath(fn):
    cwd = os.getcwd()
    home = os.path.expanduser("~")    
    os_paths = os.environ['PATH'].split(os.pathsep)
    for path in [cwd, home] + os_paths:
        for root, dirs, files in os.walk(path):
            if fn in files:
                return os.path.join(root, fn)    

def find_config():
    return find_file_in_syspath(defaults.CONFIG_FILE_NAME)
    
def loader(args):

    if args.conf_path is None:
        config_path = find_config()
        if config_path is None:
            print("No config found in PATH or set by the user using --config.  Bye.")
            return None
        else:
            args.conf_path = config_path
    else:
        if not os.path.isfile(args.conf_path):
            print("The config file '%s' does not exist.  Bye." % (args.conf_path))
            return None

    config_path = os.path.abspath(args.conf_path)
    config = configparser.ConfigParser()
    config.read(config_path)
    conf = Config(config)
    
    return conf
