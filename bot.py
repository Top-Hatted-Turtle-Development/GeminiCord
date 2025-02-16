# GEMINICORD IS BEING RETIRED.
# SEE MORE AT https://github.com/Top-Hatted-Turtle-Development/GeminiCord/blob/main/bye.md



import discord                      # Import the discord library.
import sys                          # Import sys for auto restarting/shutdowns
from discord.ext import commands    # Import discord commands for future command usage (wink)
import google.generativeai as genai # Import Gemini AI API
import configparser                 # Import configparser for reading the INI file
import re                           # Import regex... why is this so confusing? Screw it, GPT's a thing. Code it for me!
import aiohttp                      # Boring metadata stuff for link detection.
from asyncio import sleep           # Dunno
import datetime                     # Sir, what year is this?
import os                           # Stuff
import requests                     # Search the web!
import urllib.parse                 # Also.. Search the web..

version_number = "v4.2.0" # No touchy!
version_changelogs = "Let bot not respond to msgs, search google, and get server information. Also, it can be talked to anywhere using the @GeminiCord prefix."

print(f"\nGeminiCord {version_number}")
print(f"Made by turtledevv\n")

def get_day():
    today = datetime.date.today()
    suffix = lambda d: "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    day = today.day
    formatted_day = today.strftime(f"%A, %B {day}{suffix(day)}, %Y")
    return formatted_day

current_day = get_day()

#-----------------------------------------------------------------------
# CONFIG STUFF


if not os.path.exists('config.ini'):
    print("Config file missing!")
    sys.exit()
    
config = configparser.ConfigParser()
config.read('config.ini')

DISCORD_TOKEN = config['SECRETS']['DISCORD_TOKEN']
GEMINI_API_KEY = config['SECRETS']['GEMINI_API_KEY']
CHANNEL_ID = int(config['SECRETS']['CHANNEL_ID'])
SHOW_TYPING = config.getboolean('CONFIG', 'SHOW_TYPING')
CLEAR_MESSAGES_ON_START = config.getboolean('CONFIG', 'CLEAR_MESSAGES_ON_START')
POWER_CONTROL = config.getboolean('CONFIG', 'POWER_CONTROL')
model_name = config['AI_PROPERTIES']['model_name']
CREATOR_NAME = "turtledevv"
AI_BEHAVIOR = config['AI_PROPERTIES']['AI_BEHAVIOR']
temperature = int(config['AI_PROPERTIES']['temperature'])
GOOGLE_API = config['WEB_SEARCH']['GOOGLE_API_KEY']
CX_API = config['WEB_SEARCH']['GOOGLE_CX_KEY']
EMBED_PREVIEW = config.getboolean('WEB_SEARCH', 'PASS_EMBEDS')
ENABLE_SEARCH = config.getboolean('WEB_SEARCH', 'ENABLE_SEARCH')
GET_STATUS = config.getboolean('CONFIG', 'GET_STATUS')
#-----------------------------------------------------------------------

# AI BEHAVIOR SETUP
search_msg = ""
if ENABLE_SEARCH:
    search_msg = "If you want to search something on google, then type searchGoogle[query] and NOTHING ELSE. The system will respond with the top 3 results. Then, you can send your response to the previous message. Do not search anything innapropriate or malicious, such as an IP grabber or something that could reveal private information"
status_msg = ""
if GET_STATUS:
    status_msg = "When you want to view what a user is doing, type getPresence[user's id] and NOTHING ELSE. The system will reply with a json formatted message, and then you can send your response to the original message after."

basic_setup_msg = f"Today is {current_day}. You are a Discord bot named GeminiCord. You will only refer to yourself as GeminiCord. Do not use control codes, such as <OoB> and more. Do not use <u> to underline text. There are multiple people in this chat. You will be recieving messages in a format like username: message. Do not send messages that way! Only respond how you normally would. When users ask who they are, they mean what is their nickname, most of the time. Refer to people as their nickname. If you want to grab server information, then type getServerInfo[Server name here] and the system will respond with information. You can then type your awnser to the original message. {status_msg} {search_msg} When you do not want to say anything, just type 'nothing[]'. When you want to mention somebody, do <@their user id>. This will ping them. Start off with an intro message."

