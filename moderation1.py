import json
import re
import os
import asyncio
import io
from datetime import datetime, timezone, timedelta
from typing import (
    Optional,
    List, 
    Tuple,
    Dict,
    Any,
    Union, 
    Literal
    )
from io import BytesIO

import discord
import aiosqlite
from discord.ext import commands, tasks
from discord.ui import View, Button
from discord.utils import utcnow, format_dt
from discord.abc import GuildChannel
from discord import (
    app_commands,
    Embed, 
    Message, 
    User, 
    Member,
    Object,
    Guild,
    PermissionOverwrite,
    Role,
    HTTPException,
    Color,
    TextChannel, 
    File, 
    Forbidden, 
    NotFound
    )
from discord.ext.commands import (
    command, 
    Cog, 
    group, 
    has_permissions,
    bot_has_permissions,
    cooldown,
    BucketType, 
    guild_only, 
    Greedy
    )

import config
from helpers import Context
from helpers.tools.managers import (
    EmbedScript,
    ValidRole,
    Invoke,
    ValidMember
    )
from helpers.tools.utilities import (
    humanize_duration,
    human_timedelta, 
    shorten,
    regex
    )

class Moderation(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def cog_load(self):
        self.check_jail_duration.start()
        self.tempban_check.start()
    
    def cog_unload(self):
        self.check_jail_duration.cancel()
        self.tempban_check.cancel()
    
    @group(
        name="invoke",
        usage="(subcommand)",
        example="ban",
        invoke_without_command=True
    )
    @guild_only()
    async def invoke(
        self, 
        ctx: Context
    ):
        """
        Manage moderation commands custom message.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @invoke.command(
        name="variables",
        aliases=[
            "variable"
        ]
    )
    async def invoke_variables(
        self,
        ctx: Context
    ):
        """
        View all the invoke variables.
        """
        variables = "\n".join(
            [f"{m} - {Invoke(ctx).variables.get(m)}" for m in Invoke(ctx).variables]
            )
            
        return await ctx.neutral("Invoke variables", code=variables)

    @invoke.command(
        name="kick",
        usage="<code|view|none>",
        example="Rip {member.mention} got kicked for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_kick(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the kick custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @invoke.command(
        name="ban",
        usage="<code|view|none>",
        example="Rip {member.mention} got banned for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_ban(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the ban custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @invoke.command(
        name="hackban",
        usage="<code|view|none>",
        example="Rip {member.mention} got hackbanned for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_hackban(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the hackban custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @invoke.command(
        name="softban",
        usage="<code|view|none>",
        example="Rip {member.mention} got softbanned for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_softban(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the softban custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @invoke.command(
        name="unban",
        usage="<code|view|none>",
        example="Luck for {member.mention} they got unbanned for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_unban(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the unban custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @invoke.command(
        name="mute",
        usage="<code|view|none>",
        example="Rip {member.mention} got muted for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_mute(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the mute custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @invoke.command(
        name="unmute",
        usage="<code|view|none>",
        example="Rip {member.mention} got unmuted for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_unmute(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the unmute custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @invoke.command(
        name="hardban",
        usage="<code|view|none>",
        example="Rip {member.mention} got hardbanned for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_hardban(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the hardban custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @invoke.command(
        name="unhardban",
        usage="<code|view|none>",
        example="Uhhh {member.mention} got unhardban for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_unhardban(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the unhardban custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @invoke.command(
        name="jail",
        usage="<code|view|none>",
        example="Rip {member.mention} got jailed for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_jail(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the jail custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @invoke.command(
        name="unjail",
        usage="<code|view|none>",
        example="Luck for {member.mention}, they got unjailed for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_unjail(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the unjail custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @invoke.command(
        name="tempban",
        usage="<code|view|none>",
        example="Rip {member.mention} got tempbanned for {reason}"
    )
    @has_permissions(manage_guild=True)
    async def invoke_tempban(
        self,
        ctx: Context,
        *,
        code: str
    ) -> Message:
        """
        Set, view or remove the tempban custom message.
        """
        await Invoke(ctx).cmd(code)
    
    @command(
        name="setnick",
        usage="<member> <name>",
        example="qmantha Hello World",
        aliases=[
            "setnickname"
        ]
    )
    @guild_only()
    @has_permissions(manage_nicknames=True)
    @bot_has_permissions(manage_nicknames=True)
    async def setnick(
        self, 
        ctx: Context, 
        member: Member,
        *,
        name: str
    ):
        """
        Change a member nickname.
        """
        name = shorten(name, 32)
        old_nick = member.name
        try:
            await ctx.approve(f"Changed the nickname of {member.mention} from **{old_nick}** to **{name}**")
            await member.edit(nick=new_nick, reason=f"Renamed by {ctx.author}")
        
        except (Forbidden, HTTPException) as e:
            await ctx.deny(f"An error occured\n```py\n{str(e)}```")
            
    @command(
        name="kick", 
        usage="<member> [reason]",
        example="qmantha"
    )
    @guild_only()
    @has_permissions(kick_members=True)
    @bot_has_permissions(kick_members=True)
    async def kick(
        self,
        ctx: Context,
        member: ValidMember,
        *, 
        reason: str = "No reason provided."
    ):
        """
        Kick a member from the server.
        """
        act = ctx.invoked_with
        if member.premium_since:
            await ctx.prompt(f"Are you sure you want to **{act}** {member.mention}?\nThey are currently boosting the server!")
            
        await member.kick(reason=reason)
        if not await Invoke(ctx).send(member, reason):
            await ctx.approve(f"Successfully kicked {member.mention} - **{reason}**")

    @command(
        name="ban", 
        usage="<member> [delete_days] [reason]",
        example="qmantha"
    )
    @guild_only()
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True, manage_messages=True)
    async def ban(
        self,
        ctx: Context,
        member: ValidMember,
        delete_days: Optional[int] = 0,
        *,
        reason: str = "No reason provided."
    ):
        """
        Ban a member from the server.
        """
        act = ctx.invoked_with
        if member.premium_since:
            await ctx.prompt(f"Are you sure you want to **{act}** {member.mention}?\nThey are currently boosting the server!")
            
        await ctx.guild.ban(member, reason=reason, delete_message_days=delete_days)
        if not await Invoke(ctx).send(member, reason):
            await ctx.approve(
                f"Successfully banned {member.mention} - **{reason}**"
                + (f"\n\nDeleted messages history: **{delete_days}** days" if delete_days > 0 else ""))
                
    @command(
        name="hackban", 
        usage="<user> [reason]",
        example="qmantha"
    )
    @guild_only()
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def hackban(
        self,
        ctx: Context, 
        user: User, 
        *,
        reason: str = "No reason provided."
    ):
        """
        Hackban a user from the server. Use their ID if not present.
        """
        with suppress(HTTPException):
            await ctx.guild.ban(user, reason=reason)
            if not await Invoke(ctx).send(user, reason):
                await ctx.approve(f"Successfully hackbanned {user.mention} - **{reason}**")
        
    @command(
        name="softban",
        usage="<member> [reason]",
        example="qmantha insulting"
    )
    @guild_only()
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def softban(
        self, 
        ctx: Context,
        member: ValidMember,
        *,
        reason: str = "No reason provided."
    ):
        """
        Softban a member from the server.
        """
        act = ctx.invoked_with
        if member.premium_since:
            await ctx.prompt(f"Are you sure you want to **{act}** {member.mention}?\nThey are currently boosting the server!")
            
        await ctx.guild.ban(member, reason=reason)
        await ctx.guild.unban(member, reason=f"{member.name} are softbanned")
        if not await Invoke(ctx).send(member, reason):
            await ctx.approve(f"Successfully softbanned {member.mention} - **{reason}**")

    @command(
        name="unban",
        usage="<user> [reason]",
        example="qmantha appeal accepted"
    )
    @guild_only()
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def unban(
        self, 
        ctx: Context, 
        user: User,
        *, 
        reason: str = "No reason provided."
    ):
        """
        Unban a user in the server.
        """
        try:
            await ctx.guild.unban(user, reason=reason)
            if not await Invoke(ctx).send(user, reason):
                await ctx.approve(f"Successfully unbanned {user.mention} - **{reason}**")
        except NotFound:
            await ctx.warn(f"{user.mention} is **not** banned.")
        
    @command(
        name="mute",
        usage="<member> <duration> [reason]",
        example="qmantha 1d6h spam",
        aliases=[
            "timeout",
            "stfu"
        ]
    )
    @guild_only()
    @has_permissions(moderate_members=True)
    @bot_has_permissions(moderate_members=True)
    async def mute(
        self,
        ctx: Context,
        member: ValidMember,
        duration: str,
        *,
        reason: str = "No reason provided."
    ):
        """
        Mute a member in the server.
        """
        if member.bot:
            return await ctx.warn("You cannot mute a bot.")
        
        if member.is_timed_out():
            return await ctx.warn(f"{member.mention} is **already** timed outted!")

        delta = humanize_duration(duration)
        if not delta:
            return await ctx.warn("Invalid duration format. Use a combination of `d`, `h`, `m`, and `s` (e.g., `3d5h20m7s`)")

        until = utcnow() + delta

        await member.timeout(until, reason=reason)
        if not await Invoke(ctx).send(member, reason):
            await ctx.approve(f"Successfully muted {member.mention} for {human_timedelta(until)} - **{reason}**")
        
    @command(
        name="unmute", 
        usage="<member> [reason]",
        example="qmantha"
    )
    @guild_only()
    @has_permissions(moderate_members=True)
    @bot_has_permissions(moderate_members=True)
    async def unmute(
        self,
        ctx: Context, 
        member: Member,
        *,
        reason: str = "No reason provided."
    ):
        """
        Unmute a timed outted member.
        """
        if not member.is_timed_out():
            return await ctx.warn(f"{member.mention} is **not** muted!")
            
        await member.timeout(None, reason=reason)
        if not await Invoke(ctx).send(member, reason):
            await ctx.approve(f"Successfully unmuted {member.mention} - **{reason}**")
        
    @command(
        name="muted"
    )
    @guild_only()
    @has_permissions(moderate_members=True)
    @bot_has_permissions(moderate_members=True)
    async def muted(
        self,
        ctx: Context
    ) -> Message:
        """
        List all the ongoing timeouts.
        """
        now = datetime.now(timezone.utc)
        active_timeouts = [
            member for member in ctx.guild.members 
            if member.timed_out_until and member.timed_out_until > now
        ]
        
        if not active_timeouts:
            return await ctx.warn("There are **no** active timeouts found")
        
        embed = Embed(
            color=config.Color.base,
            title="Timeouts",
            description="\n".join(f"{member.mention} ends <t:{int(member.timed_out_until.timestamp())}:R>" for member in active_timeouts))
            
        await ctx.paginate(embed)
    
    @command(
        name="banned",
        aliases=[
            "bans"
        ]
    )
    @guild_only()
    @has_permissions(view_audit_log=True, ban_members=True)
    @bot_has_permissions(view_audit_log=True, ban_members=True)
    async def banned(
        self, 
        ctx: Context
    ) -> Message:
        """
        View all the banned users in the server.
        """
        bans = []
        await ctx.defer()
        async for ban in ctx.guild.bans():
            bans.append((ban.user, ban.reason))

        if not bans:
            return await ctx.warn("There are no banned users in this server")

        embed = Embed(
            color=config.Color.base,
            title="Banned",
            description="\n".join(f"{user.mention or 'Unknown User'} - **{reason}**" for user, reason in bans))
            
        await ctx.paginate(embed)
    
    @command(
        name="unmuteall"
    )
    @guild_only()
    @has_permissions(moderate_members=True)
    @bot_has_permissions(moderate_members=True)
    async def unmuteall(
        self, 
        ctx: Context
    ):
        """
        Remove every timed outted members in the server.
        """
        await ctx.prompt("Are you sure you want to remove all the timed out members?")
        
        await ctx.defer()
        timed_out = tuple(member for member in ctx.guild.members if member.timed_out_until is not None and (ctx.guild.roles.index(member.top_role) < ctx.guild.roles.index(ctx.me.top_role) if member.top_role else True))
            
        await asyncio.gather(*(
            member.timeout(None)
            for member in timed_out
        ))
        
        return await ctx.approve(f"Successfully removed **{len(timed_out)}** timeouts")
    
    @command(
        name="deleteinvites",
        aliases=[
            "clearinvites"
        ]
    )
    @guild_only()
    @has_permissions(manage_guild=True)
    @bot_has_permissions(manage_guild=True)
    async def clearinvites(
        self,
        ctx: Context
    ):
        """
        Delete every invite links in the server.
        """
        await ctx.prompt("Are you sure you want to **reset** and **delete** all this server invite links?")
        
        invites = await ctx.guild.invites()
        if not invites:
            return await ctx.warn("There aren't any invites in this server.")
        
        await ctx.defer()
        await asyncio.gather(*(invite.delete() for invite in invites))
        return await ctx.approve("Successfully **deleted** every invite links in this server")

    @command(
        name="hardban", 
        usage="<user> [reason]",
        example="qmantha"
    )
    @guild_only()
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def hardban(
        self, 
        ctx: Context,
        user: Member | User, 
        *,
        reason: str = "No reason provided."
    ):
        """
        Hardban a user, they'll remain banned even a staff member unbans them.
        """
        act = ctx.invoked_with
        if user.premium_since:
            await ctx.prompt(f"Are you sure you want to **{act}** {user.mention}?\nThey are currently boosting the server!")
            
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT *
                FROM hardbanned
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (ctx.guild.id, user.id)
            )
            result = await cursor.fetchone()
            if result:
                return await ctx.warn(f"{user.mention} is **already** hardbanned")
                
            await cursor.execute(
                """
                INSERT OR REPLACE INTO hardbanned (guild_id, user_id, reason)
                VALUES (?, ?, ?)
                """,
                (ctx.guild.id, user.id, reason)
            )
            await self.bot.db.commit()
        
        with suppress(HTTPException):
            await ctx.guild.ban(user, reason=reason)
            if not await Invoke(ctx).send(user, reason):
                await ctx.approve(f"Successfully hardbanned {user.mention} - **{reason}**")

    @command(
        name="unhardban",
        usage="<user> [reason]",
        example="qmantha"
    )
    @guild_only()
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def unhardban(
        self, 
        ctx: Context,
        user: User, 
        *,
        reason: str = "No reason provided."
    ):
        """
        Remove a user from the hardban.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT *
                FROM hardbanned
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (ctx.guild.id, user.id)
            )
            result = await cursor.fetchone()
            if not result:
                return await ctx.warn(f"{user.mention} is **not** hardbanned")
            
            await cursor.execute(
                """
                DELETE FROM hardbanned
                WHERE guild_id = ? 
                AND user_id = ?
                """,
                (ctx.guild.id, user.id)
            )
            await self.bot.db.commit()
        
        with suppress(NotFound, HTTPException):
            await ctx.guild.unban(user, reason=reason)
            if not await Invoke(ctx).send(user, reason):
                await ctx.approve(f"Successfully removed {user.mention} from the hardban - **{reason}**")

    @command(
        name="hardbanned"
    )
    @guild_only()
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def hardbanned(
        self, 
        ctx: Context
    ) -> Message:
        """
        List all the hardbanned users.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT user_id, reason
                FROM hardbanned
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            results = await cursor.fetchall()
            if not results:
                return await ctx.warn("No users are currently hardbanned")
        
        users = []
        for user_id, reason in results:
            user = self.bot.get_get_user(user_id) or await self.bot.fetch_user(user_id)
            if user:
                users.append(f"**{user.name}** (`{user.id}`) **{reason}**")
            else:
                users.append(f"**Unknown User** (`{user_id}`) **{reason}**")
        
        embed = Embed(
            color=config.Color.base,
            title="Hardbanned",
            description="\n".join(users))
        
        await ctx.paginate(embed)
    
    @command(
        name="tempban",
        usage="<member> <duration> [delete_days] [reason]",
        example="qmantha 1d12h 3 perms abuse"
    )
    @guild_only()
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def tempban(
        self,
        ctx: Context, 
        member: ValidMember, 
        duration: str,
        delete_days: Optional[int] = 0,
        *,
        reason: str = "No reason provided."
    ):
        """
        Temporarily ban a member from the server.
        """
        act = ctx.invoked_with
        if member.premium_since:
            await ctx.prompt(f"Are you sure you want to **{act}** {member.mention}?\nThey are currently boosting the server!")
            
        delta = humanize_duration(duration)
        if not delta:
            return await ctx.warn("Invalid duration format. Use a combination of `d`, `h`, `m`, and `s` (e.g., `3d5h20m7s`)")
        
        
        end_time = datetime.utcnow() + delta
        end_time_str = end_time.isoformat()


        await ctx.guild.ban(member, reason=reason, delete_message_days=delete_days)
        
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO tempban (guild_id, user_id, duration)
                VALUES (?, ?, ?)
                """,
                (ctx.guild.id, member.id, end_time_str)
            )
            await self.bot.db.commit()
        
        if not await Invoke(ctx).send(member, reason):
            await ctx.approve(f"Tempbanned {member.mention} ({human_timedelta(end_time)}) for the following reason: **{reason}**\nEnds in <t:{int(end_time.timestamp())}:R>")
    
    @command(
        name="tempbanned"
    )
    @guild_only()
    @has_permissions(view_audit_log=True, ban_members=True)
    @bot_has_permissions(embed_links=True)
    async def tempbanned(
        self,
        ctx: Context
    ) -> Message:
        """
        View a list of all the tempbanned members.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT user_id, duration
                FROM tempban
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            results = await cursor.fetchall()
            if not results:
                return await ctx.warn("There are no members are currently tempbanned")
        
        users = []
        for user_id, duration in results:
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            time = datetime.fromisoformat(duration)
            if user:
                users.append(f"**{user.name}** (`{user.id}`) ends <t:{int(time.timestamp())}:R>")
            else:
                users.append(f"**Unknown User** (`{user_id}`)")
        
        embed = Embed(
            color=config.Color.base,
            title="Tempbans",
            description="\n".join(users))
        
        await ctx.paginate(embed)
    
    @group(
        name="autoresponder",
        usage="(subcommand)",
        example="list",
        invoke_without_command=True,
        aliases=[
            "ar"
        ]
    )
    @guild_only()
    async def autoresponder(
        self, 
        ctx: Context
    ):
        """
        Set up automatic responder for a matching trigger.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @autoresponder.command(
        name="add",
        usage="<trigger>, <code> --params",
        example="pic perms, boost 4 pic {user.mention}! --reply"
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, embed_links=True)
    async def autoresponder_add(
        self,
        ctx: Context,
        *,
        code: str
    ):
        """
        Add a new autoresponder trigger and response.
        """
        try:
            main_content, *params = code.split(" --")
            trigger, response = map(str.strip, main_content.split(",", 1))

            if not trigger or not response:
                return await ctx.warn("Please provide both a **trigger** and **response**!")

            not_strict = "not_strict" in params
            delete_trigger = "delete" in params
            reply = "reply" in params

            async with self.bot.db.cursor() as cursor:
                await cursor.execute(
                    """
                    INSERT OR REPLACE INTO autoresponder (guild_id, trigger, response, not_strict, delete_trigger, reply) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ctx.guild.id,
                        trigger.lower(),
                        response,
                        not_strict,
                        delete_trigger,
                        reply
                    )
                )
                await self.bot.db.commit()

            param_list = []
            if not_strict:
                param_list.append("--not_strict")
            if delete_trigger:
                param_list.append("--delete")
            if reply:
                param_list.append("--reply")

            param_str = f" ({', '.join(param_list)})" if param_list else ""
            await ctx.approve(f"Created a new autoresponder with trigger **{trigger} (`{param_str}`)")

        except ValueError:
            return await ctx.warn("Invalid format! Use: `trigger, response [params]`")

    @autoresponder.command(
        name="remove",
        usage="<trigger>",
        example="hello",
        aliases=[
            "rmv"
        ]
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, embed_links=True)
    async def autoresponder_remove(
        self,
        ctx: Context,
        *, 
        trigger: str
    ):
        """
        Remove an autoresponder trigger.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                DELETE FROM autoresponder
                WHERE guild_id = ?
                AND trigger = ?
                """,
                (ctx.guild.id, trigger.lower())
            )
            await self.bot.db.commit()

            if cursor.rowcount > 0:
                await ctx.approve(f"Removed autoresponder trigger **{trigger}**")
            else:
                await ctx.warn(f"No autoresponder found with trigger **{trigger}**")

    @autoresponder.command(
        name="list"
    )
    @has_permissions(manage_guild=True)
    async def autoresponder_list(
        self,
        ctx: Context
    ) -> Message:
        """
        List all autoresponders trigger in the server.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT trigger, not_strict, delete_trigger, reply 
                FROM autoresponder
                WHERE guild_id = ? 
                """,
                (ctx.guild.id,)
            )
            results = await cursor.fetchall()
            if not results:
                return await ctx.warn("No autoresponders found for this server!")
        
        params = []
        for trigger, not_strict, delete_trigger, reply in results:
            if not_strict:
                params.append("`--not_strict`")
            if delete_trigger:
                params.append("`--delete`")
            if reply:
                params.append("`--reply`")
        
        params_results = ", ".join(params) if params else ""
        embed = Embed(
            color=config.Color.base,
            title="Autoresponders",
            description="\n".join(f"**{trigger}** {params_results}")
            )
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar.url)
        
        await ctx.paginate(embed)

    @autoresponder.command(
        name="reset"
    )
    @has_permissions(manage_guild=True)
    @bot_has_permissions(manage_guild=True)
    async def autoresponder_reset(
        self,
        ctx: Context
    ):
        """
        Reset all the autoresponder trigger in the server.
        """
        await ctx.prompt("Are you sure you want to **reset** all the autoresponder trigger for this server?")
        
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                DELETE FROM autoresponder
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            await self.bot.db.commit()
        
        await ctx.approve("Reset all the autoresponder trigger in the server")
            
    @autoresponder.command(
        name="view",
        usage="(trigger)",
        brief="Manage Guild",
        extras={
            "example": "pic perms"
        }
    )
    @has_permissions(manage_guild=True)
    async def autoresponder_view(
        self, 
        ctx: Context,
        *,
        trigger: str
    ):
        """
        View the raw response of an autoresponder trigger.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT response 
                FROM autoresponder
                WHERE guild_id = ? 
                AND trigger = ?
                """,
                (ctx.guild.id, trigger.lower())
            )
            result = await cursor.fetchone()
            if not result:
                return await ctx.warn(f"No autoresponder found with trigger **{trigger}**")

        response = result[0]
        await ctx.neutral(f"Current response for **{trigger}** trigger", code=f"```\n{response}\n```")

    @command(
        name='imute', 
        usage='<member> [channel]',
        example="qmantha"
    )
    @guild_only()
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, embed_links=True)
    async def imute(
        self,
        ctx: Context,
        member: ValidMember, 
        channel: TextChannel = None
    ):
        """
        Remove media permissions from a member in the current or mentioned channel.
        """
        act = ctx.invoked_with
        if member.bot:
            return await ctx.warn(f"You cannot {act} a bot.")
            
        channel = channel or ctx.channel
        
        overwrite = channel.overwrites_for(member)
        overwrite.attach_files = False
        overwrite.embed_links = False
        await channel.set_permissions(
            member, 
            overwrite=overwrite,
            reason=f"I-mute: {ctx.author} image muted {member.name}")
        
        await ctx.approve(f"Removed `attach_files` and `embed_links` permissions from {member.mention} in {channel.mention}")
    
    @command(
        name='iunmute', 
        usage='<member> [channel]',
        example="qmantha"
    )
    @guild_only()
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, embed_links=True)
    async def iunmute(
        self,
        ctx: Context, 
        member: ValidMember,
        channel: TextChannel = None
    ):
        """
        Restore media permissions for a member in the current or mentioned channel.
        """
        act = ctx.invoked_with
        if member.bot:
            return await ctx.warn(f"You cannot {act} a bot.")
            
        channel = channel or ctx.channel
        
        overwrite = channel.overwrites_for(member)
        overwrite.attach_files = True
        overwrite.embed_links = True
        await channel.set_permissions(
            member, 
            overwrite=overwrite,
            reason=f"I-unmute: {ctx.author.name} image unmuted {member.name}")
        
        await ctx.approve(f"Restored `attach_files` and `embed_links` permissions for {member.mention} in {channel.mention}")
    
    @command(
        name='rmute', 
        usage='<member> [channel]',
        example="qmantha"
    )
    @guild_only()
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, add_reactions=True)
    async def rmute(
        self, 
        ctx: Context,
        member: ValidMember,
        channel: TextChannel = None
    ):
        """
        Remove reaction permission from a member in the current or mentioned channel.
        """
        act = ctx.invoked_with
        if member.bot:
            return await ctx.warn(f"You cannot {act} a bot.")
            
        channel = channel or ctx.channel
        
        overwrite = channel.overwrites_for(member)
        overwrite.add_reactions = False
        await channel.set_permissions(
            member, 
            overwrite=overwrite,
            reason=f"R-mute: {ctx.author.name} reaction muted {member.name}")
       
        await ctx.approve(f"Removed reaction permission from {member.mention} in {channel.mention}")
    
    @command(
        name='runmute',
        usage='<member> [channel]',
        example="qmantha"
    )
    @guild_only()
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, add_reactions=True)
    async def runmute(
        self,
        ctx: Context,
        member: ValidMember,
        channel: TextChannel = None
    ):
        """
        Restore reaction permission for a member in the current or mentioned channel.
        """
        act = ctx.invoked_with
        if member.bot:
            return await ctx.warn(f"You cannot {act} a bot.")
            
        channel = channel or ctx.channel
    
        overwrite = channel.overwrites_for(member)
        overwrite.add_reactions = True
        await channel.set_permissions(
            member, 
            overwrite=overwrite,
            reason=f"R-unmute: {ctx.author.name} reaction unmuted {member.name}")
        
        await ctx.approve(f"Restored reaction permission for {member.mention} in {channel.mention}")
    
    # GUILDEDIT
    @group(
        name="guildedit",
        usage="(subcommand)",
        example="icon",
        invoke_without_command=True,
        aliases=[
            "ge"
        ]
    )
    @guild_only()
    async def guildedit(
        self, 
        ctx: Context
    ):
        """
        Edit various parts of the server.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help()
    
    @guildedit.command(
        name="name",
        usage="<name>",
        example="Chill Club"
    )
    @has_permissions(manage_guild=True)
    @bot_has_permissions(manage_guild=True)
    async def guildedit_name(
        self,
        ctx: Context,
        *,
        name: str
    ):
        """
        Change the server name.
        """
        name = shorten(name, 100)
        try:
            await ctx.guild.edit(name=name)
            await ctx.approve(f"Changed server name to **{name}**")
        except (Forbidden, HTTPException) as e:
            await ctx.deny(f"An error occurred\n```py\n{str(e)}```")

    @guildedit.command(
        name="description",
        usage="<description>",
        example="A place to chill and hangout...",
        extras={
            "note": "Type `none` to reset"
        },
        aliases=[
            "desc"
        ]
    )
    async def guildedit_description(
        self,
        ctx: Context,
        *, 
        description: str
    ):
        """
        Change the server description.
        """
        description = shorten(description, 100)
        
        if description == "none":
            try:
                await ctx.guild.edit(description=None)
                return await ctx.approve("Reset the server description")
            except:
                pass
            
        try:
            await ctx.guild.edit(description=description)
            await ctx.approve(f"Changed server description to **{description}**")
            
        except (Forbidden, HTTPException) as e:
            await ctx.deny(f"An error occurred\n```py\n{str(e)}```")

    @guildedit.command(
        name="icon",
        usage="[url or attachment]",
        example="https://",
        extras={
            "note": "Type `none` to reset"
        }
    )
    @cooldown(1, 10, BucketType.guild)
    @has_permissions(manage_guild=True)
    @bot_has_permissions(manage_guild=True)
    async def guildedit_icon(
        self,
        ctx: Context, 
        url: str = None
    ):
        """
        Change the server icon.
        """
        if url is None:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                return await ctx.warn("Please provide an icon URL or attach an image.")
        
        if url == "none":
            try:
                await ctx.guild.edit(icon=None)
                return await ctx.approve("Reset the server **icon**!")
            except:
                pass

        if not regex.IMAGE_URL.match(url):
            return await ctx.warn("Invalid **image url** given - check and try again.")

        try:
            async with self.bot.session.get(url) as response:
                if response.status in range(200, 299):
                    img_data = BytesIO(await response.read())
                    await ctx.guild.edit(icon=img_data.getvalue()
                    )
                    return await ctx.approve("Successfully changed the server **icon**!")
                else:
                    return await ctx.warn(f"Unable to change server **icon**. HTTP Status: {response.status}")
                    
        except (Forbidden, HTTPException) as e:
            return await ctx.deny(f"An error occurred\n```py\n{str(e)}```")

    @guildedit.command(
        name="banner",
        usage="<url or attachment>",
        example="https://",
        extras={
            "note": "Type `none` to reset"
        }
    )
    @cooldown(1, 10, BucketType.guild)
    @has_permissions(manage_guild=True)
    @bot_has_permissions(manage_guild=True)
    async def guildedit_banner(
        self, 
        ctx: Context, 
        url: str = None
    ):
        """
        Change the server banner.
        """
        if ctx.guild.premium_subscription_count < 7:
            return await ctx.warn("This server hasn't unlocked the banner feature.")

        if url is None:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                return await ctx.warn("Please provide a banner URL or attach an image.")
        
        if url == "none":
            try:
                await ctx.guild.edit(banner=None)
                return await ctx.approve("Reset the server **banner**!")
            except:
                pass

        if not regex.IMAGE_URL.match(url):
            return await ctx.warn("Invalid **image url** given - check and try again.")

        try:
            async with self.bot.session.get(url) as response:
                if response.status in range(200, 299):
                    img_data = BytesIO(await response.read())
                    await ctx.guild.edit(banner=img_data.getvalue()
                    )
                    return await ctx.approve("Successfully changed the server **banner**!")
                else:
                    return await ctx.warn(f"Unable to change server **banner**. HTTP Status: {response.status}")
                    
        except (Forbidden, HTTPException) as e:
            return await ctx.deny(f"An error occurred\n```py\n{str(e)}```")

    @guildedit.command(
        name="splash",
        usage="[url or attachment]",
        example="https://",
        extras={
            "note": "Type `none` to reset"
        }
    )
    @cooldown(1, 10, BucketType.guild)
    @has_permissions(manage_guild=True)
    @bot_has_permissions(manage_guild=True)
    async def guildedit_splash(
        self,
        ctx: Context, 
        url: str = None
    ):
        """
        Change the server splash.
        """
        if ctx.guild.premium_subscription_count < 14:
            return await ctx.warn("This server hasn't unlocked the splash feature.")

        if image_url is None:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                return await ctx.warn("Please provide a splash URL or attach an image.")
        
        if url == "none":
            try:
                await ctx.guild.edit(splash=None)
                return await ctx.approve("Reset the server **splash**!")
            except:
                pass

        if not regex.IMAGE_URL.match(url):
            return await ctx.warn("Invalid **image url** given - check and try again.")

        try:
            async with self.bot.session.get(url) as response:
                if response.status in range(200, 299):
                    img_data = BytesIO(await response.read()
                    )
                    await ctx.guild.edit(splash=img_data.getvalue())
                    return await ctx.approve("Successfully changed the server **splash**!")
                else:
                    return await ctx.warn(f"Unable to change server **splash**. HTTP Status: {response.status}")
                    
        except (Forbidden, HTTPException) as e:
            return await ctx.deny(f"An error occurred\n```py\n{str(e)}```")
    
    @guildedit.command(
        name="cover",
        usage="[url or attachment]",
        example="https://",
        extras={
            "note": "Type `none` to reset"
        },
        aliases=[
            "discoverycover",
            "discoverybanner"
        ]
    )
    @cooldown(1, 10, BucketType.guild)
    @has_permissions(manage_guild=True)
    @bot_has_permissions(manage_guild=True)
    async def guildedit_cover(
        self,
        ctx: Context, 
        url: str = None
    ):
        """
        Change the server discovery banner.
        """
        if ctx.guild.premium_subscription_count < 7:
            return await ctx.warn("This server hasn't unlocked the cover feature.")

        if image_url is None:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                return await ctx.warn("Please provide a cover URL or attach an image.")
        
        if url == "none":
            try:
                await ctx.guild.edit(discovery_splash=None)
                return await ctx.approve("Reset the server **cover**!")
            except:
                pass

        if not regex.IMAGE_URL.match(url):
            return await ctx.warn("Invalid **image url** given - check and try again.")

        try:
            async with self.bot.session.get(url) as response:
                if response.status in range(200, 299):
                    img_data = BytesIO(await response.read()
                    )
                    await ctx.guild.edit(discovery_splash=img_data.getvalue())
                    return await ctx.approve("Successfully changed the server **cover**!")
                else:
                    return await ctx.warn(f"Unable to change server **cover**. HTTP Status: {response.status}")
                    
        except (Forbidden, HTTPException) as e:
            return await ctx.deny(f"An error occurred\n```py\n{str(e)}```")
    
    @group(
        name="purge",
        usage="(subcommand) <args>",
        example="20",
        invoke_without_command=True
    )
    @guild_only()
    @cooldown(1, 5, BucketType.member)
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def purge(
        self, 
        ctx: Context,
        amount: int
    ):
        """
        Purge messages in the current channel (excluding pinned messages).
        """
        purged = await ctx.channel.purge(limit=amount, check=lambda m: not m.pinned, before=ctx.message)
        await ctx.approve(f"Deleted **{len(purged)}** messages", delete_after=6)

    @purge.command(
        name="member",
        usage="<member> <amount>",
        example="qmantha 15",
        aliases=[
            "members",
            "user",
            "users"
        ]
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def purge_member(
        self,
        ctx: Context,
        member: Member, 
        amount: int
    ):
        """
        Purge messages from a specific member.
        """
        purged = await ctx.channel.purge(limit=amount, check=lambda m: m.author == member, before=ctx.message)
        await ctx.approve(f"Deleted **{len(purge)}** messages sent by {member.mention}", delete_after=6)

    @purge.command(
        name="bot",
        usage="<amount>",
        example="10",
        aliases=[
            "bots",
            "app",
            "apps"
        ]
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def purge_bot(
        self,
        ctx: Context,
        amount: int
    ):
        """
        Purge messages sent by bots, including myself.
        """
        purged = await ctx.channel.purge(limit=amount, check=lambda m: m.author.bot, before=ctx.message)
        await ctx.approve(f"Deleted **{len(purged)}** messages sent by bots", delete_after=6)

    @purge.command(
        name="link",
        usage="<amount>",
        example="20",
        aliases=[
            "links"
        ]
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def purge_link(
        self, 
        ctx: Context,
        amount: int
    ):
        """
        Purge any messages containing links.
        """
        purged = await ctx.channel.purge(limit=amount, check=lambda m: re.search(regex.URL, m.content), before=ctx.message)
        await ctx.approve(f"Deleted **{len(purged)}** messages containing links", delete_after=6)
    
    @purge.command(
        name="emoji",
        usage="<amount>",
        example="30",
        aliases=[
            "emojis",
            "emote",
            "emotes"
        ]
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def purge_emoji(
        self,
        ctx: Context,
        amount: int
    ):
        """
        Purge any messages containing custom emojis.
        """
        purged = await ctx.channel.purge(limit=amount, check=lambda m: re.search(regex.DISCORD_EMOJI, m.content), before=ctx.message)
        await ctx.approve(f"Deleted **{len(purged)}** messages containing custom emojis", delete_after=6)

    @purge.command(
        name="file",
        usage="<amount>",
        example="5",
        aliases=[
            "files"
        ]
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def purge_file(
        self, 
        ctx: Context,
        amount: int
    ):
        """
        Purge messages containing files/attachments.
        """
        purged = await ctx.channel.purge(limit=amount, check=lambda m: bool(m.attachments), before=ctx.message)
        await ctx.approve(f"Deleted **{len(purged)}** messages containing files", delete_after=6)

    @purge.command(
        name="contain",
        usage="<text>",
        example="hello",
        aliases=[
            "contains"
        ]
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def purge_contain(
        self, 
        ctx: Context,
        *,
        text: str
    ):
        """
        Purge messages containing specific text (up to 100 messages).
        """
        purged = await ctx.channel.purge(limit=100, check=lambda m: text in m.content, before=ctx.message)
        await ctx.approve(f"Deleted **{len(purged)}** messages containing `{text}`", delete_after=6)

    @purge.command(
        name="startswith",
        usage="<amount>",
        example="5",
        aliases=[
            "sw", 
            "starts",
            "startwith"
        ]
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def purge_startswith(
        self,
        ctx: Context,
        *,
        text: str
    ):
        """
        Purge messages starting with specific text (up to 100 messages).
        """
        purged = await ctx.channel.purge(limit=100, check=lambda m: m.content.startswith(text), before=ctx.message)
        await ctx.approve(f"Deleted **{len(purged)}** messages starts with `{text}`", delete_after=6)

    @purge.command(
        name="endswith",
        usage="<amount>",
        example="5",
        aliases=[
            "ew", 
            "ends",
            "endwith"
        ]
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def purge_endswith(
        self,
        ctx: Context,
        *,
        text: str
    ):
        """
        Purge messages ending with specific text (up to 100 messages).
        """
        purged = await ctx.channel.purge(limit=100, check=lambda m: m.content.endswith(text), before=ctx.message)
        await ctx.approve(f"Deleted **{len(purged)}** messages ending with `{text}`", delete_after=6)

    @purge.command(
        name="cleanup",
        usage="<amount>",
        example="5"
    )
    @guild_only()
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def purge_cleanup(
        self,
        ctx: Context,
        amount: int = 15
    ):
        """
        Delete the last 15 commands (or a custom amount if provided).
        """
        if not ctx.author.guild_permissions.manage_messages and amount > 15:
            amount = 15

        prefixes = await self.bot.get_prefix(ctx.message)
        prefixes = tuple(filter(None, prefixes))

        purged = await ctx.channel.purge(limit=amount, check=lambda m: m.content.startswith(prefixes) or m.author == self.bot.user, before=ctx.message)
        await ctx.approve(f"Deleted **{len(purged)}** of my own messages", delete_after=6)
    
        # NSR
    @group(
        name="noselfreact",
        usage="(subcommand)",
        example="enable",
        invoke_without_command=True,
        aliases=[
            "nsr"
        ]
    )
    @guild_only()
    async def noselfreact(
        self,
        ctx: Context
    ):
        """
        Automatically remove member reaction when they react to their own message.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @noselfreact.command(
        name="toggle",
        usage="<true or false>",
        example="true"
    )
    @has_permissions(manage_guild=True)
    async def noselfreact_toggle(
        self,
        ctx: Context,
        state: bool
    ):
        """
        Toggle the no self-react system in the server.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO noselfreact (guild_id, is_enabled)
                VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET is_enabled = ?
                """,
                (ctx.guild.id, state, state)
            )
            await self.bot.db.commit()
        
        status = "enabled" if state else "disabled"
        await ctx.approve(f"Successfully **{status}** the no self-react")
    
    @command(
        name="setjail", 
        aliases=[
            "setupjail"
        ]
    )
    @guild_only()
    @has_permissions(manage_guild=True)
    @bot_has_permissions(manage_roles=True, manage_channels=True)
    async def setjail(
        self,
        ctx: Context
    ) -> Message:
        """
        Set up the jail system in the server.
        """
        await ctx.defer()
        
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT *
                FROM jail_config 
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            if await cursor.fetchone():
                return await ctx.warn("Jail is **already** configured in the server")
            
            msg = await ctx.loading("Configuring the jail system and creating the necessary role and channel")
            
            jail_role = await ctx.guild.create_role(
                name=f"{self.bot.user.name}-jail",
                color=Color.dark_grey(),
                reason=f"{ctx.author} configured the jail system"
            )
            
            for channel in ctx.guild.channels:
                try:
                    await channel.set_permissions(jail_role, view_channel=False)
                    await asyncio.sleep(3)
                except:
                    continue
            
            overwrites = {
                jail_role: PermissionOverwrite(view_channel=True),
                ctx.guild.default_role: PermissionOverwrite(view_channel=False)
            }
            
            jail_channel = await ctx.guild.create_text_channel(
                name="jail",
                overwrites=overwrites,
                reason=f"{ctx.author} configured the jail system"
            )
            
            await cursor.execute(
                """
                INSERT INTO jail_config (guild_id, channel_id, role_id)
                VALUES (?, ?, ?)
                """, 
                (ctx.guild.id, jail_channel.id, jail_role.id)
            )
            await self.bot.db.commit()
        
        await ctx.approve("Successfully configured the jail system!", previous_message=msg)
    
    @command(
        name="unsetjail",
        aliases=[
            "unsetupjail"
        ]
    )
    @has_permissions(manage_guild=True)
    @bot_has_permissions(manage_roles=True, manage_channels=True)
    async def unsetjail(
        self,
        ctx: Context
    ) -> Message:
        """
        Remove the jail system in the server.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT *
                FROM jail_config 
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            results = await cursor.fetchone()
            if not results:
                return await ctx.warn("Jail is **not** configured in the server")
            
            await ctx.prompt("Are you sure you want to **reset** the jail system?")
            
            role = ctx.guild.get_role(results[2])
            channel = ctx.guild.get_channel(results[1])
            
            if role:
                try:
                    await role.delete(reason=f"{ctx.author} removed the jail system")
                except:
                    pass
                
            if channel:
                try:
                    await channel.delete(reason=f"{ctx.author} removed the jail system")
                except:
                    pass
                
            await cursor.execute(
                """
                DELETE FROM jail_config 
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            await cursor.execute(
                """
                DELETE FROM jailed_members
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            await self.bot.db.commit()
                
        await ctx.approve("Successfully removed the jail system")

    @command(
        name="jail", 
        usage="<member> <duration> [reason]", 
        example="@user 3h Spamming"
    )
    @guild_only()
    @has_permissions(moderate_members=True)
    @bot_has_permissions(manage_roles=True)
    async def jail(
        self,
        ctx: Context, 
        member: ValidMember,
        duration: str,
        *, 
        reason: str = "No reason provided."
    ):
        """
        Jail a member in the server.
        """
        await ctx.defer()

        if member.bot:
            return await ctx.warn("You cannot jail a bot.")
        
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT *
                FROM jail_config 
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            results = await cursor.fetchone()
            if not results:
                return await ctx.warn(f"Jail system is **not** configured, use `{ctx.clean_prefix}setjail` to set it then try this command again.")
            
            await cursor.execute(
                """
                SELECT *
                FROM jailed_members
                WHERE guild_id = ?
                AND user_id = ?
                """, 
                (ctx.guild.id, member.id)
            )
            jailed = await cursor.fetchone()
            if jailed:
                return await ctx.warn(f"{member.mention} is **already** jailed!")
            
            delta = humanize_duration(duration)
            if not delta:
                return await ctx.warn("Invalid duration format. Use a combination of `d`, `h`, `m`, and `s` (e.g., `3d5h20m7s`)")
            
            jail_time = int(datetime.now().timestamp())
            duration_seconds = int(delta.total_seconds())
            unix_time = int((utcnow() + delta).timestamp())
            
            roles = [role.id for role in member.roles if not role.is_default() and not role.managed]
            jail_role = ctx.guild.get_role(results[2])
            
            if not jail_role:
                return await ctx.warn("I couldn't find the jail role! Please reconfigure the jail system.")
            
            await cursor.execute(
                """
                INSERT INTO jailed_members (guild_id, user_id, roles, jail_timestamp, duration)
                VALUES (?, ?, ?, ?, ?)
                """,
                (ctx.guild.id, member.id, json.dumps(roles), jail_time, duration_seconds))
            
            try:
                await member.edit(roles=[jail_role] + [role for role in member.roles if role.managed], reason=f"Jailed by {ctx.author} - {reason}")
            except HTTPException:
                await self.bot.db.rollback()
                return await ctx.deny("Failed to strip all the member roles")
            
            await self.bot.db.commit()
            
            channel = ctx.guild.get_channel(results[1])
            if channel:
                e = Embed(
                    color=config.Color.deny,
                    description=f"You have been jailed by {ctx.author.mention} for the following reason: **{reason}**")
                e.add_field(
                    name="**Duration**",
                    value=f"{human_timedelta(delta, suffix=False)} (<t:{unix_time}:R>)",
                    inline=False)
                e.set_author(
                    name=f"{member.name} ({member.id})",
                    icon_url=member.display_avatar.url)
                await channel.send(content=member.mention, embed=e)
        
        if not await Invoke(ctx).send(member, reason):
            await ctx.approve(f"Jailed {member.mention} ({human_timedelta(delta, suffix=False)}) for the following reason: **{reason}**")

    @command(
        name="unjail",
        usage="<member> [reason]",
        example="qmantha"
    )
    @guild_only()
    @has_permissions(moderate_members=True)
    @bot_has_permissions(manage_roles=True)
    async def unjail(
        self, 
        ctx: Context, 
        member: Member,
        reason: str = "No reason provided."
    ):
        """
        Unjail a member before their duration expires.
        """
        await ctx.defer()
        
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT role_id 
                FROM jail_config
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            results = await cursor.fetchone()
            if not results:
                return await ctx.warn(f"Jail system is **not** configured, use `{ctx.clean_prefix}setjail` to set it then try this command again.")
            
            await cursor.execute(
                """
                SELECT roles 
                FROM jailed_members
                WHERE guild_id = ? 
                AND user_id = ?
                """, 
                (ctx.guild.id, member.id)
            )
            jailed = await cursor.fetchone()
            if not jailed:
                return await ctx.warn(f"{member.mention} is **not** jailed!")
            
            jail_role = ctx.guild.get_role(results[0])
            roles_to_restore = [ctx.guild.get_role(rid) for rid in json.loads(jailed[0]) if rid]
            
            try:
                await member.remove_roles(jail_role, reason=f"Unjailed by {ctx.author}: {reason}")
                await member.add_roles(*filter(None, roles_to_restore), reason="Restoring pre-jail roles")
            except HTTPException:
                return await ctx.deny("Failed to unjail member")
            
            await cursor.execute(
                """
                DELETE FROM jailed_members 
                WHERE guild_id = ? AND user_id = ?
                """, 
                (ctx.guild.id, member.id)
            )
            await self.bot.db.commit()
            
            try:
                e = Embed(
                    color=config.Color.approve,
                    description=f"You have been unjailed by {ctx.author.mention} on **{ctx.guild.name}** for the following reason: **{reason}**"
                )
                e.set_author(
                    name=ctx.guild.name,
                    icon_url=ctx.guild.icon)
                await member.send(embed=e)
            except:
                pass
        
        if not await Invoke(ctx).send(member, reason):
            await ctx.approve(f"Successfully unjailed {member.mention} - **{reason}**")
    
    @group(
        name="stickymessage",
        usage="(subcommand)",
        example="add",
        invoke_without_command=True,
        aliases=[
            "stickymsg",
            "sticky",
            "sm"
        ]
    )
    @guild_only()
    async def stickymessage(
        self, 
        ctx: Context
    ):
        """
        Easily create a sticky message for a channel.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @stickymessage.command(
        name='add',
        usage="[channel] <code>",
        example="#media This isn't the channel to chat {user.mention}!"
    )
    @cooldown(1, 10, BucketType.member)
    @has_permissions(manage_guild=True)
    async def stickymessage_add(
        self, 
        ctx: Context,
        channel: Optional[TextChannel],
        *,
        code: str
    ):
        """
        Add a sticky message for a channel.
        """
        channel = channel or ctx.channel

        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT * 
                FROM stickymessage 
                WHERE guild_id = ?
                AND channel_id = ?
                """,
                (ctx.guild.id, channel.id)
            )
            result = await cursor.fetchone()
            if result:
                return await ctx.warn(f"{channel.mention} is **already** have a **stickymessage** set, remove it first then try this command again.")

            await cursor.execute(
                """
                INSERT INTO stickymessage (guild_id, channel_id, message) 
                VALUES (?, ?, ?)
                """,
                (ctx.guild.id, channel.id, code)
            )
            await self.bot.db.commit()

        await ctx.approve(f"Added a **stickymessage** for {channel.mention}")

    @stickymessage.command(
        name="remove",
        usage="<channel>",
        example="#media",
        aliases=[
            "rmv"
        ]
    )
    @cooldown(1, 10, BucketType.member)
    @has_permissions(manage_guild=True)
    async def stickymessage_remove(
        self, 
        ctx: Context,
        channel: TextChannel
    ):
        """
        Remove a sticky message from a channel.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT *
                FROM stickymessage
                WHERE guild_id = ?
                AND channel_id = ?
                """
                , 
                (ctx.guild.id, channel.id)
            )
            result = await cursor.fetchone()
            if not result:
                return await ctx.warn(f"{channel.mention} does **not** have a **stickymessage**")

            await cursor.execute(
                """
                DELETE FROM stickymessage
                WHERE guild_id = ?
                AND channel_id = ?
                """,
                (ctx.guild.id, channel.id)
            )
            await self.bot.db.commit()

        await ctx.approve(f"Removed a **stickymessage** from {channel.mention}")

    @stickymessage.command(
        name="view",
        usage="<channel>",
        example="#media"
    )
    @cooldown(1, 5, BucketType.member)
    @has_permissions(manage_guild=True)
    async def stickymessage_view(
        self, 
        ctx: Context,
        channel: TextChannel
    ):
        """
        View the sticky message of a channel.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT message 
                FROM stickymessage
                WHERE guild_id = ?
                AND channel_id = ?
                """,
                (ctx.guild.id, channel.id)
            )
            result = await cursor.fetchone()
            if not result:
                return await ctx.warn(f"{channel.mention} does **not** have a **stickymessage**")
        
        message = result[0]
        await ctx.neutral(f"Current stickymessage in {channel.mention}", code=message)

    @stickymessage.command(
        name="list"
    )
    @cooldown(1, 5, BucketType.member)
    @has_permissions(manage_guild=True)
    @bot_has_permissions(embed_links=True)
    async def stickymessage_list(
        self, 
        ctx: Context
    ) -> Message:
        """
        View a list of every existing sticky message in the server.
        """
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT channel_id
                FROM stickymessage
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            results = await cursor.fetchall()
            if not results:
                return await ctx.warn(f"This server doesn't have any **stickymessage** to show.")

        channels = []
        for (channel_id,) in results:
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                channels.append(f"{channel.mention} (`{channel.id}`)")
            else:
                channels.append(f"**Unknown Channel** (`{channel_id}`)")
        
        embed = Embed(
            color=config.Color.base,
            title="Stickymessages",
            description="\n".join(channels)
            )
        
        await ctx.paginate(embed)
    
    @stickymessage.command(
        name="reset"
    )
    @has_permissions(manage_guild=True)
    async def stickymessage_reset(
        self,
        ctx: Context
    ):
        """
        Reset every existing sticky message in the server.
        """
        await ctx.prompt("Are you sure you want to **reset** all the stickymessage in the server?")
        
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                DELETE FROM stickymessage
                WHERE guild_id = ?
                """,
                (ctx.guild.id,)
            )
            await self.bot.db.commit()
        
        await ctx.approve("Reset all the stickymessage in the server")
    
    @group(
        name="forcenickname",
        usage="(subcommand)",
        example="list"
        aliases=[
            "fn"
        ]
    )
    @guild_only()
    async def forcenickname(
        self,
        ctx: Context
    ):
        """
        Restrick a member nickname, prevent them to change their nickname.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help()
    
    

    @tasks.loop(minutes=1)
    async def check_jail_duration(self):
        async with self.bot.db.cursor() as cursor:
            current_time = int(datetime.now().timestamp())
            
            await cursor.execute(
                """
                SELECT guild_id, user_id, roles 
                FROM jailed_members 
                WHERE jail_timestamp + duration <= ?
                """,
                (current_time,)
            )
            jailed = await cursor.fetchall()
            for guild_id, user_id, roles in jailed:
                guild = self.bot.get_guild(guild_id)
                user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                if not guild:
                    continue
                
                member = guild.get_member(user_id) or await guild.fetch_member(user_id)
                if not member:
                    continue
                
                await cursor.execute(
                    """
                    SELECT *
                    FROM jail_config 
                    WHERE guild_id = ?
                    """,
                    (guild.id,)
                )
                result = await cursor.fetchone()
                if not result:
                    continue
                
                jail_role = guild.get_role(result[2])
                if not jail_role:
                    continue
                
                roles_to_restore = [guild.get_role(rid) for rid in json.loads(roles) if rid]
                
                try:
                    await member.remove_roles(jail_role, reason="Automatically unjailed as the duration has expired")
                    await member.add_roles(*filter(None, roles_to_restore), reason=f"Restoring previous {member.name} roles")
                except HTTPException:
                    continue
                
                await cursor.execute(
                    """
                    DELETE FROM jailed_members 
                    WHERE guild_id = ? 
                    AND user_id = ?
                    """,
                    (guild.id, user.id)
                )
                try:
                    e = Embed(
                        color=config.Color.approve,
                        description=f"You have been unjailed on **{guild.name}** as the duration has expired"
                    )
                    e.set_author(
                        name=guild.name,
                        icon_url=guild.icon)
                    await member.send(embed=e)
                except Forbidden:
                    pass
                
            await self.bot.db.commit()
    
    @tasks.loop(minutes=1)
    async def tempban_check(self):
        current_time = datetime.utcnow()
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                """
                SELECT guild_id, user_id, duration
                FROM tempban
                """
            )
            results = await cursor.fetchall()

            for guild_id, user_id, duration in results:
                end_time = datetime.fromisoformat(duration)
                if end_time <= current_time:
                    guild = self.bot.get_guild(guild_id)
                    user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                    if guild:
                        try:
                            await guild.unban(user, reason="Temporary ban")
                        except NotFound:
                            pass
                        except Exception as e:
                            print(f"Tempban error in {guild.name} ({guild.id}) for {user.name} ({user.id})\n{str(e)}")

                    await cursor.execute(
                        """
                        DELETE FROM tempban 
                        WHERE guild_id = ? 
                        AND user_id = ?
                        """,
                        (guild.id, user.id)
                    )
            
            await self.bot.db.commit()

async def setup(bot) -> None:
    await bot.add_cog(Moderation(bot))