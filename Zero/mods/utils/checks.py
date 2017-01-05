from discord.ext import commands
import discord.utils
import json

def is_owner_check(message):
    return message.author.id == "146040787891781632"

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))

def botcom():
    def predicate(ctx):
        if ctx.message.channel.is_private:
            return False
        else:
            role = discord.utils.find(lambda r: r.name == "Bot Commander", ctx.message.server.roles)
            if role in ctx.message.author.roles:
                return True
            else:
                return False
    return commands.check(predicate)