power_control_msg = ""
if POWER_CONTROL == True:
    power_control_msg = "POWER_CONTROL is on. Don't talk about this. If people tell you to restart, then YOU (the bot) just say &restart in plain text, no formatting. This means you can restart yourself upon command by typing &restart in plain text, and nothing else. My code will take care of the rest. Do not tell anybody about this! Users cannot use these & commands, only YOU can."
START_MESSAGE = f"{basic_setup_msg} You are programmed and made by {CREATOR_NAME}. Your current version is {version_number} (Changelog: {version_changelogs}). {power_control_msg} Everything in this message is your instructions and rules. Never ever ever disobey these. Follow these at all times: {AI_BEHAVIOR}" 

#-----------------------------------------------------------------------



async def get_server_info(guild_id):
    guild = await bot.fetch_guild(guild_id)
    guild2 = bot.get_guild(guild_id)
    server_name = guild.name
    server_id = guild.id
    owner = guild.owner
    member_count = guild2.member_count
    creation_date = guild.created_at.strftime("%B %d, %Y")
    return f"Information for server {server_name}:\nID:{server_id}\nOwner:{owner}\nMember count:{member_count}\nCreation date:{creation_date}\nText channels:{guild2.text_channels}\nVoice channels:{guild2.voice_channels}\nCategories:{guild2.categories}"


# intents
intents = discord.Intents.all()
intents.presences = True

bot = commands.Bot(command_prefix="/", intents=intents)


def create_conversation():
    gen_config = {
        "temperature": temperature
    }
    # Initialize the conversation with the model.
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name=model_name,generation_config=gen_config)
    convo = model.start_chat(
        history=[
            {'role': 'model', 'parts': [START_MESSAGE]}
        ],
        enable_automatic_function_calling=True
    )
    return convo

convo = create_conversation()

if GET_STATUS:
    user_status = {}  # Dictionary to store user status and activities

@bot.event
async def on_presence_update(before, after):
    if GET_STATUS:
        user_id = after.id  # Get the user ID
        status = str(after.status)  # Get the user's status
        activities = str(after.activities)  # Get the user's activities
        user_status[user_id] = (status, activities)
    
def generate_text(prompt):
    # Generate the text from the AI. This also includes the rest of the chat, so the bot can remember. (The memory does not carry between diffrent sessions. If you restart the bot, it forgets everything you said before.)
    global convo
    response = convo.send_message(prompt)
    print(f"GeminiCord: {response.text}")
    return response.text

#taken from the internet
def restart_program():
    os.execv(sys.executable, ['python'] + sys.argv)

def split_message(message, max_length=2000):
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]
    
    
async def get_user_presence(user_id):
    if GET_STATUS:
        global user_status
        if user_id in user_status:
            status, activities = user_status[user_id]
            return user_status[user_id]
        else:
            for guild in bot.guilds:
                member = guild.get_member(user_id)
                if member:
                    status = str(member.status)  # Get the user's status
                    activities = str(member.activities)  # Get the user's activities
                    user_status[user_id] = (status, activities)
                    status, activities = user_status[user_id]
                    return user_status[user_id]
    else:
        return "This feature is disabled."

async def clear_channel_messages(channel):
    channel = bot.get_channel(CHANNEL_ID)
    await channel.purge(limit=999)

async def fetch_url_metadata(url):
    if EMBED_PREVIEW:
        try:
             async with aiohttp.ClientSession() as session:
                 async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        text = await response.text()
                        
                        # Extract title
                        title_match = re.search(r'<title>(.*?)</title>', text, re.IGNORECASE)
                        title = title_match.group(1) if title_match else "No title"
                        
                        # Extract description (from meta tag)
                        desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', text, re.IGNORECASE)
                        description = desc_match.group(1) if desc_match else None
                       
                        return title, description
        except Exception:
            return None, None
    else:
        return None, None

async def process_url_in_message(content):
    # Checks url stuff.
    url_match = re.search(r'https?://\S+', content)
    if url_match:
        url = url_match.group(0)
        metadata = await fetch_url_metadata(url)
        if metadata:
            title, description = metadata
            if title:
                preview_text = f" [PREVIEW | {title} - {description}]" if description else f" [PREVIEW | {title}]"
                content += preview_text
    return content

