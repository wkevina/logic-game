import math

import common
import spritesystem
import ecs

class JumperAnimation(ecs.Component):
	def __init__(self):
		self.stand_left = None
		self.stand_right = None
		self.walk_left = None
		self.walk_right = None

class Jumper(ecs.Component):
	"""
	Holds data about a platformer character that can jump around.
	
	Holds state about whether or not the character is in the air, as well
	as vertical jump speed.
	
	"""
	def __init__(self, jump=200, walk=200, acc=500):
		self.in_air = False
		self.jump = jump
		self.walk = walk
		self.acc = acc
		
class JumperSystem(ecs.System):
	"""
	Makes entities with the Jumper component jump in response to user input
	
	Requires Jumper, PlayerInput, Velocity
	"""
	
	def update(self, dt, entity_manager):
		pairs = entity_manager.pairs_for_type(Jumper)
		
		for e_id, jumper in pairs:
			pi = entity_manager.component_for_entity(e_id, common.PlayerInput)
			vel = entity_manager.component_for_entity(e_id, common.Velocity)
			
			if not pi or not vel:
				continue
			
			if abs(vel.v_y) > 0:
				jumper.in_air = True
			
			
			if not jumper.in_air and pi.input['JUMP']:
				vel.v_y = jumper.jump
				jumper.in_air = True
				
class WalkerSystem(ecs.System):
	"""
	Makes entities with the Jumper component jump in response to user input
	
	Requires Walker, PlayerInput, Velocity
	"""
	
	def update(self, dt, entity_manager):
		pairs = entity_manager.pairs_for_type(Jumper)
		
		for e_id, jumper in pairs:
			pi = entity_manager.component_for_entity(e_id, common.PlayerInput)
			vel = entity_manager.component_for_entity(e_id, common.Velocity)
			if not pi or not vel:
				return
			if pi.input['HORIZONTAL_1']:
				vel.v_x += pi.input['HORIZONTAL_1'] * jumper.acc * dt
				if abs(vel.v_x) > jumper.walk:
					vel.v_x = jumper.walk * vel.v_x / abs(vel.v_x)
			elif abs(vel.v_x) > 0:
				old = vel.v_x
				vel.v_x -= vel.v_x/abs(vel.v_x) * jumper.acc * dt * 2
				if abs(old - vel.v_x) > abs(old):
					vel.v_x = 0
				
class JumperAnimationSystem(ecs.System):
	def update(self, dt, entity_manager):
		pairs = entity_manager.pairs_for_type(JumperAnimation)
		for e_id, j_a in pairs:
			sprite = entity_manager.component_for_entity(e_id, spritesystem.Sprite)
			vel = entity_manager.component_for_entity(e_id, common.Velocity)
			jumper = entity_manager.component_for_entity(e_id, Jumper)
			
			if jumper.in_air:
				if vel.v_x > 0:
					sprite.sprite.image = j_a.stand_right
				elif vel.v_x < 0:
					sprite.sprite.image = j_a.stand_left
			else:
				if vel.v_x > 0 and sprite.sprite.image is not j_a.walk_right:					
					sprite.sprite.image = j_a.walk_right
				elif vel.v_x < 0 and sprite.sprite.image is not j_a.walk_left:
					sprite.sprite.image = j_a.walk_left
				elif vel.v_x == 0:
					if sprite.sprite.image is j_a.walk_right:
						sprite.sprite.image = j_a.stand_right
					elif sprite.sprite.image is j_a.walk_left:
						sprite.sprite.image = j_a.stand_left

		
		
			