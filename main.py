import json
import os
import re
from datetime import timedelta

import requests
import requests_cache
from dotenv import load_dotenv
from ics import Calendar
from jinja2 import Environment
from jinja2 import FileSystemLoader

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

def write_html(resources, events):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("App.j2")
    rendered_template = template.render(
        resources=resources,
        events=events,
        calendar_name=os.getenv("CALENDAR_NAME")
    )
    with open("frontend/src/App.js", "w") as f:
        f.write(rendered_template)


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
write_html(resources, json.dumps(events))
