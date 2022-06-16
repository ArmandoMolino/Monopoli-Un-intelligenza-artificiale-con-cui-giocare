import json
import math
import random
import time


import pygame

from Monopoly.Blocks.MonopolyBlocks import Land, EventBlock


class Board:
    _scale_factor = 1
    _instance = None

    blockSpriteGroup = pygame.sprite.Group()
    playerSpriteGroup = pygame.sprite.Group()

    blockSpritePath = {}
    pieceSpritePath = {}
    buttonSpritePath = {}

    items = []
    game_area = [pygame.Rect(0, math.ceil(25 / _scale_factor), math.ceil(175 / _scale_factor), math.ceil(1025 / _scale_factor)),
                 pygame.Rect(math.ceil(850 / _scale_factor), math.ceil(25 / _scale_factor), math.ceil(150 / _scale_factor), math.ceil(975 / _scale_factor)),
                 pygame.Rect(math.ceil(175 / _scale_factor), math.ceil(25 / _scale_factor), math.ceil(675 / _scale_factor), math.ceil(150 / _scale_factor)),
                 pygame.Rect(math.ceil(175 / _scale_factor), math.ceil(850 / _scale_factor), math.ceil(675 / _scale_factor), math.ceil(150 / _scale_factor))]
    AI = None
    AI_text = None

    player = None
    player_text = None

    startTurnbutton = None
    start10Turnbutton = None
    startUntilEndbutton = None

    skip = 0

    class _BlockSprite(pygame.sprite.Sprite):

        def update(self, *argv) -> None:
            if type(self.block) is Land:
                i = self.block._n_house - self.house
                for x in range(i):
                    self.draw_house()
                    self.house += 1

                if self.block._hotel:
                    self.draw_house()
                    self.house = 5

            if type(self.block) is not EventBlock:
                if self.block.owner is not None:
                    self.draw_OwnerFlag(self.block.owner.color)
            if len(argv) > 0:
                screen = argv[0]
                screen.fill('olivedrab3', self.rect)
                screen.blit(self.image, self.rect)
            pygame.display.update()

        def __init__(self, path, block, center=None):
            super(Board._BlockSprite, self).__init__()
            self.path = path
            self.image = pygame.image.load(path)
            self.image = pygame.transform.scale(self.image, (self.image.get_width() // Board._scale_factor, self.image.get_height() // Board._scale_factor))
            self.image_original = self.image.copy()

            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = -self.rect.width / 2, -self.rect.height / 2

            if center is not None:
                self.set_center(center)

            self.block = block
            if type(self.block) is Land:
                self.house = 0

            self.position_for_player = self.rect.center
            self.degree = 0

        def draw_house(self):
            def get_HousesPos():
                _x, _y = 0, 0
                offset = 8 // Board._scale_factor
                width = 6 // Board._scale_factor

                if self.degree == 90:#topright
                    _x, _y = self.rect.width, width - 1
                    _x -= offset

                elif self.degree == 180:#botright
                    _x, _y = self.rect.width - width, self.rect.height
                    _y -= offset

                elif self.degree == 270:#botleft
                    _x, _y = 0, self.rect.height - width
                    _x += offset

                else: # topleft
                    _x, _y = width - 1, -1
                    _y += offset

                return _x, _y

            def get_house_points():
                points = [
                    (x + 5 // Board._scale_factor, y),
                    (x + 7 // Board._scale_factor, y + 2 // Board._scale_factor),
                    (x + 7 // Board._scale_factor, y + 1 // Board._scale_factor),
                    (x + 8 // Board._scale_factor, y + 1 // Board._scale_factor),
                    (x + 8 // Board._scale_factor, y + 3 // Board._scale_factor),
                    (x + 10 // Board._scale_factor, y + 5 // Board._scale_factor),
                    (x + 8 // Board._scale_factor, y + 5 // Board._scale_factor),
                    (x + 8 // Board._scale_factor, y + 10 // Board._scale_factor),
                    (x + 2 // Board._scale_factor, y + 10 // Board._scale_factor),
                    (x + 2 // Board._scale_factor, y + 5 // Board._scale_factor),
                    (x, y + 5 // Board._scale_factor)
                ]
                centerx, centery = x, y
                for i, h in enumerate(points):
                    temp = (h[0] - centerx) * round(math.cos(math.radians(self.degree))) - (h[1] - centery) \
                           * round(math.sin(math.radians(self.degree))) + centerx, (h[0] - centerx) * round(
                        math.sin(math.radians(self.degree))) + (h[1] - centery) \
                           * round(math.cos(math.radians(self.degree))) + centery
                    points[i] = temp
                return points

            if self.house < 5:
                x, y = get_HousesPos()
                offset = self.house * 14 // Board._scale_factor
                if self.degree in [270, 90]:
                    y = y + offset
                else:
                    x = x + offset
                color = 'green' if self.house < 4 else "red"
                house_points = get_house_points()

                pygame.draw.polygon(self.image, color, house_points)

        def draw_OwnerFlag(self, color):
            def get_OwnerFlagPos():
                _x, _y = 0, 0
                offset = 27 // Board._scale_factor
                width = 9 // Board._scale_factor

                if self.degree == 90:#topright
                    _x, _y = self.rect.width, width - 1
                    _x -= offset

                elif self.degree == 180:#botright
                    _x, _y = self.rect.width - width, self.rect.height
                    _y -= offset

                elif self.degree == 270:#botleft
                    _x, _y = 0, self.rect.height - width
                    _x += offset

                else: # topleft
                    _x, _y = width - 1, -1
                    _y += offset

                return _x, _y

            def get_ownerFlag_points():
                points = [
                    (x - 6 // Board._scale_factor, y),
                    (x, y),
                    (x + 6 // Board._scale_factor, y),
                    (x + 6 // Board._scale_factor, y + 36 // Board._scale_factor),
                    (x, y + 30 // Board._scale_factor),
                    (x - 6 // Board._scale_factor, y + 36 // Board._scale_factor)
                ]
                centerx, centery = x, y
                for i, h in enumerate(points):
                    temp = (h[0] - centerx) * round(math.cos(math.radians(self.degree))) - (h[1] - centery) \
                           * round(math.sin(math.radians(self.degree))) + centerx, (h[0] - centerx) * round(
                        math.sin(math.radians(self.degree))) + (h[1] - centery) \
                           * round(math.cos(math.radians(self.degree))) + centery
                    points[i] = temp
                return points

            if type(color) is str:
                x, y = get_OwnerFlagPos()
                ownerFlag_points = get_ownerFlag_points()
                pygame.draw.polygon(self.image, color, ownerFlag_points)
            else:
                raise Exception("il Colore deve essere una stringa")

        def set_center(self, center):
            self.rect.center = center
            self.position_for_player = self.rect.center

        def get_center(self):
            return self.rect.center

        def Move(self, screen, x, y):
            screen.fill("olivedrab3", self.rect)
            self.rect.center = (x, y)
            self.position_for_player = self.rect.center
            screen.blit(self.image, self.rect)

        def Rotate(self, degree):
            self.degree = 360 - degree
            self.image = pygame.transform.rotate(self.image, degree)

            if degree == 270 or degree == 90:
                h, w = self.rect.width, self.rect.height
                self.rect.width, self.rect.height = w, h

        def ReloadImage(self):
            self.image = self.image_original.copy()
            if self.degree > 0:
                self.image = pygame.transform.rotate(self.image, 360 - self.degree)
            self.house = 0

    class _PieceSprite(pygame.sprite.Sprite):

        def update(self, *argv) -> None:
            if len(argv) >= 3:
                screen = argv[0]
                background = argv[1]
                centers = argv[2]
                gameArea = None if len(argv) == 3 else argv[3]
                c = centers[self.position + 1:self.player.position + 1]
                if self.position >= self.player.position:
                    c = (centers[self.position + 1:])
                    c += centers[:self.player.position + 1]

                self.Move(screen, background, c, gameArea)

        def __init__(self, path, player=None, center=(0, 0), offset=None, size=None, vel=0.02):
            super(Board._PieceSprite, self).__init__()
            if offset is None:
                offset = []

            self.path = path
            self.image = pygame.image.load(path)
            self.image = pygame.transform.scale(self.image, (self.image.get_width() // (Board._scale_factor * 1.75), self.image.get_height() // (Board._scale_factor * 1.75)))
            self.image_original = self.image.copy()

            self.player = player

            self.rect = self.image.get_rect()
            self.rect.center = center
            self.position = player.position
            self.offset = offset
            self._actualOffset = offset[int(self.position / 10)]
            self.vel = vel

        def Move(self, screen, background, centers=None, gameArea=None):
            if centers is None:
                centers = []
            if gameArea is None:
                gameArea = [screen.get_rect()]

            def go_to(dest):
                clock = pygame.time.Clock()
                xVel, yVel = round((dest[0] - self.rect.centerx) * self.vel), round(
                    (dest[1] - self.rect.centery) * self.vel)
                temp = math.sqrt(math.pow(xVel, 2) + math.pow(yVel, 2))
                oldXDist, oldYDist = math.sqrt(math.pow(dest[0] - self.rect.centerx, 2)), math.sqrt(
                    math.pow(dest[1] - self.rect.centery, 2))

                while math.sqrt(
                        math.pow(dest[0] - self.rect.centerx, 2) + math.pow(dest[1] - self.rect.centery,
                                                                            2)) > math.ceil(
                    temp) and (xVel + yVel) != 0:
                    newXDist, newYDist = math.sqrt(math.pow(dest[0] - self.rect.centerx, 2)), math.sqrt(
                        math.pow(dest[1] - self.rect.centery, 2))
                    xVel = 0 if oldXDist < newXDist else xVel
                    yVel = 0 if oldYDist < newYDist else yVel

                    self.rect.center = (self.rect.centerx + xVel, self.rect.centery + yVel)
                    for area in gameArea:
                        screen.fill('olivedrab3', area)
                    background.draw(screen)
                    self.groups()[0].draw(screen)
                    pygame.display.update()
                    clock.tick(60)
                    oldXDist, oldYDist = newXDist, newYDist

                self.rect.center = (dest[0], dest[1])
                for area in gameArea:
                    screen.fill('olivedrab3', area)
                background.draw(screen)
                self.groups()[0].draw(screen)
                pygame.display.update()
                clock.tick(60)

            for center in centers:
                self.position += 1
                if self.position % 10 == 0:
                    nextOffset = self.offset[int((self.position % 40) / 10)]
                    go_to((center[0] + self._actualOffset[0] + nextOffset[0],
                           center[1] + self._actualOffset[1] + nextOffset[1]))
                    self._actualOffset = nextOffset
                else:
                    go_to((center[0] + self._actualOffset[0], center[1] + self._actualOffset[1]))
                self.position = self.position % 40

            self.position = self.player.position

        def get_center(self):
            return self.rect.center

    class _PlayerGameInfo:

        def __init__(self, player, color, topleft):
            self.player = player
            self.color = color

            self.text = [f'{self.player}(Player {self.color})']
            self.font = pygame.font.SysFont("Arial", 24)
            self.image = [self.font.render(self.text[0], True, 'black', 'olivedrab3')]
            self.rect = [self.image[0].get_rect()]
            self.rect[0].topleft = topleft

        def ShowText(self, screen, msg):
            maxwidthrect = max(self.rect, key=lambda x: x.w)
            fillArea = pygame.Rect(self.rect[0].topleft, (maxwidthrect.w, self.rect[-1].bottom - self.rect[0].y))
            screen.fill('olivedrab3', fillArea)
            pygame.display.update()
            self.text = [self.font.render(f'{self.player}', True, self.color, 'olivedrab3')]
            splitted_msg = msg.split('\n')
            self.text += [self.font.render(msg, True, 'black', 'olivedrab3') for msg in splitted_msg]
            self.font = pygame.font.SysFont("Arial", 24)
            topleft = self.rect[0].topleft

            self.image = []
            self.rect = []
            for i, t in enumerate(self.text):
                self.image.append(t)
                self.rect.append(self.image[i].get_rect())

                self.rect[i].topleft = topleft
                topleft = (topleft[0], topleft[1] + self.rect[-1].h)

                screen.blit(self.image[i], self.rect[i])

    class _Button:
        """Create a startTurnbutton, then blit the surface in the while loop"""

        def __init__(self, text, topleft, path=None):
            self.font = pygame.font.SysFont("Arial", 16)
            self.text = self.font.render(text, True, 'black')

            if path is None:
                self.button_image = pygame.surface.Surface((160, 80))
                self.button_image.fill('white')
                self.button_pressed_image = pygame.surface.Surface((160, 80))
                self.button_pressed_image.fill('grey')
            else:
                self.button_image = pygame.image.load(path[0])
                self.button_pressed_image = pygame.image.load(path[1])
                self.button_image = pygame.transform.scale(self.button_image, (160, 80))
                self.button_pressed_image = pygame.transform.scale(self.button_pressed_image, (160, 80))

            self.rect = self.button_image.get_rect()
            self.rect.topleft = topleft
            self.pressed = False

        def show(self, screen):
            if self.pressed:
                screen.fill('olivedrab3', self.rect)
                screen.blit(self.button_pressed_image, self.rect)
                rect = self.text.get_rect()
                rect.center = self.rect.center
                screen.blit(self.text, rect)
                self.pressed = False
            else:
                screen.fill('olivedrab3', self.rect)
                screen.blit(self.button_image, self.rect)
                rect = self.text.get_rect()
                rect.center = (self.rect.centerx, self.rect.centery - 8)
                screen.blit(self.text, rect)

        def click(self, event, screen):
            x, y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if self.rect.collidepoint(x, y):
                        self.pressed = True
                        self.show(screen)
                        return True
            return False

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def StartGame(cls, blocks, AI, player):
        def PrintBoard(paths):
            # instanza le caselle
            b = 0

            b = PrintLine(paths=paths, index=b, x=921 // Board._scale_factor, y=921 // Board._scale_factor, degree=0)
            b = PrintLine(paths=paths, index=b, x=100 // Board._scale_factor, y=921 // Board._scale_factor, degree=270)
            b = PrintLine(paths=paths, index=b, x=100 // Board._scale_factor, y=100 // Board._scale_factor, degree=180)
            PrintLine(paths=paths, index=b, x=921 // Board._scale_factor, y=100 // Board._scale_factor, degree=90)
            cls.items = cls.blockSpriteGroup.sprites()

        def PrintLine(paths, index, x, y, degree=0, offset=0):
            sign = 1
            orientation = lambda x, y, offset, degree: (x + offset, y) if degree == 180 or degree == 0 else (
                x, y + offset)
            newOffset = lambda rect: rect.width / 2 if degree == 0 or degree == 180 else rect.height / 2
            if degree == 0 or degree == 270:
                sign = -1

            sprite = Board._BlockSprite(paths[index], blocks[index])
            sprite.Rotate(degree)
            sprite.set_center((x, y))
            cls.screen.blit(sprite.image, sprite.rect)
            pygame.display.update()
            cls.blockSpriteGroup.add(sprite)
            offset += sign * newOffset(sprite.rect)
            index += 1

            for i in range(9):
                sprite = Board._BlockSprite(paths[index + i], blocks[index + i])
                sprite.Rotate(degree)
                offset += sign * math.floor(newOffset(sprite.rect))
                tempx, tempy = orientation(x, y, offset, degree)
                sprite.set_center((tempx, tempy))
                cls.screen.blit(sprite.image, sprite.rect)
                pygame.display.update()
                cls.blockSpriteGroup.add(sprite)
                offset += sign * math.ceil(newOffset(sprite.rect))
            index += 9

            return index

        if pygame.get_init():
            return cls.RestartGame(blocks, AI, player)

        pygame.init()
        cls.screen = pygame.display.set_mode((int(1225/Board._scale_factor), int(1025/Board._scale_factor)), pygame.RESIZABLE)
        cls.screen.fill('olivedrab3')

        with open('Monopoly/Board/Sprite/SpriteData.json') as json_file:
            data = json.load(json_file)
            cls.blockSpritePath = data['BlockSprites']
            cls.pieceSpritePath = data['PieceSprite']
            cls.buttonSpritePath = data['ButtonSprite']

        # instanza le caselle
        PrintBoard(cls.blockSpritePath)

        # instanza i giocatori

        startCenter = cls.items[AI.position].get_center()
        k = round((cls.items[0].rect.h * 3) / 12)
        offset = [(0, k), (-k, 0), (0, -k), (k, 0)]
        startPosition = (startCenter[0] + offset[0][0], startCenter[1] + offset[0][1])
        randomSprite = random.randint(0, len(cls.pieceSpritePath[f'{AI.color}']) - 1)
        cls.AI = Board._PieceSprite(path=cls.pieceSpritePath[f'{AI.color}'][randomSprite], center=startPosition,
                                    player=AI,
                                    offset=offset,
                                    size=(50, 50),
                                    vel=0.5)
        cls.AI_text = Board._PlayerGameInfo('AI', AI.color, (int(200/Board._scale_factor), int(200/Board._scale_factor)))
        cls.AI_text.ShowText(cls.screen, f'Budget={AI.Budget()}')

        startCenter = cls.items[player.position].get_center()
        offset = [(0, k - cls.AI.rect.h), (-k + cls.AI.rect.h, 0), (0, -k + cls.AI.rect.h),
                  (k - cls.AI.rect.h, 0)]
        startPosition = (startCenter[0] + offset[0][0], startCenter[1] + offset[0][1])
        randomSprite = random.randint(0, len(cls.pieceSpritePath[f'{player.color}']) - 1)
        cls.player = Board._PieceSprite(path=cls.pieceSpritePath[f'{player.color}'][randomSprite],
                                        center=startPosition,
                                        player=player,
                                        offset=offset,
                                        size=(50, 50),
                                        vel=0.5)
        cls.player_text = Board._PlayerGameInfo('player', player.color, (int(200/Board._scale_factor), int(500/Board._scale_factor)))
        cls.player_text.ShowText(cls.screen, f'Budget={player.Budget()}')

        # posizione passagio prigione
        cls.items[10].position_for_player = (
            round(abs((cls.items[10].rect.left - cls.items[10].rect.centerx) * 2) / 3) + cls.items[10].rect.left,
            round(- abs((cls.items[10].rect.bottom - cls.items[10].rect.centery) * 2) / 3) + cls.items[10].rect.bottom)

        # posizione prigione
        cls.prisonLocation = (
            round(abs(cls.items[10].rect.right - cls.items[10].rect.centerx) / 2) + cls.items[10].rect.centerx,
            round(abs(cls.items[10].rect.top - cls.items[10].rect.centery) / 2) + cls.items[10].rect.top)

        cls.playerSpriteGroup.add(cls.AI)
        cls.playerSpriteGroup.add(cls.player)
        cls.playerSpriteGroup.draw(cls.screen)

        # instanza i pulsanti
        cls.startTurnbutton = Board._Button("Prossimo Round", (int(1012/Board._scale_factor), 100), path=cls.buttonSpritePath['red'])
        cls.screen.fill('olivedrab3', cls.startTurnbutton.rect)
        cls.startTurnbutton.show(cls.screen)

        cls.start10Turnbutton = Board._Button("Prossimi 10 Round", (int(1012/Board._scale_factor), 205), path=cls.buttonSpritePath['blue'])
        cls.screen.fill('olivedrab3', cls.start10Turnbutton.rect)
        cls.start10Turnbutton.show(cls.screen)

        cls.startUntilEndbutton = Board._Button("Fino alla fine", (int(1012/Board._scale_factor), 310), path=cls.buttonSpritePath['blue'])
        cls.screen.fill('olivedrab3', cls.startUntilEndbutton.rect)
        cls.startUntilEndbutton.show(cls.screen)

        pygame.display.update()

    def RestartGame(cls, blocks, AI, player):
        cls.skip = 0

        cls.screen.fill('olivedrab3')
        pygame.display.update()

        for i, item in enumerate(cls.items):
            item.ReloadImage()
            item.block = blocks[i]
        cls.blockSpriteGroup.draw(cls.screen)
        pygame.display.update()

        cls.AI.player = AI
        cls.AI.position = AI.position
        cls.AI.rect.center = cls.items[AI.position].position_for_player
        cls.AI_text.ShowText(cls.screen, f'Budget={cls.AI.player.Budget()}')
        pygame.display.update()

        cls.player.player = player
        cls.player.position = player.position
        cls.player.rect.center = cls.items[player.position].position_for_player
        cls.player_text.ShowText(cls.screen, f'Budget={cls.player.player.Budget()}')
        pygame.display.update()

        cls.playerSpriteGroup.draw(cls.screen)
        pygame.display.update()

        cls.startTurnbutton = Board._Button("Prossimo Round", (int(1012/Board._scale_factor), 100), path=cls.buttonSpritePath['red'])
        cls.screen.fill('olivedrab3', cls.startTurnbutton.rect)
        cls.startTurnbutton.show(cls.screen)

        cls.start10Turnbutton = Board._Button("Prossimi 10 Round", (int(1012/Board._scale_factor), 205), path=cls.buttonSpritePath['blue'])
        cls.screen.fill('olivedrab3', cls.start10Turnbutton.rect)
        cls.start10Turnbutton.show(cls.screen)

        cls.startUntilEndbutton = Board._Button("Fino alla fine", (int(1012/Board._scale_factor), 310), path=cls.buttonSpritePath['blue'])
        cls.screen.fill('olivedrab3', cls.startUntilEndbutton.rect)
        cls.startUntilEndbutton.show(cls.screen)

        pygame.display.update()

    def update(cls, AI_log, player_log):

        if cls.skip == 0:
            cls._buttonLoop()
        else:
            time.sleep(0.5)
            cls.skip -= 1

        if not cls.AI.player.imprisoned:
            cls.AI.update(cls.screen, cls.blockSpriteGroup, [x.position_for_player for x in cls.items],
                          cls.game_area)
        elif cls.AI.position != cls.AI.player.position:
            cls.AI.update(cls.screen, cls.blockSpriteGroup, [x.position_for_player for x in cls.items],
                          cls.game_area)
            cls.AI.Move(cls.screen, cls.blockSpriteGroup, [cls.prisonLocation], cls.game_area)
        cls.items[cls.AI.position].update()
        cls.screen.blit(cls.AI.image, cls.AI.rect)
        if cls.AI.position == cls.player.position:
            cls.screen.blit(cls.player.image, cls.player.rect)
        cls.AI_text.ShowText(cls.screen, f'Budget={cls.AI.player.Budget()}\n{AI_log}')

        pygame.display.update()

        if not cls.player.player.imprisoned:
            cls.player.update(cls.screen, cls.blockSpriteGroup, [x.position_for_player for x in cls.items],
                              cls.game_area)
        elif cls.player.position != cls.player.player.position:
            cls.player.update(cls.screen, cls.blockSpriteGroup, [x.position_for_player for x in cls.items],
                              cls.game_area)
            cls.player.Move(cls.screen, cls.blockSpriteGroup, [cls.prisonLocation], cls.game_area)
        cls.items[cls.player.position].update()
        cls.screen.blit(cls.player.image, cls.player.rect)
        if cls.AI.position == cls.player.position:
            cls.screen.blit(cls.AI.image, cls.AI.rect)
        cls.player_text.ShowText(cls.screen, f'Budget={cls.player.player.Budget()}\n{player_log}')

        pygame.display.update()

        cls.blockSpriteGroup.update(cls.screen)
        cls.screen.blit(cls.AI.image, cls.AI.rect)
        cls.screen.blit(cls.player.image, cls.player.rect)

        pygame.display.update()

    def _buttonLoop(self):
        self.screen.fill('olivedrab3', self.startTurnbutton.rect)
        self.startTurnbutton.show(self.screen)
        self.screen.fill('olivedrab3', self.start10Turnbutton.rect)
        self.start10Turnbutton.show(self.screen)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if self.startTurnbutton.click(event, self.screen):
                    return
                if self.start10Turnbutton.click(event, self.screen):
                    self.skip = 10
                    return
                if self.startUntilEndbutton.click(event, self.screen):
                    self.skip = math.inf
                    return
