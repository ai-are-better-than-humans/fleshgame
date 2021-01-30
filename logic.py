from PIL import Image, ImageDraw, ImageFont
from random import randint
from os import listdir
from os.path import join


# Class to contain the individual colors and offsets of each rock
class Rock(object):
    def __init__(self, costume, offset):
        self.ico = costume.rotate(offset[2]).convert('RGBA')
        self.pos_offset = (offset[0], offset[1])


# Class to handle the GIF animation of the moves
class MancalaBoard(object):
    def __init__(self, asset_dir, variance, size=80):
        self.board_ico = Image.open(join(asset_dir, "board.png"))
        self.rock_icos = [Image.open(join(asset_dir, f)) for f in listdir(asset_dir) if "rock" in f]
        self.goals = ([], [])

        self.zones = ([[], [], [], [], [], []], [[], [], [], [], [], []])
        for x in range(2):
            for y in range(6):
                for z in range(4):
                    offset = (randint(-variance, variance), randint(-variance, variance), randint(0, 360))
                    costume = self.rock_icos[randint(0, len(self.rock_icos) - 1)].resize((size, size))
                    self.zones[x][y].append(Rock(costume, offset))

    def get_board(self, facing, numsize=35):
        leap = 130

        p = [(285, 280), (935, 130)]
        p2 = [(1115, 250), (140, 250)]
        score = [(1100, 60), (135, 55)]

        board = self.board_ico.copy()

        font = ImageFont.truetype(r'C:\Users\System-Pc\Desktop\arial.ttf', numsize)

        # Loop which generates an image depending on which way the board should be facing
        for x in range(2):
            for j, i in enumerate(self.zones[(x + facing) % 2]):
                for ii in i:
                    dir = [1, -1]
                    pos = (p[x][0] + leap * j * dir[x], p[x][1])
                    board.paste(ii.ico, (pos[0] + ii.pos_offset[0], pos[1] + ii.pos_offset[1]), ii.ico)

                    draw = ImageDraw.Draw(board)

                    dir[0] = 1.9
                    draw.text((pos[0], pos[1] + 50 * dir[x]), str(len(i)), fill="black", font=font, align="right")

            for l in self.goals[(x + facing) % 2]:
                board.paste(l.ico, (p2[x][0] + l.pos_offset[0], p2[x][1] + l.pos_offset[1]), l.ico)

                draw = ImageDraw.Draw(board)
                draw.text(score[x], str(len(self.goals[(x + facing) % 2])), fill="black", font=font, align="right")

        return self.add_transparency(board)

    @staticmethod
    def add_transparency(im):
        alpha = im.getchannel('A')
        im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)

        im.paste(255, mask)
        im.info['transparency'] = 255
        return im


# Class to handle the Logic of the moves
class Board(object):
    def __init__(self, asset_dir, offset):
        self.board = ([4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4])
        self.goals = [0, 0]
        self.turn = 0
        self.img_board = MancalaBoard(asset_dir, offset)

    def move(self, slot):
        images = []
        current_slot = slot
        count = [self.board[self.turn][slot], list(self.img_board.zones[self.turn][slot])]
        if count[0] == 0: return

        orientation = (self.turn+1)%2
        if not (slot + count[0]) % 6 and (slot + count[0]) % 12:
            orientation = self.turn

        images.append(self.img_board.get_board(orientation))

        self.board[self.turn][slot] = 0
        self.img_board.zones[self.turn][slot].clear()

        images.append(self.img_board.get_board(orientation))

        '''
            -This logic is a fucking mess. I think I wrote it when i was high????? 
                I try to make it better and fix some errors that ONLY come up when playing for a long time (Everything seems okay at first glance)
                But when i do it gets fucked up. I am so embarrased about this
                Im almost certain that theres a super easy way to do mancala logic but im just scared to change anything
                Have fun.
        '''

        while count[0] > 0:
            current_slot += 1
            side = int((self.turn + (current_slot - (current_slot % 6)) / 6) % 2)

            if not current_slot % 6 and current_slot % 12:
                self.goals[self.turn] += 1
                self.img_board.goals[self.turn].append(count[1][count[0]%len(count[1])])

                count[0] -= 1
                images.append(self.img_board.get_board(orientation))

            if count[0] != 0:
                self.board[side][current_slot % 6] += 1
                self.img_board.zones[side][current_slot % 6].append(count[1][count[0]%len(count[1])])

                count[0] -= 1
                images.append(self.img_board.get_board(orientation))

                # This part is the most buggy, its supposed to handle capturing peices
                # Yet for some reason it will capture peices that arent supposed to be captured???
                if count[0] == 0:

                    if self.board[self.turn][current_slot % 6] == 1 and self.board[(self.turn - 1) % 2][5 - current_slot % 6] != 0:
                        self.goals[self.turn] += self.board[self.turn][current_slot % 6] + self.board[(self.turn - 1) % 2][5 - current_slot % 6]

                        self.img_board.goals[self.turn].extend(self.img_board.zones[self.turn][current_slot % 6])
                        self.img_board.goals[self.turn].extend(self.img_board.zones[(self.turn - 1) % 2][5-current_slot % 6])

                        self.board[self.turn][current_slot % 6] = 0
                        self.board[(self.turn - 1) % 2][5 - current_slot % 6] = 0

                        self.img_board.zones[self.turn][current_slot % 6].clear()
                        self.img_board.zones[(self.turn - 1) % 2][5-current_slot % 6].clear()

                        images.append(self.img_board.get_board(orientation))

                    self.turn = (self.turn + 1) % 2

        return images
