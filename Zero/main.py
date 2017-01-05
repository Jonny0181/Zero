from discord.ext import commands
import asyncio
import discord
import json
from random import choice as randchoice
from mods.utils import checks
import time
import os
import re
import datetime
import cleverbot


description = ''
bot = commands.Bot(command_prefix=("z!"), description=description)
starttime = time.time()
starttime2 = time.ctime(int(time.time()))
wrap = "```py\n{}\n```"
bot.pm_help = True


modules = [
    'mods.Fun',
	'mods.Info',
	'mods.Help',
	'mods.Moderation',
	'mods.Music',
]


@bot.event
async def on_message(message):

    await bot.process_commands(message)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    bot.remove_command('help')
    await bot.change_presence(game=discord.Game(name="z!help | z!invite"), status=discord.Status.dnd)
    print('------')
    for extension in modules:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))


class Default():
    def __init__(self, bot):
        self.bot = bot

@bot.command(hidden=True)
@checks.is_owner()
async def load(*, module: str):
    """Loads a part of the bot."""
    module = "mods." + module
    try:
        if module in modules:
            await bot.say("Alrigt, loading {}".format(module))
            bot.load_extension(module)
            await bot.say("Loading finished!")
        else:
            await bot.say("You can't load a module that doesn't exist!")
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))


@bot.command(hidden=True)
@checks.is_owner()
async def unload(*, module: str):
    """Unloads a part of the bot."""
    module = "mods." + module
    try:
        if module in modules:
            await bot.say("Oh, ok, unloading {}".format(module))
            bot.unload_extension(module)
            await bot.say("Unloading finished!")
        else:
            await bot.say("You can't unload a module that doesn't exist!")
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))


@bot.command(hidden=True)
@checks.is_owner()
async def reload(*, module: str):
    """Reloads a part of the bot."""
    module = "mods." + module
    try:
        if module in modules:
            await bot.say("Oh, ok, reloading {}".format(module))
            bot.unload_extension(module)
            bot.load_extension(module)
            await bot.say("Reloading finished!")
        else:
            await bot.say("You can't reload a module that doesn't exist!")
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))


@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def debug(ctx, *, code: str):
    """Evaluates code."""
    try:
        result = eval(code)
        if code.lower().startswith("print"):
            result
        elif asyncio.iscoroutine(result):
            await result
        else:
            await bot.say(wrap.format(result))
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))


@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def setname(ctx, *, name: str):
    """Sets the bots name."""
    try:
        await bot.edit_profile(username=name)
        await bot.say("Username successfully changed to `{}`".format(name))
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))


@checks.is_owner()
@bot.command(hidden=True, pass_context=True)
async def stream(ctx, game, url):
    await bot.change_status(game=discord.Game(url=url, type=1, name=game))
    await bot.say("Stream set")


@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def blacklist(ctx, user: str):
    """Blacklists a user from the bot."""
    try:
        if user == "<@151461608118419461>":
            await bot.say("You can't blacklist the owner!")
        elif user in open('mods/utils/txt/blacklist.txt').read():
            await bot.say("That user is already blacklisted!")
        else:
            with open("mods/utils/txt/blacklist.txt", "a") as f:
                f.write(user + "\n")
                await bot.say("Blacklisted that user!")
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))


@bot.command(hidden=True, pass_context=True)
@checks.is_owner()
async def unblacklist(ctx, user: str):
    """Unblacklists a user from the bot."""
    try:
        if len(set(ctx.message.mentions)) > 0:
            if user == "<@151461608118419461>":
                await bot.say("You can't unblacklist the owner!")
            elif user in open('mods/utils/txt/blacklist.txt').read():
                fin = open('mods/utils/txt/blacklist.txt', 'r')
                fout = open('mods/utils/txt/blacklist.txt', 'w')
                for line in fin:
                    for word in delete_list:
                        line = line.replace(word, "")
                    fout.write(line)
                fin.close()
                fout.close()
                await bot.say("Unblacklisted that user!")
            else:
                await bot.say("That user isn't blacklisted!")
        else:
            await bot.say("You have to mention someone!")
    except Exception as e:
        await bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))


bot.add_cog(Default(bot))

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(bot.login("MjY2NTYxNzY3ODU2MDEzMzEy.C0_egg.sDlILYMVzHzg97ZhCcV7lZBzl6U"))
    loop.run_until_complete(bot.connect())
except Exception:
    loop.run_until_complete(os.system("main.py"))
finally:
    loop.close()
