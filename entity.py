import cocos
import pyglet
import component

class EntityLayer(cocos.layer.ScrollableLayer):
	"""
	A scrollable layer that contains entity objects.  Entities are objects that have
	some behavior and possibly some visual representation on screen.
	
	EntityLayer's go through an update process at some regular interval that allow
	each of its entities to update itself, resolves any sort of collisions and informs
	interested parties about collisions, and then allows entities to pass messages to each other.
	
	After this process, the EntityLayer will draw itself.  Since entities are added to a
	subclass of ScrollableLayer, tests about whether or not an entity is visible and should
	therefore be deactivated should be easy to implement.
	
	"""
	
	def __init__(self, map=None):
		super(EntityLayer, self).__init__()
		self.all_entities = []
		self.map_colliders = []
		self.map = map
		self.to_track = None
		if self.map:
			self.rect_map_collider = cocos.tiles.RectMapCollider()
		
	def add_map_collider(self, collider):
		self.map_colliders.append(collider)
	
	def add_entity(self, child):
		if not isinstance(child, Entity):		
			raise Exception('add_entity only accepts instances or subclasses of Entity')
		self.add(child, name=child.instance_name)
		self.all_entities.append(child)
	
	def track_player(self):
		if self.to_track:
			self.parent.set_focus(*self.to_track.position)	
	
	def on_enter(self):
		super(EntityLayer, self).on_enter()
			
		self.schedule(self.update)
		
	def update(self, dt, *args, **kwargs):
		"""
		The main update routine for EntityLayers.
		
		Will call the update method of each Entity it owns, and then perform
		collisions detection and response.  Finally, it allows all entities to communicate
		with other entities.
		
		>>>a = entity.update(1.0)
		>>>a == True
		"""
		
		# if the computer sleeps during the game, things can get crazy
		if dt > (1.0/15.0):
			dt = 1.0/15.0
			
		# do basic early_update
		for entity in self.all_entities:
			entity.early_update(dt) # entities are not updated in any particular order.
							  # make sure the update code for each entity does
							  # depend on a certain order
							  
		# do collision updates
		self.do_map_collisions()
		
		for entity in self.all_entities:
			entity.late_update(dt)
			
		self.track_player()
		
	#for entity in self.all_entities:
	def do_map_collisions(self):
		if self.map:
			for collider in self.map_colliders:
				if self.map:
					change = self.rect_map_collider.collide_map(self.map, 
																collider.old_rect, 
																collider.hit_rect,
																0,0)
					if any(change):
						collider.collision_update(change)
						
class Entity(cocos.cocosnode.CocosNode):
	
	_id = 0 # Subclasses should redefine this to keep things straight	
	
	def __init__(self, name=None):
		super(Entity, self).__init__()
		
		self.components = []
		
		if not name:
			self.instance_name = get_new_instance_name(self.__class__)
		else:
			self.instance_name = name
	
	def on_enter(self):
		super(Entity, self).on_enter()
		self.setup()
	
	def setup(self):
		"""
		Instructs an entities components to setup themselves.
		
		This allows any entities which weren't able to find other
		entities they needed to know when they were added to get
		those references.
		
		Called when the EntityLayer containing this entity is
		loaded into a scene.
		"""
		for comp in self.components:
			comp.setup()
	
	def add_component(self, new_comp):
		self.components.append(new_comp) # Up to the component to add cocosnodes
		#new_comp.setup()
		self.components.sort(key=lambda comp: comp.sort)				
		new_comp.parent = self
		
	def get_component(self, comp_type):
		for comp in self.components:
			if isinstance(comp, comp_type):
				return comp
		raise component.ComponentNotFoundException('No {} in {}'.format(comp_type, self))
		
	def early_update(self, dt):
		"""
		The regular interval update method for entities.  At this point,
		the entity is allowed to inspect its current state and change its state.
		It is not allowed to talk to other entities at this point.  It should only
		update its components.
		"""
		for comp in self.components:
			comp.early_update(dt)		
		
	def late_update(self, dt):
		for comp in self.components:
			comp.late_update(dt)
		
	def __str__(self):
		return self.instance_name
        
def get_blocky_image(name):
	import pyglet.gl as gl
	image = pyglet.resource.image(name)
	gl.glBindTexture(image.target, image.id)
	gl.glTexParameteri(image.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
	gl.glTexParameteri(image.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
	return image
	
def get_new_id(cls):
	"""
	Returns a new id for an instance of a class, and then increments
	the classes current id for next time.  Requires that the class has
	an attribute '_id'.
	"""
	old = cls._id
	cls._id += 1
	return old
	
def get_new_instance_name(cls):
	"""
	Helper function to return a unique name for an instance of a class.
	
	Requires that the class has an attribute '_id'.
	"""
	return '{}_{}'.format(cls.__name__,	get_new_id(cls))