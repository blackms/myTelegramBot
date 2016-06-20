from uuid import uuid1
from myTelegramBot.Exceptions import NoUserAssignedToSession
from myTelegramBot.core.auth_manager import *


class SessionManager(object):
    def __init__(self, name='Default'):
        self.name = name
        self.sessions = {}

    def add_user_session(self, session):
        assert isinstance(session, Session), Exception('Expected Session, received: {}'.format(type(session)))
        self.sessions[session.id] = session

    def remove_user_session(self, session):
        if isinstance(session, Session):
            session_id = session.id
        elif isinstance(session, str):
            session_id = session
        else:
            raise Exception('Expected Session or str, received: {}'.format(type(session)))
        try:
            del self.sessions[session_id]
        except NameError:
            raise Exception('Session not found: {}'.format(session))

    def get_user_session(self, user_id):
        session = [x.user for x in self.sessions.values() if x.user.user_id == user_id]
        return session


class Session(object):
    def __init__(self, user):
        self.id = uuid1()
        assert isinstance(user, (AdminUser, NormalUser, PowerUser)), NoUserAssignedToSession(
            message="Expected User, received: {}".format(type(user))
        )
        self.user = user
