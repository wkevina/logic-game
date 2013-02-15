import pyglet
import inputmanager

TITLE = 'Logic Game'

FS = False

JS_DEADZONE = 0.3 # The absolute value of a joystick movement must be greater than this value to count

BG_COLOR = (0.3,0.3,0.3,1)

SCALE = 3 # Global scale for all layers

TILE_SIZE = (16,16) # Size of tiles in pixels.  Could be set programmatically by other means

SIZE = (15,9) # Size of field in tiles

WIDTH, HEIGHT = tuple([a*b*SCALE for a,b in zip(TILE_SIZE, SIZE)]) # Size of window, 
                                                              # scaled for tile size, 
                                                              # field size, and scale
															  
MAPS_DIR = 'Maps/'

IMAGES_DIR = 'Images/'

pyglet.resource.path.append(MAPS_DIR)
pyglet.resource.path.append(IMAGES_DIR)
pyglet.resource.reindex()

#GRAVITY = 0.21875 # pixels/s^2
GRAVITY = 850.0

player1 = {
	'index': 1,
		
	'joystick':
		{
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
