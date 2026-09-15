import discord
from discord.ext import commands
import random
import asyncio
import aiohttp
import os
import datetime
import json
import math

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

LEVEL_FILE = "level_data.json"
CONFIG_FILE = "config_data.json"
SPAM_FILE = "spam_config.json"

def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_json(file, data):
    with open(file, "w") as f: json.dump(f, data, indent=4)

level_data = load_json(LEVEL_FILE)
config_data = load_json(CONFIG_FILE)
spam_config = load_json(SPAM_FILE)
spam_tracker = {}
auto_roles = {}
afk_users = {}
xp_cooldown = {}

jokes = ["Why did Blox Fruit go to school? To become more appeeling! 🍎","Your bounty so low, Marines use you as tutorial 😂","Bro still fighting with Combat, no Haki 💀"]
roasts = ["You fight like a level 1 bandit 💀","Your PvP so bad, NPCs dodge you","Go touch grass... I mean Sea Beasts","Your combo? Punch, miss, run 😂","Even Buggy would win against you"]
balls = ["Yes ✅","No ❌","Maybe 🤔","Definitely! 🔥","Never 💀","Ask again later","Absolutely not bruh"]
truths = ["What's your biggest secret? 🤫","Who do you have a crush on?","What's your worst Blox Fruits death?","Have you ever scammed?"]
dares = ["Send 'I love Blox Fruits' in general chat","Change your nickname to Noob for 10 min","Roast yourself 😂","Say you are level 1"]
wyr = ["Would you rather have permanent Dough or permanent Dragon? 🍩🐉","Would you rather be banned from Blox Fruits or Discord?","Would you rather fight 10 Sea Beasts or 1 admin?"]

@bot.event
async def on_ready():
    print(f'🔥 {bot.user} ONLINE - MEGA FUN BOT READY!')
    try:
        await bot.tree.sync()
        print('Slash commands synced!')
    except Exception as e:
        print(e)

@bot.event
async def on_member_join(member):
    role_id = auto_roles.get(member.guild.id) or config_data.get(str(member.guild.id), {}).get("autorole")
    if role_id:
        role = member.guild.get_role(role_id)
        if role:
            try: await member.add_roles(role)
            except: pass

def is_mod():
    def p(i: discord.Interaction): return i.user.guild_permissions.manage_messages
    return discord.app_commands.check(p)
def is_admin():
    def p(i: discord.Interaction): return i.user.guild_permissions.administrator
    return discord.app_commands.check(p)

# ========= ADMIN =========
@bot.tree.command(name="ban", description="Ban member [ADMIN]")
@is_admin()
async def ban(i: discord.Interaction, member: discord.Member, reason: str="No reason"):
    await member.ban(reason=reason)
    await i.response.send_message(f"🔨 {member.mention} BANNED | {reason}")

@bot.tree.command(name="kick", description="Kick member [ADMIN]")
@is_admin()
async def kick(i: discord.Interaction, member: discord.Member, reason: str="No reason"):
    await member.kick(reason=reason)
    await i.response.send_message(f"👢 {member.mention} KICKED | {reason}")

@bot.tree.command(name="timeout", description="Timeout member [ADMIN]")
@is_admin()
async def timeout_cmd(i: discord.Interaction, member: discord.Member, minutes: int, reason: str="No reason"):
    await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
    await i.response.send_message(f"⏰ {member.mention} timeout {minutes}min | {reason}")

@bot.tree.command(name="warn", description="Warn member [ADMIN]")
@is_admin()
async def warn(i: discord.Interaction, member: discord.Member, reason: str="No reason"):
    await i.response.send_message(f"⚠️ {member.mention} WARNED: {reason}")
    try: await member.send(f"Warned in {i.guild.name}: {reason}")
    except: pass

@bot.tree.command(name="autorole", description="Set auto role [ADMIN]")
@is_admin()
async def autorole(i: discord.Interaction, role: discord.Role):
    auto_roles[i.guild.id] = role.id
    gid = str(i.guild.id)
    if gid not in config_data: config_data[gid] = {}
    config_data[gid]["autorole"] = role.id
    save_json(CONFIG_FILE, config_data)
    await i.response.send_message(f"✅ Auto role -> {role.mention}")

