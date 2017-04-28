import datetime
import os
from abc import ABCMeta, abstractmethod

import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


class Calendar(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def get_events(self):
        raise NotImplementedError('This method must be implemented.')

    @abstractmethod
    def add_event(self):
        raise NotImplementedError('This method must be implemented.')

    @abstractmethod
    def delete_event(self):
        raise NotImplementedError('This method must be Implemented.')


class GoogleCalendar(Calendar):
    def __init__(self, scopes='https://www.googleapis.com/auth/calendar', client_secret_file='client_secret.json',
                 application_name='Rac Grosseto Bot', calendar_id='ha1i5mboaknnd8jos469thnjuk@group.calendar.google.com'):
        """

        :param scopes: Google API Endpoint
        :type scopes: str
        :param client_secret_file: File containing OAuth2 Information
        :type client_secret_file: str
        :param application_name: Name of the Application
        :type application_name: str
        """
        self.scopes = scopes
        self.client_secret_file = client_secret_file
        self.application_name = application_name
        self.calendar_id = calendar_id
        self.credentials = self._get_credentials()
        self.httpHandler = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=self.httpHandler)
        super(GoogleCalendar, self).__init__()

    def _get_credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'calendar-python-quickstart.json')
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file, self.scopes)
            flow.user_agent = self.application_name
            credentials = tools.run(flow, store)
        return credentials

    def add_event(self):
        pass

    def delete_event(self):
        pass

    def get_events(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(
            calendarId=self.calendar_id, timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events