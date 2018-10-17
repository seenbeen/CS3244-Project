from pygame import *
from func import *
from Character import *
from Room import *
from Bomb import *
from time import time as cTime
from pause import *
from Pill import *
from Banner import *
from Gurdy import *
from Duke import *
import random
from const import *
import traceback


class TrainerGame:
	def __init__(self, characterType, controls, seed, screen, sounds, textures, fonts):
		self.floor = {}
		self.floorIndex = 0
		self.currentRoom = (0,0)
		self.animatingRooms = []
		self.won = False
		self.surface = surface
		self.characterType = characterType
		self.seed = seed
		self.controls = controls
		self.sounds = sounds
		self.textures = textures
		self.fonts = fonts

		self.banners = []

		# Feed the seed to the random module
		random.seed(self.seed)

		# ---------------------------------- Prep for main loop --------------------------------------
		animatingRooms = self.animatingRooms
		currentRoom = self.currentRoom

		# Setup controls and create character
		cn = self.controls
		self.isaac = isaac = Character(self.characterType, (WIDTH//2, (HEIGHT//4)*3), [[cn[3], cn[1], cn[2], cn[0]], [cn[7], cn[5], cn[6], cn[4]]], self.textures, self.sounds, self.fonts)

		# Setup special stats
		if self.characterType == 0:
			isaac.pill = Pill((0,0), textures["pills"])
		elif self.characterType == 2:
			isaac.speed = 3
			isaac.damage = 1
			del isaac.hearts[-1]

		self.setup()

		floor = self.floor
		floorIndex = self.floorIndex
		#clock = time.Clock()

		# Create minimap
		self.minimap = Surface((textures["map"]["background"].get_width(), self.textures["map"]["background"].get_height())).convert_alpha()
		self.updateMinimap(self.currentRoom)
		self.minimap.set_clip(Rect(4, 4, 100, 86))
		
		# Define possible moves
		self.posMoves = [[1, 0], [0, 1], [-1, 0], [0, -1]]

		# Set the game (so we can modify stuff from the character class)
		self.isaac.game = self

		self.updateFloor()
		self.currTime = cTime()
		self.status = 0
		self.isaac = isaac
		self.animatingRooms = animatingRooms
		self.screen = screen

	def setup(self):
		# Load floor with custom data
		floor = loadFloor(["basement.xml", "basement.xml", "basement.xml", "basement.xml", "basement.xml", "basement.xml", "basement.xml"][self.floorIndex], self.floorIndex, randint(8, 12), self.sounds, self.textures)
		adjecent = [-1,0], [0, 1], [1, 0], [0, -1]
		doorPoss = [[13, 3], [6,7], [-1,3], [6,-1]]

		# Position isaac in the center of the room
		self.isaac.x, self.isaac.y = (WIDTH//2, (HEIGHT//4)*3)

		# Add a door to every room
		for coord in floor:
			for i in range(len(adjecent)):
				diffX = adjecent[i][0]
				diffY = adjecent[i][1]

				coordX = coord[0]
				coordY = coord[1]

				try:
					room = floor[(diffX + coordX, diffY + coordY)]
					if room.variant != 0:
						room.addDoor(doorPoss[i], room.variant, True)
					else:
						room.addDoor(doorPoss[i], floor[coord].variant, True)

				except:
					pass

		# Create a banner for the new floor
		self.floor = floor
		self.banners.append(Banner(["Basement", "Caves", "Catacombs","Necropolis","Depths","Womb","Uterus"][self.floorIndex], self.textures))

	def updateMinimap(self, currentRoom):
		# Draw the minimap

		self.minimap.fill((0,0,0,0))
		self.minimap.blit(self.textures["map"]["background"], (0, 0))
		for room in self.floor:
			self.floor[room].renderMap(self.minimap, currentRoom, False)
		for room in self.floor:
			self.floor[room].renderMap(self.minimap, currentRoom, True)

	def updateFloor(self):
		# Check if you've been in a room

		self.floor[self.currentRoom].entered = True

		for m in self.posMoves:
			mx, my = m
			x, y = self.currentRoom
			newPos = (mx+x, my+y)

			try:
				self.floor[newPos].seen = True
			except:
				pass

		self.updateMinimap(self.currentRoom)

	def advanceFrame(self, events):
		self.currTime += 1/60.0
		currTime = self.currTime
		isaac = self.isaac
		animatingRooms = self.animatingRooms
		screen = self.screen
		mWidth = self.minimap.get_width()
		mHeight = self.minimap.get_height()
		posMoves = self.posMoves

		for e in events:
			if e.type == KEYDOWN:
				# Update key value
				isaac.moving(e.key, True, False)

			elif e.type == KEYUP:
				# Update key value
				isaac.moving(e.key, False, False)

		# Draw animating rooms (The ones that are shifting in and out of frame)
		if len(animatingRooms) > 0:
			for r in animatingRooms[:]:
				r.render(screen, isaac, currTime)
				if not r.animating:
					animatingRooms.remove(r)
		else:
			screen.fill((0,0,0))

			# Render the room
			move = self.floor[self.currentRoom].render(screen, isaac, currTime)

			if move[0] != 0 or move[1] != 0:
				old = tuple(self.currentRoom[:])

				self.currentRoom = (move[0]+self.currentRoom[0], move[1]+self.currentRoom[1])
				try:
					# Animate the room
					self.floor[self.currentRoom].animateIn(move)
					self.floor[old].animateOut(move)

					# Animate the room
					animatingRooms.append(self.floor[self.currentRoom])
					animatingRooms.append(self.floor[old])

					# Animate isaac with the room
					isaac.x += 650*(-move[0])
					isaac.y += 348*(move[1])


					# Remove tears from an animating room
					isaac.clearTears()

					# Check if you enter a boss room
					if self.floor[self.currentRoom].variant == 2 and not self.floor[self.currentRoom].entered:
						self.sounds["bossIntro"].play()

						# Give the correct boss index
						bossIntro(screen, self.characterType, [Gurdy, Duke].index(type(self.floor[self.currentRoom].enemies[0])), self.floorIndex)

					self.floor[self.currentRoom].entered = True

					for m in posMoves:
						mx, my = m
						x, y = self.currentRoom
						newPos = (mx+x, my+y)

						try:
							self.floor[newPos].seen = True
						except:
							pass

					self.updateMinimap(self.currentRoom)

				except:
					print(traceback.format_exc())
					# That room doesnt exist
					self.currentRoom = old

		if self.floor[self.currentRoom].variant == 2:
			# Its a boss room
			try:
				# Draw the boss bar
				bossbar(screen, self.floor[self.currentRoom].enemies[0].health/100)
			except:
				pass

			if not self.won and self.floorIndex == 6 and len(self.floor[self.currentRoom].enemies) == 0:
				self.banners.append(Banner("You won", self.textures))
				self.won = True
				self.status = 1


		# DRAW MAP
		screen.blit(self.minimap, (MAPX-mWidth//2, MAPY-mHeight//2))

		# Blit all banners
		for banner in self.banners:
			if banner.render(screen):
				self.banners.remove(banner)

		if isaac.dead:
			self.status = -1

	def getStatus(self):
		return self.status

class Trainer:
	def __init__(self, screen):
		self.screen = screen

		self.controlStruct = ControlStruct()

		# Load all needed textures
		self.textures = {
			"hearts": loadTexture("hearts.png"),
			"pickups": loadTexture("pickups.png"),
			"character": [darken(loadTexture(["lazarus.png", "isaac.png", "eve.png"][i]), .1) for i in range(3)],
			"floors": [loadTexture("basement.png"),
					loadTexture("caves.png"),
					loadTexture("catacombs.png"),
					loadTexture("depths.png"),
					loadTexture("necropolis.png"),
					loadTexture("womb.png"),
					loadTexture("utero.png"),
					loadTexture("shop.png"),
					],
			"controls": loadTexture("controls.png"),
			"doors": [[loadTexture("door.png"), loadTexture("dark_door.png"), loadTexture("red_door.png")],
					loadTexture("treasure_door.png"),
					loadTexture("boss_door.png"),
					loadTexture("devil_door.png"),
					loadTexture("angel_door.png")],
			"controls": loadTexture("controls.png"),
			"rocks": darken(loadTexture("rocks.png"), .1),
			"poops": loadTexture("poops.png"),
			"tears": [loadTexture("tears.png"), loadTexture("tear_pop.png")],
			"fires": [loadTexture("fire_top.png"), loadTexture("fire_bottom.png")],
			"bombs": [loadTexture("bombs.png"), [loadTexture("explosion.png")], loadTexture("smut.png")],
			"coins": [loadTexture("penny.png"), loadTexture("nickel.png"), loadTexture("dime.png")],
			"keys": loadTexture("keys.png"),
			"pickupHearts": loadTexture("pickup_hearts.png"),
			"overlays": [loadTexture("%i.png"%i, dir="overlays") for i in range(5)],
			"shading": loadTexture("shading.png"),
			"loading": [loadTexture("%i.png"%(i+1), dir="loading") for i in range(56)],
			"pauseCard": loadTexture("pauseCard.png", dir="pause"),
			"seedCard": loadTexture("seedcard.png", dir="pause"),
			"arrow": loadTexture("arrow.png", dir="pause", double=False),
			"pills": loadTexture("pills.png"),
			"trapdoor": loadTexture("trap_door.png"),
			"phd": loadTexture("phd.png"),
			"streak": loadTexture("streak.png"),
			"map": {
				"background": loadTexture("minimap.png").subsurface(0, 0, 112, 102),
				"in": loadTexture("minimap.png").subsurface(113, 0, 16, 16),
				"entered": loadTexture("minimap.png").subsurface(113, 16, 16, 16),
				"seen": loadTexture("minimap.png").subsurface(113, 32, 16, 16),
				"item": loadTexture("minimap.png").subsurface(113, 48, 16, 16),
				"boss": loadTexture("minimap.png").subsurface(113, 64, 16, 16),
			},
			
			"enemies": {
				"fly": loadTexture("fly.png", dir="enemies"),
				"pooter": loadTexture("pooter.png", dir="enemies"),
				"maw": loadTexture("maw.png", dir="enemies"),
				"boil": loadTexture("boil.png", dir="enemies"),
				"host": loadTexture("host.png", dir="enemies"),
			},
			"bosses": {
				"gurdy": loadTexture("gurdy.png", dir="bosses"),
				"duke": loadTexture("duke.png", dir="bosses"),
			}
		}

		class BlankSound:
			def play(self):
				pass
			def stop(self):
				pass

		def loadSound(*args):
			return BlankSound()


		# Load all sounds we need
		self.sounds = {
			"pop": loadSound("pop.wav"),
			"explosion": loadSound("explosion.wav"),
			"hurt": [loadSound("hurt1.wav"), loadSound("hurt2.wav")],
			"tear": [loadSound("tear1.wav"), loadSound("tear2.wav"), loadSound("tearPop.wav"), loadSound("tearSplat.wav")],
			"unlock": loadSound("unlock.wav"),
			"devilRoomAppear": loadSound("devilRoomAppear.wav"),
			"angelRoomAppear": loadSound("angelRoomAppear.wav"),
			"coinDrop": loadSound("coinDrop.wav"),
			"coinPickup": loadSound("coinPickup.wav"),
			"fireBurn": loadSound("fireBurning.wav"),
			"steam": loadSound("steam.wav"),
			"keyDrop": loadSound("keyDrop.wav"),
			"keyPickup": loadSound("keyPickup.wav"),
			"heartIntake": loadSound("heartIntake.wav"),
			"holy": loadSound("holy.wav"),
			"rockBreak": loadSound("rockBreak.wav"),
			"doorOpen": loadSound("doorOpen.wav"),
			"doorClose": loadSound("doorClose.wav"),
			"deathBurst": loadSound("deathBurst.wav"),
			"pageTurn": loadSound("pageTurn.wav"),
			"error": loadSound("error.wav"),
			"selectLeft": loadSound("selectLeft.wav"),
			"selectRight": loadSound("selectRight.wav"),
			"bossIntro": loadSound("bossIntro.wav"),
		}

		# Load fonts
		self.fonts = {
			"main": loadCFont("main.png", 20, 16, 36, size=1.8),
			"pickups": loadCFont("pickup.png", 10, 12, 10),
			"ticks": loadCFont("ticks.png", 4, 17 , 8),
		}

	def initializeGame(self, seed):
		controls = [97,100,119,115,276,275,273,274,113,101]
		self.game = TrainerGame(0, controls, seed,
					self.screen, self.sounds, self.textures,
					self.fonts)

	def advanceFrame(self):
		self.game.advanceFrame(self.controlStruct.flush())
		hp = sum(map(lambda x: x.health ,self.game.isaac.hearts))
		return FrameData(self.screen, hp)
	
	def getSimulationStatus(self):
		return self.game.getStatus()

	MOVE_LEFT = 97
	MOVE_RIGHT = 100
	MOVE_UP = 119
	MOVE_DOWN = 115
	SHOOT_LEFT = 276
	SHOOT_RIGHT = 275
	SHOOT_UP = 273
	SHOOT_DOWN = 274

	def sendPushKeyEvent(self, k):
		self.controlStruct.pushKey(k)


class FakeEvent:
	def __init__(self, t, v):
		self.type = t
		self.key = v
		
class ControlStruct:
	CONTROLS = [97,100,119,115,276,275,273,274]

	def __init__(self):
		self.keys = { c : False for c in ControlStruct.CONTROLS }
		self.prev_keys = { c : False for c in ControlStruct.CONTROLS }
		self.events = []

	def pushKey(self, c):
		self.keys[c] = True

	def flush(self):
		events = self.events
		for c in self.CONTROLS:
			if self.keys[c] != self.prev_keys[c]:
				if self.keys[c]:
					events.append(FakeEvent(KEYDOWN, c))
				else:
					events.append(FakeEvent(KEYUP, c))

		self.prev_keys = { c : self.keys[c] for c in ControlStruct.CONTROLS }
		self.keys = { c : False for c in ControlStruct.CONTROLS }

		self.events = []

		return events
		
class FrameData:
	def __init__(self, surface, isaac_hp):
		self.surface = surface
		self.isaac_hp = isaac_hp
