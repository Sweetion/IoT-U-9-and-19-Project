import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause
from text import TextGroup
from sprites import LifeSprites
from sprites import MazeSprites
from mazedata import MazeData
from pygame import mixer
import random
import requests  # Import the requests library

pygame.mixer.init()
pygame.mixer.music.load("audio.mp3")
pygame.mixer.music.play(-1)

class CyberSecurityQuiz:
    def __init__(self):
        self.questions = ([
            {"question": "What is 2FA?",
             "options": ["A. Encryption", "B. Extra login step", "C. Firewall", "D. Virus"],
             "answer": "B"},

            {"question": "What does VPN do?",
             "options": ["A. Blocks ads", "B. Hides IP", "C. Detects malware", "D. Stores passwords"],
             "answer": "B"},

            {"question": "What is malware?",
             "options": ["A. Security tool", "B. Harmful software", "C. Password manager", "D. Firewall"],
             "answer": "B"},

            {"question": "What does HTTPS secure?",
             "options": ["A. Emails", "B. Websites", "C. Passwords", "D. Files"],
             "answer": "B"},

            {"question": "What is phishing?",
             "options": ["A. Fake email scam", "B. Data encryption", "C. A virus", "D. A firewall"],
             "answer": "A"},

            {"question": "What does a firewall do?",
             "options": ["A. Blocks threats", "B. Encrypts files", "C. Stores passwords", "D. Increases speed"],
             "answer": "A"},

            {"question": "What is a DDoS attack?",
             "options": ["A. Data breach", "B. Traffic overload", "C. Malware infection", "D. Firewall block"],
             "answer": "B"},

            {"question": "What should a password include?",
             "options": ["A. Name", "B. Simple words", "C. Numbers & symbols", "D. Birthdate"],
             "answer": "C"},
        ])
        random.shuffle(self.questions)  # Shuffle questions at the beginning
        self.current_question = None  # Store the current question dynamically
        self.show_question = True  # Start by showing the question
        self.feedback_timer = 0
        self.feedback_duration = 60  # Show feedback for 60 frames (~2 seconds at 30 FPS)
        self.score = 0  # Player score
        self.feedback_message = ""  # Message to show feedback (Correct or Incorrect)
        self.last_answer = None  # Store the last answer given by the player

        self.start_question()  # Pick a question when the game starts

    def get_random_question(self):
        return random.choice(self.questions)  # Pick a new random question

    def start_question(self):
        self.show_question = True
        self.feedback_message = ""  # Clear any previous feedback
        self.current_question = self.get_random_question()  # Pick a random question

    def handle_input(self, key):
        """Handles input, only accepting K_a, K_b, K_c, and K_d."""
        valid_keys = {
            pygame.K_a: "A",
            pygame.K_b: "B",
            pygame.K_c: "C",
            pygame.K_d: "D"
        }

        if key not in valid_keys:
            return False  # Ignore all keys except A, B, C, and D

        player_answer = valid_keys[key]
        correct = player_answer == self.current_question["answer"]
        self.last_answer = player_answer  # Store last answer for coloring options

        if correct:
            self.score += 200  # Add 200 points for the correct answer
            self.feedback_message = "Correct!"
        else:
            self.feedback_message = "Incorrect!"

        # Start feedback timer and temporarily hide the question
        self.feedback_timer = self.feedback_duration
        self.show_question = False

        return correct

    def draw_question(self, screen, font):
        """Renders the question and options, handling feedback delay."""
        if self.feedback_timer > 0:
            # Show feedback message for a brief time
            feedback_text = font.render(self.feedback_message, True, (0, 255, 0) if self.feedback_message == "Correct!" else (255, 0, 0))
            screen.blit(feedback_text, (200, 50))
            return  # Do not show the question yet

        # Clear feedback message before showing the next question
        self.feedback_message = ""

        if not self.current_question:
            return  # Ensure there is a valid question before trying to display it

        question_text = font.render(self.current_question["question"], True, (255, 255, 255))
        screen.blit(question_text, (50, 100))

        for i, option in enumerate(self.current_question["options"]):
            answer_letter = option[0]

        if self.last_answer:
            if answer_letter == self.current_question["answer"]:
                color = (0, 255, 0)  # Correct = green
            elif answer_letter == self.last_answer and self.last_answer != self.current_question["answer"]:
                color = (255, 0, 0)  # Wrong = red
            else:
                color = (255, 255, 255)  # Neutral
        else:
            color = (255, 255, 255)  # Default

        option_text = font.render(option, True, color)
        screen.blit(option_text, (50, 150 + i * 40))

    def update_feedback(self):
        """Handles the feedback timer to delay the next question."""
        if self.feedback_timer > 0:
            self.feedback_timer -= 1  # Count down timer (1 frame per update)
        else:
            self.show_question = True  # Show the next question
            self.last_answer = None  # Reset last answer for the next question
            self.feedback_message = ""  # Clear feedback message

    def get_score(self):
        return self.score  # Return the player's score


