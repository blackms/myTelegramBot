import ConfigParser


class BaseConfigObject(object):
    def __init__(self, *args, **kwargs):
        pass


def _write_ini_file_after(method):
    def wrapped(self, *a, **ka):
        r = method(self, *a, **ka)
        with open(self.config_file_path, 'w') as fh:
            self.config.write(fh)
        return r
    return wrapped


class FileConfigObject(BaseConfigObject):
    def __init__(self, config_file_path='config.ini'):
        self.config_file_path = config_file_path
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file_path)
        # Map the configuration into a local dictionary
        self.config_map = {k: self._config_section_map(k) for k in self.config.sections()}
        super(FileConfigObject, self).__init__()

    def _config_section_map(self, section):
        config_section_map_dict = {}
        options = self.config.options(section)
        for option in options:
            try:
                config_section_map_dict[option] = self.config.get(section, option)
                if config_section_map_dict[option] == -1:
                    pass
            except KeyError:
                config_section_map_dict[option] = None
        return config_section_map_dict

    def add_section(self, section_name):
        self.config.add_section(section_name)
        with open(self.config_file_path, 'w') as fh:
            self.config.write(fh)

    @_write_ini_file_after
    def remove_section(self, section_name):
        self.config.remove_section(section_name)

    @_write_ini_file_after
    def set_option(self, section, key, value):
        self.config.set(section=section, option=key, value=value)

    def get_option(self, section, key):
        try:
            return self.config.get(section=section, option=key)
        except ConfigParser.NoOptionError:
            return None

    def get_section(self, section):
        try:
            return self.config_map[section] if isinstance(self.config_map, dict) else None
        except KeyError:
            return None
