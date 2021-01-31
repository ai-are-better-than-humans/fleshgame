import logic
import discord
from io import BytesIO


TOKEN = 'your-token'

global players
global Game

players = []
Game = None

colors = (0xFD2D00, 0x0092FD)
emojis = ["6️⃣", "5️⃣", "4️⃣", "3️⃣", "2️⃣", "1️⃣"]
wake_command = "pp!"
assets = 'assets'

client = discord.Client()


# Concatenates the images produced by the logic file and sends them as an embed
def send_board(brd_imgs):
    embed = discord.Embed(title=f"**Its** {players[Game.turn]}**'s Turn!**", description="Move your peices by reacting with a slot number!", color=colors[Game.turn])
    embed.set_footer(text="have fun lmfao")

    output_gif = BytesIO()
    brd_imgs[0].save(output_gif, save_all=True, format='GIF', append_images=brd_imgs, duration=1000)
    output_gif.seek(0)

    file = discord.File(output_gif, filename="image.gif")
    embed.set_image(url="attachment://image.gif")
    return file, embed

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="ur mom lmao"))

@client.event
async def on_message(message):
    global Game
    global players
    global current_embed

    if message.author == client.user:
        return

    async def end_game(response):
        global Game
        global players

        if (message.author in players or message.author.guild_permissions.administrator) and Game is not None:
            Game = None
            players = []

            await response.add_reaction("👍")

        # Some help commands if anyone is confused about why 'x' didnt work
        elif Game is not None and not (response.author in players or response.author.guild_permissions.administrator):
            await response.channel.send("You do not have permission to end this game")
        elif Game is None:
            await response.channel.send("There are no games to end")

    if message.content.startswith(wake_command + "endgame"):
        await end_game(message)

    def check(m):
        return ('y' in m.content.lower() or 'n' in m.content.lower()) and m.channel == message.channel and (m.author in players or message.author.guild_permissions.administrator)

    if message.content.startswith(wake_command + "help"):
        embed = discord.Embed(title=f"alright you dumb bitch",
                             description="*heres how this shit works*:", color=0x228B22)
        embed.add_field(name="First of all - im not teaching you this shit", value="Go to https://www.ymimports.com/pages/how-to-play-mancala if you really wanna learn, dont ask me",
                        inline=False)
        embed.add_field(name="If youre so much of a social outcast that you already know how to play",
                        value="Id suggest you find some friends, and if by gods grace they like you, use `pp!startgame @person` to play with them",
                        inline=True)
        embed.add_field(name="And when your friends realize they hate playing with you",
                        value="they can use `pp!endgame` to get the fuck out of there",
                        inline=True)
        embed.set_footer(text="git good smh my h")

        await message.channel.send(message.author.mention, embed=embed)

    if message.content.startswith(wake_command + "startgame") and len(message.mentions) > 0:
        if message.mentions[0] == client.user:
            await message.channel.send("Go find a friend, loser.")
            return

        elif len(players) != 0 and (message.author in players or message.author.guild_permissions.administrator):

            await message.channel.send("You are already playing a game. End this and start a new game? **(y/n)**")
            msg = await client.wait_for('message', check=check)

            if 'y' in msg.content.lower(): await end_game(msg)
            else: await message.channel.send("Canceling new game")

        players = [message.author, message.mentions[0]]
        Game = logic.Board(assets, 15)

        await message.channel.send(f"**Starting Mancala Game**\n    -{players[0].mention} vs {players[1].mention}")

        file, embed = send_board([Game.img_board.get_board(Game.turn)])
        current_embed = await message.channel.send(players[Game.turn].mention, file=file, embed=embed)

        for emoji in emojis:
            await current_embed.add_reaction(emoji)

    elif message.content.startswith(wake_command + "startgame") and len(message.mentions) == 0:
        await message.channel.send("You need one other person to start")
    elif message.content.startswith(wake_command + "startgame") and len(players) != 0:
        await message.channel.send("There is currently a game in progress")

@client.event
async def on_reaction_add(reaction, user):
    global Game
    global current_embed

    if user.bot or Game is None or reaction.message != current_embed: return
    if user != players[Game.turn] or reaction.emoji not in emojis or players == []: return

    imgs = Game.move(emojis.index(reaction.emoji))
    if imgs is not None:
        file, embed = send_board(imgs)
        current_embed = await reaction.message.channel.send(players[Game.turn].mention, file=file, embed=embed)

        for reaction.emoji in emojis:
            await current_embed.add_reaction(reaction.emoji)
    else:
        await reaction.message.channel.send(f"{players[Game.turn].mention}, that space is empty")

    # Since there is no logic to detect a win, i do that here in the bot section
    if sum(Game.board[0]) == 0 or sum(Game.board[1]) == 0:
        Game.goals[0] += sum(Game.board[0])
        Game.goals[1] += sum(Game.board[1])

        winner = Game.goals.index(max(Game.goals))

        embed = discord.Embed(title=f"**{players[winner]} WON!!!!!11!!1!!**", description="bitch got *played*", color=colors[winner])
        embed.set_footer(text="gg")

        embed.set_image(url=players[winner].avatar_url)
        final = await reaction.message.channel.send(players[winner].mention, embed=embed)
        await final.add_reaction("👍")

        players.clear()
        Game = None


client.run(TOKEN)