class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.clock = pygame.time.Clock()
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)
        self.mazedata = MazeData()
        self.cyber_quiz = CyberSecurityQuiz()
        self.paused_for_quiz = False
        self.font = pygame.font.Font(None, 40)
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.fruitCaptured = []
        self.fruitNode = None
        self.fruit = None
        self.player_name = ""
        self.name_input_active = True

    def setBackground(self):
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.constructBackground(self.background_norm, self.level % 5)
        self.background_flash = self.mazesprites.constructBackground(self.background_flash, 5)
        self.flashBG = False
        self.background = self.background_norm

    def startGame(self):
        self.mazedata.loadMaze(self.level)
        self.mazesprites = MazeSprites(self.mazedata.obj.name + ".txt", self.mazedata.obj.name + "_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup(self.mazedata.obj.name + ".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart))
        self.pellets = PelletGroup(self.mazedata.obj.name + ".txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)

        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3)))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3)))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0)))

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)

    def startGame_old(self):
        self.mazedata.loadMaze(self.level)
        self.mazesprites = MazeSprites("maze1.txt", "maze1_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.setPortalPair((0, 17), (27, 17))
        homekey = self.nodes.createHomeNodes(11.5, 14)
        self.nodes.connectHomeNodes(homekey, (12, 14), LEFT)
        self.nodes.connectHomeNodes(homekey, (15, 14), RIGHT)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(15, 26))
        self.pellets = PelletGroup("maze1.txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(2 + 11.5, 0 + 14))
        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(2 + 11.5, 3 + 14))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(0 + 11.5, 3 + 14))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(4 + 11.5, 3 + 14))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(2 + 11.5, 3 + 14))

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.nodes.denyAccessList(2 + 11.5, 3 + 14, LEFT, self.ghosts)
        self.nodes.denyAccessList(2 + 11.5, 3 + 14, RIGHT, self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.nodes.denyAccessList(12, 14, UP, self.ghosts)
        self.nodes.denyAccessList(15, 14, UP, self.ghosts)
        self.nodes.denyAccessList(12, 26, UP, self.ghosts)
        self.nodes.denyAccessList(15, 26, UP, self.ghosts)

    def update(self):
        dt = self.clock.tick(30) / 1000.0
        self.textgroup.update(dt)
        self.pellets.update(dt)

        if self.paused_for_quiz:
            # Update quiz feedback timer
            self.cyber_quiz.update_feedback()
        elif not self.pause.paused:
            self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()

        if self.pacman.alive and not self.paused_for_quiz:
            if not self.pause.paused:
                self.pacman.update(dt)
        else:
            self.pacman.update(dt)

        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.checkEvents()
        self.render()

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.checkEvents()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

            if event.type == KEYDOWN:
                if self.name_input_active:
                    if event.key == K_RETURN:
                        self.name_input_active = False
                    elif event.key == K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    else:
                        self.player_name += event.unicode

                elif self.paused_for_quiz:
                    correct = self.cyber_quiz.handle_input(event.key)
                    if correct:
                        self.updateScore(100)  # Bonus points for correct answer
                        self.paused_for_quiz = False  # Resume game after quiz

                elif event.key == K_SPACE:
                    # Toggle pause state when spacebar is pressed
                    if not self.pause.paused:
                        self.pause.setPause(playerPaused=True)
                        self.textgroup.showText(PAUSETXT)
                    else:
                        self.pause.setPause(playerPaused=False)
                        self.textgroup.hideText()

    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.updateScore(pellet.points)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.startFreight()
            if self.pellets.isEmpty():
                self.flashBG = True
                self.hideEntities()
                self.pause.setPause(pauseTime=3, func=self.nextLevel)

    def checkGhostEvents(self):
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.updateScore(ghost.points)
                    self.textgroup.addText(str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1)
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime=1, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -= 1
                        self.lifesprites.removeImage()
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(pauseTime=3, func=self.restartGame)
                            self.sendScoreToServer()  # Send score to server when game is over
                        else:
                            self.pause.setPause(pauseTime=3, func=self.resetLevel)

    def checkFruitEvents(self):
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.getNodeFromTiles(9, 20), self.level)
                print(self.fruit)
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)
                self.textgroup.addText(str(self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8, time=1)
                fruitCaptured = False
                for fruit in self.fruitCaptured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruitCaptured = True
                        break
                if not fruitCaptured:
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def showEntities(self):
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self):
        self.pacman.visible = False
        self.ghosts.hide()

    def nextLevel(self):
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()
        self.textgroup.updateLevel(self.level)

    def restartGame(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def resetLevel(self):
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.showText(READYTXT)

    def updateScore(self, points):
        self.score += points
        self.textgroup.updateScore(self.score)

        if self.score % 500 == 0 and not self.paused_for_quiz:
            self.paused_for_quiz = True
            self.cyber_quiz.start_question()

    def sendScoreToServer(self):
        url = "https://127.0.0.1:5000"  # Replace with your server URL
        data = {
            "name": self.player_name,
            "score": self.score
        }
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print("Score submitted successfully!")
            else:
                print(f"Failed to submit score. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    def render(self):
        try:
            self.screen.fill((0, 0, 0))  # Clear screen
            if self.background:
                self.screen.blit(self.background, (0, 0))  # Draw background
            else:
                print("Warning: Background is not set!")

            self.pellets.render(self.screen)  # Render pellets
            if self.fruit:
                self.fruit.render(self.screen)  # Render fruit if available
            self.pacman.render(self.screen)  # Render Pac-Man
            self.ghosts.render(self.screen)  # Render ghosts
            self.textgroup.render(self.screen)  # Render text

            # Render life sprites
            for i in range(len(self.lifesprites.images)):
                x = self.lifesprites.images[i].get_width() * i
                y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
                self.screen.blit(self.lifesprites.images[i], (x, y))

            # Render captured fruits
            for i in range(len(self.fruitCaptured)):
                x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i + 1)
                y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
                self.screen.blit(self.fruitCaptured[i], (x, y))

            # Render quiz question if paused
            if self.paused_for_quiz:
                self.cyber_quiz.draw_question(self.screen, self.font)

            # Render player name input
            if self.name_input_active:
                name_text = self.font.render("Enter your name: " + self.player_name, True, (255, 255, 255))
                self.screen.blit(name_text, (50, 50))

            pygame.display.update()  # Refresh display

        except Exception as e:
            print(f"Render error: {e}")  # Catch rendering errors

if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()
