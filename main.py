import config # should always be first

import cocos
import pyglet
#import cocos.euclid as eu
import math

import level
import common
import graphics
import platforms
import jumper

import util

from cocos.director import director as dtor
from inputmanager import inputmanager as in_man

        
def main(): 
    # Initialize Director
    window = dtor.init(width=config.WIDTH,
              height=config.HEIGHT,
              caption=config.TITLE,
              fullscreen=config.FS,
              resizable=False,
              do_not_scale=True,
              )
    window.set_exclusive_mouse(True)
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
    img = pyglet.resource.image('contrast-robot.png')
    img = pyglet.image.ImageGrid(img, 1, 3)
    seq = img.texture_sequence
    #walk_anim = seq.get_animation(0.2)
    walk_anim = pyglet.image.Animation.from_image_sequence(seq, 0.1)
    stand_anim = pyglet.image.Animation.from_image_sequence(seq[:1], 0.1)
    anim = jumper.JumperAnimation()
    anim.walk_right = walk_anim
    anim.walk_left  = walk_anim.get_transform(flip_x=True)
    anim.stand_right = stand_anim
    anim.stand_left = stand_anim.get_transform(flip_x=True)
        
    tile_map = cocos.tiles.load('level-1.tmx')
    
    first_level = level.Level()
    first_level.foreground = tile_map['Structure']
    first_level.background = tile_map['Background']
    
    # build out level
    db = first_level.database
    
    e_1 = db.new_entity()
    sc = graphics.Sprite(align=(-1,-1))
    sc.sprite = cocos.sprite.Sprite(walk_anim, opacity=250)
    first_level.sprites.add(sc.sprite)
    pos = common.Position()
    pos.x = 50
    pos.y = 9*16
    db.add_component(e_1, pos)
    db.add_component(e_1, sc)
    
    db.add_component(e_1, common.Velocity())
    db.add_component(e_1, common.PlayerInput(1))
    db.add_component(e_1, common.RectCollider(collide_with_map=True))
    db.add_component(e_1, jumper.Jumper(jump=350))  
    db.add_component(e_1, anim)
    
    # add door
    closed_door = add_door(first_level, 30, 2, 'door.png')    
    
    add_door(first_level, 30, 7, 'door.png', open=True)
    
    add_button(first_level, 33, 7, 'button.png', closed_door)
        
    first_level.systems.add_system(jumper.JumperSystem(), 0)
    first_level.systems.add_system(jumper.WalkerSystem(), 1)

    first_level.systems.add_system(common.VelocitySystem(), 3)
    first_level.systems.add_system(common.GravitySystem(), 2)   
    
    first_level.systems.add_system(common.RectColliderTrackerSystem(), 4)
    first_level.systems.add_system(common.MapCollisionSystem(), 5)
    
    first_level.systems.add_system(platforms.DoorCollisionSystem(), 6)
    
    first_level.systems.add_system(jumper.JumperAnimationSystem(), 7)
    first_level.systems.add_system(platforms.DoorAnimationSystem(), 8)
    
    first_level.systems.add_system(platforms.ButtonCollisionSystem(), 9)
    first_level.systems.add_system(platforms.ButtonAnimationSystem(), 10)
    
    first_level.systems.add_system(graphics.TwoStateGraphicSystem(), 11)
    first_level.systems.add_system(graphics.SpriteTrackerSystem(), 12)
    
    first_level.systems.add_system(common.PlayerViewTrackerSystem(), 13)
    
    pyglet.gl.glClearColor(*config.BG_COLOR)    
    dtor.set_show_FPS(config.SHOW_FPS)
    dtor.run(first_level)   
    
def add_door(level, x, y, image, open=False):
    """
    Adds a door to the level.
    
    A door consists of Position, Sprite, TwoStateGraphic and Door components.
    
    The arguments x and y are tile indices, starting with 0,0 in the bottom-left corner.    

    """
    db = level.database
    entity = db.new_entity()
        
    pos = common.Position(*util.tile(x, y))
    sprite = graphics.Sprite(align=(-1,-1))
    sprite.sprite = cocos.sprite.Sprite(config.DEFAULT_IMAGE)
    
    level.sprites.add(sprite.sprite)
    
    door = platforms.Door(is_open=open)
    
    image = pyglet.resource.image(image)
    grid = pyglet.image.ImageGrid(image, 1, 2)    
    grid = pyglet.image.TextureGrid(grid)    
    
    closed_image = grid[0]
    opened_image = grid[1]
    
    two_state = graphics.TwoStateGraphic(closed_image, opened_image)
        
    door.hit_rect.size = closed_image.width, closed_image.height
    db.add_component(entity, pos)
    db.add_component(entity, sprite)
    db.add_component(entity, door)
    db.add_component(entity, two_state)
    
    return entity
    
def add_button(level, x, y, image, door):
    """
    Adds a door to the level.
    
    A door consists of Position, Sprite, TwoStateGraphic and Door components.
    
    The arguments x and y are tile indices, starting with 0,0 in the bottom-left corner.    

    """
    db = level.database
    entity = db.new_entity()
        
    pos = common.Position(*util.tile(x, y))
    sprite = graphics.Sprite(align=(-1,-1))
    sprite.sprite = cocos.sprite.Sprite(config.DEFAULT_IMAGE)
    
    level.sprites.add(sprite.sprite)
    
    image = pyglet.resource.image(image)
    grid = pyglet.image.ImageGrid(image, 1, 2)    
    grid = pyglet.image.TextureGrid(grid)    
    
    up = grid[0]
    down = grid[1]
    
    two_state = graphics.TwoStateGraphic(up, down)
    
    button = platforms.Button(up.width, up.height, door)    
        
    db.add_component(entity, pos)
    db.add_component(entity, sprite)
    db.add_component(entity, button)
    db.add_component(entity, two_state)
    
    return entity
        
if __name__ == '__main__':
        
    main()
