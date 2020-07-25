import pygame
import random
import time
import os
import neat
import numpy as np

WIN_WIDTH = 1500 
WIN_HEIGHT = 900
path =  os.path.join(os.path.dirname(__file__), 'fish_imgs')
BG_IMG = pygame.image.load(os.path.join(path, "back_ground.jpg"))
BG_IMG = pygame.transform.scale(BG_IMG, (WIN_WIDTH,WIN_HEIGHT))
FISH_IMGS = [pygame.image.load(os.path.join(path, "main_fish.png")),
			pygame.image.load(os.path.join(path, "fish1.png")),
			pygame.image.load(os.path.join(path, "fish2.png")),
			pygame.image.load(os.path.join(path, "fish3.png")),
			pygame.image.load(os.path.join(path, "fish4.png")),
			pygame.image.load(os.path.join(path, "fish5.png"))]
VISION_IMG = pygame.image.load(os.path.join(path, "vision.png"))
FOOD_IMG =  pygame.image.load(os.path.join(path, "food.png"))
FOOD_IMG = pygame.transform.scale(FOOD_IMG, (10, 10))
SIZES = [100, 80, 120, 160, 200, 240]
SPEEDS = [10, 10, 10, 10, 10, 10]
VISION = 400
I_DS = [1]*16+[2]*12+[3]*8+[4]*4+[5]*2

def dist(a, b):
	return ((a.x-b.x)**2 + (a.y-b.y)**2)**(0.5)

class Fish(object):
	"""docstring for Fish"""
	def __init__(self, i_d, is_left=True, x=0, y=0):
		super(Fish, self).__init__()
		self.x = x
		self.y = y
		self.size = SIZES[i_d]
		self.i_d = i_d
		self.is_left = is_left
		self.LEFT_IMG = pygame.transform.scale(FISH_IMGS[i_d], (self.size,self.size))
		self.RIGHT_IMG = pygame.transform.flip(self.LEFT_IMG, True, False)
		self.LEFT_VISION = pygame.transform.scale(VISION_IMG, (VISION,VISION))
		self.RIGHT_VISON = pygame.transform.flip(self.LEFT_VISION, True, False)
		self.img = {True : self.LEFT_IMG, False : self.RIGHT_IMG}
		self.speed = {True : -SPEEDS[i_d], False : SPEEDS[i_d]}
		self.energy = 500
		# self.vision = {True : self.LEFT_VISION, False : self.RIGHT_VISON}
		# self.vision_y = round(self.size/2 - VISION/2)
		# self.vision_x = {True : -VISION, False : self.size}

	def draw(self, win):
		win.blit(self.img[self.is_left], (self.x-self.size/2,self.y-self.size/2))
		#win.blit(self.vision[self.is_left], (self.vision_x[self.is_left]+self.x,self.vision_y+self.y))

	def main_move(self):
		self.x, self.y = pygame.mouse.get_pos()
		delta_x, delta_y = pygame.mouse.get_rel()
		if delta_x < 0:
			self.is_left = True
		elif delta_x > 0:
			self.is_left = False

	def get_mask(self):
		return pygame.mask.from_surface(self.img[self.is_left])

	def get_vision(self):
		return pygame.mask.from_surface(self.vision[self.is_left])

	def see(self, fish):
		return self.get_vision().overlap(fish.get_mask(),
			(abs(self.vision_x[self.is_left]+self.x-fish.x), 
			abs(self.vision_y+self.y-fish.y)))

	def eat(self, fish):
		if self.size <= fish.size:
		 	return False
		# if self.see(fish):
		# 	return True
		if self.is_left and self.x > fish.x:
			if dist(self,fish) < self.size/2+fish.size/2:
				self.energy += fish.size
				return True
			else:
				return False
			#return self.get_mask().overlap(fish.get_mask(), (abs(self.x-fish.x), abs(self.y-fish.y)))
		if not self.is_left and self.x < fish.x:
			if dist(self,fish) < self.size/2+fish.size/2:
				self.energy += fish.size
				return True
			else:
				return False
			#return self.get_mask().overlap(fish.get_mask(), (abs(self.x-fish.x), abs(self.y-fish.y)))
		return False

	def grow(self, delta):
		self.size += delta
		img = pygame.transform.scale(FISH_IMGS[self.i_d], (self.size,self.size))
		self.img = {True : img, False : pygame.transform.flip(img, True, False)}

	def fail(self):
		self.y += 5

	def move_forward(self):
		if self.energy <= 0:
			return False
		self.x += self.speed[self.is_left]
		self.energy -= 2
		return True

	def move_up(self):
		if self.energy <= 0:
			return False
		self.y -= SPEEDS[self.i_d]
		self.energy -= 2
		return True

	def move_down(self):
		if self.energy <= 0:
			return False
		self.y += SPEEDS[self.i_d]
		self.energy -= 2
		return True

	def turn(self):
		if self.energy <= 0:
			return False
		self.is_left = not self.is_left
		return True


