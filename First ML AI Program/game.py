#Big thanks to https://github.com/patrickloeber/snake-ai-pytorch/blob/main/game.py
#Did not use it for the game.py, but used it as a baseline for this agent.py and used his model.

import pygame
import random
import numpy as np
from enum import Enum
from collections import namedtuple

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 450
ADDENEMY = pygame.USEREVENT + 1
enemy_killed_count = 0
reward = 0

#Dynamic
n_games = 1

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class Enemy(pygame.sprite.Sprite):
    def __init__(self, idx):
        super(Enemy, self).__init__()
        self.surf = pygame.Surface((20, 10))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect()
        x = random.randint(10, SCREEN_WIDTH - 10)
        y = random.randint(10, SCREEN_HEIGHT - 10)
        self.rect.topleft = (x, y)
        self.idx = idx
        enemy_positions.append((self.rect.x, self.rect.y))

    def update(self, player):
        global enemy_killed_count, reward
        if self.rect.colliderect(player.rect):
            enemy_killed_count += 1
            reward += 10
            #add print statement to debug here
            self.kill()
            enemy_positions.pop(self.idx)
            all_sprites.remove(self.idx)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((75, 25))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.enemies = enemies
        enemy_positions = [] #fucks up here after 6/7 rounds
        self.reset()

    def update(self, action):
        global reward, n_games
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [0, 0, 0, 1]):  # turn around
            new_idx = (idx + 3) % 4
            new_direction = clock_wise[new_idx]
        elif np.array_equal(action, [0, 1, 0, 0]):  # Turn Right
            new_idx = (idx + 1) % 4
            new_direction = clock_wise[new_idx]
        elif np.array_equal(action, [0, 0, 1, 0]):  # Turn Left
            new_idx = (idx + 2) % 4
            new_direction = clock_wise[new_idx]
        else:  # go straight
            new_direction = clock_wise[idx]

        self.direction = new_direction

        x = self.rect.x
        y = self.rect.y
        if self.direction == Direction.UP:
            y -= 5
        if self.direction == Direction.DOWN:
            y += 5
        if self.direction == Direction.LEFT:
            x -= 5
        if self.direction == Direction.RIGHT:
            x += 5

        self.rect.topleft = (x, y)

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def reset(self):
        global enemy_killed_count, reward, counter, running, gameOver, enemy_positions
        enemy_killed_count = 0
        reward = 0
        counter = 10
        running = True
        gameOver = False
        self.frame_iteration = 0
        # Reset the player's position and direction
        self.rect.topleft = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.direction = Direction.RIGHT

    def play_step(self, action):
        global running, gameOver, counter, reward, enemy_killed_count, n_games
        self.frame_iteration += 1
        self.update(action)
        self._update_ui()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == ADDENEMY:
                new_enemy = Enemy(len(self.enemies))
                self.enemies.add(new_enemy)
                all_sprites.add(new_enemy)

            elif event.type == pygame.USEREVENT:
                counter -= 1
                if counter <= 0 or self.frame_iteration > 100 * (enemy_killed_count + 2):
                    gameOver = True
                    n_games += 1
                    if self.frame_iteration > 100 * (enemy_killed_count + 2):
                        reward -= 2 * counter
                    print(reward)
                    for enemy in self.enemies:
                        enemy.kill()
                    self.enemies.empty()
                    all_sprites.empty()
                    enemy_positions.clear()
                    return reward, gameOver, enemy_killed_count

        pygame.display.flip() #mayeb delete
        clock.tick(60)

        # Check for collision with enemies
        for enemy in enemies:
            enemy.update(self)

        return reward, gameOver, enemy_killed_count

    def _update_ui(self):
        screen.fill((35, 79, 30))
        font = pygame.font.Font(None, 36)
        screen.blit(font.render(f'Time: {counter}', True, (255, 255, 255)), (10, 100))
        text = font.render(f'Enemies killed: {enemy_killed_count}', True, (255, 255, 255))
        screen.blit(text, (10, 10))
        screen.blit(self.surf, self.rect)  # Draw the player sprite
        for enemy in enemies:
            screen.blit(enemy.surf, enemy.rect)

#Initialization
pygame.init()
pygame.font.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.time.set_timer(ADDENEMY, 400)
pygame.time.set_timer(pygame.USEREVENT, 1000)

enemies = pygame.sprite.Group()
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
enemy_positions = []

Point = namedtuple('Point', 'x, y')

#need to make ai move the shit