from datetime import timedelta, datetime, date

from .pocket import get_pocket_recommendations
from .strava import get_activities

WEEKNOTE_TEMPLATE = """---
title: "Notes for week {week} of {year}"
date: "{today_str}"
lastmod: "{today_str}"
draft: false
tags: ["Weekly Notes"]
summary: "Random notes for week {week} of {year}"
---

## Random

* {activity_report}

## Recommended Readings From This Week

{readings}
"""


def get_activity_report_string():
    strava_activities = get_activities(since=datetime.now() - timedelta(days=7))

    walks = 0
    walked_meters = 0.0

    runs = 0
    ran_meters = 0.0

    rides = 0
    rode_meters = 0.0

    activities = 0
    activity_time_seconds = 0

    max_speed_mps = 0.0

    for a in strava_activities:
        activities += 1
        activity_time_seconds += a["moving_time"]

        if a["max_speed"] > max_speed_mps:
            max_speed_mps = a["max_speed"]

        # https://developers.strava.com/docs/reference/#api-models-ActivityType
        if a["type"] in ["Hike", "Walk", "Snowshoe"]:
            walks += 1
            walked_meters += a["distance"]

        elif a["type"] in ["Ride", "VirtualRide"]:
            rides += 1
            rode_meters += a["distance"]

        elif ["type"] in ["Run", "VirtualRun"]:
            runs += 1
            ran_meters += a["distance"]

    acts = []
    if walks > 0:
        acts.append(f"walked {round(walked_meters/1000)} km")
    if runs > 0:
        acts.append(f"ran {round(ran_meters/1000)} km")
    if rides > 0:
        acts.append(f"rode {round(rode_meters/1000)} km")

    sentence = "I relaxed in the past week. "
    if len(acts) == 1:
        sentence = f"I've {acts[0]}. "

    elif len(acts) == 2:
        sentence = f"I've {' and '.join(acts)}. "

    elif len(acts) > 2:
        sentence = f"I've {', '.join(acts[:-1])} and {acts[-1]}. "

    sentence += f"I've been active for {round(activity_time_seconds/60/60, 1)} hours during {activities} activities. This week's max speed was {round(max_speed_mps*3.6, 1)} km/h."

    return sentence


def get_readings_string():
    recommended_articles = get_pocket_recommendations()
    return "\n".join(
        "* [{title}]({url}): {pocket_comment}".format(**r) for r in recommended_articles
    )


def generate_weeknote(weeknote_path, today):
    activity_report = get_activity_report_string()
    readings = get_readings_string()

    YEAR = today.strftime("%Y")
    WEEK = today.strftime("%W")

    note = WEEKNOTE_TEMPLATE.format(
        week=WEEK,
        today_str=today.strftime("%Y-%m-%d"),
        year=YEAR,
        readings=readings,
        activity_report=activity_report,
    )

    weeknote_path.write_text(note)