@bot.tree.command(name="poll", description="Create a poll [ADMIN]")
@is_admin()
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str=None, option4: str=None):
    options = [option1, option2]
    if option3: options.append(option3)
    if option4: options.append(option4)
    emojis = ["1️⃣","2️⃣","3️⃣","4️⃣"]
    desc = ""
    for idx, opt in enumerate(options): desc += f"{emojis[idx]} {opt}\n"
    embed = discord.Embed(title=f"📊 {question}", description=desc, color=0x00ff00)
    embed.set_footer(text=f"Poll by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    for idx in range(len(options)): await msg.add_reaction(emojis[idx])

@bot.tree.command(name="clear", description="Delete messages [ADMIN]")
@is_admin()
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages!", ephemeral=True)

@bot.tree.command(name="lock", description="Lock channel [ADMIN]")
@is_admin()
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Channel locked!")

@bot.tree.command(name="unlock", description="Unlock channel [ADMIN]")
@is_admin()
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Channel unlocked!")

@bot.tree.command(name="addrole", description="Add role to user [ADMIN]")
@is_admin()
async def addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await interaction.response.send_message(f"✅ Added {role.mention} to {member.mention}")

@bot.tree.command(name="serverinfo", description="Server info [ADMIN]")
@is_admin()
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=f"📊 {g.name}", color=0x00ffff)
    embed.add_field(name="Owner", value=g.owner.mention if g.owner else "Unknown", inline=True)
    embed.add_field(name="Members", value=str(g.member_count), inline=True)
    embed.add_field(name="Created", value=g.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Boosts", value=str(g.premium_subscription_count), inline=True)
    embed.add_field(name="Channels", value=str(len(g.channels)), inline=True)
    embed.add_field(name="Roles", value=str(len(g.roles)), inline=True)
    if g.icon: embed.set_thumbnail(url=g.icon.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="User info [ADMIN]")
@is_admin()
async def userinfo(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title=f"👤 {member.name}", color=0x00ffff)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "Unknown", inline=True)
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
    embed.add_field(name="Roles", value=str(len(member.roles)-1), inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="nick", description="Change nickname [ADMIN]")
@is_admin()
async def nick(interaction: discord.Interaction, member: discord.Member, new_nickname: str):
    try:
        await member.edit(nick=new_nickname)
        await interaction.response.send_message(f"✅ Changed {member.mention} nickname to **{new_nickname}**")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I can't change that user! My role must be higher!", ephemeral=True)

@bot.tree.command(name="announce", description="Announce embed [ADMIN]")
@is_admin()
async def announce(interaction: discord.Interaction, channel: discord.TextChannel, message: str, title: str="📢 Announcement"):
    embed = discord.Embed(title=title, description=message, color=0xff0000)
    embed.set_footer(text=f"Announced by {interaction.user.name} | Blaze Fire 🔥")
    if interaction.guild.icon: embed.set_thumbnail(url=interaction.guild.icon.url)
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Announced in {channel.mention}!", ephemeral=True)

# LV SYSTEM - GROUP
lv_group = discord.app_commands.Group(name="lv", description="Leveling system")

@lv_group.command(name="setup", description="Setup leveling channel [ADMIN]")
@is_admin()
async def lv_setup(interaction: discord.Interaction, channel: discord.TextChannel):
    gid = str(interaction.guild.id)
    if gid not in config_data: config_data[gid] = {}
    config_data[gid]["level_channel"] = channel.id
    save_json(CONFIG_FILE, config_data)
    await interaction.response.send_message(f"✅ Level up messages will be sent in {channel.mention}!\nSystem: **MEE6 Style XP 15-25 per minute** 🔥")

@lv_group.command(name="setup_channel", description="Setup leveling channel [ADMIN] (alias)")
@is_admin()
async def lv_setup_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    gid = str(interaction.guild.id)
    if gid not in config_data: config_data[gid] = {}
    config_data[gid]["level_channel"] = channel.id
    save_json(CONFIG_FILE, config_data)
    await interaction.response.send_message(f"✅ Level up channel set to {channel.mention}! MEE6 Style XP")