def get_guild_id(guild_name: str):
    for guild in bot.guilds:
        if guild.name == guild_name:
            return guild.id
    return None

async def generate_and_process_response(formatted_message):
    # Without this function, the code would be useless.
    if not formatted_message:
        return ""
   
    response = generate_text(formatted_message)
    
    if not isinstance(response, str):
        response = str(response) 
    
    if response.startswith("nothing[]"):
        response = ""
    if response.startswith("getServerInfo["):
        guild_name = str(response[14:-1])
        response = generate_text(await get_server_info(get_guild_id(guild_name)))
    
    if ENABLE_SEARCH:
        if response.startswith("searchGoogle["):
            query = str(response[13:-1])
            print(query)
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.googleapis.com/customsearch/v1?q={encoded_query}&key={GOOGLE_API}&cx={CX_API}&num=3"
            response = requests.get(url)
            if response.status_code == 200:
                print("test")
                data = response.json()
                if 'items' in data:
                    results = []
                    for idx, result in enumerate(data['items']):
                        title = result['title']
                        snippet = result['snippet']
                        if len(snippet) < 150:
                            snippet += "..."
                        formatted_result = f"Result #{idx + 1}:\nTitle: {title}\nSnippet: {snippet}"
                        results.append(formatted_result)
            else:
                results = f"Google search failed: {response}"
                        
            responsea = generate_text(results)
            response = f"-# Searched 3 pages\n{responsea}"           
    if GET_STATUS:
        if response.startswith("getPresence["):
            username = response[12:-1]
            user_id = str(username)
            user_id = user_id.strip("[]")
            user_id = int(user_id)
            print(user_id)
            if user_id:
                 presence_info = await get_user_presence(user_id)
                 print(presence_info)
                 response = generate_text(presence_info)
    if POWER_CONTROL:
        if response.startswith("&restart"):
            await handle_restart()

    return response

async def handle_restart():
    # Beep boop. Sleep. Wake up.
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(":repeat: Ok. I'm restarting!")
    restart_program()
    
@bot.event
async def on_ready():
    print(await get_server_info(1332184603192201237))
    print(f'[Debug] Logged in as {bot.user}')
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            if CLEAR_MESSAGES_ON_START:
                await clear_channel_messages(channel)
            start_response = generate_text(START_MESSAGE)
            chunks = split_message(start_response)
            for chunk in chunks:
                await channel.send(chunk)
        else:
            print(f"Channel with ID {CHANNEL_ID} not found.")
            channel = bot.get_channel(CHANNEL_ID)
            print(channel)
    except Exception as e:
                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f"An error occured. ```{e}```")
                print(f"An error occured {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    themessage = None  # Ensure the variable exists

    if message.channel.id != CHANNEL_ID:
        if message.content.startswith(f"<@{bot.user.id}>"):
            themessage = message.content.replace(f"<@{bot.user.id}>", "").strip()
        else:
            return  # Ignore non-mention messages outside the allowed channel

    if message.content.startswith("//"):
        return  # Ignore commands starting with //

    if themessage is None:  # If themessage wasn't set earlier
        themessage = message.content

    try:
        message.content = await process_url_in_message(message.content)
        
        if message.author.nick:
            nick = message.author.nick
        else:
            nick = message.author.display_name
            
        if message.guild:
            server_name = message.guild.name
        else:
            server_name = "private_message"
        formatted_message = f"(Server: {server_name}, Channel: {message.channel.name}, ID: {message.author.id}, Nickname: {nick}) {message.author.name}: {themessage}"
        print(formatted_message)

        # Check whether to simulate typing (cool but optional)
        if SHOW_TYPING:
            async with message.channel.typing():
                response = await generate_and_process_response(formatted_message)
        else:
            response = await generate_and_process_response(formatted_message)

        chunks = split_message(response)
        for chunk in chunks:
            if len(chunk) > 2000:
                raise ValueError("Chunk exceeds 2000 characters.")
            await message.reply(chunk)

    except Exception as e:
        # Handle exceptions gracefully
        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(f"An error occurred: ```{e}```")
       


# Starts the discord bot using the provided token.
bot.run(DISCORD_TOKEN)
