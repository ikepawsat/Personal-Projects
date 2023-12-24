#Author: Ike Pawsat - ike.pawsat@gmail.com
#Will not publish .env file with this because it contains token.

import os
import discord
import json
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()
intents = discord.Intents.all()
intents.voice_states = True
intents.members = True
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD') #This is conneected to my server to check it works.
if TOKEN is None:
    print("DISCORD_TOKEN is not set in the environment.")
    exit()

bot = commands.Bot(command_prefix='!', intents = intents)
isTTS = True

@bot.event # Lets server know everything operational
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    print("------")

def load_channel_config():
    try:
        with open('channel_config.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None

def save_channel_config(channel_id):
    config = {'welcome_channel_id': channel_id}
    with open('channel_config.json', 'w') as file:
        json.dump(config, file)

@bot.event # Happens when member joins
async def on_member_join(member):
    channel_config = load_channel_config()

    if channel_config and 'welcome_channel_id' in channel_config:
        channel_id = int(channel_config['welcome_channel_id'])
        channel = member.guild.get_channel(channel_id)

        if channel:
            welcome_message = f"Welcome {member.mention} to the server! Use !guide for helpful commands!"
            await channel.send(welcome_message)

@bot.event # TTS message announcing the member who joined the voice channel
async def on_voice_state_update(member, before, after):
    if isTTS:
        if after.channel and after.channel != before.channel:
            tts_message = f"{member.display_name} has joined the voice channel."
            await speak_in_channel(after.channel, tts_message)
            print(f" {member.display_name} joined a channel: {after}")

async def speak_in_channel(voice_channel, message):
    if discord.utils.get(bot.voice_clients, guild=voice_channel.guild):
        print("Bot is already connected to a voice channel.")
        return

    vc = await voice_channel.connect()

    try: #Saves message as mp3 and then plays it
        tts = gTTS(message, lang='en')
        tts.save('tts_message.mp3')
        vc.play(discord.FFmpegPCMAudio('tts_message.mp3'), after=lambda e: print('done', e))
        while vc.is_playing():
            await asyncio.sleep(1)

    finally:
        await vc.disconnect()

@bot.command() # Sets channel for welcome messages
async def set_welcome_channel(ctx):
    channel_id = ctx.channel.id
    save_channel_config(channel_id)
    await ctx.send(f"Welcome channel set to {ctx.channel.mention}.")

@bot.command() # Test for TTS Functionality
async def test_tts(ctx):
    tts_message = "This is a test TTS message."
    try:
        await ctx.send(tts_message, tts = True)
    except discord.Forbidden as e:
        print(f"Missing Permissions: {e}")
        await ctx.send("I don't have the necessary permissions to send TTS messages.")
    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.send("An error occurred while sending the TTS message.")

@bot.command() # Little guide for the users
async def guide(ctx):
    message = (
        "Here is a guide for using the bot:\n"
        "When a person joins voice chat, a TTS message will read their name out loud.\n"
        "If you would like to disable this feature, simply use the command !disableTTS.\n"
        "You can re-enable it with !enableTTS. You can use !test_tts to confirm its working.\n"
        "Use !nickname @(user) (new_nickname) to change someones nickname and announce it. (If nothing prints or changes you are probably spelling name wrong...)\n"
        "The bot will also send a message when people join the server!\n Use !set_welcome_channel to change it."
    )
    await ctx.send(message)

@bot.command() # Disables TTS
async def disableTTS(ctx):
    global isTTS
    isTTS = False
    message = "TTS has been disabled."
    await ctx.send(message)

@bot.command() # Enables TTS
async def enableTTS(ctx):
    global isTTS
    isTTS = True
    message = "TTS has been enabled."
    await ctx.send(message)

@bot.command()  # Command to change nickname and announce it
async def nickname(ctx, member: discord.Member, new_nickname: str):
    try:
        await member.edit(nick = new_nickname)
        await ctx.send(f"Nickname of {member.mention} changed to {new_nickname}!", tts=True)
    except discord.Forbidden as e:
        print(f"Missing Permissions: {e}")
        await ctx.send("I don't have the necessary permissions to change nicknames.\n "
                       "A common error is the bot cannot change nicknames of someone with higher role.")
    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.send("An error occurred while changing the nickname.")

if __name__ == '__main__':
    bot.run(TOKEN)

#Thank you!
