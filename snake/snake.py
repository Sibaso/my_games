import pygame
import os
import random
import time
import neat
import numpy as np

WIN_WIDTH = 800
WIN_HEIGHT = 800
SIZE = 40
SPACE_ENCODE = 0
WALL_ENCODE = 1
NUM_SNAKES = 50
SNAKE_ENCODE = 2
FOOD_ENCODE = 3

path =  os.path.join(os.path.dirname(__file__), 'snake_imgs')
BODY_IMG = pygame.image.load(os.path.join(path, 'body.png'))
HEAD_IMGs = {'up' : pygame.image.load(os.path.join(path, 'head_up.png')),
			'down' : pygame.image.load(os.path.join(path, 'head_down.png')),
			'left' : pygame.image.load(os.path.join(path, 'head_left.png')),
			'right' : pygame.image.load(os.path.join(path, 'head_right.png'))}
BG_IMG = pygame.image.load(os.path.join(path, 'bg.png'))
BG_IMG = pygame.transform.scale(BG_IMG, (WIN_WIDTH, WIN_HEIGHT))
FOOD_IMG = pygame.image.load(os.path.join(path, 'food.png'))

opo = {'up':'down', 'down':'up', 'left':'right', 'right':'left'}
i_d = {'up':0, 'down':1, 'left':2, 'right':3}

class Node(object):
	"""docstring for node"""
	def __init__(self, x, y, img, mask, encode):
		super(Node, self).__init__()
		self.x = x
		self.y = y
		self.mask = mask
		self.encode = encode
		self.mask[x][y]= encode
		self.img = pygame.transform.scale(img, (SIZE, SIZE))

	def draw(self, win):
		win.blit(self.img, (self.x*SIZE-SIZE, self.y*SIZE-SIZE))

	def move(self, direct):
		self.mask[self.x][self.y] = SPACE_ENCODE
		if direct == 'up':
			self.y -= 1
		elif direct == 'down':
			self.y += 1
		elif direct == 'left':
			self.x -= 1
		elif direct == 'right':
			self.x += 1
		flag = self.mask[self.x][self.y]
		self.mask[self.x][self.y] = self.encode
		return flag


class Snake(object):
	"""docstring for snake"""
	def __init__(self, x, y, direct, mask):
		super(Snake, self).__init__()
		self.direct = direct
		self.mask = mask
		self.head = Node(x, y, HEAD_IMGs[self.direct], self.mask, SNAKE_ENCODE)
		self.body = []
		while True:
			fx = random.randint(1, WIN_WIDTH/SIZE)
			fy = random.randint(1, WIN_HEIGHT/SIZE)
			if self.mask[fx][fy] == SPACE_ENCODE:	
				self.food = Node(fx, fy, FOOD_IMG, self.mask, FOOD_ENCODE)
				break

	def draw(self, win):
		self.food.draw(win)
		self.head.draw(win)
		for node in self.body:
			node.draw(win)

	def move(self):
		x, y = self.head.x, self.head.y
		flag = self.head.move(self.direct)
		self.body.append(Node(x, y, BODY_IMG, self.mask, SNAKE_ENCODE))
		if flag == WALL_ENCODE or flag == SNAKE_ENCODE:
			state = 'dead'
			node = self.body.pop(0)
			self.mask[node.x][node.y] = SPACE_ENCODE
		elif flag == FOOD_ENCODE:
			state = 'eat'
			while True:
				fx = random.randint(1, WIN_WIDTH/SIZE)
				fy = random.randint(1, WIN_HEIGHT/SIZE)
				if self.mask[fx][fy] == SPACE_ENCODE:	
					self.food = Node(fx, fy, FOOD_IMG, self.mask, FOOD_ENCODE)
					break
		else:
			state = 'alive'
			node = self.body.pop(0)
			self.mask[node.x][node.y] = SPACE_ENCODE
		return state

	def turn(self, direct):
		if direct == opo[self.direct]:
			return True
		self.direct = direct
		self.head = Node(self.head.x,self.head.y,HEAD_IMGs[self.direct],self.mask,SNAKE_ENCODE)
		return False

def draw_win(win, snakes):
	win.blit(BG_IMG, (0,0))
	for snake in snakes:
		snake.draw(win)
	pygame.display.update()

