import sys
import pygame
import random
import math
from enum import Enum
from pygame.locals import *

class Plane(pygame.sprite.Sprite):
    def __init__(self,game):
        super().__init__()
        self.game = game
        self.speed = 5
        self.hp = 100

class Player(Plane):
    def __init__(self,game):
        super().__init__(game)
        self.image = Game.PLAYER_IMAGE
        self.rect = self.image.get_rect()
        self.rect.center = (500,960)
        self.fire_CD = 5
        self.non_shoot_frame_count = 0
        self.movement = [0,0]
    def set_speed(self,new_speed):
        self.speed = new_speed
        
    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.top > 0:
            if pressed_keys[K_UP]:
                self.rect.move_ip(0, -self.speed)
                movement = {0,-self.speed}
        if self.rect.bottom < 1000:       
            if pressed_keys[K_DOWN]:
                self.rect.move_ip(0, self.speed)
                movement = {0, self.speed}
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-self.speed, 0)
                movement = {-self.speed, 0}
        if self.rect.right < 1000:       
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(self.speed, 0)
                movement = {self.speed,0}
        if self.non_shoot_frame_count > self.fire_CD:
            if pressed_keys[K_SPACE]:
                bullet = PlayerBullet(self,90)
                bullet1 = PlayerBullet(self,70,2)
                bullet2 = PlayerBullet(self,110,-2)
                self.game.BULLETS.add(bullet)
                self.game.BULLETS.add(bullet1)
                self.game.BULLETS.add(bullet2)
                self.non_shoot_frame_count = 0
        
        self.non_shoot_frame_count += 1

        if self.hp < 0:
            Display.displayGameOverScreen()
        #position = self.rect.center
        #print(f"Player is at ({position[0],position[1]})) HITBOX:({self.rect.left},{self.rect.right}).")

    def gotHitBy(self,bullets):
        for bullet in bullets:
            if isinstance(bullet,EnemyBullet):
                self.hp -= bullet.damage

    def draw(self,surface):
        surface.blit(self.image, self.rect)

class Enemy(Plane):
    def __init__(self,game,spawnoffset = 0):
        super().__init__(game)
        self.image = Game.ENEMY_IMAGE
        self.rect = self.image.get_rect()
        self.rect.center = (500+spawnoffset,-100)
        self.radius = 25
        self.fire_CD = 10
        self.non_shoot_frame_count = 0

        self.move_cooldown = 60
        self.angle = 270
        self.speed = 3


    def set_speed(self,new_speed):
        self.speed = new_speed

    def update(self):

        playerposition = self.game.PLAYER.rect.center
        playermovement = self.game.PLAYER.movement
        
        tagetpositionX = playerposition[0] + playermovement[0]
        tagetpositionY = playerposition[1] + playermovement[1]

        currentpositionX = self.rect.center[0]
        currentpositionY = self.rect.center[1]

        if self.move_cooldown<0:
            targetAngle = math.degrees(math.atan2(-(tagetpositionY - currentpositionY),(tagetpositionX - currentpositionX)))
            if(targetAngle < 0):
                targetAngle += 360

            if((((targetAngle - self.angle) + 180) % 360 - 180) > 0):
                self.angle += 0.5
            if((((targetAngle - self.angle) + 180) % 360 - 180) < 0):
                self.angle -= 0.5
            
            self.angle %= 360
        else:
            targetAngle = 270
            self.move_cooldown -= 1
        #print(f"Difference: X:{currentpositionX - tagetpositionX} Y: {currentpositionY - tagetpositionY} angle:{targetAngle} angle_real: {self.angle}")


        old_rect = self.rect
        self.image = pygame.transform.rotate(Game.ENEMY_IMAGE,self.angle-90)
        self.rect = self.image.get_rect()
        self.rect.center = old_rect.center

        dx = math.cos(math.radians(self.angle)) * self.speed
        dy = math.sin(math.radians(self.angle)) * self.speed
        self.rect.move_ip(dx, -dy)

        #print(f"{dx},{dy}")
        if self.non_shoot_frame_count > self.fire_CD and abs(targetAngle - self.angle) < 30:
            bullet = EnemyBullet(self,self.angle)
            self.game.BULLETS.add(bullet)
            self.non_shoot_frame_count = 0
        else:
            self.non_shoot_frame_count += 1

        #print(self.hp)
        if self.hp < 0:
            self.kill()
    def gotHitBy(self,bullets):
        for bullet in bullets:
            if isinstance(bullet,PlayerBullet):
                self.hp -= bullet.damage
    def draw(self,surface):
        surface.blit(self.image, self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,plane,angle):
        super().__init__()
        self.shooter: Plane = plane
        self.image =  pygame.transform.rotate(Game.BULLET_IMAGE,angle-90)
        self.speed = 50
        self.angle = angle
    
    def update(self):
        self.image = pygame.transform.rotate(Game.BULLET_IMAGE,self.angle-90)
        dx = math.cos(math.radians(self.angle)) * self.speed
        dy = math.sin(math.radians(self.angle)) * self.speed
        self.rect.move_ip(dx, -dy)

    def getDamage(self):
        return self.damage

    def draw(self,surface):
        surface.blit(self.image, self.rect)