bot.tree.add_command(lv_group)

# ========= SPAM SYSTEM - GROUP =========
spam_group = discord.app_commands.Group(name="spam", description="Anti-spam system")

@spam_group.command(name="setup", description="Setup anti-spam system [ADMIN]")
@is_admin()
async def spam_setup(interaction: discord.Interaction, log_channel: discord.TextChannel=None):
    gid = str(interaction.guild.id)
    if gid not in spam_config:
        spam_config[gid] = {}
    spam_config[gid]["enabled"] = True
    if log_channel:
        spam_config[gid]["log_channel"] = log_channel.id
    save_json(SPAM_FILE, spam_config)
    await interaction.response.send_message(f"✅ Anti-Spam ENABLED! 3 msgs in 5 sec = Spam\n- Will DM all Admins with server & user info\n- Auto-delete spam\n{f'- Logs in {log_channel.mention}' if log_channel else ''}")

@spam_group.command(name="disable", description="Disable anti-spam [ADMIN]")
@is_admin()
async def spam_disable(interaction: discord.Interaction):
    gid = str(interaction.guild.id)
    if gid in spam_config:
        spam_config[gid]["enabled"] = False
        save_json(SPAM_FILE, spam_config)
    await interaction.response.send_message("❌ Anti-Spam DISABLED!", ephemeral=True)

bot.tree.add_command(spam_group)

async def handle_spam(guild, member, channel):
    gid = str(guild.id)
    if gid not in spam_config or not spam_config[gid].get("enabled"):
        return False
    now = datetime.datetime.now().timestamp()
    if gid not in spam_tracker: spam_tracker[gid] = {}
    uid = str(member.id)
    if uid not in spam_tracker[gid]: spam_tracker[gid][uid] = []
    spam_tracker[gid][uid].append(now)
    spam_tracker[gid][uid] = [t for t in spam_tracker[gid][uid] if now - t < 5]
    if len(spam_tracker[gid][uid]) >= 3:
        spam_tracker[gid][uid] = []
        try:
            def check(m):
                return m.author.id == member.id and (now - m.created_at.timestamp() < 6)
            deleted = await channel.purge(limit=10, check=check)
        except:
            deleted = []
        admins = [m for m in guild.members if m.guild_permissions.administrator and not m.bot]
        for admin in admins:
            try:
                embed = discord.Embed(title="🚨 SPAM DETECTED!", color=0xff0000, timestamp=datetime.datetime.now())
                embed.add_field(name="Server", value=f"**{guild.name}**\nID: {guild.id}", inline=False)
                embed.add_field(name="Spammer", value=f"{member.mention}\n`{member.name}` | {member.id}", inline=False)
                embed.add_field(name="Channel", value=f"{channel.mention}", inline=False)
                embed.add_field(name="Deleted", value=f"{len(deleted)} msgs deleted", inline=False)
                embed.set_thumbnail(url=member.display_avatar.url)
                await admin.send(embed=embed)
            except: pass
        if "log_channel" in spam_config.get(gid, {}):
            ch = guild.get_channel(spam_config[gid]["log_channel"])
            if ch:
                try:
                    await ch.send(embed=discord.Embed(title="🚨 Spam", description=f"{member.mention} spammed in {channel.mention} - {len(deleted)} msgs deleted", color=0xff0000))
                except: pass
        try:
            await channel.send(f"🧹 Anti-Spam: Deleted {len(deleted)} msgs from {member.mention}! No spamming! (3 msgs / 5s)", delete_after=5)
        except: pass
        return True
    return False

# ========= MOD =========
@bot.tree.command(name="meme", description="Random meme [MOD]")
@is_mod()
async def meme(i: discord.Interaction):
    async with aiohttp.ClientSession() as s:
        async with s.get("https://meme-api.com/gimme") as r:
            d = await r.json()
            e = discord.Embed(title=d['title'], color=0xff4500)
            e.set_image(url=d['url'])
            await i.response.send_message(embed=e)

