import sys
import pygame
import random
import math
from pygame.locals import *

pygame.init()

#config
WINDOWSIZE_WIDTH = 1000
WINDOWSIZE_LENGTH = 1000



BLACK = pygame.Color(0, 0, 0)         # Black
WHITE = pygame.Color(255, 255, 255)   # White
GRAY = pygame.Color(128, 128, 128)   # Grey
RED = pygame.Color(255, 0, 0)       # Red
LIGHTBLUE = pygame.Color(0, 191, 255)

DISPLAYSURF = pygame.display.set_mode((WINDOWSIZE_WIDTH,WINDOWSIZE_LENGTH))
DISPLAYSURF.fill(LIGHTBLUE)

PLAYER = None
BULLETS = pygame.sprite.Group()
ENEMIES = pygame.sprite.Group()

#IMAGES
PLAYER_IMAGE = pygame.image.load("images/f16_50p.png")
ENEMY_IMAGE = pygame.image.load("images/MIG29_50p.png")
BULLET_IMAGE = pygame.image.load("images/bullet_i.png")


FPS = pygame.time.Clock()

class Plane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.speed = 5
        self.hp = 100

class Player(Plane):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMAGE
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
                BULLETS.add(bullet)
                BULLETS.add(bullet1)
                BULLETS.add(bullet2)
                self.non_shoot_frame_count = 0
        



        self.non_shoot_frame_count += 1
        #position = self.rect.center
        #print(f"Player is at ({position[0],position[1]})) HITBOX:({self.rect.left},{self.rect.right}).")

    def draw(self,surface):
        surface.blit(self.image, self.rect)

class Enemy(Plane):
    def __init__(self,spawnoffset = 0):
        super().__init__()
        self.image = ENEMY_IMAGE
        self.rect = self.image.get_rect()
        self.rect.center = (500+spawnoffset,160)
        self.radius = 25
        self.fire_CD = 30
        self.non_shoot_frame_count = 0

        self.angle = 270
        self.speed = 3


    def set_speed(self,new_speed):
        self.speed = new_speed

    def update(self):

        playerposition = PLAYER.rect.center
        playermovement = PLAYER.movement
        
        tagetpositionX = playerposition[0] + playermovement[0]
        tagetpositionY = playerposition[1] + playermovement[1]

        currentpositionX = self.rect.center[0]
        currentpositionY = self.rect.center[1]


        targetAngle = math.degrees(math.atan2(-(tagetpositionY - currentpositionY),(tagetpositionX - currentpositionX)))
        if(targetAngle < 0):
            targetAngle += 360

        if((((targetAngle - self.angle) + 180) % 360 - 180) > 0):
            self.angle += 1
        if((((targetAngle - self.angle) + 180) % 360 - 180) < 0):
            self.angle -= 1
        
        self.angle %= 360

        #print(f"Difference: X:{currentpositionX - tagetpositionX} Y: {currentpositionY - tagetpositionY} angle:{targetAngle} angle_real: {self.angle}")


        old_rect = self.rect
        self.image = pygame.transform.rotate(ENEMY_IMAGE,self.angle-90)
        self.rect = self.image.get_rect()
        self.rect.center = old_rect.center

        dx = math.cos(math.radians(self.angle)) * self.speed
        dy = math.sin(math.radians(self.angle)) * self.speed
        self.rect.move_ip(dx, -dy)

        #print(f"{dx},{dy}")
        if self.non_shoot_frame_count > self.fire_CD:
            bullet = EnemyBullet(self,self.angle)
            BULLETS.add(bullet)
            self.non_shoot_frame_count = 0
        else:
            self.non_shoot_frame_count += 1

        #print(self.hp)
        if self.hp < 0:
            self.kill()
        

    def draw(self,surface):
        surface.blit(self.image, self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,plane,angle):
        super().__init__()
        self.shooter: Plane = plane
        self.image =  pygame.transform.rotate(BULLET_IMAGE,angle-90)
        self.speed = 50
        self.angle = angle
    
    def update(self):
        self.image = pygame.transform.rotate(BULLET_IMAGE,self.angle-90)
        dx = math.cos(math.radians(self.angle)) * self.speed
        dy = math.sin(math.radians(self.angle)) * self.speed
        self.rect.move_ip(dx, -dy)

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
        #print(f"Enenmy bullet spawned at {posistionX},{posistionY} angle: {self.angle} offset: {spawnoffset} plane rect size: {self.shooter.rect.w}, {self.shooter.rect.h}")
        self.rect.center = (posistionX,posistionY)




PLAYER = Player()
ENEMY = Enemy()
ENEMIES.add(ENEMY)
score = 0


#Game Loop 
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    BULLETS.update()
    PLAYER.update()
    ENEMIES.update()

    #enemy spawning
    if len(ENEMIES) <5:
        randomoffset = random.randint(-480,480)
        new_enemy = Enemy(randomoffset)
        ENEMIES.add(new_enemy)
    DISPLAYSURF.fill(LIGHTBLUE)
    PLAYER.draw(DISPLAYSURF)
    ENEMIES.draw(DISPLAYSURF)
    BULLETS.draw(DISPLAYSURF)

    playerHits = pygame.sprite.groupcollide(ENEMIES,BULLETS,False,True,pygame.sprite.collide_circle).items()
    for enemy,bullets in playerHits:
        enemy.hp -= len(bullets) * 20

    pygame.display.update()
    FPS.tick(60)

