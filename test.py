
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import random
import pickle
import os.path
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

guilds = json.load(open('./guilds.json'))

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)

sheets = service.spreadsheets()

info = guilds['710932856251351111']

id_col = sheets.values().get(spreadsheetId=info['sheet_id'], range='{}!{}2:{}'.format(info['sheet_name'], info['id_col'], info['id_col'])).execute()
discord_col = sheets.values().get(spreadsheetId=info['sheet_id'], range='{}!{}2:{}'.format(info['sheet_name'], info['discord_col'], info['discord_col'])).execute()

print(id_col)
print(discord_col)