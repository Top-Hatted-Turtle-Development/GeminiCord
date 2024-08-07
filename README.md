# GeminiCord
GeminiCord is a discord bot that uses Google's Gemini AI to respond to messages from all users in a certain channel.

### Latest version: v3.1.2

## How to setup

### Preperation
1. Download the latest release of GeminiCord
2. Open up a text/code editor. (Such as VSCode or Notepad++)

### Discord Bot 
3. Create a discord bot and put the token in the code at the variable DISCORD_TOKEN (https://discord.com/developers) ![image](https://github.com/user-attachments/assets/d0eae4ed-a9f3-4da6-8ca9-03f1c737cf41)


### AI Setup
4. Create a new Google Cloud project. (https://console.cloud.google.com/home/dashboard) ![image](https://github.com/user-attachments/assets/8dd24414-0f73-4215-9b6d-9fb12103f447) ![image](https://github.com/user-attachments/assets/9f221b67-12a6-41e2-ba2a-f28dc88816ff)
5. Go to the Google AI Studio and create a new API key with your Google Cloud project. (https://aistudio.google.com/app/apikey) ![image](https://github.com/user-attachments/assets/8546e170-2cfd-4589-85d3-0e4fc31b31b0)
6. Copy your token and put it in the code where it says GEMINI_API_KEY ![image](https://github.com/user-attachments/assets/541e72a8-e00c-40c7-b5eb-d368e6c724ac)

### Config setup
7. Enable developer mode in discord, then rightclick on the channel you want the AI to be in, then click copy channel ID. Put the channel ID in the correct variable. ![image](https://github.com/user-attachments/assets/056552c3-9d06-44b3-9341-44ecbd8e613b)
8. SHOW_TYPING variable: I would recommend setting this to True, it just shows that the bot is typing while generating text.
9. CLEAR_MESSAGES_ON_START variable: If set to True, the bot will delete all messages in the channel when it starts up.
10. POWER_CONTROL variable: If set to True, the bot can restart itself when people ask it to.
11. model_name variable: I would highly recommend keeping this variable the way it is UNLESS you know exactly what you're doing.

### AI Behavior setup
12. Keep CREATOR_NAME the way it is
13. Change SERVER_NAME to the name of your server
14. Change SERVER_DESC to 1-3 sentences explaing what your server is
15. Change AI_BEHAVIOR to what you want the AI to do. (Default is AI tech support)

16. Now start it up!



 
