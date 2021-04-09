from datetime import date, timedelta
from urllib.request import urlopen

from pocket_recommendations import parse

POCKET_USERNAME = "Almad"


def get_pocket_recommendations(recommended_days=6):
    """
    Return recommended articles for the last reported_days.
    I am using 6 days instead of 7 as I am running this on Sunday evening,
    and want to avoid having Sunday shares twice.
    This means losing shares between generating this and midnight,
    which I am fine with.
    """

    with urlopen(f"https://www.getpocket.com/@{POCKET_USERNAME}") as res:
        html = res.read()

    items = parse(html, today=date.today())
    news = filter(
        lambda i: i["pocket_recommended_at"]
        >= (date.today() - timedelta(days=recommended_days)),
        items,
    )

    return news
