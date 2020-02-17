from __future__ import print_function

import os.path
import pickle
from datetime import date

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from factories.ResourceEventFactory import ResourceEventFactory


class GoogleCalendarFactory(ResourceEventFactory):
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    def __init__(self, users):
        super().__init__()
        self.users = users
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        self.service = build("calendar", "v3", credentials=creds)

    def generate(self):
        # Call the Calendar API
        # now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        start_of_year = (
            date(date.today().year, 1, 1).strftime("%Y-%m-%dT%H:%M:%S.%f%z") + "Z"
        )
        page_token = None
        exported_events = []
        PTO_STRINGS = ["PTO", "Vacation", "🏝️", "🌴"]
        for user in self.users:
            while True:
                events = (
                    self.service.events()
                    .list(calendarId=user, pageToken=page_token, timeMin=start_of_year,)
                    .execute()
                )
                for event in events["items"]:
                    wfh = event.get("summary") in ["WFH"]
                    pto = event.get("summary") in PTO_STRINGS
                    if wfh or pto:
                        exported_events.append(
                            self.format_event(event, user, wfh, pto,)
                        )
                    page_token = events.get("nextPageToken")
                if not page_token:
                    break
        return exported_events

    def format_event(self, event, user, wfh, pto):
        return {
            "id": event["id"],
            "resourceId": user,
            "title": "🏠 WFH" if wfh else "🌴 PTO",
            "start": event["start"].get("date", event["start"].get("dateTime")),
            "end": event["end"].get("date", event["end"].get("dateTime")),
        }
