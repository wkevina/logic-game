import cocos
import config
import pyglet

class InputBinding(object):
	"""
	Holds information about user input bindings.
	
	Used internally by InputManager
	"""
	
	INPUT_NAMES = (
	'VERTICAL_1',
	'HORIZONTAL_1',
	'VERTICAL_2',
	'HORIZONTAL_2',
	'PRIMARY_ACTION',
	'SECONDARY_ACTION',
	'JUMP',
	'START',
	'SELECT',
	)
	
	AXIS_NAMES = (
	'x',
	'y',
	'z',
	'rx', # not likely to show up
	'ry', # not likely to show up
	'rz',	
	)
	
	general_options = (
		'invert_y',
		'invert_x',	
	)
	
	sample_binding = {
		'index': 0,
		
		'joystick':
			{
				#	Format:
				#	For axes:
				#	'axis-name': 'input-name',
				#	or
				#	'axis-name': ('high-input', 'low-input')
				#	
				#	For buttons:
				#	button-number: 'input-name'
				#
				'x': 'HORIZONTAL_1',
				'y': ('VERTICAL_1', 'invert'),
				14: 'JUMP',			
			},
		'keyboard':
			{
				# 	Format:
				#	'key': 'input-name'		
				#	'key' should be the symbol string according to
				#	pyglet.  The keys assigned to the names UP, DOWN,
				#	LEFT, and RIGHT, will be automatically mapped to show
				#	up as VERTICAL and HORIZONTAL scalars.		
				('UP', 'DOWN'): 'VERTICAL_1',
				('RIGHT', 'LEFT'): 'HORIZONTAL_1',
				'SPACE': 'JUMP',
			},	
		'general':
			{
				'invert_y': True,
			}	
	}
	
	
	model_dict = {}
	for name in INPUT_NAMES:
		model_dict[name] = 0

	
	axes_dict = {}
	for axis_name in AXIS_NAMES:
		axes_dict[axis_name] = 0.0
		
	def __init__(self, binding=None):
				
		self.binding = binding
		if self.binding is None:
			self.binding = InputBinding.sample_binding
		
		self.index = self.binding['index']
		
		self.joystick = None # Reference to a pyglet joystick device
							 # InputManager will set up this reference
		self.input_dict = InputBinding.model_dict.copy()
		
		self._axes = InputBinding.axes_dict.copy()
		
		try:
			self.key_binding = self.binding['keyboard']
		except KeyError:
			self.key_binding = None
			
		try:
			self.joy_binding = self.binding['joystick']
		except KeyError:
			self.joy_binding = None
						
	def add_joystick(self, joystick):
		self.joystick = joystick
		joystick.on_joyaxis_motion = self.on_joyaxis_motion
	
	def remove_joystick(self):
		self.joystick.on_joyaxis_motion = None
		self.joystick = None
		
	def on_joyaxis_motion(self, joystick, axis, value):
		if abs(value) > config.JS_DEADZONE:
			#print 'js:{0}, axis:{1}, value:{2:+.5f}'.format(joystick, axis, value)
			self._axes[axis] = value
			return
		self._axes[axis] = 0.0
		
	def update_keys(self, key_set):
		d = {}
		for key_name, input_name in self.key_binding.iteritems():
			# try to access key_name as a 2-tuple
			if type(key_name) is tuple:
				if key_name[0] in key_set:
					d[input_name] = 1.0
				elif key_name[1] in key_set:
					d[input_name] = -1.0
			else:
				if key_name in key_set:
					d[input_name] = 1
		return d
		
	def update_joystick(self):
		d = {}
		if self.joystick:
			for j_name, input_name in self.joy_binding.iteritems():
				# start with axis names
				if type(j_name) is str:
					a_value = self._axes[j_name]
					if a_value:				
						if type(input_name) is tuple:		
							d[input_name[0]] = -a_value if input_name[1] == 'invert' else a_value
						else: 
							d[input_name] = a_value
				else:
					if self.joystick.buttons[j_name]: # lookup button by index j_name
						d[input_name] = 1.0
		return d
		
	def update(self, key_set):
		"""
		Updates the input_dict to relfect current user input state
		Called every frame by the InputManager
		"""		
		self.input_dict.update(self.model_dict) # reset input_dict
		key_input = self.update_keys(key_set)
		js_input = self.update_joystick()
		self.input_dict.update(key_input)
		self.input_dict.update(js_input)
		
		
class InputManager(cocos.cocosnode.CocosNode):
	"""
	A class that provides state information about user input.
	
	Provides keyboard, joystick, and mouse information.
	
	In the future, it may implement an event/listener pattern to
	alert other objects about input events.
	"""
	
	is_event_handler = True
	
	def __init__(self):
		pass
		
	def init(self):
		"""
		Method to setup the InputManager.
		
		Needed to implement the pseudo-singleton interface.
	
		Call after calling cocos.director.director.init()
	
		Should be called before scenes are run by the director.
		
		"""
		super(InputManager, self).__init__()
		
		from cocos.director import director
	
		director.window.push_handlers(self.on_key_press, self.on_key_release)
		
		self._keys = set()
		self._joysticks = []
		self.__unused_joysticks = []
		self._bindings = {} # Dictionary containing InputBindings, by index
		
		self.find_joysticks() # Find and open all joystick devices
				
		self.is_running = True
		
		self.schedule(self.step)

		
	def find_joysticks(self):
		"""
		Gets a reference to each joystick device and populates a list with them.
		Also opens each device for reading, but does not assign any event handlers
		to them.  Therefore, the joystick will not be read by any input binding
		yet.
		
		"""
		self._joysticks = pyglet.input.get_joysticks()
		self.__unused_joysticks = list(self._joysticks)
		if len(self._joysticks) == 0:
			print 'No joysticks found'
		else:
			print '{} joysticks found!'.format(len(self._joysticks))
			print self._joysticks
			for device in self._joysticks:
				device.open()
				
	def bind(self, binding_dict):
		"""
		Takes a dictionary describing input bindings
		and creates an InputBinding object containing that
		information and sets up up the callbacks.
		
		"""		
		new_input_binding = InputBinding(binding_dict)
		# Check before adding to bindings dictionary
		index = new_input_binding.index
		
		if index in self._bindings:
			# reclaim joystick if the current binding for that index had one
			old_binding = self._bindings[index]
			if old_binding.joystick:
				self.__unused_joysticks.insert(0, old_binding.joystick)
				old_binding.remove_joystick()
			del self._bindings[index]
		# Store the binding
		self._bindings[index] = new_input_binding
		
		if new_input_binding.joy_binding and len(self.__unused_joysticks):
			new_input_binding.add_joystick(self.__unused_joysticks.pop(0))
	
	@property
	def keys(self):
		return self._keys
	
	@property
	def joystick_count(self):
		return len(self._joysticks)
		
	def on_key_press(self, key, modifiers):
		self._keys.add(pyglet.window.key.symbol_string(key))
	
	def on_key_release(self, key, modifiers):
		self._keys.remove(pyglet.window.key.symbol_string(key))
		
	def get_input_dict(self, index):
		return self._bindings[index].input_dict
			
	#def on_enter(self):
	#	super(InputManager, self).on_enter()
	#	self.schedule(self.step)
		
	def step(self, dt, *args, **kwargs):
		for binding in self._bindings.itervalues():
			binding.update(self._keys)

inputmanager = InputManager()