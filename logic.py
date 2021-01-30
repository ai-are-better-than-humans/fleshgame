from PIL import Image, ImageDraw, ImageFont
from random import randint
from os import listdir
from os.path import join



class Rock(object):
    def __init__(self, costume, offset):
        self.ico = costume.rotate(offset[2]).convert('RGBA')
        self.pos_offset = (offset[0], offset[1])


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

    def get_board(self, numsize=35):
        leap = 130

        p = [(285, 280), (935, 130)]
        p2 = [(1115, 250), (140, 250)]
        score = [(1100, 60), (135, 55)]

        board1 = self.board_ico.copy()
        board2 = self.board_ico.copy()

        font = ImageFont.truetype(r'C:\Users\System-Pc\Desktop\arial.ttf', numsize)

        for x in range(2):
            for j, i in enumerate(self.zones[x]):
                for ii in i:
                    dir = [1, -1]
                    pos = (p[x][0] + leap * j * dir[x], p[x][1])
                    board1.paste(ii.ico, (pos[0] + ii.pos_offset[0], pos[1] + ii.pos_offset[1]), ii.ico)

                    draw = ImageDraw.Draw(board1)

                    dir[0] = 1.9
                    draw.text((pos[0], pos[1] + 50 * dir[x]), str(len(i)), fill="black", font=font, align="right")

            for l in self.goals[x]:
                board1.paste(l.ico, (p2[x][0] + l.pos_offset[0], p2[x][1] + l.pos_offset[1]), l.ico)

                draw = ImageDraw.Draw(board1)
                draw.text(score[x], str(len(self.goals[x])), fill="black", font=font, align="right")

            for j, i in enumerate(self.zones[(x + 1) % 2]):
                for ii in i:
                    dir = [1, -1]
                    pos = (p[x][0] + leap * j * dir[x], p[x][1])
                    board2.paste(ii.ico, (pos[0] + ii.pos_offset[0], pos[1] + ii.pos_offset[1]), ii.ico)

                    draw = ImageDraw.Draw(board2)

                    dir[0] = 1.9
                    draw.text((pos[0], pos[1] + 50 * dir[x]), str(len(i)), fill="black", font=font, align="right")

            for l in self.goals[(x + 1) % 2]:
                board2.paste(l.ico, (p2[x][0] + l.pos_offset[0], p2[x][1] + l.pos_offset[1]), l.ico)

                draw = ImageDraw.Draw(board2)
                draw.text(score[x], str(len(self.goals[(x + 1) % 2])), fill="black", font=font, align="right")

        return self.gen_frame(board1), self.gen_frame(board2)

    @staticmethod
    def gen_frame(im):
        alpha = im.getchannel('A')
        im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)

        im.paste(255, mask)
        im.info['transparency'] = 255
        return im


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

        images.append(self.img_board.get_board())

        self.board[self.turn][slot] = 0
        self.img_board.zones[self.turn][slot].clear()

        images.append(self.img_board.get_board())

        while count[0] > 0:
            current_slot += 1
            side = int((self.turn + (current_slot - (current_slot % 6)) / 6) % 2)

            if not current_slot % 6 and current_slot % 12:
                self.goals[self.turn] += 1
                self.img_board.goals[self.turn].append(count[1][count[0]%len(count[1])])

                count[0] -= 1
                images.append(self.img_board.get_board())

            if count[0] != 0:
                self.board[side][current_slot % 6] += 1
                self.img_board.zones[side][current_slot % 6].append(count[1][count[0]%len(count[1])])

                count[0] -= 1
                images.append(self.img_board.get_board())

                if count[0] == 0:

                    if self.board[self.turn][current_slot % 6] == 1 and self.board[(self.turn - 1) % 2][5 - current_slot % 6] != 0:
                        self.goals[self.turn] += self.board[self.turn][current_slot % 6] + self.board[(self.turn - 1) % 2][5 - current_slot % 6]

                        self.img_board.goals[self.turn].extend(self.img_board.zones[self.turn][current_slot % 6])
                        self.img_board.goals[self.turn].extend(self.img_board.zones[(self.turn - 1) % 2][5-current_slot % 6])

                        self.board[self.turn][current_slot % 6] = 0
                        self.board[(self.turn - 1) % 2][5 - current_slot % 6] = 0

                        self.img_board.zones[self.turn][current_slot % 6].clear()
                        self.img_board.zones[(self.turn - 1) % 2][5-current_slot % 6].clear()

                        images.append(self.img_board.get_board())

                    self.turn = (self.turn + 1) % 2

        return [i[0] for i in images], [i[1] for i in images]
