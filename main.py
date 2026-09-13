import discord
from discord.ext import commands
import random
import asyncio
import aiohttp
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

jokes = ["Why did Blox Fruit go to school? To become more appeeling! 🍎","Your bounty so low, Marines use you as tutorial 😂","Bro still fighting with Combat, no Haki 💀"]
roasts = ["You fight like a level 1 bandit 💀","Your PvP so bad, NPCs dodge you","Go touch grass... I mean Sea Beasts","Your combo? Punch, miss, run 😂","Even Buggy would win against you"]
balls = ["Yes ✅","No ❌","Maybe 🤔","Definitely! 🔥","Never 💀","Ask again later","Absolutely not bruh"]
truths = ["What's your biggest secret? 🤫","Who do you have a crush on?","What's your worst Blox Fruits death?","Have you ever scammed?"]
dares = ["Send 'I love Blox Fruits' in general chat","Change your nickname to Noob for 10 min","Roast yourself 😂","Say you are level 1"]
wyr = ["Would you rather have permanent Dough or permanent Dragon? 🍩🐉","Would you rather be banned from Blox Fruits or Discord?","Would you rather fight 10 Sea Beasts or 1 admin?"]

auto_roles = {}
afk_users = {}

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
    role_id = auto_roles.get(member.guild.id)
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
async def timeout(i: discord.Interaction, member: discord.Member, minutes: int, reason: str="No reason"):
    await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=minutes), reason=reason)
    await i.response.send_message(f"⏰ {member.mention} timeout {minutes}min")

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
    await i.response.send_message(f"✅ Auto role -> {role.mention}")

@bot.tree.command(name="poll", description="Create a poll [ADMIN]")
@is_admin()
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str=None, option4: str=None):
    options = [option1, option2]
    if option3: options.append(option3)
    if option4: options.append(option4)
    emojis = ["1️⃣","2️⃣","3️⃣","4️⃣"]
    desc = ""
    for idx, opt in enumerate(options):
        desc += f"{emojis[idx]} {opt}\n"
    embed = discord.Embed(title=f"📊 {question}", description=desc, color=0x00ff00)
    embed.set_footer(text=f"Poll by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    for idx in range(len(options)):
        await msg.add_reaction(emojis[idx])

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
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
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

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.author.id in afk_users and not message.content.startswith("!"):
        del afk_users[message.author.id]
        await message.channel.send(f"👋 Welcome back {message.author.mention}! AFK removed.")
    for uid, rsn in afk_users.items():
        if f"<@{uid}>" in message.content or f"<@!{uid}>" in message.content:
            await message.channel.send(f"💤 <@{uid}> is AFK: {rsn}")
            break
    await bot.process_commands(message)

bot.run(TOKEN)
