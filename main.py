import logic
import discord


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

    brd_imgs[0].save(f'gif_files\current_board.gif', save_all=True, append_images=brd_imgs, duration=1000)
    file = discord.File("gif_files\current_board.gif", filename="image.gif")
    embed.set_image(url="attachment://image.gif")
    return file, embed

@client.event
async def on_message(message):
    global Game
    global players
    global current_embed

    if message.author == client.user:
        return

    if message.content.startswith(wake_command + "endgame") and (message.author in players or message.author.guild_permissions.administrator) and Game is not None:
        Game = None
        players = []

        await message.add_reaction("👍")

    # Some help commands if anyone is confused about why 'x' didnt work
    elif message.content.startswith(wake_command + "endgame") and Game is not None and not (message.author in players or message.author.guild_permissions.administrator):
        await message.channel.send("You do not have permission to end this game")
    elif message.content.startswith(wake_command + "endgame") and Game is None:
        await message.channel.send("There are no games to end")

    if message.content.startswith(wake_command + "startgame") and len(message.mentions) > 0 and len(players) == 0:
        if message.mentions[0] == client.user:
            await message.channel.send("Go find a friend, loser.")
            return

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
    if user != players[Game.turn] or reaction.emoji not in emojis: return

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

        embed = discord.Embed(title=f"**{players[winner]} WON!!!!!11!!1!!**", color=colors[winner])
        embed.set_footer(text="gg")

        embed.set_image(url=players[winner].avatar_url)
        final = await reaction.message.channel.send(players[winner].mention, embed=embed)
        await final.add_reaction("👍")

        players.clear()
        Game = None


client.run(TOKEN)
