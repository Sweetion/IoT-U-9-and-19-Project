import pygame
from vector import Vector2
from constants import *

class Text:
    def __init__(self, text, color, x, y, size, time=None, id=None, visible=True):
        self.id = id
        self.text = text
        self.color = color
        self.size = size
        self.visible = visible
        self.position = Vector2(x, y)
        self.timer = 0
        self.lifespan = time
        self.label = None
        self.destroy = False
        self.setupFont("PressStart2P-Regular.ttf")  # Ensure this file exists
        self.createLabel()

    def setupFont(self, fontpath):
        try:
            self.font = pygame.font.Font(fontpath, self.size)
        except FileNotFoundError:
            print(f"Font file '{fontpath}' not found. Falling back to default font.")
            self.font = pygame.font.SysFont(None, self.size)  # Default font fallback

    def createLabel(self):
        self.label = self.font.render(self.text, 1, self.color)

    def setText(self, newtext):
        self.text = str(newtext)
        self.createLabel()

    def update(self, dt):
        if self.lifespan is not None:
            self.timer += dt
            if self.timer >= self.lifespan:
                self.timer = 0
                self.lifespan = None
                self.destroy = True

    def render(self, screen):
        if self.visible:
            x, y = self.position.asTuple()
            screen.blit(self.label, (x, y))

class TextGroup:
    def __init__(self):
        pygame.font.init()  # Make sure fonts are initialized in pygame
        self.nextid = 10
        self.alltext = {}
        self.setupText()
        self.showText(READYTXT)

    def addText(self, text, color, x, y, size, time=None, id=None):
        self.nextid += 1
        self.alltext[self.nextid] = Text(text, color, x, y, size, time=time, id=id)
        return self.nextid

    def removeText(self, id):
        if id in self.alltext:
            self.alltext.pop(id)

    def setupText(self):
        size = TILEHEIGHT
        self.alltext[SCORETXT] = Text("0".zfill(8), WHITE, 0, TILEHEIGHT, size)
        self.alltext[LEVELTXT] = Text(str(1).zfill(3), WHITE, 23 * TILEWIDTH, TILEHEIGHT, size)
        self.alltext[READYTXT] = Text("READY!", YELLOW, 11.25 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)
        self.alltext[PAUSETXT] = Text("PAUSED!", YELLOW, 10.625 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)
        self.alltext[GAMEOVERTXT] = Text("GAMEOVER!", YELLOW, 10 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)
        self.addText("SCORE", WHITE, 0, 0, size)
        self.addText("LEVEL", WHITE, 23 * TILEWIDTH, 0, size)

    def update(self, dt):
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].update(dt)
            if self.alltext[tkey].destroy:
                self.removeText(tkey)

    def showText(self, id):
        self.hideText()
        if id in self.alltext:
            self.alltext[id].visible = True

    def hideText(self):
        for key in [READYTXT, PAUSETXT, GAMEOVERTXT]:
            if key in self.alltext:
                self.alltext[key].visible = False

    def updateScore(self, score):
        self.updateText(SCORETXT, str(score).zfill(8))

    def updateLevel(self, level):
        self.updateText(LEVELTXT, str(level + 1).zfill(3))

    def updateText(self, id, value):
        if id in self.alltext:
            self.alltext[id].setText(value)

    def render(self, screen):
        for tkey in self.alltext:
            self.alltext[tkey].render(screen)
    def font(self):
        self.font = pygame.font.SysFont("Arial", self.size)

