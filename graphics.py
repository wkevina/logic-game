import cocos
import ecs
import common

class Sprite(ecs.Component):
    """
    Encapsulates a cocos sprite.
    
    properties:
    
    sprite - a cocos sprite instance
    align - a tuple denoting where to position the sprite relative to its entity's position.
            Valid values are (0,0) for the center to be drawn at position, (-1, -1) for 
            bottom-left to be drawn at position, and so on.
    """
    def __init__(self, align=(0,0)):
        self.sprite = None
        self.align_x = align[0]
        self.align_y = align[1]
        
class TwoStateGraphic(ecs.Component):
    """
    Encapsulates a graphic that should look different depending on which of two
    states it is in.
    
    """
    def __init__(self, zero, one):
        self.zero = zero
        self.one = one
        self.state = 0
        
class TwoStateGraphicSystem(ecs.Component):
    def update(self, dt, entity_manager):
        two_states = entity_manager.pairs_for_type(TwoStateGraphic)
        for e_id, two_state in two_states:
            sprite = entity_manager.component_for_entity(e_id, Sprite)
            if not sprite:
                continue
            
            if two_state.state == 0:
                sprite.sprite.image = two_state.zero
            else:
                sprite.sprite.image = two_state.one
    
class SpriteTrackerSystem(ecs.System):
    """
    Makes sure that sprites are rendered at the same coordinates as its entity's
    position
    """
    def update(self, dt, entity_manager):
        
        sprites = entity_manager.pairs_for_type(Sprite)
        # We have a list of (e_id, component)
        for e_id, sprite in sprites:
            # get position for this entity
            pos = entity_manager.component_for_entity(e_id, common.Position)
            if pos:
                c_spr = sprite.sprite
                offset_x = 0.5 * (sprite.align_x * c_spr.width + c_spr.width)
                offset_y = 0.5 * (sprite.align_y * c_spr.height + c_spr.height)
                #c_spr.position = (pos.x + offset_x, pos.y + offset_y)
                
                c_spr.position = (pos.x, pos.y)
                c_spr.image_anchor = offset_x, offset_y
                
                #print 'pos: {}, a: {}'.format((pos.x, pos.y), (sprite.align_x, sprite.align_y))
                #print 'spr w: {}, h:{}'.format(c_spr.width, c_spr.height)
                #print 'offset: {}'.format((offset_x, offset_y))
                #print 'sprite pos: {}\n--------'.format(c_spr.position)