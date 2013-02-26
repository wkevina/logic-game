"""
Module for the Level class, which encapsulates the data and workings of a game-level.
"""

import ecs
import cocos

class Level(cocos.scene.Scene):
	"""
	Class which can be run by the director, which contains all the functionality and data
	to run a level of the game.
	
	Has these attributes:
	
	background	: a RectMapLayer which displays background imagery
	
	foreground	: a RectMapLayer which displays foreground imagery.  This map is also used for
				  map collisions.
	
	sprite_layer: a ScrollableLayer to which sprites can be added
	
	scroll_man	: a ScrollingManager to look after scrolling of the view
				 
	system_man	: a SystemManager from ecs
	
	database	: an EntityManager from ecs
	
	"""
	def __init__(self, fg=None, bg=None):
		"""
		Construct a Level object.  
		
		Keyword arguments:
		
		fg : a RectMapLayer for foreground scenery
		bg : a RectMapLayer for background scenery
		
		"""
		
		self._background = None
		self._foreground = None
		
		self.background = bg
		self.foreground = fg
		
		self.sprites = cocos.layer.ScrollableLayer()
		self.scroller = cocos.layer.ScrollingManager()
		
		self.database = ecs.EntityManager() # a database to hold all component data
		self.systems = ecs.SystemManager(self.database) # the container for Systems
		
	@property
	def background(self):
		return self._background
		
	@background.setter
	def background(self, new_bg):
		self.remove(self._background)
		self._background = new_bg
		self.add(new_bg, z=-1)
		
	@property
	def foreground(self):
		return self._foreground
		
	@background.setter
	def foreground(self, new_fg):
		self.remove(self._foreground)
		self._foreground = new_fg
		self.add(new_fg, z=0)