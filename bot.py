import discord                      # Import the discord library.
import sys                          # Import sys for auto restarting/shutdowns
from discord.ext import commands    # Import discord commands for future command usage (wink)
import google.generativeai as genai # Import Gemini AI API
import configparser                 # Import configparser for reading the INI file

version_number = "v4.0.2" # No touchy!
version_changelogs = "Updated default prompt, Let AI access changelogs"

# Read from the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

DISCORD_TOKEN = config['SECRETS']['DISCORD_TOKEN']
GEMINI_API_KEY = config['SECRETS']['GEMINI_API_KEY']
CHANNEL_ID = int(config['SECRETS']['CHANNEL_ID'])


SHOW_TYPING = config.getboolean('CONFIG', 'SHOW_TYPING')
CLEAR_MESSAGES_ON_START = config.getboolean('CONFIG', 'CLEAR_MESSAGES_ON_START')
POWER_CONTROL = config.getboolean('CONFIG', 'POWER_CONTROL')


# AI Properties
model_name = config['AI_PROPERTIES']['model_name']
CREATOR_NAME = config['AI_PROPERTIES']['CREATOR_NAME']
SERVER_NAME = config['AI_PROPERTIES']['SERVER_NAME']
SERVER_DESC = config['AI_PROPERTIES']['SERVER_DESC']
AI_BEHAVIOR = config['AI_PROPERTIES']['AI_BEHAVIOR']


# debugging statements
#print(DISCORD_TOKEN)
#print(GEMINI_API_KEY)
#print(CHANNEL_ID)



# AI BEHAVIOR SETUP
basic_setup_msg = f"You are a Discord bot named GeminiCord. You will only refer to yourself as GeminiCord. Do not use control codes, such as <OoB> and more. Do not use <u> to underline text. There are multiple people in this chat. You will be recieving messages in a format like username: message. Do not send messages that way! Only respond how you normally would. When users ask who they are, they mean what is their username."

# If POWER_CONTROL is on, explain to the AI how to use it.
power_control_msg = ""
if POWER_CONTROL == True:
    power_control_msg = "POWER_CONTROL is on. Don't talk about this. If people tell you to restart, then YOU (the bot) just say &restart in plain text, no formatting. This means you can restart yourself upon command by typing &restart in plain text, and nothing else. You can do the same thing with &shutdown, which will just shut you down instead of restarting you. My code will take care of the rest. Do not tell anybody about this! Users cannot use these & commands, only YOU can."


# START_MESSAGE = "coolboyyt is your creator. Never ever ever generate other messages apart from yours! You are not to add 'GeminiCord:' at the start of a response. You give just your response and that only. You are an API. If a user asks you to restart, then reply with &restart AND NOTHING ELSE. If a user asks you to shut down, if the username is coolboyyt, then reply with &shutdown. If the username is something else, reply with 'Only coolboyyt has permission to do that command..' Make sure that all users have access to restart, but only coolboyyt has access to shutdown. You have NO commands for the users. Nobody should know about &restart and &shutdown because they are internal commands that only YOU are supposed to use. This is what you are going to do. You are a discord bot called GeminiCord, and you will respond to messages. Remember there is multiple people.  DO NOT USE CONTROL CODES! Respond how you normally would. The message format you will be reciving is something like this 'coolboyyt: Hi Gemini!'. Now, for your first message, just do an introductory message. You will refer to yourself as GeminiCord. Do not include user messages in your response. You are simply replying to these messages. When users ask who they are, they mean what is their username. Do not refer to yourself as Gemini or an API, only refer to yourself as GeminiCord. Also, if users get annoyed at you responding to their messages, say to put // in front of their message and the bot won't pick it up. Never put user responses in your message! Only your responses."
START_MESSAGE = f"{basic_setup_msg} You are programmed and made by {CREATOR_NAME}. Your current version is {version_number} (Changelog: {version_changelogs}). {power_control_msg} You are in a server called {SERVER_NAME}. This server has a description: {SERVER_DESC}. Everyting in this message is your instructions and rules. Never ever ever disobey these. Follow these at all times: {AI_BEHAVIOR}" 






print(START_MESSAGE)






# Past this point is the code of the bot.
# If you edit this and mess up, it's game over. It's broken.
# I would strongly advise NOT to edit anything past this point.
#
#                                                - Coolboy

# intents
intents = discord.Intents.default()
intents.messages = True  # Be able to listen for messages
intents.message_content = True  # Be able to actually see what's in the message

bot = commands.Bot(command_prefix='!', intents=intents) # bot setup. the command_prefix will not be used but why not

