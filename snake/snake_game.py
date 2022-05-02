import pygame
from enum import Enum
from easydict import EasyDict
from random import randint

pygame.init()
font = pygame.font.Font('font.ttf', 25)

Direction = {
    'RIGHT': 0,
    'LEFT': 2,
    'UP': 3,
    'DOWN': 1,
    '0': 'R',
    '1': 'D',
    '2': 'L',
    '3': 'U'
}
Direction = EasyDict(Direction)
# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE = (22, 124, 245)
GREEN = (117, 250, 97)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 40

DEAD = 0
ALIVE = 1
EAT = 2

class Snake:
    def __init__(self, cord):
        self.next = None
        self.cord = cord
    
    def update(self):
        if self.next != None:
            self.next.update()
            self.next.cord = self.cord
    
    def check(self, cord):
        if self.next != None:
            return self.next.check(cord) or self.cord == cord
        elif self.cord == cord:
            return True
        else:
            return False
        

class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()
    
    def reset(self):
        self._create_snake(1)
        self.score = 0
        self._food_reset()
        self.direction = Direction.RIGHT
        self._update_ui(ALIVE)
    
    def _create_snake(self, body_cnt:int):
        self.snake_head = Snake((self.w // 2, self.h // 2))
        self.snake_tail = self.snake_head
        
        self.now_x, self.now_y = self.snake_head.cord
        
        for i in range(1, body_cnt + 2):
            new_body = Snake((self.snake_tail.cord[0] - BLOCK_SIZE, self.snake_tail.cord[1]))
            self.snake_tail.next = new_body
            self.snake_tail = new_body

    def _status(self):        
        if self.now_x < 0 or self.now_x > self.w:
            return DEAD
        elif self.now_y < 0 or self.now_y > self.h:
            return DEAD
        elif self.snake_head.check((self.now_x, self.now_y)):
            return DEAD
        elif (self.now_x, self.now_y) == self.food:
            return EAT
        else:
            return ALIVE

    def play(self, action):
        '''
        action: (r, s, l) 우회전 직진 좌회전
        '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.move(action)
        s = self._status()

        if s == DEAD:
            reward = -10
        elif s == EAT:
            reward = 10
            self.score += 1

            new_head = Snake((self.now_x, self.now_y))
            new_head.next = self.snake_head
            self.snake_head = new_head

            self._food_reset()
        else:
            reward = 0
            self.score -= 0.01

            self.snake_update((self.now_x, self.now_y))

        self.score = max(0, self.score)
        if s != DEAD:
            self._update_ui(s)
            self.clock.tick(SPEED)

        return reward, s, self.score

    def _food_reset(self):
        while True:
            now_x, now_y = randint(0, (self.w - 1) // BLOCK_SIZE) * BLOCK_SIZE, randint(0, (self.h - 1) // BLOCK_SIZE) * BLOCK_SIZE
            if not self.snake_head.check((now_x, now_y)):
                break
        self.food = (now_x, now_y)
        if not self.snake_head.check((340, 240)):
            self.food = (340, 240)

    def _update_ui(self, status):
        if status == DEAD:
            return
        self.display.fill(BLACK)
        s = self.snake_head
        
        a = []

        while s != None:
            if s == self.snake_head:
                pygame.draw.rect(self.display, BLUE, pygame.Rect(s.cord[0], s.cord[1], BLOCK_SIZE, BLOCK_SIZE))
            else:
                pygame.draw.rect(self.display, GREEN, pygame.Rect(s.cord[0], s.cord[1], BLOCK_SIZE, BLOCK_SIZE))
            a.append(s.cord)
            s = s.next
        
        if status != EAT:
            pygame.draw.rect(self.display, RED, pygame.Rect(self.food[0], self.food[1], BLOCK_SIZE, BLOCK_SIZE))
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def move(self, action):
        i1 = action[1]
        i2 = action[0] - action[2]

        if self.direction in [Direction.DOWN, Direction.UP]:
            i1 = i1 + i2
            i2 = i1 - i2
            i1 = i1 - i2
        
        if self.direction in [Direction.DOWN, Direction.LEFT]:
            i1 *= -1
        
        if self.direction in [Direction.UP, Direction.LEFT]:
            i2 *= -1
        
        self.now_x += i1 * BLOCK_SIZE
        self.now_y += i2 * BLOCK_SIZE

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        self.direction = clock_wise[(4 + self.direction + action[0] - action[2]) % 4]

    def snake_update(self, cord):
        self.snake_head.update()
        self.snake_head.cord = cord


move_dict = {
    0: (1, 0, 0),
    1: (0, 1, 0),
    2: (0, 0, 1),
}

while True:
    test = SnakeGame()

    for i in range(100):
        reward, s, score = test.play(move_dict[randint(0, 2)])
        print(f'reward:{reward}, state:{s}, score:{score}')
        if s == DEAD:
            break

    a = input()
    if a == 'q':
        break
