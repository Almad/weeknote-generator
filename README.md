# Weekly Notes Generator

This package is used to generate [weekly notes on Almad's Changelog](https://almad.blog/tags/weekly-notes/). 

* Scrape [Strava](https://www.strava.com) for activities summary while handling tokens responsibly
* Scrape [Pocket](https://getpocket.com/) for recommended articles
* Generate nice [CommonMark](https://commonmark.org/) skeleton for Hugo blogpost

If run between Monday and Friday, it acts as if it's last Sunday. 

## Runtime Requirements

* Correct username for Pocket set in `pocket.py`
* Register your own API application [in Strava API page](https://www.strava.com/settings/api)
    * `Category` is `Data importer`
    * `Authorization Callback Domain` is `localhost`
    * Website is your github fork, I guess
* During the first run, when you do the OAuth2 authorization dance with Strava, hard-coded port `9999` must be free

## Package Installation 

I have intentionally not published the package to PyPI. Fork and adjust as you see fit; defaults are in code and not in config files etc.

For proper build check:

* `python3 -m pip install --upgrade build`
* `python3 -m build`
* `pipenv install dist/almad_weekly_notes-0.0.1-py3-none-any.whl`

Alternatively just

* `pip install .`

You can then use `generate-weeknotes` command. If you want to generate weeknotes retrospectively, you can use `WEEK=week_number` environment variable. 

If you have installed this inside a virtual environment and want to use it outside of it, the easiest way is to just add an alias into your `~/.zshrc`

    * alias generate-weekote=~/path/to/virtualenv/bin/generate-weeknote
