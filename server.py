import base64
from flask import Flask
import json

import gspread
from google.oauth2 import service_account
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
with open(google_creds_file, 'r') as f:
    google_creds_data = json.loads(f.read())
google_creds = service_account.Credentials.from_service_account_info(google_creds_data)
scoped_creds = google_creds.with_scopes(['https://www.googleapis.com/auth/drive'])
google_file = gspread.authorize(scoped_creds)

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
    except requests.exception.RequestException as e:
        print(e.message)
        return 'Failed connecting to MySportsFeeds'

    #Occasionally, MySportsFeeds will error out, and not send JSON back as a result
    #In these circumstances, requests treats the request as successful, but the JSON decode will fail
    #This code catches this instance
    try:
        data = response.json()
    except json.decoder.JSONDecodeError as e:
        print(response.text, 'cannot be decoded as JSON')
        return 'Failed connecting to MySportsFeeds'

    #Write the results to the Google Sheet
    try:
        sheet_file = google_file.open('2020 Football Season')
    except gspread.exceptions.GSpreadException as e:
        #Gspread uses their own exception class, which doesn't inherit from BaseException
        #As a result, it doesn't have a "message" attribute
        #As a result, we're going to print e.__class__ to get an idea of what the issue is
        print(e.__class__)
        return 'Failed connecting to Google Sheets'

    sheet = sheet_file.worksheet('Automation Test Sheet')
    sheet.update('A1', 'Successfully wrote data to the sheet!')
    for game in data['games']:
        print(game)
    return data

if __name__ == '__main__':
    app.run(port = PORT)