@bot.tree.command(name="giveaway", description="Start giveaway [MOD]")
@is_mod()
async def giveaway(i: discord.Interaction, prize: str, minutes: int=1):
    e = discord.Embed(title="🎉 GIVEAWAY 🎉", description=f"Prize: **{prize}**\nReact 🎉 to enter!\nEnds in {minutes}m", color=0xffd700)
    await i.response.send_message(embed=e)
    msg = await i.original_response()
    await msg.add_reaction("🎉")
    await asyncio.sleep(minutes*60)
    msg = await i.channel.fetch_message(msg.id)
    users = [u async for u in msg.reactions[0].users() if not u.bot]
    if users: await i.channel.send(f"🎉 Winner of **{prize}** is {random.choice(users).mention}!")
    else: await i.channel.send("No one entered 😢")

# ========= EVERYONE =========
@bot.tree.command(name="ping", description="Bot ping")
async def ping(i: discord.Interaction): await i.response.send_message(f"🏓 {round(bot.latency*1000)}ms")
@bot.tree.command(name="membercount", description="Member count")
async def membercount(i: discord.Interaction): await i.response.send_message(f"👥 **{i.guild.member_count}** members in **{i.guild.name}**")
@bot.tree.command(name="8ball", description="Magic 8ball")
async def eightball(i: discord.Interaction, question: str): await i.response.send_message(f"🎱 Q: {question}\nA: {random.choice(balls)}")
@bot.tree.command(name="joke", description="Random joke")
async def joke(i: discord.Interaction): await i.response.send_message(random.choice(jokes))
@bot.tree.command(name="roast", description="Roast someone")
async def roast(i: discord.Interaction, member: discord.Member=None):
    t = member.mention if member else i.user.mention
    await i.response.send_message(f"{t} {random.choice(roasts)}")
@bot.tree.command(name="roll", description="Roll dice 1-100")
async def roll(i: discord.Interaction): await i.response.send_message(f"🎲 {random.randint(1,100)}")
@bot.tree.command(name="coinflip", description="Flip coin")
async def coinflip(i: discord.Interaction): await i.response.send_message(f"🪙 **{random.choice(['Heads','Tails'])}**!")
@bot.tree.command(name="rps", description="Rock Paper Scissors")
async def rps(i: discord.Interaction, choice: str):
    bot_choice = random.choice(["rock","paper","scissors"])
    result = "Tie! 🤝"
    if choice.lower() not in bot_choice:
        if (choice=="rock" and bot_choice=="scissors") or (choice=="paper" and bot_choice=="rock") or (choice=="scissors" and bot_choice=="paper"): result="You WIN! 🎉"
        else: result="You LOSE! 💀"
    await i.response.send_message(f"You: {choice} | Bot: {bot_choice} -> {result}")
@bot.tree.command(name="ship", description="Ship 2 people ❤️")
async def ship(i: discord.Interaction, person1: discord.Member, person2: discord.Member):
    percent = random.randint(0,100)
    await i.response.send_message(f"💘 {person1.mention} + {person2.mention} = **{percent}%** {'Perfect match! ❤️🔥' if percent>80 else 'Not bad 😉' if percent>50 else 'Oof... 💀'}")
@bot.tree.command(name="avatar", description="Show avatar")
async def avatar(i: discord.Interaction, member: discord.Member=None):
    m = member or i.user
    e = discord.Embed(title=f"{m.name}'s avatar", color=0x00ffff)
    e.set_image(url=m.display_avatar.url)
    await i.response.send_message(embed=e)
@bot.tree.command(name="howgay", description="How gay? 🌈")
async def howgay(i: discord.Interaction, member: discord.Member=None):
    m = member or i.user
    await i.response.send_message(f"🌈 {m.mention} is **{random.randint(0,100)}%** gay!")
@bot.tree.command(name="pp", description="pp size 💀")
async def pp(i: discord.Interaction, member: discord.Member=None):
    m = member or i.user
    size = random.randint(0,15)
    await i.response.send_message(f"🍆 {m.mention}'s pp: 8{'='*size}D ({size}cm)")
