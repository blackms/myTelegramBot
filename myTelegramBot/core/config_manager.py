from abc import ABCMeta, abstractproperty, abstractmethod
from myTelegramBot.Exceptions import ModuleNotAvailable
from functools import wraps


class BaseConfigObject(object):
    def __init__(self, *args, **kwargs):
        pass


class SqliteConfigObject(BaseConfigObject):
    def __init__(self, path='local.db'):
        try:
            import sqlite3
        except ImportError:
            raise ModuleNotAvailable(message='Sqlite module not available.', module_name='sqlite3')

        self.conn = sqlite3.connect(path)
        super(SqliteConfigObject, self).__init__()


class FileConfigObject(BaseConfigObject):
    def __init__(self, config_file_path='config.ini'):
        import ConfigParser
        self.config_file_path = config_file_path
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file_path)
        # Map the configuration into a local dictionary
        self.config_map = map(lambda x: self._config_section_map(x), self.config.sections())
        super(FileConfigObject, self).__init__()

    @staticmethod
    def _write_ini_file_after(method):
        def wrapper(f):
            @wraps(f)
            def wrapped(self, *m_args, **m_kwargs):
                if callable(method):
                    f(self, *m_args, **m_kwargs)
                    with open(self.config_file_path, 'w') as fh:
                        self.config.write(fh)
                return wrapped
            return wrapper

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

    @_write_ini_file_after
    def add_section(self, section_name):
        self.config.add_section(section_name)

    @_write_ini_file_after
    def remove_section(self, section_name):
        self.config.remove_section(section_name)
