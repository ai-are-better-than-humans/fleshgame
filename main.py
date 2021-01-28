import logic
import discord


TOKEN = 'your-token'

global players
global Game

players = []
Game = None

emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
assets = 'assets'

client = discord.Client()
wake_command = "pp!"

def send_board(brd_imgs):
    colors = (0xFD2D00, 0x0092FD)

    embed = discord.Embed(title=f"**Its** {players[Game.turn]}**'s Turn!**", description="Move your peices by reacting with a slot number!", color=colors[Game.turn])
    embed.set_footer(text="have fun lmfao")

    brd_imgs[0].save(f'gif_files\current_board.gif', save_all=True, append_images=brd_imgs, duration=1000)
    file = discord.File("gif_files\current_board.gif", filename="image.gif")
    embed.set_image(url="attachment://image.gif")
    return file, embed

@client.event
async def on_message(message):
    global Game
    if message.author == client.user:
        return

    if message.content.startswith(wake_command + "endgame") and message.author in players and Game is not None:
        Game = None
        players.clear()
        await message.add_reaction("👍")
    elif message.content.startswith(wake_command + "endgame") and Game is None:
        await message.channel.send("There are no games to end")

    if message.content.startswith(wake_command + "startgame") and len(message.mentions) > 0 and len(players) == 0:
        if message.mentions[0] == client.user:
            await message.channel.send("Go find a friend, loser.")
            return

        players.append(message.author)
        players.append(message.mentions[0])

        Game = logic.Board(assets, 15)
        await message.channel.send(f"**Starting Mancala Game**\n    -{players[0].mention} vs {players[1].mention}")

        file, embed = send_board([Game.img_board.get_board(Game.turn)[Game.turn]])
        start_grid = await message.channel.send(file=file, embed=embed)
        await message.channel.send(players[Game.turn].mention)

        for emoji in emojis:
            await start_grid.add_reaction(emoji)
    elif len(players) != 0:
        message.channel.send("You need one other person to start")

@client.event
async def on_reaction_add(reaction, user):
    global Game
    emoji = reaction.emoji

    if user.bot or len(players) == 0: return
    if user != players[Game.turn] or emoji not in emojis: return

    imgs = Game.move(emojis.index(emoji))
    if imgs is not None:
        file, embed = send_board(imgs[Game.turn])
        next_board = await reaction.message.channel.send(file=file, embed=embed)
        await reaction.message.channel.send(players[Game.turn].mention)

        for emoji in emojis:
            await next_board.add_reaction(emoji)
    else:
        await reaction.message.channel.send(f"{players[Game.turn].mention}, that space is empty")

    if sum(Game.board[0]) == 0 or sum(Game.board[1]) == 0:
        Game.goals[0] += sum(Game.board[0])
        Game.goals[1] += sum(Game.board[1])

        winner = Game.goals.index(max(Game.goals))
        colors = (0xFD2D00, 0x0092FD)
        await reaction.message.channel.send(players[winner].mention)

        embed = discord.Embed(title=f"**{players[winner]} WON!!!!!11!!1!!**", color=colors[winner])
        embed.set_footer(text="gg")

        embed.set_image(url=players[winner].avatar_url)
        final = await reaction.message.channel.send(embed=embed)
        await final.add_reaction("👍")
        players.clear()

        Game = None


client.run(TOKEN)