@bot.tree.command(name="hug", description="Hug someone 🤗")
async def hug(i: discord.Interaction, member: discord.Member): await i.response.send_message(f"🤗 {i.user.mention} hugged {member.mention}! So cute!")
@bot.tree.command(name="slap", description="Slap someone 👊")
async def slap(i: discord.Interaction, member: discord.Member): await i.response.send_message(f"👊 {i.user.mention} slapped {member.mention}! OUCH!")
@bot.tree.command(name="kiss", description="Kiss someone 😘")
async def kiss(i: discord.Interaction, member: discord.Member): await i.response.send_message(f"😘 {i.user.mention} kissed {member.mention}! Awww!")
@bot.tree.command(name="say", description="Make bot say something")
async def say(i: discord.Interaction, text: str): await i.response.send_message(text)
@bot.tree.command(name="truth", description="Truth question")
async def truth(i: discord.Interaction): await i.response.send_message(f"🤔 Truth: {random.choice(truths)}")
@bot.tree.command(name="dare", description="Dare challenge")
async def dare(i: discord.Interaction): await i.response.send_message(f"😈 Dare: {random.choice(dares)}")
@bot.tree.command(name="wyr", description="Would you rather")
async def wyr_cmd(i: discord.Interaction): await i.response.send_message(f"🤨 {random.choice(wyr)}")
@bot.tree.command(name="compliment", description="Give compliment")
async def compliment(i: discord.Interaction, member: discord.Member):
    comps = ["You are cracked at Blox Fruits! 🔥","Your grinding is insane!","You look like a future Pirate King! 👑","Your bounty should be 30M!"]
    await i.response.send_message(f"✨ {member.mention} {random.choice(comps)}")
@bot.tree.command(name="afk", description="Set AFK status")
async def afk(interaction: discord.Interaction, reason: str="AFK"):
    afk_users[interaction.user.id] = reason
    await interaction.response.send_message(f"💤 {interaction.user.mention} is now AFK: {reason}")
@bot.tree.command(name="balance", description="Check your coins [ECONOMY]")
async def balance(i: discord.Interaction): await i.response.send_message(f"💰 {i.user.mention} has **{random.randint(100,5000)}** coins!")
@bot.tree.command(name="daily", description="Daily coins [ECONOMY]")
async def daily(i: discord.Interaction): await i.response.send_message(f"✅ {i.user.mention} claimed 500 daily coins! Come back tomorrow!")

@bot.tree.command(name="rank", description="Check your level [LEVELING]")
async def rank_cmd(i: discord.Interaction, member: discord.Member=None):
    m = member or i.user
    gid = str(i.guild.id)
    uid = str(m.id)
    data = level_data.get(gid, {}).get(uid, {"xp":0, "level":0, "msgs":0})
    xp = data.get("xp", 0)
    lvl = data.get("level", 0)
    next_xp = int(((lvl+1)/0.1)**2)
    curr_xp = int((lvl/0.1)**2)
    need = next_xp - xp
    prog = xp - curr_xp
    total = next_xp - curr_xp
    pct = prog/total if total else 0
    bar = "█"*int(pct*10) + "░"*(10-int(pct*10))
    embed = discord.Embed(title=f"⭐ {m.display_name}'s Rank", color=0x5865F2)
    embed.add_field(name="Level", value=str(lvl), inline=True)
    embed.add_field(name="XP", value=f"{xp} / {next_xp}", inline=True)
    embed.add_field(name="Progress", value=f"`{bar}` {int(pct*100)}%\n{need} XP to next level!", inline=False)
    embed.set_thumbnail(url=m.display_avatar.url)
    await i.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="Top 10 leaderboard")
async def leaderboard(i: discord.Interaction):
    gid = str(i.guild.id)
    if gid not in level_data or not level_data[gid]:
        await i.response.send_message("No data yet!")
        return
    sorted_users = sorted(level_data[gid].items(), key=lambda x: x[1].get("xp",0), reverse=True)[:10]
    desc = ""
    for idx, (uid, data) in enumerate(sorted_users, 1):
        desc += f"**{idx}.** <@{uid}> — Level **{data.get('level',0)}** ({data.get('xp',0)} XP)\n"
    embed = discord.Embed(title=f"🏆 {i.guild.name} Leaderboard", description=desc, color=0xFFD700)
    await i.response.send_message(embed=embed)

