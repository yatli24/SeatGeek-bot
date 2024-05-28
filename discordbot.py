import os
from random import randint
import time
import discord
from discord.ext import commands
from discord import Message, Client, Intents
import price_tracker_script
import image_recognition_script


client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Bot's token
token = 'token'


# Initiate bot
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running.')
    print("____________________________")


@client.command(name="roll")
async def hello(ctx):
    var = randint(1, 6)
    if var < 4:
        response = f'{var}, Below 4, Unlucky.'
    elif var == 4 or var == 5:
        response = f'{var}, 4 or 5, Sorta Lucky'
    else:
        response = f'{var}, 6! So Lucky!'
    await ctx.send(response)


@client.command(name="speak")
async def speak(ctx, user_input):
    lowered: str = user_input.lower()
    if lowered == '':
        response = 'Speak up please!'
    elif 'hello' in lowered:
        response = 'Hello'
    elif 'how are you' in lowered:
        response = 'Doing Fine, how are you?'
    elif 'bye' in lowered:
        response = 'Talk to you later!'
    else:
        response = 'Say something like hello/how are you/bye'
    await ctx.send(response)


@client.command(name='use')
async def use(ctx, user_input):
    lowered: str = user_input.lower()
    await ctx.send(f'Use {lowered} in a sentence.')

@client.command(name='track')
async def track(ctx, user_input):
    price_tracker_script.track()
    price_tracker_script.plot_stats()
    await ctx.send(f'Loading...')

@client.command(name='reccommend')
async def track(ctx, user_input):
    price_tracker_script.plot_stats()
    await ctx.send(f'Loading...')

@client.command(name='discuss')
async def discuss(ctx, *user_input, name='Anonymous'):
    empty = ['']
    if (user_input in empty) or (len(user_input) < 3):
        await ctx.channel.purge(limit=1)
        # set the sent bot message as msg, sleep for 3 seconds, then delete the bot's own message
        msg = await ctx.send(f"{ctx.message.author.mention}, Please input a discussion question/topic/answer.")
        time.sleep(3)
        await msg.delete()
    else:
        # find out how to get the user to set their own desired channel
        channel_id = 1229995535696396329
        channel = client.get_channel(channel_id)
        string = (" ").join(user_input)
        await channel.send(f'{string}\n-Sent by {name}')
        await ctx.channel.purge(limit=1)
        return


@client.command(aliases=['purge'])
async def prune(ctx, user_int):
    if int(user_int) > 26:
        await ctx.channel.purge(limit=1)
        msg = await ctx.send(f"{ctx.message.author.mention}, I cannot delete more than 25 messages.")
        time.sleep(3)
        await msg.delete()
    else:
        # this prunes the user's !prune message as well as user_int amount of messages
        await ctx.channel.purge(limit=int(user_int) + 1)
        msg = await ctx.send(f"{ctx.message.author.mention} Cleared {user_int} messages")
        time.sleep(3)
        await msg.delete()

@client.command(name='helpme')
async def helpme(ctx):
    await ctx.send("List of commands:\n\n"
                   "roll - rolls a 6 sided die\n"
                   "Usage: !roll\n\n"
                   "speak - speak to the bot\n"
                   "Usage: !speak [Enter hello/bye]\n\n"
                   "use - uses a word in a sentence\n"
                   "Usage: !use [Enter word here]\n\n"
                   "discuss - sends messages anonymously to the discussion chat\n"
                   "Usage: !discuss [Enter text here]\n\n"
                   "prune - prunes x above messages\n"
                   "Usage: !prune 10\n\n")


def main() -> None:
    client.run(token)


if __name__ == '__main__':
    main()
