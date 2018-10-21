# -----------------------------
# File: train Isaac AI
# Author: Yizhuo, Eugene
# Date: 2018.10.21
# -----------------------------

from pygame import *
from trainerbinding import *
import numpy as np
import cv2
import sys
sys.path.append("game/")
from BrainDQN_Nature import BrainDQN

# preprocess input frame, resize to 80*80 and to grayscale
def preprocess(observation):
	observation = cv2.cvtColor(cv2.resize(observation, (80, 80)), cv2.COLOR_BGR2GRAY)
	return np.reshape(observation,(80,80,1))

def TestTrainer():
	init()
	screen = display.set_mode((WIDTH, HEIGHT))
	surf = Surface((WIDTH, HEIGHT))
	trainerBinding = Trainer(surf)

	# start game, create DQN
	trainerBinding.initializeGame("ASDFASDF",startAtBoss=True)
	clock = time.Clock()
	actions = 8
	brain = BrainDQN(actions)
	actionList = [Trainer.MOVE_LEFT,
	  Trainer.MOVE_RIGHT,
	  Trainer.MOVE_UP,
	  Trainer.MOVE_DOWN,
	  Trainer.SHOOT_LEFT,
	  Trainer.SHOOT_RIGHT,
	  Trainer.SHOOT_UP,
	  Trainer.SHOOT_DOWN]
    
    # initialize first state
	action0 = np.array([1,0,0,0,0,0,0,0])
	trainerBinding.sendPushKeyEvent(actionList[np.argmax(action0)])
	frameData0 = trainerBinding.advanceFrame()
	observation0 = surfarray.array3d(frameData0.surface)
	observation0 = cv2.cvtColor(cv2.resize(observation0, (80, 80)), cv2.COLOR_BGR2GRAY)
	ret, observation0 = cv2.threshold(observation0,1,255,cv2.THRESH_BINARY)
	brain.setInitState(observation0)
	lastIsaacHP = frameData0.isaac_hp
	lastBossHP = frameData0.boss_hp

    #start trainings
	running = True
	score = 0
	epochs = 0
	winEpoch = 0
	while running:
		# print current epoch and score
		print("epoch", epochs, "/ score", score)
		# a harness for computer input, detects when the x
		# on the window has been clicked and exits accordingly
		for evt in event.get():
			if evt.type == QUIT:
				print("first win epoch", winEpoch)
				running = False;
		# get action from the DQN
		action = brain.getAction()
		currentAction = actionList[np.argmax(action)]
		trainerBinding.sendPushKeyEvent(currentAction)
		# advance the simulation
		frameData = trainerBinding.advanceFrame()
		# get hp
		currentIsaacHP = frameData.isaac_hp
		currentBossHP = frameData.boss_hp
		# if boss is dead, restart game and update score and epochs
		if currentBossHP == 0:
			score = score + 1
			epochs = epochs + 1
			if score = 1:
				winEpoch = epochs
		    trainerBinding.initializeGame("ASDFASDF",startAtBoss=True)
		# get reward
		reward = getReward(currentIsaacHP, lastIsaacHP, currentBossHP, lastBossHP)
		lastIsaacHP = currentIsaacHP
		lastBossHP = currentBossHP
		# get terminal state, if terminal, restart game and update epochs
		terminal = terminalState(trainerBinding.getSimulationStatus())
		if terminal == True:
			epochs = epochs + 1
	                trainerBinding.initializeGame("ASDFASDF",startAtBoss=True)
		# train
		nextObservation = surfarray.array3d(frameData.surface)
		nextObservation = preprocess(nextObservation)
		brain.setPerception(nextObservation,action,reward,terminal)
		# pull out some frame information
		screen.blit(frameData.surface, (0, 0))
		display.flip()
		clock.tick(60)
	quit()

def main():                  
	TestTrainer()

def terminalState(terminal):
	if terminal == -1:
		return True
	return False

def getReward(isaacHP, isaacLastHP, bossHP, bossLastHP):
	if bossHP < bossLastHP:
		return 1
	if isaacHP < isaacLastHP:
		return -1
	return 0

if __name__ == '__main__':
	main()
