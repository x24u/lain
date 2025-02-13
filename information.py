import calendar  
import colorsys  
import io  
import json  
import os  
import asyncio
import re  
import textwrap  
from asyncio import TimeoutError
from datetime import datetime, timedelta, timezone  
from random import choice
from typing import (
    Dict,
    List,
    Tuple, 
    Optional,
    Union,
    Literal,
    Any
    )
from io import BytesIO
from random import choice
from time import time
from psutil import Process
from contextlib import suppress

import requests 
import urllib.parse
import aiohttp
from yarl import URL
from dateutil.parser import isoparse

import discord  
from discord import (  
    app_commands,  
    CategoryChannel,  
    Embed,  
    Emoji,  
    Guild,  
    Asset,
    Invite,  
    Role,
    Status,
    Member,
    Message,  
    Permissions,  
    Spotify,  
    TextChannel,  
    User,  
    VoiceChannel 
    )  
from discord.ext import commands, tasks  
from discord.ext.commands import (  
    BucketType,  
    Cog,  
    command,  
    has_permissions,
    group,
    Command,
    Group,
    cooldown,  
    hybrid_group,
    guild_only,  
    hybrid_command  
    )  
from discord.ui import Button, View  
from discord.utils import format_dt, utcnow

import config  

from helpers import Context
from helpers.tools.book.utils_bookery import fetch_google_books
from helpers.tools.book.utils_discord import embed_google_books
from helpers.tools.anime.anime_discord import *
from helpers.tools.anime.anime_utils import *
from helpers.tools.managers import HexConverter, HelpView
from helpers.tools.managers.tools import _handle_search_results
from helpers.tools.utilities import regex, perform_search, human_timedelta, human_size

