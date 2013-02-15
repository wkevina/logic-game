import entity
import cocos.euclid as eu
import cocos
import inputmanager
import config

class ComponentNotSetupException(Exception):
	pass
	
class ComponentNotFoundException(Exception):
	pass

class Component(object):
	_id = 0
	sort = 0 # Helps with sorting components.
			 # subclasses should set a number that reflects the order
			 # that it should be updated in regard to other components.
	def __init__(self):
		self.instance_name = entity.get_new_instance_name(self.__class__)
		self.is_setup = False
		self.parent = None
		
	def early_update(self, dt):
		if not self.is_setup:
			raise ComponentNotSetupException(self.instance_name)
	
	def late_update(self, dt):
		pass
	
	def setup(self):
		"""
		Called when a component is added to an entity.	Gives the component
		a chance to get any needed references and possibly add itself
		to any required batches.
		
		Any subclass should set self.is_setup to True if it is successfully
		set up.	 
		"""
		self.is_setup = self.parent is not None
	
	def cleanup(self):
		self.is_setup = False

	def __str__(self):
		return self.instance_name
		
		
class SpriteComponent(Component):
	"""
	A component that gives an entity a visual representation.
	
	A Sprite will be drawn at the center of the entity.
	"""
	
	_id = 0
	sort = 0 # Should be updated after any components that may affect the
			  # the position of the entity
	def __init__(self, image):
		super(SpriteComponent, self).__init__()
		self.image = image
		
	def setup(self):
		if self.is_setup:
			return # quit if we're set-up 
		
		if isinstance(self.image, str):
			self.sprite = cocos.sprite.Sprite(entity.get_blocky_image(self.image))
		else:
			self.sprite = cocos.sprite.Sprite(self.image)
		self.sprite_name = self.instance_name + '_sprite'
		self.parent.add(self.sprite, name=self.sprite_name)
		
		self.is_setup = True
	
	def cleanup(self):
		super(SpriteComponent, self).cleanup()
		self.parent.remove(self.sprite_name)
		self.sprite = None
		self.sprite_name = None
		self.is_setup = False
			
		
class InputComponent(Component):
	_id = 0
	sort = 5
	def setup(self):
		self.input_dict = inputmanager.input_manager.get_input_dict(0)
		self.is_setup = True
		self.vel = 100
		
	def early_update(self, dt):
		super(InputComponent, self).early_update(self, dt)
		direction = eu.Vector2(self.input_dict['HORIZONTAL_1'], 
									self.input_dict['VERTICAL_1'])
		self.parent.position += direction*self.vel*dt
		
class Jumper(Component):
	sort = 8
	
	def __init__(self, player_index=1):
		super(Jumper, self).__init__()
		self.player_index = player_index
	
	def setup(self):
		self.input_dict = inputmanager.input_manager.get_input_dict(self.player_index)
		self.is_setup = True
		try:
			self.physics = self.parent.get_component(PhysicsComponent)
		except ComponentNotFoundException:
			raise ComponentNotFoundException('Jumper component requires a physics component')
		
		self.jumping = True
		
		self.vel_x = 200
		self.vel_y = 339
		self.x_acc = 300

		# register callback
		try:
			self.parent.get_component(MapColliderComponent).register_callback(self.collider_callback)
		except ComponentNotFoundException:
			raise ComponentNotFoundException('Jumper component requires a map collider component')
		
	def early_update(self, dt):
		jump = self.input_dict['JUMP']
		if jump and not self.jumping:
			self.physics.velocity.y = self.vel_y
			self.jumping = True
		#if not jump and self.jumping:
		#	self.jumping = False
		if abs(self.physics.velocity.y) > 0:
			self.jumping = True
		hor = self.input_dict['HORIZONTAL_1']
		if hor:
			self.physics.velocity.x += hor*self.x_acc*dt
		else:
			self.physics.velocity.x = 0.8*self.physics.velocity.x
			
		if self.physics.velocity.x > self.vel_x:
			self.physics.velocity.x = self.vel_x
		
		if self.physics.velocity.x < -self.vel_x:
			self.physics.velocity.x = -self.vel_x
				
	def collider_callback(self, collider, change):
		if change.x:
			self.physics.velocity.x = 0
		if change.y:
			self.physics.velocity.y = 0
		if change.y > 0:
			self.jumping = False
		#print change

