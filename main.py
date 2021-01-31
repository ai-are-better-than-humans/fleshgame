import logic
import discord
from io import BytesIO


TOKEN = 'your-token'

global players
global Game

players = []
Game = []

colors = (0xFD2D00, 0x0092FD)
emojis = ["6️⃣", "5️⃣", "4️⃣", "3️⃣", "2️⃣", "1️⃣"]
wake_command = "pp!"
assets = 'assets'

client = discord.Client()


# Concatenates the images produced by the logic file and sends them as an embed
def send_board(brd_imgs, index):
    embed = discord.Embed(title=f"**Its** {players[index][Game[index][0].turn]}**'s Turn!**", description="Move your peices by reacting with a slot number!", color=colors[Game[index][0].turn])
    embed.set_footer(text="have fun lmfao")

    output_gif = BytesIO()
    brd_imgs[0].save(output_gif, save_all=True, format='GIF', append_images=brd_imgs, duration=1000)
    output_gif.seek(0)

    file = discord.File(output_gif, filename="image.gif")
    embed.set_image(url="attachment://image.gif")
    return file, embed

# Grabs the index of the current player
def player_index(author):
    games = [j for j, i in enumerate(players) if author.id in (i[0].id, i[1].id)]
    if len(games) > 0:
        return games[0]
    return False

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="ur mom lmao"))

@client.event
async def on_message(message):
    global Game
    global players

    if message.author == client.user:
        return
    if message.channel.type is discord.ChannelType.private:
        await message.channel.send("Why are you dm'ing me\n*im a fucking robot*")
        return

    async def end_game(response):
        games = player_index(message.author)
        if games is not False:
            Game.pop(games)
            players.pop(games)

            await response.add_reaction("👍")

        else:
            await response.channel.send("You are not currently in a game")


    if message.content.startswith(wake_command + "endgame"):
        await end_game(message)

    if message.content.startswith(wake_command + "endall") and message.author.guild_permissions.administrator:
        games = [j for j, i in enumerate(Game) if i[1].guild == message.guild]

        if len(games) > 0:
            for i in games:
                Game.pop(i)
                players.pop(i)

            await message.add_reaction("👍")
        else:
            await message.channel.send("Your server currently has no active games")
    elif message.content.startswith(wake_command + "endall") and not message.author.guild_permissions.administrator:
        await message.channel.send("You must be an administrator to end all active games")

    def check(m):
        return ('y' in m.content.lower() or 'n' in m.content.lower()) and m.channel == message.channel and player_index(m.author) is not False

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
        embed.add_field(name="And when the mods realize youre playing this trash",
                        value="they can stop that shit with `pp!endall`",
                        inline=False)
        embed.set_footer(text="git good smh my h")

        await message.channel.send(message.author.mention, embed=embed)

    if message.content.startswith(wake_command + "startgame") and len(message.mentions) > 0:
        if message.mentions[0] == client.user:
            await message.channel.send("Go find a friend, loser.")
            return

        elif player_index(message.author) is not False:

            await message.channel.send("You are already playing a game. End this and start a new game? **(y/n)**")
            msg = await client.wait_for('message', check=check)

            if 'y' in msg.content.lower(): await end_game(msg)
            else:
                await message.channel.send("Canceling new game")
                return

        players.append([message.author, message.mentions[0]])
        Game.append([logic.Board(assets, 15)])
        current_game = Game[len(Game)-1][0]

        await message.channel.send(f"**Starting Mancala Game**\n    -{players[len(players)-1][0].mention} vs {players[len(players)-1][1].mention}")

        file, embed = send_board([current_game.img_board.get_board(current_game.turn)], len(Game)-1)
        Game[len(Game)-1].append(await message.channel.send(players[len(players)-1][current_game.turn].mention, file=file, embed=embed))

        for emoji in emojis:
            await Game[len(Game)-1][1].add_reaction(emoji)

    elif message.content.startswith(wake_command + "startgame") and len(message.mentions) == 0:
        await message.channel.send("You need one other person to start")

@client.event
async def on_reaction_add(reaction, user):
    global Game
    global players

    if user.bot or reaction.emoji not in emojis:
        return

    index = player_index(user)
    if index is False or reaction.message != Game[index][1]:
        return

    current_game = Game[index][0]
    imgs = current_game.move(emojis.index(reaction.emoji))
    if imgs is not None:
        file, embed = send_board(imgs, index)
        Game[index][1] = await reaction.message.channel.send(players[index][current_game.turn].mention, file=file, embed=embed)

        for reaction.emoji in emojis:
            await Game[index][1].add_reaction(reaction.emoji)
    else:
        await reaction.message.channel.send(f"{players[index][current_game.turn].mention}, that space is empty")

    # Since there is no logic to detect a win, i do that here in the bot section
    if sum(current_game.board[0]) == 0 or sum(current_game.board[1]) == 0:
        current_game.goals[0] += sum(current_game.board[0])
        current_game.goals[1] += sum(current_game.board[1])

        winner = current_game.goals.index(max(current_game.goals))

        embed = discord.Embed(title=f"**{players[index][winner]} WON!!!!!11!!1!!**", description="bitch got *played*", color=colors[winner])
        embed.set_footer(text="gg")

        embed.set_image(url=players[index][winner].avatar_url)
        final = await reaction.message.channel.send(players[index][winner].mention, embed=embed)
        await final.add_reaction("👍")

        players.pop(index)
        Game.pop(index)


client.run(TOKEN)