class Information(Cog):
    def __init__(self, bot):
        self.bot = bot

    @hybrid_command(
        name="help",
        usage="[command]",
        example="ban",
        aliases=[
            "commands", 
            "command",
            "cmds",
            "cmd",
            "h"
        ]
    )
    @guild_only()
    async def help(
        self, 
        ctx: Context, 
        *, 
        command: str = None
    ) -> Message:
        """
        View the help menu or information about a command.
        """
        if not command:
            x = self.bot.get_command("showthehelp")
            return await ctx.invoke(x)
        
        command_obj: Command | Group = self.bot.get_command(command)
        if not command_obj:
            return await ctx.warn(f"Command `{command}` does **not** exist")

        embeds = []
        for command in [command_obj] + (
            list(command_obj.walk_commands()) if isinstance(command_obj, Group) else []
        ):
            embed = Embed(
                color=config.Color.neutral,
                title=(
                    ("Group Command: " if isinstance(command, Group) else "Command: ")
                    + command.qualified_name
                ),
                description=command.help or "No description provided.",
            )

            embed.add_field(
                name="**Aliases**",
                value=", ".join(command.aliases) if command.aliases else "n/a",
                inline=True,
            )
            embed.add_field(
                name="**Parameters**",
                value=", ".join(key.replace("_", " ") for key in command.clean_params.keys()) if command.clean_params else "n/a",
                inline=True,
            )

            information = []
            note = command.extras.get("note", None)
            if cooldown := command.cooldown:
                information.append(f"{config.Emoji.cooldown} {int(cooldown.per)} seconds")

            if hasattr(command.callback, "required_permissions"):
                permissions = command.callback.required_permissions
                perm_strings = []

                if permissions.get("bot_owner"):
                    perm_strings.append("Bot Owner")

                if permissions.get("guild_owner"):
                    perm_strings.append("Server Owner")
                
                if permissions.get("donator"):
                    perm_strings.append("Donator")
                
                perm_strings += [
                    perm.replace("_", " ").title()
                    for perm, value in permissions.items()
                    if value and perm not in["bot_owner", "guild_owner", "donator"]
                ]

                if perm_strings:
                    information.append(f"{config.Emoji.warn} {' & '.join(perm_strings)}")
            
            if note:
                information.append(f"{config.Emoji.note} {note}")
                
            exist_info = "\n".join(information) if information else "n/a"
            
            embed.add_field(
                name="**Information**",
                value=exist_info,
                inline=True,
            )

            embed.add_field(
                name="**Usage**", 
                value=(
                    f"```\nSyntax: {ctx.clean_prefix}{command.qualified_name} {command.usage or ''}"
                    + (
                        f"\nExample: {ctx.clean_prefix}{command.qualified_name} {command.example}"
                        if command.example
                        else ""
                    )
                    + "```"
                ),
                inline=False
            )
            embed.set_footer(
                text="Module: " + command.cog_name.lower() if command.cog_name else "n/a"
            )

            embeds.append(embed)

        await ctx.paginate(embeds)
    
    @command(
        name="showthehelp"
    )
    @guild_only()
    async def showthehelp(
        self,
        ctx: Context
    ):
        """
        Displays an interactive help menu.
        """
        embed = Embed(
            description="Select a category from the dropdown menu below to see all of its commands. ",
            color=config.Color.neutral
        )
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url)
        embed.add_field(
            name="**Parameters**",
            value="<> - Required\n[] - Optional",
            inline=False)
        embed.set_footer(text="Commands with an asterisk (*) have a subcommand")

        await ctx.send(embed=embed, view=HelpView(self.bot))
    
    @hybrid_command(
        name="ping",
        aliases=[
            "latency"
        ]
    )
    @guild_only()
    async def ping(
        self, 
        ctx: Context
    ) -> Message:
        """
        Check the bot latency.
        """
        start = time()
        message = await ctx.send(content="...")
        finished = time() - start

        return await message.edit(
            content=f"it took `{int(self.bot.latency * 1000)}ms` to ping **{choice(config.ping_responses)}** (edit: `{finished:.2f}ms`)"
            )
    
    @command(
        name="uptime"
    )
    @guild_only()
    async def uptime(
        self,
        ctx: Context
    ) -> Message:
        """
        Check how long the bot been alive.
        """
        return await ctx.channel.neutral(
            f"**{self.bot.user.name}** has been alive for: **{human_timedelta(self.bot.uptime, suffix=False)}**",
            emoji="⏰"
            )
    
    @command(
        name="stats",
        aliases=[
            "about",
            "bi",
            "botinfo"
        ]
    )
    @guild_only()
    async def stats(
        self,
        ctx: Context
    ) -> Message:
        """
        View the bot statistics
        """
        process = Process()
        cogs_directory = './cogs'
        total_lines = 0
        for root, dirs, files in os.walk(cogs_directory):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), 'r', encoding="utf-8") as f:
                        total_lines += sum(1 for line in f)

        embed = Embed(
            description=(
                f"Bot statistics, developed by qmantha\n"
                f"**Memory:** {human_size(process.memory_full_info().uss, trim=True)}\n"
                f"**Commands:** {len(set(self.bot.walk_commands()))}\n"
                f"**Lines:** {total_lines:,}"
            ),
            timestamp=ctx.message.created_at,
        )
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.display_avatar.url,
        )
        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url)

        total_members = sum(guild.member_count or 0 for guild in self.bot.guilds)
        unique_members = len(self.bot.users)

        online_members = sum(
            1
            for guild in self.bot.guilds
            for member in guild.members
            if not member.bot and member.status != Status.offline
        )

        embed.add_field(
            name="**Users**",
            value=(
                f"{total_members:,} total\n"
                f"{unique_members:,} unique\n"
                f"{online_members:,} unique online"
            ),
            inline=True
        )

        text_channels = sum(len(guild.text_channels) for guild in self.bot.guilds)
        voice_channels = sum(len(guild.voice_channels) for guild in self.bot.guilds)
        total_channels = text_channels + voice_channels

        embed.add_field(
            name="**Channels**",
            value=(
                f"{total_channels:,} total\n"
                f"{text_channels:,} text\n"
                f"{voice_channels:,} voice"
            ),
            inline=True
        )

        embed.add_field(
            name="**Guilds**",
            value=(
                f"{len(self.bot.guilds):,} (private)\n"
            ),
            inline=True
        )
        embed.set_footer(
            text=f"Uptime: {human_timedelta(self.bot.uptime, suffix=False)}"
        )

        return await ctx.send(embed=embed)
    
    @command(
        name="shards",
        aliases=[
            "shard"
        ]
    )
    @guild_only()
    async def shards(
        self, 
        ctx: Context
    ) -> Message:
        """
        Check the status of each bot shard.
        """
        embed = Embed(
            color=config.Color.base, 
            title=f"Total Shards ({self.bot.shard_count})"
        )

        for shard in self.bot.shards:
            guilds = [g for g in self.bot.guilds if g.shard_id == shard]
            users = sum([g.member_count for g in guilds])
            embed.add_field(
                name=f"**Shard {shard}**",
                value=f"**Ping:** `{round(self.bot.shards.get(shard).latency * 1000)}ms`\n**Guilds:** `{len(guilds):,}`\n**Users:** `{users:,}`",
                inline=False
            )

        return await ctx.send(embed=embed)
    
    @hybrid_command(
        name="topcommands",
        aliases=[
            "topcmds",
            "topcmd",
            "topcommand"
        ]
    )
    @guild_only()
    async def topcommands(
        self,
        ctx: Context
    ) -> Message:
        """
        View the most used commands.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT command, uses 
                FROM topcommands 
                WHERE uses > 0
                ORDER BY uses DESC 
                LIMIT 100
                """
            )
            commands = await cursor.fetchall()
            if not commands:
                return await ctx.warn("No commands have been used yet.")

        embed = Embed(
            color=config.Color.base,
            title="Top Commands",
            description="\n".join(f"**{command}:** used `{uses:,}` times" for command, uses in commands)
            )
        
        await ctx.paginate(
            embed,
            text="command|commands"
        )
    
    @hybrid_command(
        name="anime",
        usage="<title>", 
        example="Overlord",
        aliases=[
            "ani"
        ]
    )
    @guild_only()
    async def anime(
        self, 
        ctx: Context,
        *, 
        title: str
    ):
        """
        Search for anime on Anilist.
        """
        msg = await ctx.send(embeds=[discord_embed_source(NAME_ANILIST, COLOR_ANILIST)])
        embeds = await discord_anilist_embeds(ctx, "ANIME", title)
        
        await _handle_search_results(ctx, embeds, msg)

    @hybrid_command(
        name="manga",
        usage="<title>",
        example="Standard of Reincarnation",
        aliases=[
            "manhwa",
            "manhua", 
            "lightnovel", 
            "ln"
        ]
    )
    @guild_only()
    async def manga(
        self, 
        ctx: Context,
        *, 
        title: str
    ):
        """
        Search for manga, manhwa, manhua, and lightnovel on various services. (Anilist, MangaDex, Batoto) 
        """
        msg = await ctx.send(embeds=[discord_embed_source(NAME_ANILIST, COLOR_ANILIST)])
        embeds = await discord_anilist_embeds(ctx, "MANGA", title)
        if embeds:
            return await _handle_search_results(ctx, embeds, msg)

        await msg.edit(embeds=[discord_embed_source(NAME_MANGADEX, COLOR_MANGADEX)])
        embeds = await discord_mangadex_embeds(title)
        if embeds:
            return await _handle_search_results(ctx, embeds, msg)

        await msg.edit(embeds=[discord_embed_source(NAME_BATOTO, COLOR_BATOTO)])
        embeds = await discord_batoto_embeds(title)
        if embeds:
            return await _handle_search_results(ctx, embeds, msg)

        return await msg.edit(embeds=[discord_embed_source(None)])

    @hybrid_command(
        name="character",
        usage="<name>", 
        example="Naofumi Iwatani",
        aliases=[
            "char"
        ]
    )
    @guild_only()
    async def character(
        self, 
        ctx: Context, 
        *, 
        name: str
    ):
        """
        Search for anime or manga character on Anilist.
        """
        msg = await ctx.send(embeds=[discord_embed_source(NAME_ANILIST, COLOR_ANILIST)])
        try:
            embeds, data = await discord_anilist_search_character(ctx, name)

            if embeds is not None:
                await _handle_search_results(ctx, embeds, msg)
            else:
                await msg.edit(embeds=[discord_embed_source(None)])

        except TypeError:
            await msg.edit(embeds=[discord_embed_source(None)])

    @group(
        name="anilist",
        usage="(subcommand)",
        example="user",
        invoke_without_command=True
    )
    @guild_only()
    async def anilist(
        self, 
        ctx: Context
    ):
        """
        Search various thing only on Anilist.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @anilist.command(
        name="anime",
        usage="<title>",
        example="Majo to Yajuu"
    )
    async def anilist_anime(
        self,
        ctx: Context,
        *, 
        title: str
    ):
        """
        Search for anime only on Anilist.
        """
        msg = await ctx.send(embeds=[discord_embed_source(NAME_ANILIST, COLOR_ANILIST)])
        embeds = await discord_anilist_embeds(ctx, "ANIME", title)
        
        await _handle_search_results(ctx, embeds, msg)

    @anilist.command(
        name="manga", 
        usage="<title>",
        example="Killer Peter",
        aliases=[
            "manhwa", 
            "manhua", 
            "lightnovel", 
            "ln"
        ]
    )
    async def anilist_manga(
        self, 
        ctx: Context, 
        *, 
        title: str
    ):
        """
        Search for manga, manhwa, manhua, and light novel only on Anilist.
        """
        msg = await ctx.send(embeds=[discord_embed_source(NAME_ANILIST, COLOR_ANILIST)])
        embeds = await discord_anilist_embeds(ctx, "MANGA", title)
        
        await _handle_search_results(ctx, embeds, msg)

    @anilist.command(
        name="user",
        usage="<username>",
        example="Mitsu"
    )
    async def anilist_user(
        self, 
        ctx: Context, 
        *, 
        username: str
    ):
        """
        Search for user profile on Anilist.
        """
        msg = await ctx.send(embeds=[discord_embed_source(NAME_ANILIST, COLOR_ANILIST)])
        try:
            embeds, data = await discord_anilist_search_user(ctx, username)

            if embeds is not None:
                await _handle_search_results(ctx, embeds, msg)
            else:
                await msg.edit(embeds=[discord_embed_source(None)])

        except TypeError:
            await msg.edit(embeds=[discord_embed_source(None)])

    @hybrid_command(
        name="mangadex",
        usage="<title>", 
        example="Designated Bully"
    )
    @guild_only()
    async def mangadex(
        self,
        ctx: Context, 
        *, 
        title: str
    ):
        """
        Search for manga, manhwa and manhua on MangaDex.
        """
        msg = await ctx.send(embeds=[discord_embed_source(NAME_MANGADEX, COLOR_MANGADEX)])
        embeds = await discord_mangadex_embeds(title)
        
        await _handle_search_results(ctx, embeds, msg)
    
    @hybrid_command(
        name="batoto",
        usage="<title>",
        example="God of Blackfield"
    )
    @guild_only()
    async def batoto(
        self,
        ctx: Context,
        *,
        title: str
    ):
        """
        Search for manga, manhwa, and manhua on Batoto.
        """
        msg = await ctx.send(embeds=[discord_embed_source(NAME_BATOTO, COLOR_BATOTO)])
        embeds = await discord_batoto_embeds(title)
        
        await _handle_search_results(ctx, embeds, msg)
        
    @hybrid_command(
        name="book",
        usage="<title>",
        example="A Light in the Attic"
    )
    @guild_only()
    async def book(
        self, 
        ctx: Context,
        *, 
        title: str
    ) -> Message:
        """
        Shows information about a book from Google Books.
        """
        results = await fetch_google_books(title)
        if results in [None, False]:
            return await ctx.warn(f"No results were found for **{title}**")

        books = results.get("items", [])
        if not books:
            return await ctx.warn(f"No results were found for **{title}**")

        embeds = [
            embed_google_books(book, config.Color.base) for book in books[:10]
        ]

        for embed in embeds:
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar.url)

        await ctx.paginate(
            embeds,
            of_text="Google Books Results",
        )

    @hybrid_group(
        name="wikipedia",
        usage="(subcommand) <args>",
        example="english Panzer VIII Maus",
        invoke_without_command=True,
        aliases=[
            "wiki"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def wikipedia(
        self, 
        ctx: Context,
        *, 
        query: str
    ) -> Message:
        """
        Gets information on English wikipedia.
        """
        async with ctx.typing():
            embeds, url = await perform_search(query, 'en')
        
        if not embeds:
            await ctx.warn(f"Sorry, no results were found for **{query}**")
        else:
            await ctx.paginate(
                embeds,
                of_text="Wikipedia Results"
            )
    
    @wikipedia.command(
        name="english",
        usage="<query>",
        example="Panzer VIII Maus",
        aliases=[
            "en",
            "eng"
        ]
    )
    @cooldown(1, 5, BucketType.member)
    async def wikipedia_english(
        self, 
        ctx: Context,
        *, 
        query: str
    ) -> Message:
        """
        Gets information on English wikipedia.
        """
        async with ctx.typing():
            embeds, url = await perform_search(query, 'en')
        
        if not embeds:
            await ctx.warn(f"Sorry, no results were found for **{query}**")
        else:
            await ctx.paginate(
                embeds,
                of_text="Wikipedia Results"
            )

    @wikipedia.command(
        name="indonesia",
        usage="<query>",
        example="Bandung Lautan Api",
        aliases=[
            "id",
            "ina",
            "idn"
        ]
    )
    @cooldown(1, 5, BucketType.member)
    async def wikipedia_indonesia(
        self, 
        ctx: Context,
        *,
        query: str
    ) -> Message:
        """
        Gets information on Indonesian wikipedia.
        """
        async with ctx.typing():
            embeds, url = await perform_search(query, 'id')
        
        if not embeds:
            await ctx.warn(f"Sorry, no results were found for **{query}**")
        else:
            await ctx.paginate(
                embeds,
                of_text="Wikipedia Results"
            )
    
    @wikipedia.command(
        name="german",
        usage="<query>",
        example="Verwundetenabzeichen",
        aliases=[
            "deutsch",
            "de",
            "ger",
            "germany"
        ]
    )
    @cooldown(1, 5, BucketType.member)
    async def wikipedia_deutsch(
        self, 
        ctx: Context,
        *,
        query: str
    ) -> Message:
        """
        Gets information on German wikipedia.
        """
        async with ctx.typing():
            embeds, url = await perform_search(query, 'de')
        
        if not embeds:
            return await ctx.warn(f"Sorry, no results were found for **{query}**")
        else:
            await ctx.paginate(
                embeds,
                of_text="Wikipedia Results"
            )
    
    @command(
        name="enlarge", 
        usage="<emoji>",
        example="Emoji_Goes_Here",
        aliases=[
            "big",
            "jumbo"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def enlarge(
        self, 
        ctx: Context,
        *,
        emoji: str
    ) -> Message:
        """
        Enlarge one or multiple custom emojis.
        """
        matched_emojis = regex.DISCORD_EMOJI.findall(emoji)
        
        if not matched_emojis:
            return await ctx.warn("No valid custom emojis found")

        embeds = []
        for index, (is_animated, name, emoji_id) in enumerate(matched_emojis, start=1):
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if is_animated else 'png'}"
            
            embed = Embed(
                title=name,
                color=config.Color.base
                )
            embed.add_field(
                name="**Emoji ID**",
                value=f"`{emoji_id}`",
                inline=False)
            embed.add_field(
                name="**Image URL**",
                value=f"[**Click here to open the image**]({emoji_url})")
            embed.set_image(
                url=emoji_url)
            
            embed.set_author(
                name=ctx.author.name, 
                icon_url=ctx.author.display_avatar.url)
            
            embeds.append(embed)

        await ctx.paginate(
            embeds,
            text="emoji|emojis"
        )
    
    @hybrid_command(
        name="urbandictionary",
        usage="<word>",
        example="ayt",
        aliases=[
            "urban",
            "ud"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def urbandictionary(
        self,
        ctx: Context,
        *, 
        word: str
    ) -> Message:
        """
        Gets the definition of a word/slang from Urban Dictionary.
        """
        await ctx.typing()
        try:
            async with self.bot.session.get(
                "https://api.urbandictionary.com/v0/define",
                params={"term": word}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    return await ctx.warn(f"Failed to fetch data. Status: {response.status}")
        except Exception:
            raise

        if not data.get('list'):
            return await ctx.warn(f"No results were found for **{word}**")

        embeds = []
        total_entries = len(data['list'])
        for i, item in enumerate(data['list'], 1):
            embed = Embed(
                url=item['permalink'],
                title=item['word'],
                description=item['definition'],
                color=config.Color.base
            )
            embed.add_field(name="**Example**", value=item['example'], inline=False)
            embed.add_field(
                name="**Votes**",
                value=f"👍 `{item['thumbs_up']:,} / {item['thumbs_down']:,}` 👎",
                inline=False
            )
            embed.set_author(
                name=ctx.author.name, 
                icon_url=ctx.author.display_avatar.url)
                
            embeds.append(embed)

        await ctx.paginate(
            embeds,
            of_text="Urban Dictionary Results"
        )
    
    @hybrid_command(
        name="github",
        usage="<user>",
        example="qmantha",
        aliases=[
            "gh",
            "git"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def github(
        self,
        ctx: Context,
        *, 
        user: str
    ):
        """
        Lookup for a github profile.
        """
        url = f'https://api.github.com/users/{user}'
        
        async with self.bot.session.get(url) as response:
            if response.status != 200:
                return await ctx.warn(f"No gitHub user were found with name **{user}**")
            
            res = await response.json()
            
            name = res.get('login')
            avatar_url = res.get('avatar_url')
            html_url = res.get('html_url')
            email = res.get('email')
            public_repos = res.get('public_repos')
            followers = res.get('followers')
            following = res.get('following')
            twitter = res.get('twitter_username')
            location = res.get('location')
            company = res.get('company')

            embed = Embed(
                color=config.Color.base, 
                title=f"@{name}", url=html_url,
                timestamp=utcnow())
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(name="**Followers**", value=f"{followers:,}", inline=False)
            embed.add_field(name="**Following**", value=f"{following:,}", inline=False)
            embed.add_field(name="**Repository**", value=f"{public_repos:,}", inline=False)
            
            if email:
                embed.add_field(name="**Email**", value=email, inline=False)
            if location:
                embed.add_field(name="**Location**", value=location, inline=False)
            if twitter:
                embed.add_field(name="**Twitter**", value=twitter, inline=False)
            if company:
                embed.add_field(name="**Company**", value=company, inline=False)

            embed.set_footer(
                text='GitHub', 
                icon_url='https://cdn.discordapp.com/attachments/1279019189625032755/1306076505536987197/images.png?ex=67355a08&is=67340888&hm=a26b7e41023eeaf1a73dbceb40ae77f2c37005b0a043145724a3ffe07663d567&')
            await ctx.send(embed=embed)
    
    @command(
        name="randomhex",
        aliases=[
            "randomcolor",
            "randomcolour"
        ]
    )
    @guild_only()
    async def randomhex(
        self,
        ctx: Context
    ):
        """
        Show a random hex color code in an embed.
        """
        random_color = await HexConverter().convert(ctx, "random")
        
        return await self.color(ctx, color=random_color)
    
    @command(
        name="color", 
        usage="<hex code>",
        example="random",
        extras={
            "note": "Dominant color available, type `dominant`"
        },
        aliases=[
            "colour"
        ]
    )
    @guild_only()
    async def color(
        self,
        ctx: Context,
        *, 
        color: HexConverter
    ):
        """
        Show a hex color code in a embed.
        """
        embed = Embed(color=color)
        embed.set_author(name=f"Showing hex code: {str(color).upper()}")

        embed.add_field(
            name="**RGB Value**",
            value=", ".join([str(x) for x in color.to_rgb()]),
            inline=True
        )
        embed.add_field(
            name="**INT Value**", 
            value=color.value, 
            inline=True
        )
        embed.add_field(
            name="**HSL Value**",
            value=", ".join(
                f"{int(value * (360 if index == 0 else 100))}%"
                for index, value in enumerate(
                    colorsys.rgb_to_hls(*[x / 255.0 for x in color.to_rgb()])
                )
            ),
            inline=True
        )

        embed.set_thumbnail(
            url=(
                "https://place-hold.it/250x219/"
                + str(color).replace("#", "")
                + "?text=%20"
            )
        )

        return await ctx.send(embed=embed)
    
    @hybrid_command(
        name="inviteinfo",
        usage="<invite>",
        example="codm",
        extras={
            "note": "Server Invite available"
        },
        aliases=[
            "ii",
            "icode",
            "codeinfo",
            "vanity"
        ]
    )
    @guild_only()
    async def inviteinfo(
        self, 
        ctx: Context,
        invite: Invite
    ):
        """
        View an invite code information.
        """
        color = await self.bot.dominant(invite.guild.icon)
        embed = Embed(
            title=f"Invite Code: {invite.code}",
            color=color)
        embed.set_thumbnail(url=invite.guild.icon)

        embed.add_field(
            name="**Channel & Invite**",
            value=(
                f"**Name:** {invite.channel.name} (`{invite.channel.type}`)\n"
                f"**ID:** `{invite.channel.id}`\n"
                "**Created:** "
                + format_dt(
                    invite.channel.created_at,
                    style="f",
                )
                + "\n"
                "**Invite Expiration:** "
                + (
                    format_dt(
                        invite.expires_at,
                        style="R",
                    )
                    if invite.expires_at
                    else "Never"
                )
                + "\n"
                "**Inviter:** Unknown\n"
                "**Temporary:** N/A\n"
                "**Usage:** N/A"
            ),
            inline=True,
        )
        embed.add_field(
            name="**Guild**",
            value=(
                f"**Name:** {invite.guild.name}\n"
                f"**ID:** `{invite.guild.id}`\n"
                "**Created:** "
                + format_dt(
                    invite.guild.created_at,
                    style="f",
                )
                + "\n"
                f"**Members:** {invite.approximate_member_count:,}\n"
                f"**Members Online:** {invite.approximate_presence_count:,}\n"
                f"**Verification Level:** {invite.guild.verification_level.name.title()}"
            ),
            inline=True,
        )

        view = View()
        for button in [
            Button(
                emoji=emoji,
                label=key,
                url=asset.url,
            )
            for emoji, key, asset in [
                ("🖼", "Icon", invite.guild.icon),
                ("🎨", "Splash", invite.guild.splash),
                ("🏳", "Banner", invite.guild.banner),
            ]
            if asset
        ]:
            view.add_item(button)

        return await ctx.send(embed=embed, view=view)
    
    @hybrid_command(
        name="avatar",
        usage="<user>",
        example="qmantha",
        extras={
            "note": "User ID available"
        },
        aliases=[
            "av",
            "pfp",
            "pp"
        ],
    )
    @guild_only()
    async def avatar(
        self,
        ctx: Context,
        user: Member | User = None
    ):
        """
        View the avatar of a user or yourself.
        """
        if user is None and ctx.message.reference:
            ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            user = ref_msg.author

        user = user or ctx.author

        color = await self.bot.dominant(user)
        embed = Embed(
            title=f"{user.name}'s avatar",
            url=user.display_avatar.url,
            color=color
        )
        embed.set_image(url=user.display_avatar.url)

        await ctx.send(embed=embed)
    
    @hybrid_command(
        name="banner",
        usage="<user>",
        example="qmantha",
        extras={
            "note": "User ID available"
        }
    )
    @guild_only()
    async def banner(
        self,
        ctx: Context,
        *,
        user: Member | User = None
    ):
        """
        View the banner of a user or yourself.
        """
        if user is None:
            user = ctx.author

        user = self.bot.get_user(user.id) or await self.bot.fetch_user(user.id)
        banner_url = user.banner.url if user.banner else None

        if banner_url:
            color = await self.bot.dominant(banner_url)
            embed = Embed(
                title=f"{user.name}'s banner",
                url=banner_url,
                color=color
            )
            embed.set_image(url=banner_url)
            await ctx.send(embed=embed)
        else:
            if user == ctx.author:
                await ctx.warn("You don't have a **banner**")
            else:
                await ctx.warn(f"{user.mention} does **not** have a **banner**")
    
    # Normal
    @command(
        name="joinposition",
        usage="<member>",
        example="qmantha",
        aliases=[
            "pos",
            "joinpos"
        ]
    )
    @guild_only()
    async def joinposition(
        self, 
        ctx: Context,
        *,
        member: Member = None
    ):
        """
        Checks the join position of a member or yourself in the server.
        """
        member = member or ctx.author
        pos = sum(m.joined_at < member.joined_at for m in sorted(ctx.guild.members, key=lambda m: m.joined_at) if m.joined_at)
        if member == ctx.author:
            await ctx.neutral(f"Your join position is **{pos + 1}**")
        else:
            await ctx.neutral(f"{member.mention} join position is **{pos + 1}**")
        
    @command(
        name="invitecount",
        usage="<member>",
        example="qmantha"
    )
    @guild_only()
    @cooldown(1, 3, BucketType.member)
    async def invitecount(
        self, 
        ctx: Context,
        member: Member = None
    ):
        """
        Check how many invites a member have or yourself.
        """
        totalInvites = 0
        member = member or ctx.author

        for invite in await ctx.guild.invites():
            if invite.inviter == member:
                totalInvites += invite.uses

        if member == ctx.author:
            await ctx.neutral(f"You currently have **{totalInvites}** invites!", emoji="🔗")
        else:
            await ctx.neutral(f"{member.mention} currently has **{totalInvites}** invites!", emoji="🔗")

    @command(
        name="mspotify",
        usage="<member>",
        example="qmantha",
        aliases=[
            "sptfy"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def mspotify(
        self, 
        ctx: Context,
        user: Member = None
    ):
        """
        Shows the Spotify track a member is listening to.
        """
        user = user or ctx.author
        spotify_activity = next((activity for activity in user.activities if isinstance(activity, Spotify)), None)
        color = await self.bot.dominant(spotify_activity.album_cover_url)
        
        if spotify_activity:
            embed = Embed(
                color=color
            )
            embed.add_field(
                name="**Song**", 
                value=f"[**{spotify_activity.title}**](https://open.spotify.com/track/{spotify_activity.track_id})", 
                inline=True
            )
            embed.add_field(
                name="**Artist**", 
                value=f"**{spotify_activity.artist}**", 
                inline=True
            )
            embed.set_thumbnail(url=spotify_activity.album_cover_url)
            embed.set_author(name=user.name, icon_url=user.display_avatar.url)
            embed.set_footer(text=f"Album: {spotify_activity.album}")

            button = Button(
                emoji=config.Emoji.spotify, 
                label="Play on Spotify", 
                style=discord.ButtonStyle.url, 
                url=f"https://open.spotify.com/track/{spotify_activity.track_id}"
            )
            view = discord.ui.View()
            view.add_item(button)
            
            await ctx.send(embed=embed, view=view)
        else:
            if user == ctx.author:
                await ctx.warn("You're not currently listening to **Spotify**")
            else:
                await ctx.warn(f"{user.mention} is not currently listening to **Spotify**")
            
    @command(
        name="devices", 
        usage="<member>",
        example="qmantha",
        aliases=[
            "device",
            "platform"
        ]
    )
    @guild_only()
    async def devices(
        self, 
        ctx: Context,
        *,
        member: Member = None
    ):
        """
        Shows the devices of a member or yourself are using.
        """
        member = member or ctx.author
        
        desktop_status = str(member.desktop_status)
        mobile_status = str(member.mobile_status)
        web_status = str(member.web_status)
        
        if any(isinstance(activity, discord.Streaming) for activity in member.activities):
            desktop_status = 'streaming' if desktop_status != 'offline' else desktop_status
            mobile_status = 'streaming' if mobile_status != 'offline' else mobile_status
            web_status = 'streaming' if web_status != 'offline' else web_status
        
        status_icons = {
            'online': '\U0001f7e2',
            'idle': '\U0001f7e0',
            'dnd': '\U0001f534',  # Large Red Circle
            'offline': '\U000026aa',  # Medium White Circle
            'streaming': '\U0001f7e3'  # Purple Circle
        }

        embed = Embed(
            color=config.Color.base,
            timestamp=utcnow(),
            title=f"{member.display_name}'s devices",
            description=(
                f"{status_icons.get(desktop_status, '')} Desktop\n"
                f"{status_icons.get(mobile_status, '')} Mobile\n"
                f"{status_icons.get(web_status, '')} Web"
            )
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @command(
        name="calendar",
        usage="[month] [year]",
        example="2 2010",
        extras={
            "note": "Month & Year available"
        }
    )
    @guild_only()
    async def _calendar(
        self,
        ctx: Context, 
        month: int = None,
        year: int = None
    ):
        """
        View the calendar for a specific month and year, or default to the current month and year if not specified.
        """
        now = datetime.utcnow()
        month = month or now.month
        year = year or now.year

        if not (1 <= month <= 12) or not (1 <= year <= 9999):
            return await ctx.warn("Invalid month or year provided. Please provide a valid month (`1` - `12`) and year!")

        width = 4 if ctx.author.is_on_mobile() else 5
        cal = calendar.month(year, month, w=width, l=2)

        embed = Embed(
            title=f"Calendar for {calendar.month_name[month]} {year}",
            description=f"```\n{cal}\n```",
            color=config.Color.base
        )
        await ctx.send(embed=embed)
    
    @command(
        name="membercount",
        aliases=[
            "mc"
        ]
    )
    @guild_only()
    async def membercount(
        self, 
        ctx: Context
    ):
        """
        Show the member count.
        """
        humans = len([m for m in ctx.guild.members if not m.bot])
        bots = len([m for m in ctx.guild.members if m.bot])
        members = ctx.guild.member_count
        
        embed = Embed(color=config.Color.base)
        embed.set_author(
            name=f"{ctx.guild.name} statistics",
            icon_url=ctx.guild.icon)
        
        embed.add_field(
            name="**Members**",
            value=f"{members:,}",
            inline=True)
        embed.add_field(
            name="**Humans**",
            value=f"{humans:,}",
            inline=True)
        embed.add_field(
            name="**Bots**",
            value=f"{bots:,}",
            inline=True)
            
        await ctx.send(embed=embed)

    @command(
         name="gas",
         aliases=[
             "solar",
             "infogas"
         ]
     )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def gas(
        self, 
        ctx: Context
    ):
         """
         View the current Ethereum gas prices.
         """
         await ctx.typing()
         response = await self.bot.session.get(
             "https://api.owlracle.info/v3/eth/gas",
         )
         data = await response.json()

         embed = Embed(
             title="Ethereum Gas Prices",
             color=config.Color.base
         )

         embed.add_field(
             name="**Slow**",
             value=f"**GWEI:** {data['speeds'][0]['maxFeePerGas']:,.2f}\n**FEE:** ${data['speeds'][0]['estimatedFee']:,.2f} USD",
             inline=True,
         )
         embed.add_field(
             name="**Standard**",
             value=f"**GWEI:** {data['speeds'][1]['maxFeePerGas']:,.2f}\n**FEE:** ${data['speeds'][1]['estimatedFee']:,.2f} USD",
             inline=True,
         )
         embed.add_field(
             name="**Fast**",
             value=f"**GWEI:** {data['speeds'][2]['maxFeePerGas']:,.2f}\n**FEE:** ${data['speeds'][2]['estimatedFee']:,.2f} USD",
             inline=True,
         )
         embed.set_footer(
             text="OwlRacle"
         )
         embed.timestamp = utcnow()
         
         return await ctx.send(embed=embed)
    
    @command(
        name="firstmessage",
        usage="[channel]",
        example="#general",
        aliases=[
            "firstmsg",
            "first"
        ]
    )
    @guild_only()
    async def firstmessage(
        self, 
        ctx: Context, 
        *, 
        channel: TextChannel = None
    ):
        """
        View the first message of the current or mentioned channel.
        """
        channel = channel or ctx.channel

        async for message in channel.history(limit=1, oldest_first=True):
            break

        return await ctx.neutral(f"The first message sent in {channel.mention} - [**Jump to Message**]({message.jump_url})")
    
    @command(
        name="roleinfo",
        usage="[role]",
        example="Member",
        aliases=[
            "rinfo",
            "ri"
        ]
    )
    @guild_only()
    async def roleinfo(
        self,
        ctx: Context,
        *, 
        role: Role = None
    ):
        """
        View information about a role.
        """
        role = role or ctx.author.top_role

        embed = Embed(
            color=role.color,
            title=role.name,
        )
        if isinstance(role.display_icon, Asset):
            embed.set_thumbnail(url=role.display_icon)

        embed.add_field(
            name="**Role ID**",
            value=f"`{role.id}`",
            inline=True,
        )
        embed.add_field(
            name="**Guild**",
            value=f"{ctx.guild} (`{ctx.guild.id}`)",
            inline=True,
        )
        embed.add_field(
            name="**Color**",
            value=f"`{str(role.color).upper()}`",
            inline=True,
        )
        embed.add_field(
            name="**Hoisted**", 
            value=config.Emoji.approve if role.hoist else config.Emoji.deny,
            inline=True
        )
        embed.add_field(
            name="**Mentionable**", 
            value=config.Emoji.approve if role.mentionable else config.Emoji.deny,
            inline=True
        )
        embed.add_field(
            name="**Position**", 
            value=role.position,
            inline=True
        )
        embed.add_field(
            name="**Managed**", 
            value=config.Emoji.approve if role.managed else config.Emoji.deny, 
            inline=True
        )
        embed.add_field(
            name="**Creation Date**",
            value=(
                format_dt(role.created_at, style="F")
                + " ("
                + format_dt(role.created_at, style="R")
                + ")"
            ),
            inline=True
        )
        count = len(role.members)
        embed.add_field(
            name=f"**{count:,} {'Member' if count == 1 else 'Members'}**",
            value=(
                "No members in this role"
                if not role.members
                else ", ".join([user.name for user in role.members][:10])
                + ("..." if len(role.members) > 10 else "")
            ),
            inline=False,
        )

        return await ctx.send(embed=embed)
    
    @command(
        name="channelinfo",
        usage="[channel]",
        example="#general",
        extras={
            "note": "Voice & Category available"
        },
        aliases=[
            "cinfo",
            "ci"
        ]
    )
    @guild_only()
    async def channelinfo(
        self, 
        ctx: Context,
        *, 
        channel: TextChannel | VoiceChannel | CategoryChannel = None
    ):
        """
        View information about the current or mentioned channel.
        """
        channel = channel or ctx.channel
        if not isinstance(
            channel,
            (TextChannel, VoiceChannel, CategoryChannel),
        ):
            return await ctx.warn(f"Please mention a valid channel!")

        embed = Embed(
            title=channel.name, 
            color=config.Color.base)

        embed.add_field(
            name="**Channel ID**",
            value=f"`{channel.id}`",
            inline=True,
        )
        embed.add_field(
            name="**Type**",
            value=f"`{channel.type}`",
            inline=True,
        )
        embed.add_field(
            name="**Guild**",
            value=f"{ctx.guild} (`{ctx.guild.id}`)",
            inline=True,
        )

        if category := channel.category:
            embed.add_field(
                name="**Category**",
                value=f"{category} (`{category.id}`)",
                inline=False,
            )

        if isinstance(channel, TextChannel) and channel.topic:
            embed.add_field(
                name="**Topic**",
                value=channel.topic,
                inline=False,
            )

        elif isinstance(channel, VoiceChannel):
            embed.add_field(
                name="**Bitrate**",
                value=f"**{int(channel.bitrate / 1000)}** Kbps",
                inline=False,
            )
            embed.add_field(
                name="**User Limit**",
                value=(channel.user_limit or "Unlimited"),
                inline=False,
            )

        elif isinstance(channel, CategoryChannel) and channel.channels:
            embed.add_field(
                name=f"**{len(channel.channels)} Children**",
                value=", ".join([child.name for child in channel.channels]),
                inline=False,
            )

        embed.add_field(
            name="**Creation Date**",
            value=(
                format_dt(channel.created_at, style="F")
                + " **("
                + format_dt(channel.created_at, style="R")
                + ")**"
            ),
            inline=False,
        )

        return await ctx.send(embed=embed)

    @command(
        name="serveravatar",
        usage="[member]",
        example="qmantha",
        extras={
            "note": "User ID available"
        },
        aliases=[
            "sav",
            "sab",
            "sag",
            "savi",
            "spfp"
        ]
    )
    @guild_only()
    async def serveravatar(
        self,
        ctx: Context,
        member: Member = None
    ):
        """
        View the server avatar of a member or yourself.
        """
        member = member or ctx.author
        if not member.guild_avatar:
            if member == ctx.author:
                return await ctx.warn("You don't have a **server avatar**")
            else:
                return await ctx.warn(f"{member.mention} does **not** have a **server avatar**")

        color = await self.bot.dominant(member.guild_avatar.url)
        embed = Embed(
            url=member.guild_avatar.url,
            title=f"{member.name}'s server avatar",
            color=color)
        embed.set_image(url=member.guild_avatar)

        await ctx.send(embed=embed)
    
    @command(
        name="serverbanner",
        usage="[id or invite code]",
        example="codm",
        extras={
            "note": "Server ID & Invite available"
        },
        aliases=[
            "sbanner",
            "guildbanner",
            "gbanner"
        ]
    )
    @guild_only()
    async def serverbanner(
        self,
        ctx: Context,
        *,
        server: Guild | Invite = None
    ):
        """
        View the banner of a server, either using its ID or invite code.
        """
        if isinstance(server, Invite):
            server = server.guild

        server = server or ctx.guild

        if not server.banner:
            return await ctx.warn(f"server **{server}** does not have a **banner**!")

        color = await self.bot.dominant(server.icon.url)
        embed = Embed(
            url=server.banner,
            title=f"{server}'s banner", 
            color=config.Color.base)
        embed.set_image(url=server.banner)
        
        await ctx.send(embed=embed)
    
    @command(
        name="splash",
        usage="[id or invite code]",
        example="codm",
        extras={
            "note": "Server ID & Invite available"
        },
        aliases=[
            "ssplash",
            "guildsplsh",
            "gsplash"
        ]
    )
    @guild_only()
    async def splash(
        self,
        ctx: Context,
        *,
        server: Guild | Invite = None
    ):
        """
        View the splash of a server, either using its ID or invite code.
        """
        if isinstance(server, Invite):
            server = server.guild

        server = server or ctx.guild

        if not server.splash:
            return await ctx.warn(f"server **{server}** does not have a **splash**!")

        color = await self.bot.dominant(server.icon.url)
        embed = Embed(
            url=server.splash,
            title=f"{server}'s splash",
            color=color)
        embed.set_image(url=server.splash)
        
        await ctx.send(embed=embed)
    
    @command(
        name="icon",
        usage="[id or invite code]",
        example="codm",
        extras={
            "note": "Server ID & Invite available"
        },
        aliases=[
            "servericon",
            "sicon",
            "guildicon",
            "gicon"
        ]
    )
    @guild_only()
    async def icon(
        self,
        ctx: Context,
        *,
        server: Guild | Invite = None
    ):
        """
        View the icon of a server, either using its ID or invite code.
        """
        if isinstance(server, Invite):
            server = server.guild

        server = server or ctx.guild

        if not server.icon:
            return await ctx.warn(f"server **{server}** does not have an **icon**!")

        color = await self.bot.dominant(server.icon.url)
        embed = Embed(
            url=server.icon, 
            title=f"{server}'s icon",
            color=color)
        embed.set_image(url=server.icon)
        
        await ctx.send(embed=embed)

    @hybrid_command(
        name="userinfo",
        usage="[user]",
        example="qmantha",
        extras={
            "note": "User ID available"
        },
        aliases=[
            "whois",
            "uinfo",
            "info",
            "ui"
        ]
    )
    @guild_only()
    async def userinfo(
        self, 
        ctx: Context,
        *, 
        user: Member | User = None
    ) -> Message:
        """
        View information about a user or yourself.
        """
        user = user or ctx.author
        color = await self.bot.dominant(user.display_avatar.url)

        embed = Embed(
            color=color
        )
        embed.set_author(
            name=f"{user.name} ({user.id})",
            icon_url=user.display_avatar,
        )
        embed.set_thumbnail(url=user.display_avatar)
        footer = list()

        if user.bot:
            footer.append("Discord Bot")
        elif user.id in self.bot.owner_ids:  # Owner
            footer.append(f"Owner of {self.bot.user.name}")

        # Account creation and join dates
        embed.add_field(
            name="**Dates**",
            value=(
                f"**Created:** "
                + format_dt(user.created_at, style="F")
                + " (" + format_dt(user.created_at, style="R") + ")"
                + (
                    f"\n**Joined:** "
                    + format_dt(user.joined_at, style="F")
                    + " (" + format_dt(user.joined_at, style="R") + ")"
                    if isinstance(user, Member) and user.joined_at
                    else ""
                )
                + (
                    f"\n**Boosted:** "
                    + format_dt(user.premium_since, style="F")
                    + " (" + format_dt(user.premium_since, style="R") + ")"
                    if isinstance(user, Member) and user.premium_since
                    else ""
                )
            ),
            inline=False,
        )
        # Spotify Activity
        description_parts = []
        if isinstance(user, Member):
            spotify_activity = next((a for a in user.activities if isinstance(a, Spotify)), None)
            if spotify_activity:
                description_parts.append(
                    f"{config.Emoji.spotify} Listening to [**{spotify_activity.title}**](https://open.spotify.com/track/{spotify_activity.track_id}) "
                    f"by **{', '.join(spotify_activity.artists)}**"
                )

        # Voice channel information
        if isinstance(user, Member) and user.voice:
            other_members = len(user.voice.channel.members) - 1
            description_parts.append(
                f"**In voice channel:** {user.voice.channel.mention} "
                + (
                    "by themselves"
                    if other_members == 0
                    else f"with **{other_members}** other{'s' if other_members != 1 else ''}"
                )
            )

        if description_parts:
            embed.description = "\n".join(description_parts)

        # Badges Section
        badge_list = user.badges()
        if badge_list:
            embed.add_field(
                name="**Badges**",
                value=" ".join(badge_list),
                inline=False,
            )
        
        if isinstance(user, Member):
            roles = [role for role in user.roles if not role.is_default()]
            roles_sorted = sorted(roles, key=lambda r: r.position, reverse=True)[:10]

            count = len(roles)
            embed.add_field(
                name=f"**{'Role' if count == 1 else 'Roles'} ({len(roles)})**",
                value=(
                    "Member doesn't have any role in this server"
                    if not roles
                    else ", ".join([role.mention for role in roles_sorted])
                    + (f", (**+{len(roles) - 10} more**)" if len(roles) > 10 else "")
                ),
                inline=False,
            )

        if isinstance(user, Member):
            if (
                any(
                    [
                        user.guild_permissions.ban_members,
                        user.guild_permissions.kick_members,
                        user.guild_permissions.manage_channels,
                        user.guild_permissions.manage_roles,
                        user.guild_permissions.manage_emojis_and_stickers,
                        user.guild_permissions.manage_messages,
                        user.guild_permissions.mention_everyone,
                        user.guild_permissions.manage_nicknames,
                        user.guild_permissions.manage_webhooks,
                        user.guild_permissions.view_audit_log,
                        user.guild_permissions.manage_threads,
                        user.guild_permissions.move_members,
                        user.guild_permissions.mute_members,
                        user.guild_permissions.deafen_members
                    ]
                )
                and not user.guild_permissions.administrator
            ):
                embed.add_field(
                    name="**Key Permissions**",
                    value=", ".join(
                        [
                            perm.replace("_", " ").title()
                            for perm, value in user.guild_permissions
                            if perm
                            in [
                                "ban_members",
                                "kick_members",
                                "manage_channels",
                                "manage_roles",
                                "manage_emojis_and_stickers",
                                "manage_messages",
                                "mention_everyone",
                                "manage_nicknames",
                                "manage_webhooks",
                                "view_audit_log",
                                "manage_threads",
                                "move_members",
                                "mute_members",
                                "deafen_members"
                            ]
                            and value
                        ]
                    ),
                    inline=False
                )

        if isinstance(user, Member):
            if user.id == ctx.guild.owner_id:
                footer.append("Server Owner")
            if user.guild_permissions.administrator:
                footer.append("Administrator")

            join_position = sorted(ctx.guild.members, key=lambda m: m.joined_at or utcnow()).index(user) + 1
            footer.append(f"Join position: {join_position:,}")

        if user != self.bot.user:
            shared_servers = len(user.mutual_guilds)
            footer.append(f"{shared_servers} mutual {'server' if shared_servers == 1 else 'servers'}")

        if footer:
            embed.set_footer(text=" ・ ".join(footer))

        return await ctx.send(embed=embed)

    @command(
        name="serverinfo",
        usage="[id]",
        example="123456789",
        extras={
            "note": "Server ID available"
        },
        aliases=[
            "guildinfo",
            "sinfo",
            "ginfo",
            "si",
            "gi"
        ]
    )
    @guild_only()
    async def serverinfo(
        self,
        ctx: Context,
        guild_id: Guild = None
    ):
        """
        View information about a server.
        """
        guild = guild_id or ctx.guild

        embed = Embed(
            title=guild.name, 
            color=config.Color.base,
            description=(
                (guild.description + "\n\n" if guild.description else "")
                + "Server created on "
                + (
                    format_dt(guild.created_at, style="F")
                    + " ("
                    + format_dt(guild.created_at, style="R")
                    + ")"
                )
                + f"\n__{guild.name}__ is on bot shard ID: **{guild.shard_id}/{self.bot.shard_count}**"
            ),
            timestamp=guild.created_at,
        )
        embed.set_thumbnail(url=guild.icon)

        embed.add_field(
            name="**Owner**",
            value=(guild.owner or guild.owner_id),
            inline=True,
        )
        embed.add_field(
            name="**Members**",
            value=(
                f"**Total:** {guild.member_count:,}\n"
                f"**Humans:** {len([m for m in guild.members if not m.bot]):,}\n"
                f"**Bots:** {len([m for m in guild.members if m.bot]):,}"
            ),
            inline=True,
        )
        information_value = ""
        if guild.vanity_url:
            information_value += f"**Vanity:** {guild.vanity_url.split('/')[-1]}\n"
        information_value += f"**Verification:** {guild.verification_level.name.title()}\n"
        information_value += f"**Level:** {guild.premium_tier}/{guild.premium_subscription_count:,} boosts"

        embed.add_field(
            name="**Information**",
            value=information_value,
            inline=True,
        )
        embed.add_field(
            name="**Design**",
            value=(
                f"**Banner:** "
                + (f"[Click here]({guild.banner})\n" if guild.banner else "N/A\n")
                + f"**Splash:** "
                + (f"[Click here]({guild.splash})\n" if guild.splash else "N/A\n")
                + f"**Icon:** "
                + (f"[Click here]({guild.icon})\n" if guild.icon else "N/A\n")
            ),
            inline=True,
        )
        embed.add_field(
            name=f"**Channels ({len(guild.channels)})**",
            value=f"**Text:** {len(guild.text_channels)}\n**Voice:** {len(guild.voice_channels)}\n**Category:** {len(guild.categories)}\n",
            inline=True,
        )
        embed.add_field(
            name="**Counts**",
            value=(
                f"**Roles:** {len(guild.roles)}/250\n"
                f"**Emojis:** {len(guild.emojis)}/{guild.emoji_limit}\n"
                f"**Boosters:** {len(guild.premium_subscribers):,}\n"
            ),
            inline=True,
        )

        if guild.features:
            embed.add_field(
                name="**Features**",
                value=(
                    "```\n"
                    + ", ".join(
                        [
                            feature.replace("_", " ").title()
                            for feature in guild.features
                        ]
                    )
                    + "```"
                ),
                inline=False
            )

        embed.set_footer(text=f"Guild ID: {guild.id}")

        return await ctx.send(embed=embed)
    
    @group(
        name="boosters",
        usage="(subcommand)",
        example="lost",
        invoke_without_command=True,
        aliases=[
            "booster"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def boosters(
        self,
        ctx: Context
    ) -> Message:
        """
        View a list of the server boosters.
        """
        if not (
            members := sorted(
                filter(
                    lambda member: member.premium_since,
                    ctx.guild.members,
                ),
                key=lambda member: member.premium_since,
                reverse=True,
            )
        ):
            return await ctx.warn("No **members** are currently boosting!")
        
        embed = Embed(
            title="Boosters",
            description="\n".join(
                f"{member.mention} boosted "
                + format_dt(member.premium_since, style="R")
                for member in members
            ),
            color=config.Color.base
            )
        
        embed.set_author(
            name=ctx.author.name, 
            icon_url=ctx.author.display_avatar.url)

        await ctx.paginate(
            embed,
            text="booster|boosters"
        )
    
    @boosters.command(
        name="lost"
    )
    async def boosters_lost(
        self,
        ctx: Context
    ) -> Message:
        """
        View a list of most recently lost boosters.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT user_id, started_at, expired_at
                FROM boosters_lost
                ORDER BY expired_at DESC
                """
            )
            results = await cursor.fetchall()
            if not results:
                return await ctx.warn("No **boosters** have been lost recently!")
        
        users = []
        for user_id, started_at, expired_at in results:
            # Ensure timestamps are not None before converting
            started_at = datetime.fromisoformat(started_at).replace(tzinfo=timezone.utc) if started_at else None
            expired_at = datetime.fromisoformat(expired_at).replace(tzinfo=timezone.utc) if expired_at else None

            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            lasted = human_timedelta(started_at, accuracy=1, brief=True, suffix=False) if started_at else "Unknown duration"
            expired_text = format_dt(expired_at, style="R") if expired_at else "Unknown time"

            if user:
                users.append(
                    f"{user.mention} stopped boosting {expired_text} (lasted: {lasted})"
                )
            else:
                users.append(
                    f"**Unknown User** (`{user_id}`) stopped boosting {expired_text} (lasted: {lasted})"
                )
        
        embed = Embed(
            color=config.Color.base,
            title="Recently lost boosters",
            description="\n".join(users)
            )
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar.url)
        
        await ctx.paginate(embed)
    
    @command(
        name="listemojis",
        aliases=[
            "listemoji",
            "emojis"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def listemojis(
        self, 
        ctx: Context
    ) -> Message:
        """
        View all the server emojis and its markdown.
        """
        if not ctx.guild.emojis:
            return await ctx.warn("This server does **not** have any emoji")
            
        embed = Embed(
            title="Emojis",
            description="\n".join(f"{emoji} — `<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>`" for emoji in ctx.guild.emojis
            ),
            color=config.Color.base
            )
        
        embed.set_author(
            name=ctx.author.name, 
            icon_url=ctx.author.display_avatar.url)
        
        await ctx.paginate(
            embed,
            text="emoji|emojis"
        )
    
    @command(
        name="liststickers",
        aliases=[
            "liststicker",
            "stickers"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def liststickers(
        self, 
        ctx: Context
    ) -> Message:
        """
        View all the server stickers and its IDs.
        """
        if not ctx.guild.stickers:
            return await ctx.warn("This server does **not** have any sticker")
            
        embed = Embed(
            color=config.Color.base,
            title="Stickers",
            description="\n".join(f"[**{sticker.name}**]({sticker.url}) (`{sticker.id}`)" for sticker in  ctx.guild.stickers)
            )
        embed.set_author(
            name=ctx.author.name, 
            icon_url=ctx.author.display_avatar.url)
        
        await ctx.paginate(
            embed,
            text="sticker|stickers"
        )
    
    @command(
        name="recentmembers",
        usage="[amount]",
        example="50",
        aliases=[
            "recentmember",
            "recent"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.guild)
    async def recentmembers(
        self, 
        ctx: Context,
        amount: int = 10
    ):
        """
        Lists the most recent members who joined the server.
        """
        members_list = sorted(
            ctx.guild.members,
            key=lambda member: member.joined_at or utcnow(),
            reverse=True
        )[:amount]

        members = [
            f"{member.mention} joined {format_dt(member.joined_at, style='R')}"
            for member in members_list
        ]
        
        embed = Embed(
            color=config.Color.base,
            title=f"Recent members",
            description="\n".join(members)
            )
        embed.set_author(
            name=ctx.author.name, 
            icon_url=ctx.author.display_avatar.url)

        await ctx.paginate(embed)

    @command(
        name="listbots",
        aliases=[
            "listapps",
            "listapp",
            "listbot",
            "bots"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def listbots(
        self,
        ctx: Context
    ) -> Message:
        """
        View all bots in the server
        """
        bots = "\n".join(
            f"{bot.mention} (`{bot.id}`)" for bot in ctx.guild.members if bot.bot
        )
        if not bots:
            return await ctx.warn("No bots found in this server.")
        
        embed = Embed(
            title="Bots",
            description=bots,
            color=config.Color.base
            )
        embed.set_author(
            name=ctx.author.name, 
            icon_url=ctx.author.display_avatar.url)

        await ctx.paginate(
            embed,
            text="bot|bots"
        )
    
    @command(
        name="listroles",
        aliases=[
            "listrole",
            "roles"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def listroles(
        self,
        ctx: Context
    ) -> Message:
        """
        View all the server roles.
        """
        roles = "\n".join(f"{role.mention} (`{role.id}`)" for role in sorted(ctx.guild.roles, key=lambda role: role.position, reverse=True) if role.name != "@everyone"
        )
        if not roles:
            return await ctx.warn("No roles found in this server.")

        embed = Embed(
            title="Roles",
            description=roles,
            color=config.Color.base
            )
        embed.set_author(
            name=ctx.author.name, 
            icon_url=ctx.author.display_avatar.url)
            
        await ctx.paginate(
            embed,
            text="role|roles"
        )
    
    @command(
        name="withroles",
        aliases=[
            "withrole",
            "wroles"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def withroles(
        self,
        ctx: Context
    ) -> Message:
        """
        View all the server roles and its member count.
        """
        roles = "\n".join(
            f"{role.mention} - **{len(role.members)}** {'member' if len(role.members) == 1 else 'members'}"
            for role in ctx.guild.roles if role.name != "@everyone"
        )
        if not roles:
            return await ctx.warn("No roles found in this server.")

        embed = Embed(
            title="With Roles",
            description=roles,
            color=config.Color.base
            )
        embed.set_author(
            name=ctx.author.name, 
            icon_url=ctx.author.display_avatar.url)
            
        await ctx.paginate(
            embed,
            text="role|roles"
        )
    
    @command(
        name="inrole",
        usage="[role]",
        example="Member"
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def inrole(
        self,
        ctx: Context,
        *, 
        role: Role = None
    ) -> Message:
        """
        View how many members in a role.
        """
        role = role or ctx.author.top_role

        if not role.members:
            return await ctx.warn(f"No **members** have the {role.mention} role")

        roles = "\n".join(
            f"{member.mention}"
            + (" (you)" if member == ctx.author else "")
            + (" (bot)" if member.bot else "")
            for member in role.members
        )
        embed = Embed(
            title=f"Members in {role}",
            description="\n".join(
                f"{member.mention}"
                + (" (you)" if member == ctx.author else "")
                + (" (bot)" if member.bot else "")
                for member in role.members
            ),
            color=config.Color.base
            )
        embed.set_author(
            name=ctx.author.name, 
            icon_url=ctx.author.display_avatar.url)

        await ctx.paginate(
            embed,
            text="member|members"
        )
    
    @command(
        name="listmembers",
        aliases=[
            "members",
            "member"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def listmembers(
        self, 
        ctx: Context
    ) -> Message:
        """
        View all the human members in the server.
        """
        members = "\n".join(f"{member.mention}" for member in ctx.guild.members if not member.bot
        )
        if not members:
            return await ctx.warn("No human members found in this server.")
        
        embed = Embed(
            title=f"Humans",
            description=members,
            color=config.Color.base
            )
        embed.set_author(
            name=ctx.author.name, 
            icon_url=ctx.author.display_avatar.url)
        
        await ctx.paginate(
            embed,
            text="member|members"
        )
    
    @command(
        name="listchannels",
        aliases=[
            "listchannel",
            "channels"
        ]
    )
    @guild_only()
    async def listchannels(
        self,
        ctx: Context
    ) -> Message:
        """
        View a list of all channels in the server.
        """
        if not ctx.guild.channels:
            return await ctx.warn("This server doesn't have any channel to show.")
        
        embed = Embed(
            color=config.Color.base,
            title="Channels",
            description="\n".join(f"**{channel.name}** (`{channel.id}`)" for channel in ctx.guild.channels))
        
        await ctx.paginate(embed)

    @command(
        name="listinvites", 
        aliases=[
            "invites"
        ]
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    async def listinvites(
        self,
        ctx: Context
    ) -> Message:
        """
        View all the server invite code and their expiration date.
        """
        invites = await ctx.guild.invites()
        invites_list = "\n".join(
            f"[**{invite.code}**]({invite.url}) ({format_dt(invite.expires_at, style='R')})" if invite.expires_at else f"[**{invite.code}**]({invite.url}) (Never)"
            for invite in invites
        )
        if not invites_list:
            return await ctx.warn("No active invites found in this server.")
        
        embed = Embed(
            title="Invites",
            description=invites_list,
            color=config.Color.base
            )
        embed.set_author(
            name=ctx.author.name, 
            icon_url=ctx.author.display_avatar.url)

        await ctx.paginate(
            embed,
            text="invite|invites"
        )
            
async def setup(bot) -> None:
    await bot.add_cog(Information(bot))