from __future__ import print_function

import os.path
import pickle
from datetime import *

import dateutil.parser as parser
from dateutil.rrule import rrule
from dateutil.rrule import rruleset
from dateutil.rrule import rrulestr
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
        PTO_STRINGS = ["pto", "vacation", "🏝️", "🌴"]
        WFH_STRINGS = ["wfh", "working from home", "ooo"]
        for user in self.users:
            while True:
                events = (
                    self.service.events()
                    .list(calendarId=user, pageToken=page_token, timeMin=start_of_year,)
                    .execute()
                )
                for event in events["items"]:
                    if event.get("creator", {}).get("self", False):
                        wfh = any(
                            title in event.get("summary", "").lower()
                            for title in WFH_STRINGS
                        )
                        pto = any(
                            title in event.get("summary", "").lower()
                            for title in PTO_STRINGS
                        )
                        if wfh or pto:
                            start = parser.parse(
                                event["start"].get(
                                    "date", event["start"].get("dateTime")
                                )
                            )
                            if event.get("recurrence"):
                                recurring_events = parse_recurring_event(event)
                                original_end = parser.parse(
                                    event["end"].get(
                                        "date", event["end"].get("dateTime")
                                    ),
                                )
                                difference = original_end - start
                                all_day = difference == timedelta(days=1)
                                for recurring_event in recurring_events:
                                    exported_events.append(
                                        self.format_event(
                                            event["id"]
                                            + recurring_event.strftime("%Y-%m-%d"),
                                            user,
                                            recurring_event.strftime("%Y-%m-%d"),
                                            (recurring_event + difference).strftime(
                                                "%Y-%m-%d"
                                            )
                                            if not all_day
                                            else None,
                                            wfh,
                                            pto,
                                            all_day,
                                        )
                                    )
                            else:
                                end = parser.parse(
                                    event["end"].get(
                                        "date", event["end"].get("dateTime")
                                    )
                                )
                                all_day = (
                                    int((end - start).total_seconds()) % 86400 == 0
                                )
                                exported_events.append(
                                    self.format_event(
                                        event["id"],
                                        user,
                                        start.isoformat(),
                                        end.isoformat(),
                                        wfh,
                                        pto,
                                        all_day,
                                    )
                                )
                    page_token = events.get("nextPageToken")
                if not page_token:
                    break
        return exported_events

    def format_event(self, event_id, user, start, end, wfh, pto, all_day):
        return {
            "id": event_id,
            "resourceId": user,
            "title": "🏠 WFH" if wfh else "🌴 PTO",
            "start": start,
            "end": end,
            "allDay": all_day,
        }


def parse_recurring_event(event):
    start = parser.parse(event["start"].get("date", event["start"].get("dateTime")))
    event_rrule = next(filter(lambda x: x.startswith("RRULE"), event["recurrence"]))
    end_of_year = date(date.today().year, 12, 31).strftime("%Y%m%d")
    excl_dates = parse_exdate(event)
    until_str = ";UNTIL=" + end_of_year if "UNTIL" not in event_rrule else ""
    event_rules = rrulestr(s=event_rrule + until_str, dtstart=start)
    if isinstance(event_rules, rrule):
        rules = rruleset()
        rules.rrule(event_rules)
        event_rules = rules

    for exd in excl_dates:
        event_rules.exdate(exd)

    return list(event_rules)


def parse_exdate(event):
    excl_dates = []
    if "EXDATE" in event.get("recurrence"):
        exdate = next(filter(lambda x: x.startswith("EXDATE"), event["recurrence"]))
        name, values = exdate.split(":", 1)
        for v in values.split(","):
            excl_dates.append(datetime.strptime(v, "%Y%m%d"))
    return excl_dates
