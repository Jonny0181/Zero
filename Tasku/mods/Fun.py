import os
import asyncio
from discord.ext import commands
import io
import discord.utils
import json
import aiohttp
from mods.utils import checks
from bs4 import BeautifulSoup as bs
from bs4 import BeautifulSoup
from collections import OrderedDict
import cleverbot
from mods.utils import checks


with open("mods/utils/config.json") as f:
	config = json.load(f)

wrap = "```py\n{}\n```"

if os.path.isfile("tags.json"):
	pass
else:
	with open("tags.json", "w") as f:
		f.write("{}")

async def get_file(url):
	"""
	Get a file from the web using aiohttp.
	"""
	with aiohttp.ClientSession() as sess:
		async with sess.get(url) as get:
			assert isinstance(get, aiohttp.ClientResponse)
			data = await get.read()
			return data

class Fun():
	def __init__(self, bot):
		self.bot = bot

	@commands.group(pass_context=True, invoke_without_command=True)
	async def t(self, ctx, *, name:str):
		if ctx.invoked_subcommand is None:
			with open("tags.json", "r+") as f:
				db = json.load(f)
				try:
					await self.bot.say(db[name])
				except:
					await self.bot.say("Sorry, I couldn't find that tag...")

	@t.command()
	@checks.is_PR()
	async def add(self, name:str, *, content:str):
		with open("tags.json", "r+") as f:
			db = json.load(f)
			db[name] = content
			with open("tags.json", "w") as f:
				json.dump(db, f)
				await self.bot.say(":white_check_mark:")

	@t.command()
	@checks.is_PR()
	async def delete(self, *, name:str):
		with open("tags.json", "r+") as f:
			db = json.load(f)
			try:
				db.pop(name)
				with open("tags.json", "w") as f:
					json.dump(db, f)
			except:
				await self.bot.say("ehhhhh")

	@commands.command(pass_context=True)
	async def talk(self, ctx):
		"""Clever bot"""
		cb1 = cleverbot.Cleverbot()
		unsplit = ctx.message.content.split("-talk")
		print(ctx.message.content.split("-talk "))
		split = unsplit[1]
		answer = (cb1.ask(split))
		await self.bot.send_message(ctx.message.channel, answer)

	@commands.command(hide=True)
	@checks.is_PR()
	async def setavatar(self, *, url: str):
		"""
		Change the bot's avatar.
		"""
		avatar = await get_file(url)
		await self.bot.edit_profile(avatar=avatar)
		await self.bot.say("Changed avatar.")


def setup(bot):
	bot.add_cog(Fun(bot))
