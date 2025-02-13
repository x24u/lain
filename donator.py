import asyncio
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import (
    Dict,
    List,
    Optional, 
    Tuple,
    Any,
    Union
    )

import discord
from discord.ext import commands
from discord.ext.commands import (
    command,
    group,
    guild_only,
    Cog,
    cooldown,
    BucketType,
    has_permissions
    )
from discord import (
    Member,
    User,
    Role,
    TextChannel,
    File,
    Message,
    Embed,
    HTTPException,
    Attachment,
    NotFound,
    Forbidden
    )

import config
from helpers import Context
from helpers.tools.utilities import regex, shorten
from helpers.tools.managers import (
    find_message, 
    ValidMember,
    has_donator
    )

class Donator(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.locks = defaultdict(asyncio.Lock)
        self.speak_cache = {}
    
    @command(
        name="makemp3",
        usage="<attachment>",
        example="video.mp4",
        extras={
            "note": "Message reference available"
        }
    )
    @guild_only()
    @has_permissions(donator=True)
    async def makemp3(
        self,
        ctx: Context,
        video: Optional[Attachment] = None
    ) -> Message:
        """
        Convert a video to MP3.
        """
        if not video and ctx.message.reference:
            ref_msg: Message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if ref_msg.attachments:
                video = ref_msg.attachments[0]

        if not video:
            return await ctx.warn("You must attach a video or reply to a message with a video.")

        if not video.content_type or not video.content_type.startswith("video"):
            return await ctx.warn("The attachment must be a video.")

        if video.size > 10_000_000:
            return await ctx.warn("Maximum file size must be 10 MB.")

        input_path = f"./{video.filename}"
        output_path = f"./{video.filename.rsplit('.', 1)[0]}.mp3"

        try:
            await video.save(input_path)
            os.system(f"ffmpeg -i {input_path} {output_path}")

            await ctx.reply(file=File(output_path))
        except HTTPException:
            await ctx.warn("The converted file is too large to send.")
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

    @command(
        name="videotogif",
        usage="<attachment>",
        example="video.mp4",
        extras={
            "note": "Message reference available"
        },
        aliases=[
            "vid2gif"
        ]
    )
    @guild_only()
    @has_permissions(donator=True)
    async def videotogif(
        self,
        ctx: Context,
        video: Optional[Attachment] = None
    ) -> Message:
        """
        Convert a video to GIF.
        """
        if not video and ctx.message.reference:
            ref_msg: Message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if ref_msg.attachments:
                video = ref_msg.attachments[0]

        if not video:
            return await ctx.warn("You must attach a video or reply to a message with a video.")

        if not video.content_type or not video.content_type.startswith("video"):
            return await ctx.warn("The attachment must be a video.")

        if video.size > 10_000_000:
            return await ctx.warn("Maximum file size must be 10 MB.")

        input_path = f"./{video.filename}"
        output_path = f"./{video.filename.rsplit('.', 1)[0]}.gif"

        try:
            await video.save(input_path)
            os.system(f"ffmpeg -i {input_path} {output_path}")

            await ctx.reply(file=File(output_path))
        except HTTPException:
            await ctx.warn("The converted file is too large to send.")
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
    
    @command(
        name="say",
        usage="[channel] <message>",
        example="Hello World!"
    )
    @guild_only()
    @has_permissions(donator=True, manage_messages=True)
    async def say(
        self,
        ctx: Context,
        channel: Optional[TextChannel],
        *, 
        message: str
    ) -> Message:
        """
        Make the bot says your message.
        """
        message = shorten(message, 2048)
        channel = channel or ctx.channel
        try:
            await channel.send(message)
            await ctx.check()
            
        except Forbidden:
            await ctx.warn(f"Missing permission to send message in {channel.mention}")
        
    @command(
        name="edit",
        usage="<message link> <message>",
        example=".../channels/... Testing"
    )
    @guild_only()
    @has_permissions(donator=True, manage_messages=True)
    async def edit(
        self, 
        ctx: Context, 
        message_id: str,
        *,
        new_message: str
    ) -> Message:
        """
        Edit the bot original message.
        """
        message = await find_message(ctx, message_id)
        new_message = shorten(new_message, 2048)

        if message.author != ctx.guild.me:
            return await ctx.warn(f"[`{message.id}`]({message.jump_url}) is **not** my message")

        await message.edit(content=new_message)
        return await ctx.check()
        
    @command(
        name="selfpurge",
        usage="<amount>",
        example="50"
    )
    @guild_only()
    @has_permissions(donator=True)
    async def selfpurge(
        self, 
        ctx: Context, 
        amount: int
    ):
        """
        Delete your own messages.
        """
        if amount > 100:
            return await ctx.warn("You can only purge your last **100** message!")
            
        await ctx.channel.purge(
            limit=amount,
            check=lambda m: m.author.id == ctx.author.id and not m.pinned,
            bulk=True
        )
    
    @command(
        name="impersonate",
        usage="[member] <message>",
        example="Hello World!"
    )
    @guild_only()
    @has_permissions(donator=True)
    @cooldown(1, 10, BucketType.guild)
    async def impersonate(
        self,
        ctx: Context, 
        member: Optional[Member],
        *,
        content: str
    ):
        """
        Impersonate a member or yourself using webhook.
        """
        content = shorten(content, 2048)
        member = member or ctx.author
        
        if member.bot:
            return await ctx.warn("You **cannot** impersonate as bot!")
            
        if member.id == ctx.guild.owner.id:
            return await ctx.warn("You cannot impersonate as the **server owner**!")
        
        try:
            webhook = await ctx.channel.create_webhook(
                name=member.display_name, 
                reason=f'{ctx.author} used the impersonate command')
            
            await ctx.delete()
            await webhook.send(content, username=member.display_name, avatar_url=member.display_avatar.url)
            await webhook.delete(
                reason=f'Auto deletion of webhook after member used the impersonate command')
        
        except (Forbidden, HTTPException) as e:
            return await ctx.deny(f"An error occured while creating the webhook\n```py\n{str(e)}```")
    
    @command(
        name='speak',
        usage="<channel> <true or false>",
        example="#general true"
    )
    @guild_only()
    @has_permissions(donator=True, manage_channels=True)
    async def speak(
        self,
        ctx: Context, 
        channel: TextChannel,
        state: bool
    ):
        """
        Speak as the bot.
        """
        self.speak_cache[ctx.channel.id] = (channel.id, option)
        status = {'enabled' if state else 'disabled'}
        await ctx.approve(f"{status.capitalize()} forwarding message!\n\nI will now forward any message that were sent in this channel to {channel.mention}\n\n_ Mention {channel.mention} again with state to `false` to stop forwarding._")
    
    # SELFALIAS
    @group(
        name="selfalias",
        usage="(subcommand)",
        example="list",
        invoke_without_command=True
    )
    @guild_only()
    async def selfalias(
        self,
        ctx: Context
    ):
        """
        Manage your command selfaliases across all servers.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @selfalias.command(
        name="add",
        usage="<shortcut> <command>",
        example="i invitecode"
    )
    @has_permissions(donator=True)
    async def selfalias_add(
        self,
        ctx: Context,
        shortcut: str, 
        *, 
        command: str
    ):
        """
        Add a new selfalias for a command.
        """
        original_command = self.bot.get_command(command)
        if not original_command:
            return await ctx.warn(f"Command `{command}` does **not** exist")

        if len(shortcut) > 10:
            return await ctx.warn("Shortcut **cannot** be longer than **10** characters!")
            
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT *
                FROM selfaliases 
                WHERE user_id = ? 
                AND alias = ?
                """,
                (ctx.author.id, shortcut)
            )
            if await cursor.fetchone():
                return await ctx.warn(f"Selfalias `{shortcut}` **already** exists")

            await cursor.execute(
                """
                INSERT INTO selfaliases (user_id, alias, command)
                VALUES (?, ?, ?)
                """,
                (ctx.author.id, shortcut, original_command.qualified_name)
            )
            await self.bot.db.commit()

        await ctx.approve(f"Added `{shortcut}` as an alias for `{original_command.qualified_name}`")

    @selfalias.command(
        name="remove",
        usage="<shortcut>",
        aliases=[
            "rmv"
        ]
    )
    @has_permissions(donator=True)
    async def selfalias_remove(
        self,
        ctx: Context,
        shortcut: str
    ):
        """
        Remove a selfalias for a command.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT command
                FROM selfaliases
                WHERE user_id = ? 
                AND alias = ?
                """,
                (ctx.author.id, shortcut)
            )
            alias_result = await cursor.fetchone()
        
            if not alias_result:
                return await ctx.warn(f"Selfalias `{shortcut}` does **not** exist")
            
            await cursor.execute(
                """
                DELETE FROM selfaliases
                WHERE user_id = ? 
                AND alias = ?
                """,
                (ctx.author.id, shortcut)
            )
            await self.bot.db.commit()
            
        await ctx.approve(f"Removed selfalias `{shortcut}` for `{alias_result[0]}`")

    @selfalias.command(
        name="list",
    )
    @has_permissions(donator=True)
    async def selfalias_list(
        self, 
        ctx: Context
    ) -> Message:
        """
        List all of your command selfaliases.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT alias, command 
                FROM selfaliases
                WHERE user_id = ?
                """, 
                (ctx.author.id,)
            )
            results = await cursor.fetchall()
            if not results:
                return await ctx.warn("You don't have any selfalias to list")

        embed = Embed(
            color=config.Color.base,
            title="Self Aliases",
            description="\n".join(f"**{alias}** - `{command}`" for alias, command in results)
            )
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar.url)
        
        await ctx.paginate(embed)

    @selfalias.command(
        name="reset",
        brief="Donator"
    )
    @has_permissions(donator=True)
    async def selfalias_reset(
        self,
        ctx: Context
    ):
        """
        Reset all of your command selfaliases.
        """
        await ctx.prompt("Are you sure you want to **reset** all of your command selfalias?")
        
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                DELETE FROM selfaliases 
                WHERE user_id = ?
                """, 
                (ctx.author.id,)
            )
            await self.bot.db.commit()
            
        await ctx.approve("All of your command selfaliases have been removed")
    
    # FN
    @group(
        name="forcenickname",
        usage="(subcommand)",
        example="list",
        aliases=[
            'fn',
            'fnickname',
            'fnick', 
            'fnicks', 
            'fname', 
            'fnames', 
            'forcenick'
        ],
        invoke_without_command=True
    )
    @guild_only()
    async def forcenickname(
        self, 
        ctx: Context
    ):
        """
        Restrict a member nickname.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @forcenickname.command(
        name="add",
        usage="<member> <nickname>",
        example="qmantha John Doe",
        aliases=[
            "set"
        ]
    )
    @has_permissions(donator=True, manage_nicknames=True)
    async def forcenickname_add(
        self,
        ctx: Context,
        member: ValidMember, 
        *, 
        nickname: str = "John Doe"
    ):
        """
        Set or update the force nickname of a member.
        """
        nickname = shorten(nickname, 32)
        
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT * 
                FROM forcenick
                WHERE guild_id = ? 
                AND user_id = ?
                """,
                (ctx.guild.id, member.id)
            )
            results = await cursor.fetchone()
            if results:
                await cursor.execute(
                    """
                    UPDATE forcenick
                    SET nickname = ?
                    WHERE guild_id = ?
                    AND user_id = ?
                    """,
                    (nickname, ctx.guild.id, member.id)
                )
                await self.bot.db.commit()
                try:
                    await member.edit(nick=nickname)
                    return await ctx.approve(f"Updated **existing forcenickname** for {member.mention} to **{nickname}**")
                    
                except Forbidden:
                    await ctx.warn(f"Missing permission to update the **nickname**, but the **forcenick** is **already** set for {member.mention}")
            
            else:
                await cursor.execute(
                    """
                    INSERT INTO forcenick (user_id, nickname, guild_id, previous_nick) 
                    VALUES (?, ?, ?, ?)
                    """,
                    (member.id, nickname, ctx.guild.id, member.nick)
                )
                await self.bot.db.commit()
                try:
                    await member.edit(nick=nickname)
                    return await ctx.approve(f"Fornickname set for {member.mention} to **{nickname}**")
                    
                except Forbidden:
                    await ctx.warn(f"Missing permission to update the **nickname**, but the **forcenick** is **already** set for {member.mention}")

    @forcenickname.command(
        name="remove",
        usage="<member>",
        example="qmantha",
        aliases=[
            "rmv"
        ]
    )
    @has_permissions(donator=True, manage_nicknames=True)
    async def forcenickname_remove(
        self, 
        ctx: Context, 
        member: ValidMember
    ):
        """
        Remove the force nickname of a member.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT previous_nick 
                FROM forcenick 
                WHERE user_id = ?
                AND guild_id = ?
                """,
                (member.id, ctx.guild.id)
            )
            data = await cursor.fetchone()
            if not data:
                return await ctx.warn(f"{member.mention} is **not** force nicknamed")

            await cursor.execute(
                """
                DELETE FROM forcenick 
                WHERE user_id = ?
                AND guild_id = ?
                """, 
                (member.id, ctx.guild.id)
            )
            await self.bot.db.commit()

        try:
            await member.edit(nick=data[0])
            await ctx.approve(f"Removed the force nickname of {member.mention}\n\n> Nickname restored to **{data[0] or 'N/A'}**")
        
        except Forbidden:
            await ctx.warn("Failed to remove the **nickname** from the **forcenick** but its entry has been removed from the database.")

    @forcenickname.command(
        name="list"
    )
    @has_permissions(donator=True, manage_nicknames=True)
    async def forcenickname_list(
        self,
        ctx: Context
    ) -> Message:
        """
        List all the force nicknamed members in the server.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT user_id, nickname 
                FROM forcenick 
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            results = await cursor.fetchall()
            if not results:
                return await ctx.warn("This server doesn't have any force nicknamed members to list")
        
        members = []
        for user_id, nickname in results:
            member = ctx.guild.get_member(user_id)
            if member:
                members.append(f"{member.mention} - **{nickname}**")
            else:
                members.append(f"**Unknown Member** (`{user_id}`)")
        
        embed = Embed(
            color=config.Color.base,
            title="Force Nicknames",
            description="\n".join(members)
            )
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar.url)
        
        await ctx.paginate(embed)

    @forcenickname.command(
        name="reset"
    )
    @has_permissions(donator=True, manage_guild=True)
    async def forcenickname_reset(
        self, 
        ctx: Context
    ):
        """
        Reset all the force nicknamed members in the server.
        """
        await ctx.prompt("Are you sure you want to **reset** all the **force nicknamed** members in the server?")
        
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                DELETE FROM forcenick 
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            await self.bot.db.commit()

        await ctx.approve("All force nickname data has been cleared. Members can now change their nicknames freely.")
    
    # Asynchronous
    # SELFALIAS
    async def get_selfaliases(self, user_id, alias):
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT command 
                FROM selfaliases
                WHERE user_id = ?
                AND alias = ?
                """,
                (user_id, alias)
            )
            result = await cursor.fetchone()
            return result[0] if result else None
    
    # SELFALIAS EVENT
    @Cog.listener("on_message")
    async def selfalias_check(self, message):
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        command_name = ctx.invoked_with
        if command_name:
            alias_command = await self.get_selfaliases(message.author.id, command_name)
            if alias_command:
                new_content = f"{ctx.prefix}{alias_command} {ctx.message.content[len(ctx.prefix) + len(command_name):]}"
                new_message = message
                new_message.content = new_content.strip()
                await self.bot.process_commands(new_message)
    
    # FN EVENT
    @Cog.listener("on_member_update")
    async def Forcenickname_check(self, before: Member, after: Member):
        if before.guild is None:
            return

        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT nickname 
                FROM forcenick 
                WHERE user_id = ?
                AND guild_id = ?
                """,
                (before.id, before.guild.id)
            )
            data = await cursor.fetchone()

        if data and after.nick != data[0]:
            try:
                await after.edit(nick=data[0])
                
            except:
                pass
    
    # SPEAK EVENT
    @Cog.listener("on_message")
    async def speak_check(self, message):
        if message.author == self.bot.user:
            return
        
        if message.channel.id in self.speak_cache:
            target_channel_id, state = self.speak_cache[message.channel.id]
            if state:
                target_channel = self.bot.get_channel(target_channel_id)
                await target_channel.send(message.content)

        for original_channel_id, (mapped_channel_id, state) in self.speak_cache.items():
            if message.channel.id == mapped_channel_id and state:
                original_channel = self.bot.get_channel(original_channel_id)
                await original_channel.send(f"**{message.author.display_name}:** {message.content}")
        
async def setup(bot):
    await bot.add_cog(Donator(bot))