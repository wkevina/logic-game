import ecs
import cocos

class Sprite(ecs.Component):
	"""
	Encapsulates a cocos sprite.
	"""
	def __init__(self):
		self.sprite = None
	
class Position(ecs.Component):
	"""
	Represents a coordinate in 2D space
	"""
	def __init__(self):
		self.x = 0
		self.y = 0
	
class SpriteSystem(ecs.System):
	"""
	Makes sure that sprites are rendered at the same coordinates as its entity's
	position
	"""
	def update(self, dt, entity_manager):
		
		sprites = entity_manager.pairs_for_type(Sprite)
		#print sprites
		# We have a list of (e_id, component)
		for e_id, sprite in sprites:
			# get position for this entity
			pos = entity_manager.component_for_entity(e_id, Position)
			#print pos
			if pos:
#				print sprite.sprite.position
				sprite.sprite.position = (pos.x, pos.y)