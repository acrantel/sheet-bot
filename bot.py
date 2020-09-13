import discord
from discord.utils import get

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import random
import pickle
import os.path
import json
import numpy as np

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

guilds = json.load(open('guilds.json'))

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

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    latest_channel = message.channel
    msg = message.content.lower().strip()
    if message.author == client.user or len(msg) == 0 or msg[0] != '.':
        return

    msg = msg[1:]

    # admin functionality
    print(message.author)
    if message.author.guild_permissions.administrator:
        split = msg.split(' ')
        if split[0] == 'all':
            await add_members_sheet(message.guild)
            await strike_members_sheet(message.guild)
        elif split[0] == 'add':
            await add_members_sheet(message.guild)
        elif split[0] == 'remove':
            await strike_members_sheet(message.guild)


@client.event
async def on_member_update(before, after):
    pass


@client.event
async def on_member_join(member):
    await add_members_sheet(member.guild)


@client.event
async def on_member_remove(member):
    await strike_members_sheet(member.guild)


async def respond(message, responses, emoji):
    response = responses[random.randint(0, len(responses))]
    print(response)
    await message.add_reaction(emoji)
    await message.channel.send(response)


def get_members_ids_sheet(guild):
    ''' Get a list of member ids from a guild's sheet '''
    guild_info = guilds[str(guild.id)]
    spreadsheet_id = guild_info['spreadsheet_id']
    sheet_name = guild_info['sheet_name']
    id_col = guild_info['id_col']

    id_range = '{}!{}2:{}'.format(sheet_name, id_col, id_col)
    id_col = sheets.values().get(spreadsheetId=spreadsheet_id, range=id_range).execute()

    return [(int(x[0]) if len(x) > 0 else 0) for x in id_col['values']]


async def add_members_sheet(guild):
    ''' Add missing members to the sheet '''
    print('adding new members to sheet for', guild.name)
    guild_info = guilds[str(guild.id)]
    spreadsheet_id = guild_info['spreadsheet_id']
    sheet_name = guild_info['sheet_name']
    id_col = guild_info['id_col']
    discord_col = guild_info['discord_col']

    members = guild.members
    # current members of server
    current_ids = [m.id for m in members]

    # members of server, as recorded in sheet
    ids_from_sheet = get_members_ids_sheet(guild)

    # find ids in current_ids that are not in ids_from_sheet
    new_ids = np.setdiff1d(current_ids, ids_from_sheet).tolist()
    new_discords = [str(guild.get_member(id)) for id in new_ids]

    print('new members:', new_ids)

    table_range = '{0}!A2:A'.format(sheet_name)
    values = format_values([(discord_col, new_discords)])
    
    value_range = {
        'range': table_range,
        'majorDimension': 'ROWS',
        'values': [format_values([(discord_col, new_discords[i]), (id_col, str(new_ids[i]))]) for i in range(len(new_ids))]
    }
    request = sheets.values().append(spreadsheetId=spreadsheet_id, range=table_range,
                                     valueInputOption='RAW', insertDataOption='INSERT_ROWS', body=value_range)
    response = request.execute()
    print(response)

def format_values(values):
    ''' Takes an array of tuples where each element is a (column_letter, value) tuple. 
        Returns a formatted values array ready to be sent to sheets '''
    sorted_vals = sorted(values, key=lambda tup: tup[0])
    res = ['?'] * (ord(sorted_vals[-1][0])-ord('A')+1)
    for tup in sorted_vals:
        res[ord(tup[0])-ord('A')] = tup[1]
    print(res)
    return res

async def strike_members_sheet(guild):
    ''' Update sheet with members who are no longer in the server '''
    print('updating sheet with members who are no longer in ', guild.name)

    guild_info = guilds[str(guild.id)]
    spreadsheet_id = guild_info['spreadsheet_id']
    sheet_name = guild_info['sheet_name']
    gone_sheet_name = guild_info['gone_sheet_name']
    sheet_id = guild_info['sheet_id']
    id_col = guild_info['id_col']

    members = guild.members
    # current members of server
    current_ids = [m.id for m in members]

    # members of server, as recorded in sheet
    ids_from_sheet = get_members_ids_sheet(guild)

    # ids in sheet that are not in current member ids
    gone_ids = np.setdiff1d(ids_from_sheet, current_ids).tolist()

    request_body = {
        'valueInputOption': 'RAW',
        'data': [{
            'range': '{}!A:A'.format(gone_sheet_name),
            'majorDimension': 'ROWS',
            'values': [[str(gone_ids[i])] for i in range(len(gone_ids))]
        }]
    }

    request = sheets.values().batchUpdate(
        spreadsheetId=spreadsheet_id, body=request_body)
    response = request.execute()
    print(response)

client.run(open('discord_token.txt').readline().strip())
