# sheet-bot

required files:

`discord_token.txt`: one line text file containing discord bot token

`guilds.json`:

```
{
  "GUILD_ID": {
    "spreadsheet_id": "SPREADSHEET_ID",
    "sheet_name": "MAIN_MEMBER_SHEET",
    "gone_sheet_name": "GONE_MEMBER_SHEET",
    "sheet_id": 0,
    "id_col": "LETTER OF THE COLUMN CONTAINING IDs",
    "discord_col": "LETTER OF THE COLUMN CONTAINING DISCORD NAME+TAG"
  }
}
```

`credentials.json`: (Instructions)[https://developers.google.com/sheets/api/quickstart/python]

