#!/usr/bin/env python3
# Based https://raw.githubusercontent.com/honzajavorek/honzajavorek.cz/b91bcadf4dba7e83a37d431b5d78103c4b7a267c/strava.py
# based on https://medium.com/swlh/using-python-to-connect-to-stravas-api-and-analyse-your-activities-dummies-guide-5f49727aac86

from datetime import timedelta, datetime
from getpass import getpass
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import os.path
import json
from pathlib import Path
from subprocess import run
from time import sleep
from threading import Thread
from urllib.parse import urlparse, parse_qs

from keyring import get_keyring, get_password
import requests

# MAC OS X only and you have to deal with it! (PRs welcome)
PRIVATE_FOLDER = Path(os.path.expanduser("~")) / "Library/Application Support/Weeknotes"
CONFIG_FILE = PRIVATE_FOLDER / "config.json"

APPLICATION_KEYRING_NAME = "blog.almad.weeknotes.strava"

ACTIVITIES_PER_PAGE = 50
ACTIVITIES_SCAN_MAX = 100

# we could copy&paste from the page as well, but whatever
ASSUMED_TOKEN_EXPIRATION = timedelta(hours=3)

# Should be dynamically allocated, but whatever
SERVER_PORT = 9999
SERVER_SHUTDOWN_TIMEOUT = 5


def store_tokens_from_response(client_id, response_json):
    keyring = get_keyring()
    keyring.set_password(
        APPLICATION_KEYRING_NAME,
        client_id + ".refresh_token",
        response_json["refresh_token"],
    )

    keyring.set_password(
        APPLICATION_KEYRING_NAME,
        client_id + ".access_token",
        json.dumps(
            {
                "token": response_json["access_token"],
                "expires_at": (
                    datetime.now() + timedelta(seconds=response_json["expires_in"])
                ).isoformat(),
            }
        ),
    )


def get_access_token_from_strava(client_id, client_secret):
    class ResponseStoringServer(SimpleHTTPRequestHandler):
        def do_GET(self):
            url_params = parse_qs(urlparse(self.path).query)
            code = url_params["code"][0]

            self.exchange_code(code)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                "<html><body>All OK, go back to console. <script>window.close('','_parent','');</script></body></html>".encode(
                    "utf-8"
                )
            )

        def exchange_code(self, oauth_code):
            response = requests.post(
                url="https://www.strava.com/oauth/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": oauth_code,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            # refresh_token, access_token, expires_in (in seconds)
            store_tokens_from_response(client_id, response.json())

    with HTTPServer(("", SERVER_PORT), ResponseStoringServer) as httpd:
        thread = Thread(target=httpd.serve_forever, daemon=True)
        thread.start()

        run(
            [
                "open",
                f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri=http://localhost:{SERVER_PORT}/exchange_token&approval_prompt=force&scope=activity:read_all",
            ]
        )

        while not get_password(APPLICATION_KEYRING_NAME, client_id + ".access_token"):
            sleep(1)

        httpd.shutdown()
        thread.join(timeout=5)


def get_refreshed_access_token(client_id, client_secret, refresh_token):
    response = requests.post(
        url="https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )
    response.raise_for_status()
    response_json = response.json()
    store_tokens_from_response(client_id, response_json)

    return response_json["access_token"]


def get_access_token(config):
    stored_access_token = get_password(
        APPLICATION_KEYRING_NAME, config["client_id"] + ".access_token"
    )

    if stored_access_token:
        stored_access_token = json.loads(stored_access_token)
        expire_at = datetime.fromisoformat(stored_access_token["expires_at"])
        if expire_at > datetime.now():
            return stored_access_token["token"]

    stored_refresh_token = get_password(
        APPLICATION_KEYRING_NAME, config["client_id"] + ".refresh_token"
    )

    if stored_refresh_token:
        return get_refreshed_access_token(
            config["client_id"], config["client_secret"], stored_refresh_token
        )

    token = get_access_token_from_strava(config["client_id"], config["client_secret"])
    return token


def get_config():
    keyring = get_keyring()
    try:
        config = json.loads(CONFIG_FILE.read_text())
        config["client_secret"] = keyring.get_password(
            APPLICATION_KEYRING_NAME, config["client_id"]
        )
    except FileNotFoundError:
        client_id = input("Enter client id: ").strip()
        client_secret = getpass("Enter client secret: ").strip()

        keyring.set_password(APPLICATION_KEYRING_NAME, client_id, client_secret)

        if not os.path.exists(PRIVATE_FOLDER):
            os.makedirs(PRIVATE_FOLDER)

        CONFIG_FILE.write_text(json.dumps(dict(client_id=client_id)))
        config = {"client_id": client_id, "client_secret": client_secret}

    return config


def get_strava_activities(access_token, since=None):
    activities = []
    page = 1
    qs = ""
    if since:
        qs = f"?after={str(int(since.timestamp()))}"

    while True:
        response = requests.get(
            f"https://www.strava.com/api/v3/activities{qs}",
            headers={"Authorization": f"Bearer {access_token}"},
            params=dict(page=page, per_page=ACTIVITIES_PER_PAGE),
        )
        response.raise_for_status()
        batch = response.json()
        activities.extend(batch)

        if len(activities) >= ACTIVITIES_SCAN_MAX:
            break
        elif len(batch) < ACTIVITIES_PER_PAGE:
            break
        else:
            page += 1

    return activities


def get_activities(since=None):
    config = get_config()
    access_token = get_access_token(config)
    activities = get_strava_activities(access_token, since)
    return activities


if __name__ == "__main__":
    activities = get_activities()
    if activities:
        print("According to Strava, you've moved.")