@bot.tree.command(name="help", description="List all bot commands [UTILITY]")
async def help_cmd(i: discord.Interaction):
    embed = discord.Embed(title="🔥 Rexo - Blaze Fire Bot | All Commands", description="Blaze Fire Community's ultimate bot! MEE6 style leveling!", color=0xff0000)
    embed.add_field(name="🛡️ Admin", value="`/ban, /kick, /timeout, /warn, /clear, /lock, /unlock, /addrole, /autorole, /poll, /serverinfo, /userinfo, /nick, /announce, /lv setup, /spam setup`", inline=False)
    embed.add_field(name="🎮 Fun & Game", value="`/8ball, /joke, /roast, /roll, /coinflip, /rps, /ship, /howgay, /pp, /truth, /dare, /wyr, /compliment`", inline=False)
    embed.add_field(name="💬 Social", value="`/hug, /slap, /kiss, /avatar, /say, /afk`", inline=False)
    embed.add_field(name="💰 Economy", value="`/balance, /daily`", inline=False)
    embed.add_field(name="⭐ Leveling [MEE6 STYLE]", value="`/rank, /leaderboard` - 15-25 XP per 60s! Level = 0.1 * sqrt(XP)", inline=False)
    embed.add_field(name="🚨 Anti-Spam", value="`/spam setup, /spam disable` - 3 msgs / 5 sec = delete + DM Admins", inline=False)
    embed.add_field(name="🛠️ Utility", value="`/ping, /membercount, /meme, /giveaway, /help`", inline=False)
    embed.set_footer(text="Blaze Fire Community 🔥 | MEE6 Style XP + Anti-Spam")
    await i.response.send_message(embed=embed)

# ========= MEE6 STYLE LV + SPAM =========
@bot.event
async def on_message(message):
    if message.author.bot: return

    if message.guild:
        # ANTI-SPAM CHECK FIRST
        if await handle_spam(message.guild, message.author, message.channel):
            return

        gid = str(message.guild.id)
        uid = str(message.author.id)
        now = datetime.datetime.now().timestamp()

        if uid not in xp_cooldown or now - xp_cooldown[uid] >= 60:
            xp_cooldown[uid] = now
            xp_gain = random.randint(15, 25)

            if gid not in level_data: level_data[gid] = {}
            if uid not in level_data[gid]: level_data[gid][uid] = {"xp":0, "level":0, "msgs":0}
            if "xp" not in level_data[gid][uid]: level_data[gid][uid]["xp"] = 0
            if "msgs" not in level_data[gid][uid]: level_data[gid][uid]["msgs"] = 0

            level_data[gid][uid]["xp"] += xp_gain
            level_data[gid][uid]["msgs"] += 1

            old_level = level_data[gid][uid]["level"]
            new_level = int(0.1 * math.sqrt(level_data[gid][uid]["xp"]))

            if new_level > old_level:
                level_data[gid][uid]["level"] = new_level
                save_json(LEVEL_FILE, level_data)
                if gid in config_data and "level_channel" in config_data[gid]:
                    ch_id = config_data[gid]["level_channel"]
                    ch = message.guild.get_channel(ch_id)
                    if ch:
                        embed = discord.Embed(title="🎉 LEVEL UP!", description=f"GG {message.author.mention}! You reached **Level {new_level}**! 🔥", color=0x00ff00)
                        embed.set_thumbnail(url=message.author.display_avatar.url)
                        try: await ch.send(embed=embed)
                        except: pass
            else:
                if random.random() < 0.15:
                    save_json(LEVEL_FILE, level_data)
        else:
            if gid in level_data and uid in level_data[gid]:
                level_data[gid][uid].setdefault("msgs",0)
                level_data[gid][uid]["msgs"] += 1

    if message.author.id in afk_users and not message.content.startswith("!"):
        del afk_users[message.author.id]
        await message.channel.send(f"👋 Welcome back {message.author.mention}! AFK removed.")
    for uid, rsn in afk_users.items():
        if f"<@{uid}>" in message.content or f"<@!{uid}>" in message.content:
            await message.channel.send(f"💤 <@{uid}> is AFK: {rsn}")
            break
    await bot.process_commands(message)

bot.run(TOKEN)
