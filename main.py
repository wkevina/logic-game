import config # should always be first
import cocos
import pyglet
import inputmanager
#import cocos.euclid as eu
import math
import entity as en
import component as comp
		
def main():
	from cocos.director import director as dtor
	
	# Initialize Director
	dtor.init(width=config.WIDTH,
			  height=config.HEIGHT,
			  caption=config.TITLE,
			  fullscreen=config.FS,
			  resizable=False,
			  do_not_scale=True,
			  )
	# Initialize the InputManager
	inputmanager.init()
		
	inputmanager.input_manager.bind(config.player1)
			
	print config.WIDTH, config.HEIGHT
				
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
	
	pyglet.gl.glClearColor(*config.BG_COLOR)	
	#dtor.set_show_FPS(True)
	dtor.run(main_scene)		
		
if __name__ == '__main__':
		
	main()
	
		
## TODO

# To implement collisions:

# Create a collider component.	That gets added to an entity.  On setup, the collider
# adds itself to the parents ColliderManager or similar.  During the update phase, the
# the collider will detect collisions and message the collider about collisions with
# the environment.	The Collider component can then move the entity appropriately in response 
# to the collision.
		
