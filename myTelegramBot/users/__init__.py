

class User(object):
    def __init__(self, username, password, auth_method):
        self.username = username
        self.password = password
        self.auth_method = auth_method

    def __str__(self):
        return 'user: {}'.format(self.username)

    def login(self):
        self.auth_method.find_user()
