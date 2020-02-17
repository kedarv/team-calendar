import json
from factories.PagerdutyFactory import PagerdutyFactory
from factories.GoogleCalendarFactory import GoogleCalendarFactory

def write_data(resources, events):
    with open("frontend/src/generated_data/events.json", "w") as f:
        json.dump(events, f, ensure_ascii=False, indent=4, sort_keys=True)
    with open("frontend/src/generated_data/resources.json", "w") as f:
        json.dump(resources, f, ensure_ascii=False, indent=4, sort_keys=True)


def main():
    users = [
        'alfredt@yelp.com',
        'gemperle@yelp.com',
        'kedar@yelp.com',
        'robbiep@yelp.com',
        'saqif@yelp.com',
        'slamba@yelp.com',
        'timkitc@yelp.com',
        'angellee@yelp.com',
        'maulik@yelp.com',
        'aryanc@yelp.com',
        'qiqixu@yelp.com',
        'bchan@yelp.com',
        'dbajj@yelp.com',
        'owenev@yelp.com',
    ]
    factories = [
        PagerdutyFactory(users),
        GoogleCalendarFactory(users)
    ]
    events = []
    for factory in factories:
        events.extend(factory.generate())
    resources = [{"id": user, "title": user} for user in sorted(users)]
    write_data(resources, events)

if __name__ == '__main__':
    main()