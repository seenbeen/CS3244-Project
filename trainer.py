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

import csv

# For storing visualisation data
totalRewardsInEpochs = []
averageQValuesInEpochs = []
positions = []
size = [WIDTH, HEIGHT]

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
	#trainerBinding.initializeGame("ASDFASDF",startAt=Trainer.START_AT_MONSTER_ROOM)
	start(trainerBinding)
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
	lastNumEnemies = frameData0.num_enemies

    #start trainings
	running = True
	score = 0
	epochs = 0
	winEpoch = 0

	# Initialize variables used for visualizations
	totalReward = 0
	numQValues = 0
	totalQValue = 0

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
		action, QValue = brain.getAction()
		totalQValue += QValue
		numQValues += 1
		currentAction = actionList[np.argmax(action)]
		trainerBinding.sendPushKeyEvent(currentAction)
		# advance the simulation
		frameData = trainerBinding.advanceFrame()
		# Record position
		pos = np.array(frameData.isaac_position)
		positions.append(np.round(pos, decimals=2))
		# if enter another room, restart
		if frameData.has_room_changed:
			start(trainerBinding)
		# get hp
		currentIsaacHP = frameData.isaac_hp
		currentNumEnemies = frameData.num_enemies
		# if boss is dead, restart game and update score and epochs
		if currentNumEnemies == 0:
			score = score + 1
			epochs = epochs + 1
			if score == 1:
				winEpoch = epochs

			totalRewardsInEpochs.append(totalReward)
			totalReward = 0

			averageQValuesInEpochs.append(totalQValue/numQValues)
			totalQValue = 0
			numQValues = 0

			start(trainerBinding)
				#trainerBinding.initializeGame("ASDFASDF",startAt=Trainer.START_AT_MONSTER_ROOM)
		# get reward
		reward = getReward(currentIsaacHP, lastIsaacHP, currentNumEnemies, lastNumEnemies)
		totalReward += reward
		lastIsaacHP = currentIsaacHP
		lastNumEnemies = currentNumEnemies
		# get terminal state, if terminal, restart game and update epochs
		terminal = terminalState(trainerBinding.getSimulationStatus())
		if terminal == True: #or reward == -1:
			epochs = epochs + 1

			totalRewardsInEpochs.append(totalReward)
			totalReward = 0

			averageQValuesInEpochs.append(np.round(totalQValue/numQValues, decimals=2))
			totalQValue = 0
			numQValues = 0

			start(trainerBinding)
			#trainerBinding.initializeGame("ASDFASDF",startAt=Trainer.START_AT_MONSTER_ROOM)
		# train
		nextObservation = surfarray.array3d(frameData.surface)
		nextObservation = preprocess(nextObservation)
		brain.setPerception(nextObservation,action,reward,terminal)
		# pull out some frame information
		screen.blit(frameData.surface, (0, 0))
		display.flip()
		clock.tick(60)

	quit()

def start(trainerBinding):
	trainerBinding.initializeGame("fuck",startAt=Trainer.START_AT_MONSTER_ROOM)
	#trainerBinding.initializeGame("fuck",startAt=Trainer.START_AT_BOSS)

def main():                  
	TestTrainer()

def terminalState(terminal):
	if terminal == -1:
		return True
	return False

def getReward(isaacHP, isaacLastHP, numEnemies, lastNumEnemies):
	if numEnemies < lastNumEnemies:
		return 1
	if isaacHP < isaacLastHP:
		return -1
	return 0

def saveRewardData():
	with open("visualizations/totalRewardsInEpochs.csv", 'w') as f:
		wr = csv.writer(f, delimiter='\t')
		wr.writerow(['TotalReward', 'Episode'])
		for i in range(len(totalRewardsInEpochs)):
			wr.writerow([totalRewardsInEpochs[i], i])

	with open("visualizations/averageQValuesInEpochs.csv", 'w') as f:
		wr = csv.writer(f, delimiter='\t')
		wr.writerow(['AverageQValue', 'Episode'])
		for i in range(len(averageQValuesInEpochs)):
			wr.writerow([averageQValuesInEpochs[i], i])

	with open("visualizations/positions.csv", 'w') as f:
		wr = csv.writer(f, delimiter='\t')
		wr.writerow(['Map Width', 'Map Height'])
		wr.writerow([size[0], size[1]])
		wr.writerow(['Pos X', 'Pos Y'])
		for i in range(len(positions)):
			wr.writerow([positions[i][0], positions[i][1]])


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		saveRewardData()