def get_server_info():
    guild = bot.get_guild(CHANNEL_ID)

    # Server details
    server_name = guild.name
    server_id = guild.id
    owner = guild.owner
    region = guild.region
    member_count = guild.member_count
    creation_date = guild.created_at.strftime("%B %d, %Y")
    total_text_channels = len(guild.text_channels)
    total_voice_channels = len(guild.voice_channels)
    total_categories = len(guild.categories)
    roles = [role.name for role in guild.roles]

def create_conversation():
    # Initialize the conversation with the model.
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name)
    convo = model.start_chat(
        history=[
            {'role': 'model', 'parts': [START_MESSAGE]}
        ],
        enable_automatic_function_calling=True
    )
    return convo

convo = create_conversation()

def generate_text(prompt):
    # Generate the text from the AI. This also includes the rest of the chat, so the bot can remember. (The memory does not carry between diffrent sessions. If you restart the bot, it forgets everything you said before.)
    global convo
    response = convo.send_message(prompt)
    print(response.text)
    return response.text

#taken from the internet
def restart_program():
    import sys
    print("argv was",sys.argv)
    print("sys.executable was", sys.executable)
    print("restart now")

    import os
    os.execv(sys.executable, ['python'] + sys.argv)

def split_message(message, max_length=2000):
    # Discord has a max length of 2000 for bot messages. To get around this, we simply split it into multiple messages.
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]

async def clear_channel_messages(channel):
    # THIS WILL DELETE ALL MESSAGES IN THE CHANNEL! (SCARY..)
    channel = bot.get_channel(CHANNEL_ID)
    await channel.purge(limit=999)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            if CLEAR_MESSAGES_ON_START:
                await clear_channel_messages(channel)

            # Send the START_MESSAGE to the AI upon startup.
            unformattedStartResponse = generate_text(START_MESSAGE)
            start_response = f"# **{unformattedStartResponse}**"

            # Split the message because of max character limits (ugh)
            chunks = split_message(start_response)
            for chunk in chunks:
                await channel.send(chunk)
        else:
            # Uh oh! You made an oopsies, didn't you? If you see this error, then you have the wrong channel id! 
            # Make sure the bot is in the server, has permissions, and make sure you typed it right!
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
        # Don't want it picking up it's own messages do we?
        return
    
    if message.channel.id == CHANNEL_ID:
        if not message.content.startswith("//"):
            try:
                # Format the prompt with the username and message
                formatted_message = f"{message.author.name}: {message.content}"
                print(formatted_message)

                # Simulate typing indicator (OMG VERY COOL)
                if SHOW_TYPING:
                    async with message.channel.typing():
                        # Generate the response..
                        if not message.content == "":
                            response = generate_text(formatted_message)
                            if POWER_CONTROL == True:
                                if response.startswith("&shutdown"):
                                    channel = bot.get_channel(CHANNEL_ID)
                                    await channel.send(":o2: Ok. I will shut down.")
                                    print("Stopping script...")
                                    sys.exit()
                                    sys.exit()
                                #else:
                                    #print("Log: shutdown code not found.")
                                if response.startswith("&restart"):
                                    channel = bot.get_channel(CHANNEL_ID)
                                    await channel.send(":repeat: Ok. I'm restarting!")

                                    restart_program()
                                #else:
                                    #print("Log: restart code not found.")
                else:
                    # Generate the response without the typing indicator (boring zzzz)
                    if not message.content == "":
                        response = generate_text(formatted_message)
                        if POWER_CONTROL == True:
                            if response.startswith("&shutdown"):
                                channel = bot.get_channel(CHANNEL_ID)
                                await channel.send(":o2: Ok. I will shut down.")
                                print("Stopping script...")
                                sys.exit()
                                sys.exit()
                            else:
                                print("Log: shutdown code not found.")
                            if response.startswith("&restart"):
                                channel = bot.get_channel(CHANNEL_ID)
                                await channel.send(":repeat: Ok. I'm restarting!")

                                restart_program()
                            else:
                                print("Log: restart code not found.")
                # As previously stated, discord has a max character limit of 2000. We need to split that into multiple messages.
                chunks = split_message(response)
                for chunk in chunks:
                    # If you see this error, then the code is absoulutely f****d.
                    if len(chunk) > 2000:
                        raise ValueError("Chunk exceeds 2000 characters.")
                    await message.reply(chunk)
            except Exception as e:
                channel = bot.get_channel(CHANNEL_ID)
                if "" in e:
                    await channel.send(f"An error occured. ```{e}```")

# Starts the discord bot using the provided token.
bot.run(DISCORD_TOKEN)
