import re
from datetime import timedelta

import requests
import requests_cache
import yaml
from ics import Calendar

from factories.ResourceEventFactory import ResourceEventFactory

EXPIRE_AFTER = timedelta(hours=1)
requests_cache.install_cache("pd_cache", expire_after=EXPIRE_AFTER)


class PagerdutyFactory(ResourceEventFactory):
    PATTERN = r"(?<=ATTENDEE:).*?(?=\r)"
    pd_token = None
    pd_teams = None

    def __init__(self, users):
        super().__init__()
        self.users = users
        cfg = None
        with open("config.yaml", "r") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
            self.pd_token = cfg["pagerduty"]["token"]
            self.pd_teams = cfg["pagerduty"]["teams"]

    def generate(self):
        events = []
        for team in self.pd_teams:
            team_config = next(iter(team.values()))
            cal = self.get_calendar_data(team_config["id"])
            for event in cal.events:
                user = re.findall(self.PATTERN, str(event.extra))[0]
                if user in self.users:
                    events.append(
                        {
                            "id": event.uid,
                            "resourceId": user,
                            "title": team_config["display_text"],
                            "start": str(event.begin.to("US/Pacific")),
                            "end": str(event.end.to("US/Pacific")),
                        }
                    )
        return events

    def get_calendar_data(self, team_id):
        schedule_url = "https://api.pagerduty.com/schedules/{}?time_zone=America/Los_Angeles".format(
            team_id
        )
        headers = {
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Authorization": f"Token token={self.pd_token}",
        }
        schedule_response = requests.get(schedule_url, headers=headers).json()
        return Calendar(
            requests.get(schedule_response["schedule"]["http_cal_url"]).text
        )
