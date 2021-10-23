# Discord-Music-Bot
Discord bot to play music from youtube in your discord server.

# Setup
## Dependencies
    - Python 3.5.3 or newer
    - discord.py
    - numpy
    - youtube-dl
    - asyncio
    - discord.ext
    - discord.utils
There is a requirements.txt file in the root of this repo. Doing ```pip install -r requirements.txt``` should install all the nessecary packages.

## Required Data
The API key for your discord bot is expected to be in a json file at ```Data Files/server_info.json```. The json is expected to have the following schema
```json
{
    "music_bot_api_key" : "YOUR API KEY"
}
```
