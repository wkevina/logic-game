"""
Some common components that aren't too specialized.

"""
import ecs
import inputmanager
import cocos
import spritesystem

class Position(ecs.Component):
	"""
	An entity's position in 2D space
	
	"""
	def __init__(self):
		self.x = 0
		self.y = 0
		
class Velocity(ecs.Component):
	"""
	Holds velocity data
	
	"""
	def __init__(self):
		self.v_x = 0
		self.v_y = 0
		
class PlayerInput(ecs.Component):
	"""
	Holds an input dictionary from the InputManager
	
	"""
	def __init__(self, index=None):
		self.input = None
		
		if index:
			self.input = inputmanager.inputmanager.get_input_dict(index)
			
class RectCollider(ecs.Component):
	"""
	Maintains a rectangular hit-area for collision tests,
	as well as a flag to indicate whether or not the collider should collide
	with tile-maps
	"""			
	def __init__(self, x=0, y=0, w=0, h=0, collide_with_map=False):
		self.collide_with_map = collide_with_map
		self.hit_rect = cocos.rect.Rect(x,y,w,h)
			
	
class PlayerMoverSystem(ecs.System):
	"""
	Moves an entity around according to user input
	
	Works on entities that have Velocity and PlayerInput
	
	"""
	def update(self, dt, entity_manager):
		players = entity_manager.pairs_for_type(PlayerInput)
		
		for e_id, player in players:
			velocity = entity_manager.component_for_entity(e_id, Velocity)
			if velocity:
				velocity.v_x = player.input['HORIZONTAL_1']*100.0
				velocity.v_y = player.input['VERTICAL_1']*100.0
			
class PhysicsMoverSystem(ecs.System):
	"""
	Updates an entity's position based on its velocity
	
	Requires Velocity and Position
	"""
	def update(self, dt, entity_manager):
		velocities = entity_manager.pairs_for_type(Velocity)
		
		for e_id, velocity in velocities:
			pos = entity_manager.component_for_entity(e_id, Position)
			if pos:
				pos.x += velocity.v_x * dt
				pos.y += velocity.v_y * dt
			
class RectColliderTrackerSystem(ecs.System):
	"""
	Makes sure that an entity's RectCollider hit_rect is at the 
	same position as the entity's position component.
	
	It also ensures that if an entity has a Sprite, the dimensions of the
	hit_rect match that of the sprite.
	
	Making a system explicitly for this purpose is better than implicitly leaving
	it to another system, so as to minimize the side-effects required of other
	systems.
	"""
	def update(self, dt, entity_manager):
		"""
		For every RectCollidable, updates its position to match the entity.
		
		Also sets the dimensions of the rect to match of the entity's sprite, if it has one.
		"""
		colliders = entity_manager.pairs_for_type(RectCollider)
		
		for e_id, collider in colliders:
			pos = entity_manager.component_for_entity(e_id, Position)
			if pos:
				collider.hit_rect.center = (pos.x, pos.y)
			sprite = entity_manager.component_for_entity(e_id, spritesystem.Sprite)
			if sprite:
				collider.hit_rect.width  = sprite.sprite.width
				collider.hit_rect.height = sprite.sprite.height
	
			
	