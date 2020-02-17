import json
import os
import re
from datetime import timedelta

import requests
import requests_cache
from dotenv import load_dotenv
from ics import Calendar

load_dotenv()


expire_after = timedelta(hours=1)
requests_cache.install_cache("pd_cache", expire_after=expire_after)

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

def write_data(resources, events):
    with open("frontend/src/generated_data/events.json", "w") as f:
        json.dump(events, f, ensure_ascii=False)
    with open("frontend/src/generated_data/resources.json", "w") as f:
        json.dump(resources, f, ensure_ascii=False)

req_json = requests.get(SCHEDULE_URL, headers=HEADERS).json()

cal = Calendar(requests.get(req_json["schedule"]["http_cal_url"]).text)
users = set()
events = []
for event in cal.events:
    user = re.findall(PATTERN, str(event.extra))[0]
    assert user
    users.add(user)

    events.append(
        {
            "id": event.uid,
            "resourceId": user,
            "title": "📞" + req_json["schedule"]["summary"],
            "start": str(event.begin.to("US/Pacific")),
            "end": str(event.end.to("US/Pacific")),
        }
    )

resources = [{"id": user, "title": user} for user in sorted(users)]
write_data(resources, events)
