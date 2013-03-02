import cocos
import ecs
from common import *

class Sprite(ecs.Component):
	"""
	Encapsulates a cocos sprite.
	"""
	def __init__(self):
		self.sprite = None
	
class SpriteSystem(ecs.System):
	"""
	Makes sure that sprites are rendered at the same coordinates as its entity's
	position
	"""
	def update(self, dt, entity_manager):
		
		sprites = entity_manager.pairs_for_type(Sprite)
		# We have a list of (e_id, component)
		for e_id, sprite in sprites:
			# get position for this entity
			pos = entity_manager.component_for_entity(e_id, Position)
			if pos:
				sprite.sprite.position = (pos.x, pos.y)