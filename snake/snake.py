import pygame
import os
import random
import time

WIN_WIDTH = 1000
WIN_HEIGHT = 1000

path =  os.path.join(os.path.dirname(__file__), 'snake_imgs')
BODY_IMG = pygame.image.load(os.path.join(path, 'body.png'))
HEAD_IMGs = {'up' : pygame.image.load(os.path.join(path, 'head_up.png')),
			'down' : pygame.image.load(os.path.join(path, 'head_down.png')),
			'left' : pygame.image.load(os.path.join(path, 'head_left.png')),
			'right' : pygame.image.load(os.path.join(path, 'head_right.png'))}
BG_IMG = pygame.image.load(os.path.join(path, 'bg.png'))
BG_IMG = pygame.transform.scale(BG_IMG, (WIN_WIDTH, WIN_HEIGHT))
FOOD_IMG = pygame.image.load(os.path.join(path, 'food.png'))

class Node(object):
	"""docstring for node"""
	def __init__(self, x, y, img):
		super(Node, self).__init__()
		self.x = x
		self.y = y
		self.img = pygame.transform.scale(img, (50, 50))

	def draw(self, win):
		win.blit(self.img, (self.x, self.y))

	def move(self, direct):
		if direct == 'up':
			self.y -= 50
		elif direct == 'down':
			self.y += 50
		elif direct == 'left':
			self.x -= 50
		elif direct == 'right':
			self.x += 50

class Snake(object):
	"""docstring for snake"""
	def __init__(self, x, y, direct):
		super(Snake, self).__init__()
		self.direct = direct
		self.head = Node(x, y, HEAD_IMGs[self.direct])
		self.body = []

	def draw(self, win):
		self.head.draw(win)
		for node in self.body:
			node.draw(win)

	def move(self, grow):
		self.body.append(Node(self.head.x, self.head.y, BODY_IMG))
		if not grow:
			self.body.pop(0)
		self.head.move(self.direct)

	def turn(self, direct):
		self.direct = direct
		self.head = Node(self.head.x, self.head.y, HEAD_IMGs[self.direct])


def draw_win(win, snake, food):
	win.blit(BG_IMG, (0,0))
	food.draw(win)
	snake.draw(win)
	pygame.display.update()

def get_input(snake):
	if snake.direct == 'up':
		return ()

def game(genomes, config):
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	run = True
	clock = pygame.time.Clock()

	for _, g in genomes:
		snake = Snake(random.randint(0, WIN_WIDTH/50-1)*50,
						random.randint(0, WIN_HEIGHT/50-1)*50,
						random.choice(['up','down','left','right']))
		gen = g 
		gen.fitness = 0
		net = neat.nn.FeedForwardNetwork.create(gen, config)

	food = Node(random.randint(0, WIN_WIDTH/50-1)*50,
				random.randint(0, WIN_HEIGHT/50-1)*50,
				FOOD_IMG)
	while run:
		clock.tick(5)
		grow = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
			# if event.type == pygame.KEYDOWN:
			# 	if event.key == pygame.K_UP:
			# 		snake.turn('up')
			# 	elif event.key == pygame.K_DOWN:
			# 		snake.turn('down')
			# 	elif event.key == pygame.K_LEFT:
			# 		snake.turn('left')
			# 	elif event.key == pygame.K_RIGHT:
			# 		snake.turn('right')


		output = net.activate()

		if snake.head.x == food.x and snake.head.y == food.y:
			food = Node(random.randint(0, WIN_WIDTH/50-1)*50,
						random.randint(0, WIN_HEIGHT/50-1)*50,
						FOOD_IMG)
			grow = True

		snake.move(grow)
		if snake.head.x < 0 or snake.head.y < 0 or snake.head.x >= WIN_WIDTH or snake.head.y >= WIN_HEIGHT:
			run = False
		for node in snake.body:
			if snake.head.x == node.x and snake.head.y == node.y:
				run = False
		draw_win(win, snake, food)
	
def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
								neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
	p = neat.Population(config)
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	winner = p.run(main,100)

if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'neat_config.txt')
	run(config_path)