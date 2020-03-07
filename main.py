import json

import yaml

from factories.GoogleCalendarFactory import GoogleCalendarFactory
from factories.PagerdutyFactory import PagerdutyFactory


def write_data(resources, events, config):
    with open("frontend/src/generated_data/events.json", "w") as f:
        json.dump(events, f, ensure_ascii=False, indent=4, sort_keys=True)
    with open("frontend/src/generated_data/resources.json", "w") as f:
        json.dump(resources, f, ensure_ascii=False, indent=4, sort_keys=True)
    with open("frontend/src/generated_data/config.json", "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=4, sort_keys=True)


def main():
    cfg = None
    users = []
    with open("config.yaml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        users = cfg["users"]
    factories = [PagerdutyFactory(), GoogleCalendarFactory(users)]
    events = []

    for factory in factories:
        events.extend(factory.generate())

    resources = [{"id": user, "title": user.split("@")[0]} for user in sorted(users)]
    config = {
        'title': cfg["calendar_name"]
    }
    write_data(resources, events, config)


if __name__ == "__main__":
    main()