def get_mask():
	mask = [[WALL_ENCODE for _ in range(int(WIN_WIDTH/SIZE)+2)]]
	mask = mask + [[WALL_ENCODE]+[SPACE_ENCODE for _ in range(int(WIN_WIDTH/SIZE))]+[WALL_ENCODE] 
					for _ in range(int(WIN_HEIGHT/SIZE))]
	mask = mask + [[WALL_ENCODE for _ in range(int(WIN_WIDTH/SIZE)+2)]]
	return mask

def get_input(snake):
	x, y, mask = snake.head.x, snake.head.y, snake.mask
	_input = [((x-snake.food.x)**2 + (y-snake.food.y)**2)**(0.5)]

	t, dist = y, 0
	while True:
		t-=1
		dist += 1
		if mask[x][t] == WALL_ENCODE or mask[x][t] == SNAKE_ENCODE:
			_input.append(dist)
			break
		elif mask[x][t] == FOOD_ENCODE:
			_input.append(-dist)
			break

	t, dist = y, 0
	while True:
		t+=1
		dist += 1
		if mask[x][t] == WALL_ENCODE or mask[x][t] == SNAKE_ENCODE:
			_input.append(dist)
			break
		elif mask[x][t] == FOOD_ENCODE:
			_input.append(-dist)
			break

	t, dist = x, 0
	while True:
		t-=1
		dist += 1
		if mask[t][y] == WALL_ENCODE or mask[t][y] == SNAKE_ENCODE:
			_input.append(dist)
			break
		elif mask[t][y] == FOOD_ENCODE:
			_input.append(-dist)
			break

	t, dist = x, 0
	while True:
		t+=1
		dist += 1
		if mask[t][y] == WALL_ENCODE or mask[t][y] == SNAKE_ENCODE:
			_input.append(dist)
			break
		elif mask[t][y] == FOOD_ENCODE:
			_input.append(-dist)
			break

	return _input

def player_game():
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	run = True
	clock = pygame.time.Clock()
	mask = get_mask()
	snake = Snake(random.randint(1, WIN_WIDTH/SIZE),
					random.randint(1, WIN_HEIGHT/SIZE),
					random.choice(['up','down','left','right']),
					mask)
	while run:
		clock.tick(5)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				break
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					snake.turn('up')
				elif event.key == pygame.K_DOWN:
					snake.turn('down')
				elif event.key == pygame.K_LEFT:
					snake.turn('left')
				elif event.key == pygame.K_RIGHT:
					snake.turn('right')

		state = snake.move()
		if state == 'dead':
			run = False
			break

		draw_win(win, [snake])
	pygame.quit()
	quit()


def game(genomes, config):
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	run = True
	clock = pygame.time.Clock()
	snakes, gens, nets = [], [], []

	for i, gen in genomes:
		mask = get_mask()
		snake = Snake(int(WIN_WIDTH/SIZE/2), int(WIN_HEIGHT/SIZE/2), 'up', mask)
		# snake = Snake(random.randint(1, WIN_WIDTH/SIZE),
		# 				random.randint(1, WIN_HEIGHT/SIZE),
		# 				random.choice(['up','down','left','right']),
		# 				mask)
		gen.fitness = 0
		net = neat.nn.FeedForwardNetwork.create(gen, config)
		snakes.append(snake)
		gens.append(gen)
		nets.append(net)

	while run:
		clock.tick(5)
		if len(snakes) == 0:
			run = False
			break

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()


		for i, snake in enumerate(snakes):
			output = nets[i].activate(get_input(snake))
			direct = np.argmax(output)
			if direct == 0:
				if snake.turn('up'):
					gens[i].fitness -=10
			elif direct == 1:
				if snake.turn('down'):
					gens[i].fitness -=10
			elif direct == 2:
				if snake.turn('left'):
					gens[i].fitness -=10
			elif direct == 3:
				if snake.turn('right'):
					gens[i].fitness -=10

			state = snake.move()
			if state == 'eat':
				gens[i].fitness += 10
			elif state == 'dead':
				gens[i].fitness -= 100
				snakes.pop(i)
				gens.pop(i)
				nets.pop(i)

		draw_win(win, snakes)
	
def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
								neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
	p = neat.Population(config)
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	winner = p.run(game,1000)

if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'neat_config.txt')
	#run(config_path)
	player_game()