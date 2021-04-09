from datetime import timedelta, datetime, date

from .pocket import get_pocket_recommendations
from .strava import get_activities

WEEKNOTE_TEMPLATE = """
---
title: "Notes for Week {week}"
date: "{today_str}"
lastmod: "{today_str}"
draft: false
tags: ["weekly-notes"]
summary: "Random notes for week {week} of {year}"
---

## Random

* {activity_report}

## Recommended Readings From This Week

{readings}
"""

TODAY = date.today()
YEAR = TODAY.strftime("%Y")
WEEK = TODAY.strftime("%W")


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

    for a in strava_activities:
        activities += 1
        activity_time_seconds += a["elapsed_time"]

        # https://developers.strava.com/docs/reference/#api-models-ActivityType
        if a["type"] in ["Hike", "Walk", "Snowshoe"]:
            walks += 1
            walked_meters += a["distance"]

        elif ["type"] in ["Ride", "VirtualRide"]:
            rides += 1
            rode_meters += a["distance"]

        elif ["type"] in ["Run", "VirtualRun"]:
            runs += 1
            ran_meters += a["distance"]

    acts = []
    if walks > 0:
        acts.append(f"walked {round(walked_meters/1000)}km")
    if runs > 0:
        acts.append(f"ran {round(ran_meters/1000)}km")
    if rides > 0:
        acts.append(f"rode {round(rode_meters/1000)}km")

    sentence = "I relaxed in the past week. "
    if len(acts) == 1:
        sentence = f"I {acts[0]}. "

    elif len(acts) == 2:
        sentence = f"I {acts.join(' and ')}. "

    elif len(acts) > 2:
        sentence = f"I {acts[:-1].join(', ')} and {acts[-1]}. "

    sentence += f"I moved for {round(activity_time_seconds/60/60, 1)} hours during {activities} activities."

    return sentence


def get_readings_string():
    recommended_articles = get_pocket_recommendations()
    return "\n".join(
        "* [{title}]({url}): {pocket_comment}".format(**r) for r in recommended_articles
    )


def generate_weeknote(weeknote_path):
    activity_report = get_activity_report_string()
    readings = get_readings_string()

    WEEKNOTE_TEMPLATE.format(
        week=WEEK,
        today_str=TODAY.strftime("%Y-%m-%d"),
        year=YEAR,
        readings=readings,
        activity_report=activity_report,
    )
