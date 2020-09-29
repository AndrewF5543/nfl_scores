import base64
from flask import Flask
import json

import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.client import SignedJwtAssertionCredentials
import requests

PORT = 3435
MSF_BASE_ENDPOINT = 'https://scrambled-api.mysportsfeeds.com/'

#Build out the MySportsFeeds authentication header
keyfile = 'keys.json'
with open(keyfile, 'r') as f:
    key_data = json.loads(f.read())
msf_api_key = key_data['MySportsFeeds']
msf_auth_str = msf_api_key + ':MYSPORTSFEEDS'
msf_auth_b64 = base64.b64encode(msf_auth_str.encode('utf-8'))
MSF_AUTH_HEADER = 'Basic ' + msf_auth_b64.decode('ascii')

#Authenticate with Google Sheets
google_creds_file = 'gspread_creds.json'
with open(google_creds_file, 'r') as data:
    google_creds_data = json.loads(f.read())
scope = ['https://spreadsheets.google.com/feeds']
google_creds = SignedJwtAssertionCredentials(google_creds_data['client_email'], google_creds_data['private_key'].encode(), scope)
google_file = gspread.authorize(google_creds)

app = Flask(__name__)

@app.route('/')
def hello_world():
    return('Hello, world!')

@app.route('/msf_test_request')
def basic_msf_request():
    url = MSF_BASE_ENDPOINT
    headers = {'Authorization': MSF_AUTH_HEADER}
    response = requests.get(url, headers = headers, timeout = 30)
    return response.text

@app.route('/games')
def get_games():
    url = MSF_BASE_ENDPOINT + '/v2.1/pull/nfl/2020-2021-regular/week/1/games.json'
    headers = {'Authorization': MSF_AUTH_HEADER}
    try:
        response = requests.get(url, headers = headers, timeout = 30)
    except requests.exception.RequestException:
        return 'HTTP response failed'

    data = response.json()

    #Write the results to the Google Sheet
    sheet = google_file.open('2020 Football Season').testsheet
    sheet.update('A1', 'Hello, and welcome to Gillette Stadium!')
    for game in data['games']:
        print(game)
    return data

if __name__ == '__main__':
    app.run(port = PORT)
