***NFL Scores Server***

This is a simple web server that will consume NFL game and score data, and write it to a Google sheet.

For now, it requires an active GET call to the /games route to generate data, and write it to the sheet; in the future, this will instead become a passive process that listens to a webhook instead

USAGE:

*Recommended*: Set up a Python3 virtual environment for the server

Install the requirements with `pip3 install -r requirements.txt`
You'll need a copy of `keys.json` (This includes API keys for NFL-related resources) and `gspread_creds.json` (This includes authentication data for the Google Sheet) to run the server

Start the server with `python3 server.py`. When the server starts, it will listen on port 3435 for incoming requests

Good luck, and go Patriots!
