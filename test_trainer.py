from pygame import *
from trainerbinding import *

def TestTrainer():
	init()
	screen = display.set_mode((WIDTH, HEIGHT))
	surf = Surface((WIDTH, HEIGHT))
	trainerBinding = Trainer(surf)
	trainerBinding.initializeGame("ASDFASDF")
	clock = time.Clock()
	while trainerBinding.getSimulationStatus() == 0:
		frameData = trainerBinding.advanceFrame([])
		screen.blit(frameData.surface, (0, 0))
		display.flip()
		clock.tick(60)
	quit()
		
TestTrainer()
