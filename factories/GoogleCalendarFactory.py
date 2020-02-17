from __future__ import print_function
from factories.ResourceEventFactory import ResourceEventFactory
import requests_cache
from datetime import timedelta
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

EXPIRE_AFTER = timedelta(hours=1)
requests_cache.install_cache("gcal_cache", expire_after=EXPIRE_AFTER)
class GoogleCalendarFactory(ResourceEventFactory):
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    def __init__(self, users):
        super().__init__()
        self.users = users
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def generate(self):
         # Call the Calendar API
        # now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        page_token = None
        exported_events = []
        PTO_STRINGS = ['PTO', 'Vacation', '🏝️', '🌴']
        while True:
            events = self.service.events().list(calendarId='robbiep@yelp.com', pageToken=page_token, timeMin='2020-01-01T00:00:00-07:00').execute()
            for event in events['items']:
                if(event.get('summary') in PTO_STRINGS):
                    exported_events.append({
                        "id": event['id'],
                        "resourceId": 'robbiep@yelp.com',
                        "title": "🌴 PTO",
                        "start": event['start'].get('date', event['start'].get('dateTime')),
                        "end": event['end'].get('date', event['end'].get('dateTime')),
                    })
                    # import pdb;pdb.set_trace()
                    print(event['start'].get('date', event['start'].get('dateTime')))
                elif(event.get('summary') in ['WFH']):
                    exported_events.append({
                        "id": event['id'],
                        "resourceId": 'robbiep@yelp.com',
                        "title": "🏠 WFH",
                        "start": event['start'].get('date', event['start'].get('dateTime')),
                        "end": event['end'].get('date', event['end'].get('dateTime')),
                    })
                    print(event['start'].get('date', event['start'].get('dateTime')))
                page_token = events.get('nextPageToken')
            if not page_token:
                break
        return exported_events