class MapColliderComponent(Component):
	"""
	A component that contains information used in collisions with other objects.
	
	Works in conjunction with the Sprite components to get
	size information.
	
	Maintains a rectangular hit area, with center at the origin of the entity
	in layer-space, and with the dimensions of the parent entity's SpriteComponent.
	"""
	_id = 0
	sort = 11
	def __init__(self):
		super(MapColliderComponent, self).__init__()
		self.hit_rect = cocos.rect.Rect(0,0,-1,-1)
		self.old_rect = None
		self.__added_ = False
		self._callbacks = []
		self.change = None
		
	def setup(self):
		if self.is_setup:
			return # quit if we're already set-up
		if self.parent.parent:
			self.parent.parent.add_map_collider(self)
			self.__added_ = True
		sprite = self.parent.get_component(SpriteComponent)
		if sprite:
			sprite_box = sprite.sprite.get_AABB()
			self.hit_rect.size = sprite_box.size
			self.hit_rect.center = self.parent.position
			self.old_rect = self.hit_rect.copy()
		if self.__added_ and self.old_rect:
			self.is_setup = True	
	
	def early_update(self, dt):
		super(MapColliderComponent, self).early_update(dt)
		self.old_rect.position = self.hit_rect.position # save the old position of the collider
		self.hit_rect.center = self.parent.position # update the collider
		self.change = None
		# The collider is now ready to participate in collisions

	def register_callback(self, func):
		"""
		Registers a function to call when this collider has a collision.
		The callback should have the signature:
		func(collider, change_vec2d)
		"""
		self._callbacks.append(func)
		
	def late_update(self, dt):
		if self.change:
			for cb in self._callbacks:
				cb(self, self.change)
		self.parent.position = self.hit_rect.center
		#print 'pos: {} dt: {}'.format(self.parent.position, dt)
		
	def collision_update(self, change):
		# probably want to move the entity according to the new hit_rect position
		if not self.change:
			self.change = eu.Vector2(*change)
		else:
			self.change += change
	
class PhysicsComponent(Component):
	"""
	A component that moves the entity according basic Newtonian physics
	It moves the entity according this component's velocity
	Velocity changes according to gravity
	"""
	
	_id = 0
	sort = 9
	
	def setup(self):
		#super(PhysicsComponent, self).setup()
		if not self.parent:
			return # quit if there isn't a parent yet
		if self.is_setup:
			return # already setup
		
		self.first_try = True
		
		if self.first_try:
			self.gravity = config.GRAVITY
			self.velocity = eu.Vector2(0,0)
			self.position = eu.Vector2(*self.parent.position)
			self.max_fall = None # Determines the maximum speed at which the component
								 # can move in the vertical direction
		self.collider = self.parent.get_component(MapColliderComponent)
		if self.collider:
			self.is_setup = True
			return
		if self.first_try is True and self.collider is None:
			self.is_setup = False
		if not self.first_try:
			self.is_setup = True
		self.first_try = False
		
	def apply_gravity(self, dt):
		"""
		Updates the component's velocity according to gravity.
		This does not change the component's position
		"""
		
		
	def early_update(self, dt):
		self._integrate(dt)
		
		#print 'v: {}, p: {}'.format(self.velocity.y, self.position.y)
		#print 'v*60: {} g*60: {}'.format(self.velocity.y*60, self.gravity*60)
		
	def _integrate(self, dt):		
		self.velocity.y = self.velocity.y - self.gravity * dt
		if self.max_fall:
			if self.velocity.y < -self.max_fall:
				self.velocity.y = -self.max_fall 
									# Clamp y velocity to max_fall when falling
		self.position.x,self.position.y = self.parent.position
		print self.position
		self.position += self.velocity * dt
		self.parent.position = self.position.x, self.position.y