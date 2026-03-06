import sys
import pygame
import random
import math
from pygame.locals import *

class Plane(pygame.sprite.Sprite):
    def __init__(self,game):
        super().__init__()
        self.game = game
        self.speed = 5
        self.hp = 100
            
    def gotHitBy(self, bullets):
        for bullet in bullets:
            self.hp -= bullet.getDamage()

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
        #position = self.rect.center
        #print(f"Player is at ({position[0],position[1]})) HITBOX:({self.rect.left},{self.rect.right}).")

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

class Game:
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
        pygame.init()

        Game.PLAYER_IMAGE = pygame.image.load("images/f16_50p.png")
        Game.ENEMY_IMAGE = pygame.image.load("images/MIG29_50p.png")
        Game.BULLET_IMAGE = pygame.image.load("images/bullet_i.png")

        #define window size
        self.WINDOWSIZE_WIDTH = 1000;
        self.WINDOWSIZE_LENGTH = 1000;

        self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWSIZE_WIDTH,self.WINDOWSIZE_LENGTH))
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

        pygame.display.update()

    def tick(self):
        self.FPS.tick(60)


if __name__ == '__main__':
    g = Game()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        g.spawnEnemies()
        g.update()
        g.draw()
        g.tick()