class PlayerBullet(Bullet):
    def __init__(self,plane,angle,offset = 0):
        super().__init__(plane,angle)
        self.rect = self.image.get_rect()
        self.radius = 5
        self.rect.center = (int((self.shooter.rect.left + self.shooter.rect.right) / 2) + offset, self.shooter.rect.top)
        self.damage = 20
    
class EnemyBullet(Bullet):
    def __init__(self,plane,angle):
        super().__init__(plane,angle)
        self.rect = self.image.get_rect()
        self.radius = 5
        self.damage = 5

        spawnoffset = 50 #TODO: flexible spawn offset 
        posistionX = self.shooter.rect.centerx + spawnoffset * math.cos(math.radians(self.angle))
        posistionY = self.shooter.rect.centery - spawnoffset * math.sin(math.radians(self.angle))
        self.rect.center = (posistionX,posistionY)

        #print(f"Enenmy bullet spawned at {posistionX},{posistionY} angle: {self.angle} offset: {spawnoffset} plane rect size: {self.shooter.rect.w}, {self.shooter.rect.h}")

class Display():
    WINDOWSIZE_WIDTH = 1000;
    WINDOWSIZE_HEIGHT = 1000;
    DISPLAYSURF = pygame.display.set_mode((WINDOWSIZE_WIDTH,WINDOWSIZE_HEIGHT))
    GAMESTATE = None

    @staticmethod
    def update():
        Display.GAMESTATE.update()
        Display.GAMESTATE.draw()
        Display.GAMESTATE.tick()
        pygame.display.update()  

    @staticmethod
    def displayTitleScreen():
        Display.GAMESTATE = TitleScreen()

    @staticmethod
    def displayGameScreen():
        Display.GAMESTATE = Game()

    @staticmethod
    def displayGameOverScreen():
        Display.GAMESTATE = GameOverScreen()

class GameState():
    pass


class Game(GameState):
    #images
    PLAYER_IMAGE = None
    ENEMY_IMAGE = None
    BULLET_IMAGE = None

    #define colour
    BLACK = pygame.Color(0, 0, 0)         # Black
    WHITE = pygame.Color(255, 255, 255)   # White
    GRAY = pygame.Color(128, 128, 128)   # Grey
    RED = pygame.Color(255, 0, 0)       # Red
    LIGHTBLUE = pygame.Color(0, 191, 255)

    def __init__(self):

        Game.PLAYER_IMAGE = pygame.image.load("images/f16_50p.png")
        Game.ENEMY_IMAGE = pygame.image.load("images/MIG29_50p.png")
        Game.BULLET_IMAGE = pygame.image.load("images/bullet_i.png")

        self.DISPLAYSURF = Display.DISPLAYSURF
        self.DISPLAYSURF.fill(self.LIGHTBLUE) 

        #define objects
        self.PLAYER = Player(self)
        self.ENEMIES = pygame.sprite.Group()
        self.BULLETS = pygame.sprite.Group()

        self.FPS = pygame.time.Clock()

    def spawnEnemies(self):
        if len(self.ENEMIES) < 3:
            randomoffset = random.randint(-480,480)
            new_enemy = Enemy(self,randomoffset)
            self.ENEMIES.add(new_enemy)

    def update(self):
        self.spawnEnemies()

        self.BULLETS.update()
        self.PLAYER.update()
        self.ENEMIES.update()

        playerHits = pygame.sprite.groupcollide(self.ENEMIES,self.BULLETS,False,True,pygame.sprite.collide_circle).items()
        for enemy,bullets in playerHits:
            enemy.gotHitBy(bullets)

        enemyHits = pygame.sprite.spritecollide(self.PLAYER,self.BULLETS,False,pygame.sprite.collide_circle)
        self.PLAYER.gotHitBy(enemyHits)

    def draw(self):        
        self.DISPLAYSURF.fill(self.LIGHTBLUE)
        self.PLAYER.draw(self.DISPLAYSURF)
        self.ENEMIES.draw(self.DISPLAYSURF)
        self.BULLETS.draw(self.DISPLAYSURF)

    def tick(self):
        self.FPS.tick(60)


