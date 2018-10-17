from pygame import *
from trainerbinding import *

def TestTrainer():
	init()
	screen = display.set_mode((WIDTH, HEIGHT))
	surf = Surface((WIDTH, HEIGHT))
	trainerBinding = Trainer(surf)
	trainerBinding.initializeGame("ASDFASDF")
	clock = time.Clock()

	running = True
	while running and trainerBinding.getSimulationStatus() == 0:
		# a harness for computer input, detects when the x
		# on the window has been clicked and exits accordingly
		for evt in event.get():
			if evt.type == QUIT:
				running = False;

		# a harness for computer input, detects all keyboard keys
		# - you can remove this and just have the agent send
		# these events :)
		keys = key.get_pressed()
		for k in [Trainer.MOVE_LEFT,
			  Trainer.MOVE_RIGHT,
			  Trainer.MOVE_UP,
			  Trainer.MOVE_DOWN,
			  Trainer.SHOOT_LEFT,
			  Trainer.SHOOT_RIGHT,
			  Trainer.SHOOT_UP,
			  Trainer.SHOOT_DOWN]:
			if keys[k]:
				# this indicates that this frame,
				# key k is pushed
				trainerBinding.sendPushKeyEvent(k)

		# advance the simulation
		frameData = trainerBinding.advanceFrame()

		# pull out some frame information
		screen.blit(frameData.surface, (0, 0))
		display.flip()
		clock.tick(60)
	quit()
		
TestTrainer()
