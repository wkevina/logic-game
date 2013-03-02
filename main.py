import config # should always be first

import cocos
import pyglet
#import cocos.euclid as eu
import math

import level
import spritesystem
import common

from cocos.director import director as dtor
from inputmanager import inputmanager as in_man

		
def main():	
	# Initialize Director
	dtor.init(width=config.WIDTH,
			  height=config.HEIGHT,
			  caption=config.TITLE,
			  fullscreen=config.FS,
			  resizable=False,
			  do_not_scale=True,
			  )
	# Initialize the InputManager
	in_man.init()
		
	in_man.bind(config.PLAYER_1)
			
	print config.WIDTH, config.HEIGHT
	
	"""			
	main_scene = cocos.scene.Scene()
	
	sm = cocos.layer.ScrollingManager()
	sm.scale = config.SCALE

	tile_map = cocos.tiles.load('logic-map-1.tmx')
	structure = tile_map['Structure']
	sm.add(structure, z=0, name='structure')
	el = en.EntityLayer(map=structure)
	sm.add(el, z=1)
	
	player = en.Entity()
	
	robot = en.get_blocky_image('animated-robot.png')
	robot = pyglet.image.ImageGrid(robot, 1, 3)
	seq = robot.texture_sequence
	robo_anim = pyglet.image.Animation.from_image_sequence(seq, 0.1)
	player.add_component(comp.SpriteComponent(robo_anim))
	player.add_component(comp.MapColliderComponent())
	player.add_component(comp.PhysicsComponent())
	player.add_component(comp.Jumper())
	
	player.position = 24, 32
	
	el.add_entity(player)
	el.to_track = player
	
	main_scene.add(sm, name='Scroller')
	
	def track_player(dt, *args, **kwargs):
		sm.set_focus(*player.position)
		
	#main_scene.schedule(track_player)
	
	dtor.interpreter_locals['el'] = el
	
	"""
	
	tile_map = cocos.tiles.load('logic-map-1.tmx')
	
	first_level = level.Level()
	first_level.foreground = tile_map['Structure']
	
	# build out level
	db = first_level.database
	
	e_1 = db.new_entity()
	sc = spritesystem.Sprite()
	sc.sprite = cocos.sprite.Sprite('animated-robot.png')
	first_level.sprites.add(sc.sprite)
	pos = spritesystem.Position()
	pos.x = 100
	pos.y = 100
	db.add_component(e_1, pos)
	db.add_component(e_1, sc)
	
	db.add_component(e_1, common.Velocity())
	db.add_component(e_1, common.PlayerInput(1))
	db.add_component(e_1, common.RectCollider(collide_with_map=True))
	
	
	first_level.systems.add_system(common.PlayerMoverSystem(), 0)
	first_level.systems.add_system(common.PhysicsMoverSystem(), 1)
	first_level.systems.add_system(spritesystem.SpriteSystem(), 3)
	first_level.systems.add_system(common.RectColliderTrackerSystem(), 2)
	
	
	pyglet.gl.glClearColor(*config.BG_COLOR)	
	dtor.set_show_FPS(True)
	dtor.run(first_level)		
		
if __name__ == '__main__':
		
	main()