class TitleScreen(GameState):
    def __init__(self):
        titleText = '1999'
        titleColour = (255,255,255)
        options = ['START']
        optionColour = (255,255,255)

        self.optionFont = pygame.font.SysFont('Arial',30)
        self.titleFont = pygame.font.SysFont('Arial',100)
        self.displaysurf = Display.DISPLAYSURF
        
        self.previousKeyPressed = pygame.key.get_pressed()
        self.titleSurface = self.titleFont.render(titleText,False,titleColour)

        self.selectedOptionIndex = 0
        self.optionSurfaces = []
        for option in options:
            self.optionSurfaces.append(self.optionFont.render(option,False,optionColour))

        self.clock = pygame.time.Clock()


    def update(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_UP] and not self.previousKeyPressed[K_UP]:
            if self.selectedOptionIndex > 0:
                self.selectedOptionIndex -= 1
        if pressed_keys[K_DOWN] and not self.previousKeyPressed[K_DOWN]:
            if self.selectedOptionIndex < len(self.optionSurfaces) - 1:
                self.selectedOptionIndex += 1  

        if pressed_keys[K_RETURN]:
            if self.selectedOptionIndex == 0:
                Display.displayGameScreen()

        self.previousKeyPressed = pressed_keys

    def draw(self):
            titleSurfaceWidth,titleSurfaceHeight = self.titleSurface.get_size()
            titlePositionX = Display.WINDOWSIZE_WIDTH/2 - titleSurfaceWidth/2
            titlePositionY = (Display.WINDOWSIZE_HEIGHT/2)*2/3 - titleSurfaceHeight/2
            self.displaysurf.blit(self.titleSurface,(titlePositionX,titlePositionY))

            optionVerticalPosition = Display.WINDOWSIZE_HEIGHT * 2/3

            for value,optionSurface in enumerate(self.optionSurfaces):
                optionSurfaceWidth,optionSurfaceHeight = optionSurface.get_size()

                boxSurface = pygame.Surface((optionSurfaceWidth,optionSurfaceHeight))
                if value == self.selectedOptionIndex:
                    pygame.draw.rect(boxSurface,(255,0,0),optionSurface.get_rect(),1)
                else:
                    pygame.draw.rect(boxSurface,(0,0,0),optionSurface.get_rect(),1)

                optionPositionX = Display.WINDOWSIZE_WIDTH/2 - optionSurfaceWidth/2
                optionPositionY = optionVerticalPosition
                self.displaysurf.blit(boxSurface,(optionPositionX,optionPositionY))
                self.displaysurf.blit(optionSurface,(optionPositionX,optionPositionY))
                optionVerticalPosition += optionSurfaceHeight 
            
    def tick(self):
        self.clock.tick(30)

class GameOverScreen(GameState):
    def __init__(self):
        self.gameOverText = 'GAME OVER'
        self.gameOverTextFont = pygame.font.SysFont('Arial',100)

        self.deathMessage = 'Continue? (Press Esc to return to title, Press ENTER to play again)'
        self.deathMessageFont = pygame.font.SysFont('Arial',30)

        self.displaysurf = Display.DISPLAYSURF
        self.displaysurf.fill((0, 191, 255))

        self.clock = pygame.time.Clock()

    def update(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_RETURN]:
            Display.displayGameScreen()
        if key_pressed[K_ESCAPE]:
            Display.displayTitleScreen()
    def draw(self):
        gameOverTextSurface = self.gameOverTextFont.render(self.gameOverText,False,(255,0,0))

        gameOverTextSurfaceWidth, gameOverTextSurfaceHeight = gameOverTextSurface.get_size()
        gameOverTextPositionX = Display.WINDOWSIZE_WIDTH/2 - gameOverTextSurfaceWidth/2
        gameOverTextPositionY = (Display.WINDOWSIZE_HEIGHT/2 - gameOverTextSurfaceHeight/2)*2/6

        deathMessageSurface = self.deathMessageFont.render(self.deathMessage,False,(255,0,0))

        deathMessageSurfaceWidth, deathMessageSurfaceHeight = deathMessageSurface.get_size()
        deathMessagePositionX = Display.WINDOWSIZE_WIDTH/2 - deathMessageSurfaceWidth/2
        deathMessagePositionY = (Display.WINDOWSIZE_HEIGHT/2 - deathMessageSurfaceHeight/2)*3/6

        self.displaysurf.blit(gameOverTextSurface,(gameOverTextPositionX,gameOverTextPositionY))
        self.displaysurf.blit(deathMessageSurface,(deathMessagePositionX,deathMessagePositionY))

    def tick(self):
        self.clock.tick(30)

if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    gs = GameState()
    Display.displayTitleScreen()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        Display.update()
        


