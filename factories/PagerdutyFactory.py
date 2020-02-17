import os
import re
from datetime import timedelta

import requests
import requests_cache
from dotenv import load_dotenv
from ics import Calendar

from factories.ResourceEventFactory import ResourceEventFactory

EXPIRE_AFTER = timedelta(hours=1)
requests_cache.install_cache("pd_cache", expire_after=EXPIRE_AFTER)
load_dotenv()


class PagerdutyFactory(ResourceEventFactory):
    PD_TOKEN = os.getenv("PD_TOKEN")
    PD_TEAM = os.getenv("PD_TEAM")
    SCHEDULE_URL = "https://api.pagerduty.com/schedules/{}?time_zone=America/Los_Angeles".format(
        PD_TEAM
    )
    HEADERS = {
        "Accept": "application/vnd.pagerduty+json;version=2",
        "Authorization": f"Token token={PD_TOKEN}",
    }
    PATTERN = r"(?<=ATTENDEE:).*?(?=@)"

    def __init__(self, users):
        super().__init__()
        self.users = users

    def generate(self):
        schedule_response = requests.get(self.SCHEDULE_URL, headers=self.HEADERS).json()

        cal = Calendar(requests.get(schedule_response["schedule"]["http_cal_url"]).text)
        events = []
        for event in cal.events:
            user = re.findall(self.PATTERN, str(event.extra))[0]
            assert user
            events.append(
                {
                    "id": event.uid,
                    "resourceId": user + "@yelp.com",
                    "title": "📞 On Call",
                    "start": str(event.begin.to("US/Pacific")),
                    "end": str(event.end.to("US/Pacific")),
                }
            )
        return events
