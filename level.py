"""
Module for the Level class, which encapsulates the data and workings of a game-level.
"""
import config
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
	
	sprites		: a ScrollableLayer to which sprites can be added
	
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
		super(Level, self).__init__()
		
		self._background = None
		self._foreground = None
		
		self.background = bg
		self.foreground = fg
		
		self.sprites = cocos.layer.ScrollableLayer()
		self.scroller = cocos.layer.ScrollingManager()
		
		self.database = ecs.EntityManager() # a database to hold all component data
		self.systems = ecs.SystemManager(self.database) # the container for Systems
		
		self.add(self.scroller)
		#self.scroller.add(self.background, z=-1)
		#self.scroller.add(self.foreground, z=0)
		self.scroller.add(self.sprites, z=1)
		
		self.scroller.scale = config.SCALE
		
		# add self to the director's interpreter_locals
		cocos.director.director.interpreter_locals['level'] = self
		
	@property
	def background(self):
		return self._background
		
	@background.setter
	def background(self, new_bg):
		if self._background:
			self.scroller.remove(self._background)
		if new_bg:
			self._background = new_bg
			self.scroller.add(new_bg, z=-1)
		
	@property
	def foreground(self):
		return self._foreground
		
	@background.setter
	def foreground(self, new_fg):
		if self._foreground:
			self.scroller.remove(self._foreground)
		if new_fg:
			self._foreground = new_fg
			self.scroller.add(new_fg, z=0)
			
	def on_enter(self):
		super(Level, self).on_enter()
		
		self.schedule(self.update_on_frame)
		
	def update_on_frame(self, dt):
		#print 'update_on_frame called'
		self.systems.update_systems(dt)
