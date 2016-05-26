import os
import hashlib
import abc
from myTelegramBot.Exceptions import UserNotFound
from myTelegramBot.users import User


class BaseAuthMethod(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        pass

    def find_user(self, *args, **kwargs):
        raise NotImplementedError

    def compare_password(self, *args, **kwargs):
        raise NotImplementedError

    def add_user(self, *args, **kwargs):
        raise NotImplementedError

    def delete_user(self, *args, **kwargs):
        raise NotImplementedError


class Md5hashFile(BaseAuthMethod):
    def __init__(self):
        self._file_path = None
        self.user_dict = {}
        self.__load_user_file()
        super(BaseAuthMethod, self).__init__()

    def __load_user_file(self):
        with open(self.file_path, 'r') as user_file:
            for user in user_file:
                u, p = user.split(':')
                self.user_dict[u] = p

    @staticmethod
    def __str_to_md5(string):
        return hashlib.md5(string).hexdigest()

    def find_user(self, username):
        u, p = username, self.user_dict[username]
        if u is not None:
            return User(username, p)
        return None

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        if not os.path.exists(file_path):
            raise Exception('File Not found.')
        self._file_path = file_path

    def compare_password(self, user, clear_text_password):
        hashed_password = self.__str_to_md5(clear_text_password)
        if self.user_dict[user] == hashed_password:
            return True
        return False

    def add_user(self, *args, **kwargs):
        super(Md5hashFile, self).add_user()

    def delete_user(self, *args, **kwargs):
        super(Md5hashFile, self).delete_user()





