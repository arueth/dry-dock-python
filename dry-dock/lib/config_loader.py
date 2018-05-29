import os

from exception.unsupported_config_error import UnsupportedConfigError


class ConfigLoader:
    __path = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, conf_dir, configs=None):
        self.conf_dir = conf_dir

        self.__config_map = {
            'auth': f"{self.__path}/../conf/{self.conf_dir}/auth.yml",
            'certbot': f"{self.__path}/../conf/{self.conf_dir}/certbot.yml",
            'dtr': f"{self.__path}/../conf/{self.conf_dir}/dtr.yml",
            'interlock':  f"{self.__path}/../conf/{self.conf_dir}/interlock.yml",
            'logging': f"{self.__path}/../conf/{self.conf_dir}/logging.yml",
            'ucp': f"{self.__path}/../conf/{self.conf_dir}/ucp.yml"
        }

        if configs is None:
            configs = self.__config_map.keys()
        elif isinstance(configs, str):
            configs = [configs]

        self.configs = list(set([config.lower() for config in configs]))

        return

    def load(self):
        all_configs = {}

        for config in self.configs:
            try:
                file = self.__config_map[config]

            except KeyError as e:
                raise UnsupportedConfigError(e)

            filename, file_type = os.path.splitext(file)
            file_type = file_type.lower()

            if file_type in ['.yml', '.yaml']:
                from config_loaders.yaml import Yaml
                all_configs[config] = Yaml(file).load()

        return all_configs
