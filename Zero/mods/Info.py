import discord
import random
import datetime
import time
from discord.ext import commands
wrap = "```py\n{}\n```"
starttime = time.time()
class Info:
    def __init__(self, bot):
	    self.bot = bot
		
    def fetch_joined_at(self, user, server):
        """Just a special case for someone special :^)"""
        if user.id == "96130341705637888" and server.id == "133049272517001216":
            return datetime.datetime(2016, 1, 10, 6, 8, 4, 443000)
        else:
            return user.joined_at
		
    @commands.command(pass_context=True, no_pm=True)
    async def serverinfo(self, ctx):
        """Shows server's informations"""
        server = ctx.message.server
        mfa_level = server.mfa_level
        vl = server.verification_level
        total = len([e.name for e in server.members if not e.bot])
        bots = len([e.name for e in server.members if e.bot])
        text_channels = len([x for x in server.channels
                             if x.type == discord.ChannelType.text])
        voice_channels = len(server.channels) - text_channels
        passed = (ctx.message.timestamp - server.created_at).days
        created_at = ("**Created {}. {} days ago.**"
                      "".format(server.created_at.strftime("%d %b %Y %H:%M"),
                                passed))

        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        x = -1
        emojis =  []
        while x < len([r for r in ctx.message.server.emojis]) -1:
            x = x + 1
            emojis.append("<:{}:{}>".format([r.name for r in ctx.message.server.emojis][x], [r.id for r in ctx.message.server.emojis][x]))

        data = discord.Embed(
            description=created_at,
            colour=discord.Colour(value=colour))
        data.add_field(name="Info", value=str("**Region:** {0.region}\n**Id:** {0.id}".format(server)))
        data.add_field(name="Users", value="**Humans:** {}\n**Bots:** {}".format(total, bots))
        data.add_field(name="Text Channels", value=text_channels)
        data.add_field(name="Voice Channels", value=voice_channels)
        data.add_field(name="Verification Level", value=vl)
        data.add_field(name="Require 2FA", value=bool(mfa_level))
        data.add_field(name="Default Channel", value=server.default_channel.mention)
        data.add_field(name="Roles", value=len(server.roles))
        data.set_footer(text="Owner: {}".format(str(server.owner)))

        if server.icon_url:
            data.set_author(name=server.name, url=server.icon_url)
            data.set_thumbnail(url=server.icon_url)
        else:
            data.set_author(name=server.name)
        if server.emojis:
            data.add_field(name="Emotes", value=" ".join(emojis))
        else:
            data.add_field(name="Emotes", value="None")

        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            await self.bot.say("Your server perm's are fucked. I need `embed links`.")
			
    @commands.command(pass_context=True, no_pm=True)
    async def userinfo(self, ctx, *, user: discord.Member=None):
        """Shows users's informations"""
        author = ctx.message.author
        server = ctx.message.server

        if not user:
            user = author

        roles = [x.name for x in user.roles if x.name != "@everyone"]

        joined_at = self.fetch_joined_at(user, server)
        since_created = (ctx.message.timestamp - user.created_at).days
        since_joined = (ctx.message.timestamp - joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        member_number = sorted(server.members,
                               key=lambda m: m.joined_at).index(user) + 1

        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

        game = "Chilling in {} status".format(user.status)

        if user.game is None:
            pass
        elif user.game.url is None:
            game = "Playing {}".format(user.game)
        else:
            game = "Streaming: [{}]({})".format(user.game, user.game.url)

        if roles:
            roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                       if x.name != "@everyone"].index)
            roles = ", ".join(roles)
        else:
            roles = "None"

        data = discord.Embed(description=game, colour=user.colour)
        data.add_field(name="Joined Discord on", value=created_on)
        data.add_field(name="Joined this server on", value=joined_on)
        data.add_field(name="Roles", value=roles)
        if author.voice_channel:
            data.add_field(name="Voice connected to", value="{}".format(author.voice_channel))
        else:
            data.add_field(name="Voice connected to", value="Not voice connected")
        data.set_footer(text="Member Number: {} | User ID:{}"
                             "".format(member_number, user.id))

        if user.avatar_url:
            name = str(user)
            name = " ~ ".join((name, user.nick)) if user.nick else name
            data.set_author(name=name, url=user.avatar_url)
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(name=user.name)

        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            await self.bot.say("Your server perm's are fucked. I need `embed links`.")
			
    @commands.command(pass_context=True)
    async def serveremotes(self, ctx):
        """ServerEmote List"""
        server = ctx.message.server
        
        list = [e for e in server.emojis if not e.managed]
        emoji = ''
        for emote in list:
            emoji += "<:{0.name}:{0.id}> ".format(emote)
        try:
            await self.bot.say(emoji)
        except:
            await self.bot.say("**This server has no fucking emotes??? What is this a ghost town ???**")
			
    @commands.command(pass_context=True)
    async def inrole(self, ctx, *, rolename):
        """Check members in the role specified."""
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        server = ctx.message.server
        message = ctx.message
        channel = ctx.message.channel
        await self.bot.send_typing(ctx.message.channel)
        therole = discord.utils.find(lambda r: r.name.lower() == rolename.lower(), ctx.message.server.roles)
        if therole is not None and len([m for m in server.members if therole in m.roles]) < 50:
            await asyncio.sleep(1) #taking time to retrieve the names
            server = ctx.message.server
            member = discord.Embed(description="**{1} users found in the {0} role.**\n".format(rolename, len([m for m in server.members if therole in m.roles])), colour=discord.Colour(value=colour))
            member.add_field(name="Users", value="\n".join(m.display_name for m in server.members if therole in m.roles))
            await self.bot.say(embed=member)
        elif len([m for m in server.members if therole in m.roles]) > 50:
            awaiter = await self.bot.say("Getting Member Names")
            await asyncio.sleep(1)
            await self.bot.edit_message(awaiter, " :raised_hand: Woah way too many people in **{0}** Role, **{1}** Members found\n".format(rolename,  len([m.mention for m in server.members if therole in m.roles])))
        else:
            embed=discord.Embed(description="**Role was not found**", colour=discord.Colour(value=colour))
            await self.bot.say(embed=embed)
			
    @commands.command()
    async def names(self, user : discord.Member):
        """Show previous names/nicknames of a user"""
        server = user.server
        names = self.past_names[user.id] if user.id in self.past_names else None
        try:
            nicks = self.past_nicknames[server.id][user.id]
            nicks = [escape_mass_mentions(nick) for nick in nicks]
        except:
            nicks = None
        msg = ""
        if names:
            names = [escape_mass_mentions(name) for name in names]
            msg += "**Past 20 names**:\n"
            msg += ", ".join(names)
        if nicks:
            if msg:
                msg += "\n\n"
            msg += "**Past 20 nicknames**:\n"
            msg += ", ".join(nicks)
        if msg:
            await self.bot.say(msg)
        else:
            await self.bot.say("That user doesn't have any recorded name or "
                               "nickname change.")
							   
    @commands.command(pass_context=True)
    async def mods(self, ctx):
        """Show's mods in the server."""
        colour = "".join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        server = ctx.message.server
        one = [e.mention for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.online]
        two = [e.mention for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.idle]
        three = [e.mention for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.dnd]
        four = [e.mention for e in server.members if e.permissions_in(ctx.message.channel).manage_messages and not e.bot and e.status == discord.Status.offline]
        embed = discord.Embed(description="Listing mods for this server.", colour=discord.Colour(value=colour))
        if one:
            embed.add_field(name="Online", value=":green_heart: {0}".format((" \n:green_heart: ".join(one)).replace("`", "")), inline=False)
        else:
            embed.add_field(name="Offline", value=":green_heart: None", inline=False)
        if two:
            embed.add_field(name="Idle", value=":yellow_heart: {0}".format((" \n:yellow_heart: ".join(two)).replace("`", "")), inline=False)
        else:
            embed.add_field(name="Idle", value=":yellow_heart: None", inline=False)
        if three:
            embed.add_field(name="Dnd", value=":heart: {0}".format((" \n:heart: ".join(three)).replace("`", "")), inline=False)
        else:
            embed.add_field(name="Dnd", value=":heart: None", inline=False)
        if four:
            embed.add_field(name="Offline", value=":black_heart: {0}".format((" \n:black_heart: ".join(four)).replace("`", "")), inline=False)
        else:
            embed.add_field(name="Offline", value=":black_heart: None", inline=False)
        if server.icon_url:
            embed.set_author(name=server.name, url=server.icon_url)
            embed.set_thumbnail(url=server.icon_url)
        else:
            embed.set_author(name=server.name)
        await self.bot.say(embed=embed)
        
    @commands.command(pass_context=True)
    async def admins(self, ctx):
        """Show's mods in the server."""
        colour = "".join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        server = ctx.message.server
        one = [e.mention for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.online]
        two = [e.mention for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.idle]
        three = [e.mention for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.dnd]
        four = [e.mention for e in server.members if e.permissions_in(ctx.message.channel).administrator and not e.bot and e.status == discord.Status.offline]
        embed = discord.Embed(description="Listing admins for this server.", colour=discord.Colour(value=colour))
        if one:
            embed.add_field(name="Online", value=":green_heart: {0}".format((" \n:green_heart: ".join(one)).replace("`", "")), inline=False)
        else:
            embed.add_field(name="Offline", value=":green_heart: None", inline=False)
        if two:
            embed.add_field(name="Idle", value=":yellow_heart: {0}".format((" \n:yellow_heart: ".join(two)).replace("`", "")), inline=False)
        else:
            embed.add_field(name="Idle", value=":yellow_heart: None", inline=False)
        if three:
            embed.add_field(name="Dnd", value=":heart: {0}".format((" \n:heart: ".join(three)).replace("`", "")), inline=False)
        else:
            embed.add_field(name="Dnd", value=":heart: None", inline=False)
        if four:
            embed.add_field(name="Offline", value=":black_heart: {0}".format((" \n:black_heart: ".join(four)).replace("`", "")), inline=False)
        else:
            embed.add_field(name="Offline", value=":black_heart: None", inline=False)
        if server.icon_url:
            embed.set_author(name=server.name, url=server.icon_url)
            embed.set_thumbnail(url=server.icon_url)
        else:
            embed.set_author(name=server.name)
        await self.bot.say(embed=embed)
		
    @commands.command(pass_context=True)
    async def uptime(self, ctx):
        """Shows how long the bot has been online."""
        try:
            if "<@" + ctx.message.author.id + ">" in open('mods/utils/txt/blacklist.txt').read():
                pass
            else:
                seconds = time.time() - starttime
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                w, d = divmod(d, 7)
                await self.bot.say("Zero has been up for %d Weeks," % (w) + " %d Days," % (d) + " %d Hours,"
                                   % (
                h) + " %d Minutes," % (m) + " and %d Seconds!" % (s))
        except Exception as e:
            await self.bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))
			
    @commands.command(pass_context=True)
    async def ping(self,ctx):
        """Pong."""
        channel = ctx.message.channel
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        t1 = time.perf_counter()
        await self.bot.send_typing(channel)
        t2 = time.perf_counter()
        em = discord.Embed(description="**Pong: {}ms! :ping_pong:**".format(round((t2-t1)*100)), colour=discord.Colour(value=colour))

        await self.bot.say(embed=em)
		
def setup(bot):
	bot.add_cog(Info(bot))