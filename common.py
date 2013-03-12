"""
Some common components that aren't too specialized.

"""
import cocos
import ecs
import inputmanager
import graphics
import jumper
import config
import util

class Position(ecs.Component):
	"""
	An entity's position in 2D space
	
	"""
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
		
class Velocity(ecs.Component):
	"""
	Holds velocity data
	
	"""
	def __init__(self, x=0, y=0, gravity=True):
		self.v_x = 0
		self.v_y = 0
		self.use_gravity = gravity
		
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
		self.last = None
			
	
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
			
class VelocitySystem(ecs.System):
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
				
				
class GravitySystem(ecs.System):
	"""
	Accelerates an entity according to gravity
	
	Requires Velocity
	
	"""
	def update(self, dt, entity_manager):
		pairs = entity_manager.pairs_for_type(Velocity)
		
		for e_id, velocity in pairs:
			if velocity.use_gravity:
				velocity.v_y -= dt*config.GRAVITY
				
			
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
				collider.last = collider.hit_rect.copy()
				collider.hit_rect.position = (pos.x, pos.y)
			sprite = entity_manager.component_for_entity(e_id, graphics.Sprite)
			if sprite:
				collider.hit_rect.width  = sprite.sprite.width
				collider.hit_rect.height = sprite.sprite.height
				
	
class MapCollisionSystem(ecs.System):
	"""
	Implements collisions between RectColliders and a level's foreground tile-map.
	
	Enforces that entities with RectColliders do not pass through the tiles in the
	level's foreground tile-map.
	
	Furthermore, if the entity has a Jumper, it will set the in_air flag to false
	if the collider hits a floor
	
	Requires RectCollider, Velocity, and Position
	
	Optional: Jumper
	
	"""
	def __init__(self):
		super(MapCollisionSystem, self).__init__()
		
		# uses this object to calculate collisions
		self.map_collider_manager = cocos.tiles.RectMapCollider()
	
	def update(self, dt, entity_manager):
		"""
		For every entity with Velocity, Position, and RectCollider, tests for collision
		with the level's foreground tile-map. If a collision is found, it moves the entity
		out of intersection and kills the velocity of the entity in the direction it had to
		move.
		"""
		pairs = entity_manager.pairs_for_type(RectCollider)
		
		map = self.sys_man.parent.foreground
		if not map:
			return
		
		for e_id, collider in pairs:
			if collider.collide_with_map: # filter non-map colliders
				# now we need the velocity and position of the entity
				pos = entity_manager.component_for_entity(e_id, Position)
				vel = entity_manager.component_for_entity(e_id, Velocity)
				
				# move on if one of these is missing
				if not pos or not vel:
					continue
				
				# collider.hit_rect will be mutated to conform to the map
				delta = self.map_collider_manager.collide_map(map, 
															  collider.last, 
															  collider.hit_rect, 
															  0, 0)
				pos.x, pos.y = collider.hit_rect.position
				if delta[0]: # if there was some penetration in the x-direction
					vel.v_x = 0 # kill the x velocity
				if abs(delta[1]):
					vel.v_y = 0
					if delta[1] > 0:
						j = entity_manager.component_for_entity(e_id, jumper.Jumper)
						if j:
							j.in_air = False
				
class PlayerViewTrackerSystem(ecs.System):	
	def update(self, dt, entity_manager):
		scroller = self.sys_man.parent.scroller
		pairs = entity_manager.pairs_for_type(PlayerInput)
		for e_id, pi in pairs:
			pos = entity_manager.component_for_entity(e_id, Position)
			new_x = util.lerp(pos.x, scroller.restricted_fx, 0.6)
			new_y = util.lerp(pos.y, scroller.restricted_fy, 0.6)
			
			if new_x < pos.x - 50:
				new_x = util.lerp(new_x, pos.x - 50, 0.5)
			elif new_x > pos.x + 50:
				new_x = util.lerp(new_x, pos.x + 50, 0.5)
				
			if new_y < pos.y - 50:
				new_y = util.lerp(new_y, pos.y - 50, 0.5)
			elif new_y > pos.y + 50:
				new_y = util.lerp(new_y, pos.y + 50, 0.5)
			
			scroller.set_focus(new_x, new_y)
		
		
		
					