class Food():
	"""docstring for Food"""
	def __init__(self):
		self.x = random.randint(0, WIN_WIDTH)
		self.y = 0
		self.size = 10
		self.is_left = False

	def fail(self):
		self.y += 5

	def draw(self, win):
		win.blit(FOOD_IMG, (self.x, self.y))
		

def draw_window(win, main_fish, fishs, foods):
	win.blit(BG_IMG, (0,0))
	main_fish.draw(win)
	for fish in fishs:
		fish.draw(win)

	for food in foods:
		food.draw(win)
	pygame.display.update()

def gen_fish(k):
	fishs = []
	for i_d in random.choices(I_DS, k=k):
		is_left = random.choice([True, False])
		pos_x = {True :  WIN_WIDTH, False : 0-SIZES[i_d]}
		fish = Fish(i_d, is_left, pos_x[is_left], random.randint(0, WIN_HEIGHT))  
		fishs.append(fish)
	return fishs


def game(genomes, config):
	run = True
	clock = pygame.time.Clock()
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	main_fish = Fish(0, True, 500, 500)
	fishs = []
	gens = []
	nets = []
	foods = []
	pygame.mouse.set_visible(False)
	points = 0
	ctr = 0

	for _, gen in genomes:
		net = neat.nn.FeedForwardNetwork.create(gen, config)
		nets.append(net)
		gen.fitness = 0
		gens.append(gen)

	while  run:
		clock.tick(20)
		rem = set()
		foods.append(Food())
		if ctr < len(gens) and random.choice([True, False, False]):
			fishs += gen_fish(1)
			ctr += 1

		if len(fishs) <= 0:
			run = False
			break

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()

		main_fish.main_move()
		for food in foods:
			food.fail()
			if food.y > WIN_HEIGHT:
				foods.remove(food)
		for i, fish in enumerate(fishs):
			fish.fail()
			objs = fishs + foods
			distances = [dist(fish, obj) for obj in objs if obj != fish]
			if len(distances) > 0:
				nearest = np.argmin(distances)
				output = nets[i].activate(
						(objs[nearest].x/WIN_WIDTH, 
						objs[nearest].y/WIN_HEIGHT, 
						1 if objs[nearest].is_left else 0, 
						(objs[nearest].size-10)/230,
						fish.x/WIN_WIDTH, 
						fish.y/WIN_HEIGHT, 
						1 if fish.is_left else 0, 
						(fish.size-10)/230, 
						fish.energy/500))
			else:
				output = nets[i].activate((0, 0, fish.energy))

			direct = np.argmax(output)
			if direct == 3:
				if fish.move_up():
					gens[i].fitness += 5
			elif direct == 2:
				if fish.move_down():
					gens[i].fitness += 5
			elif direct == 0:
				if fish.move_forward():
					gens[i].fitness += 5
			elif direct == 1:
				fish.turn()
				if fish.move_forward():
					gens[i].fitness += 5

			if fish.x + fish.size < 0 or fish.x > WIN_WIDTH or fish.y + fish.size < 0 or fish.y > WIN_HEIGHT: 
				gens[i].fitness -=1000
				gens.pop(i)
				fishs.pop(i)
				nets.pop(i)

		for j, fish1 in enumerate(fishs):
			for i, fish2 in enumerate(fishs):
				if fish1.eat(fish2):
					gens[i].fitness -=1000
					#gens[j].fitness += fish2.size
					gens.pop(i)
					fishs.pop(i)
					nets.pop(i)
			for food in foods:
				if fish1.eat(food):
					#gens[j].fitness += food.size
					foods.remove(food)
			# if main_fish.eat(fish1):
			# 	rem.add(fish1)
			# 	points += fish1.size

		# for i in rem:
		# 	gens[i].fitness -=10
		# 	gens.pop(i)
		# 	fishs.pop(i)
		# 	nets.pop(i)

		# if points > 500:
		# 	points = 0
		# 	main_fish.grow(40)
		for i, fish in enumerate(fishs):
			if fish.energy <= 0:
				gens[i].fitness -=1000
				gens.pop(i)
				fishs.pop(i)
				nets.pop(i)

		draw_window(win, main_fish, fishs, foods)

def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
								neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
	p = neat.Population(config)
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	winner = p.run(game,1000000)

if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'neat_config.txt')
	run(config_path)