from uuid import uuid1
from myTelegramBot.core.users import User
from myTelegramBot.Exceptions import NoUserAssignedToSession


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


class Session(object):
    def __init__(self, user):
        self.id = uuid1()
        assert isinstance(user, User), NoUserAssignedToSession(
            message="Expected User, received: {}".format(type(user))
        )
        self.user = user
