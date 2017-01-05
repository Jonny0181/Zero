import discord
from discord.ext import commands
from mods.utils import checks, settings
from mods.utils.dataIO import dataIO
from collections import deque, defaultdict
from mods.utils.chat_formatting import escape_mass_mentions, box
import os
import re
import logging
import asyncio

default_settings = {
    "mod-log"          : None
                   }

class ModError(Exception):
    pass


class UnauthorizedCaseEdit(ModError):
    pass


class CaseMessageNotFound(ModError):
    pass


class NoModLogChannel(ModError):
    pass
				   
class Moderation:
    def __init__(self, bot):
        self.bot = bot
        self.whitelist_list = dataIO.load_json("data/mod/whitelist.json")
        self.blacklist_list = dataIO.load_json("data/mod/blacklist.json")
        self.ignore_list = dataIO.load_json("data/mod/ignorelist.json")
        self.filter = dataIO.load_json("data/mod/filter.json")
        self.past_names = dataIO.load_json("data/mod/past_names.json")
        self.past_nicknames = dataIO.load_json("data/mod/past_nicknames.json")
        settings = dataIO.load_json("data/mod/settings.json")
        self.settings = defaultdict(lambda: default_settings.copy(), settings)
        self.cache = defaultdict(lambda: deque(maxlen=3))
        self.cases = dataIO.load_json("data/mod/modlog.json")
        self.last_case = defaultdict(dict)
        self._tmp_banned_cache = []
        perms_cache = dataIO.load_json("data/mod/perms_cache.json")
        self._perms_cache = defaultdict(dict, perms_cache)
		
    @commands.command(pass_context=True, no_pm=True)
    @checks.botcom()
    async def modlogtoggle(self, ctx, channel : discord.Channel=None):
        """Sets a channel as mod log
        Leaving the channel empty will deactivate it"""
        server = ctx.message.server
        if channel:
            self.settings[server.id]["mod-log"] = channel.id
            await self.bot.say(":+1: Mod logging channel set to {}"
                               "".format(channel.mention))
        else:
            if self.settings[server.id]["mod-log"] is None:
                await send_cmd_help(ctx)
                return
            self.settings[server.id]["mod-log"] = None
            await self.bot.say("I will no longer log bans/kicks. :+1:")
        dataIO.save_json("data/mod/settings.json", self.settings)
		
    @commands.command(pass_context=True, no_pm=True)
    @checks.botcom()
    async def modlogreset(self, ctx):
        """Resets modlog cases"""
        server = ctx.message.server
        self.cases[server.id] = {}
        dataIO.save_json("data/mod/modlog.json", self.cases)
        await self.bot.say("I have reset the cases for this server! :+1:.")
		
    @commands.command(no_pm=True, pass_context=True)
    @checks.botcom()
    async def ban(self, ctx, user: discord.Member, days: int=0):
        """Bans user and deletes last X days worth of messages.
        Minimum 0 days, maximum 7. Defaults to 0."""
        author = ctx.message.author
        server = author.server
        if days < 0 or days > 7:
            await self.bot.say("Invalid days. Must be between 0 and 7.")
            return
        try:
            self._tmp_banned_cache.append(user)
            await self.bot.ban(user, days)
            await self.new_case(server,
                                action="Ban!",
                                mod=author,
                                user=user)
            await self.bot.say("I have banned the user from the server, well done. Another mission accomplished.")
        except discord.errors.Forbidden:
            await self.bot.say("I'm sorry fam, but I just don't have the perms to do so. Or your luck is out and you don't have the perms to do so. :shrug:")
        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(1)
            self._tmp_banned_cache.remove(user)
			
    @commands.command(no_pm=True, pass_context=True)
    @checks.botcom()
    async def kick(self, ctx, user: discord.Member):
        """Kicks a user."""
        author = ctx.message.author
        server = author.server
        try:
            await self.bot.kick(user)
            logger.info("{}({}) kicked {}({})".format(
                author.name, author.id, user.name, user.id))
            await self.new_case(server,
                                action="Kick!}",
                                mod=author,
                                user=user)
            await self.bot.say("I have kicked the user from the server, well done. Another mission accomplished.")
        except discord.errors.Forbidden:
            await self.bot.say("I'm sorry fam, but I just don't have the perms to do so. Or your luck is out and you don't have the perms to do so. :shrug:")
        except Exception as e:
            print(e)
			
    @commands.command(pass_context=True, no_pm=True)
    @checks.botcom()
    async def prune(self, ctx, number: int):
        """Prunes messages from chat."""

        channel = ctx.message.channel
        author = ctx.message.author
        server = author.server
        is_bot = self.bot.user.bot
        has_permissions = channel.permissions_for(server.me).manage_messages

        to_delete = []

        if not has_permissions:
            await self.bot.say("I'm sorry fam, but I just don't have the perms to do so. :shrug:")
            return

        async for message in self.bot.logs_from(channel, limit=number+1):
            to_delete.append(message)

        if is_bot:
            await self.mass_purge(to_delete)
        else:
            await self.slow_deletion(to_delete)
			
    @commands.group(pass_context=True)
    @checks.botcom()
    async def editrole(self, ctx):
        """Edits roles settings"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @editrole.command(aliases=["color"], pass_context=True)
    async def colour(self, ctx, role: discord.Role, value: discord.Colour):
        """Edits a role's colour
        Use double quotes if the role contains spaces.
        Colour must be in hexadecimal format."""
        author = ctx.message.author
        try:
            await self.bot.edit_role(ctx.message.server, role, color=value)
            await self.bot.say("I have changed the role's color. :+1:")
        except discord.Forbidden:
            await self.bot.say("I'm sorry fam, but I just don't have the perms to do so. :shrug:")
        except Exception as e:
            print(e)
            await self.bot.say("Fam something just blew up in my face. :flushed:")

    @editrole.command(name="name", pass_context=True)
    @checks.botcom()
    async def edit_role_name(self, ctx, role: discord.Role, name: str):
        """Edits a role's name
        Use double quotes if the role or the name contain spaces."""
        if name == "":
            await self.bot.say("You need to specify a name bro. :face_palm:")
            return
        try:
            author = ctx.message.author
            old_name = role.name
            await self.bot.edit_role(ctx.message.server, role, name=name)
            await self.bot.say("I have changed the role's name. :+1:")
        except discord.Forbidden:
            await self.bot.say("I'm sorry fam, but I just don't have the perms to do so. :shrug:")
        except Exception as e:
            print(e)
            await self.bot.say("Fam something just blew up in my face. :flushed:")


    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await bot.send_message(ctx.message.channel, page)
        else:
            pages = bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await bot.send_message(ctx.message.channel, page)
				
    async def mass_purge(self, messages):
        while messages:
            if len(messages) > 1:
                await self.bot.delete_messages(messages[:100])
                messages = messages[100:]
            else:
                await self.bot.delete_message(messages[0])
                messages = []
            await asyncio.sleep(1.5)

    async def slow_deletion(self, messages):
        for message in messages:
            try:
                await self.bot.delete_message(message)
            except:
                pass
				
    async def new_case(self, server, *, action, mod=None, user, reason=None):
        channel = server.get_channel(self.settings[server.id]["mod-log"])
        if channel is None:
            return

        if server.id in self.cases:
            case_n = len(self.cases[server.id]) + 1
        else:
            case_n = 1

        case = {"case"         : case_n,
                "action"       : action,
                "user"         : user.name,
                "user_id"      : user.id,
                "reason"       : reason,
                "moderator"    : mod.name if mod is not None else None,
                "moderator_id" : mod.id if mod is not None else None}

        if server.id not in self.cases:
            self.cases[server.id] = {}

        tmp = case.copy()
        if case["reason"] is None:
            tmp["reason"] = "Type z!reason {} <reason> to add it".format(case_n)
        if case["moderator"] is None:
            tmp["moderator"] = "Unknown"
            tmp["moderator_id"] = "Nobody has claimed responsibility yet"

        case_msg = discord.Embed(description="**Case Number: {case}**".format(**tmp), colour=discord.Colour.red())
        case_msg.add_field(name="Action", value="{action}".format(**tmp))
        case_msg.add_field(name="User", value="{user}\n({user_id})".format(**tmp))
        case_msg.add_field(name="Moderator", value="{moderator}\n({moderator_id})".format(**tmp))
        case_msg.add_field(name="Reason", value="{reason}".format(**tmp))

        try:
            msg = await self.bot.send_message(channel, embed=case_msg)
        except:
            msg = None

        case["message"] = msg.id if msg is not None else None

        self.cases[server.id][str(case_n)] = case

        if mod:
            self.last_case[server.id][mod.id] = case_n

        dataIO.save_json("data/mod/modlog.json", self.cases)

    async def update_case(self, server, *, case, mod, reason):
        channel = server.get_channel(self.settings[server.id]["mod-log"])
        if channel is None:
            raise NoModLogChannel()

        case = str(case)
        case = self.cases[server.id][case]

        if case["moderator_id"] is not None:
            if case["moderator_id"] != mod.id:
                raise UnauthorizedCaseEdit()

        case["reason"] = reason
        case["moderator"] = mod.name
        case["moderator_id"] = mod.id

        case_msg = discord.Embed(description="**Case Number: {case}**".format(**case), colour=discord.Colour.green())
        case_msg.add_field(name="Action", value="{action}".format(**case))
        case_msg.add_field(name="User", value="{user}\n({user_id})".format(**case))
        case_msg.add_field(name="Moderator", value="{moderator}\n({moderator_id})".format(**case))
        case_msg.add_field(name="Reason", value="{reason}".format(**case))

        dataIO.save_json("data/mod/modlog.json", self.cases)

        msg = await self.bot.get_message(channel, case["message"])
        if msg:
            await self.bot.edit_message(msg, embed=case_msg)
        else:
            raise CaseMessageNotFound()
			
    async def on_member_ban(self, member):
        if member not in self._tmp_banned_cache:
            server = member.server
            await self.new_case(server,
                                user=member,
                                action="Ban!")

def check_folders():
    folders = ("data", "data/mod/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)


def check_files():
    ignore_list = {"SERVERS": [], "CHANNELS": []}

    files = {
        "blacklist.json"      : [],
        "whitelist.json"      : [],
        "ignorelist.json"     : ignore_list,
        "filter.json"         : {},
        "past_names.json"     : {},
        "past_nicknames.json" : {},
        "settings.json"       : {},
        "modlog.json"         : {},
        "perms_cache.json"    : {}
    }

    for filename, value in files.items():
        if not os.path.isfile("data/mod/{}".format(filename)):
            print("Creating empty {}".format(filename))
            dataIO.save_json("data/mod/{}".format(filename), value)

				
def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("red.mod")
    if logger.level == 0:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(
            filename='data/mod/mod.log', encoding='utf-8', mode='a')
        handler.setFormatter(
            logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    n = Moderation(bot)
    bot.add_cog(n)