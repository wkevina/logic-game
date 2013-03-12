"""
Components and systems to implement doors and movable platforms

"""

import ecs
import common
import graphics
import cocos
import util

class ImpenetrableCollider(ecs.Component):
    """
    Represents an object that other objects cannot pass through.
    
    Properties are a cocos Rect instance that represents the hit area of the
    collider.
    
    """
    def __init__(self, width=0, height=0):
        self.hit_rect = cocos.rect.Rect(0, 0, width, height)
        #self.enabled = enabled

class Door(ecs.Component):
    """
    Represents an object that may be passed through when open, and which blocks
    when closed.
    
    Not recommended to be used with the Velocity component as the collision system
    is not able to handle moving doors.
    
    Properties:
    
    is_open - boolean, indicating if the door is open or closed.
    
    hit_rect - The area of the door, defines the region through which an entity cannot
               pass.
    
    """
    def __init__(self, width = 16, height = 16, is_open=True):
        self.is_open = is_open
        self.hit_rect = cocos.rect.Rect(0, 0, width, height)
        
class Button(ecs.Component):
    def __init__(self, width, height, door):
        self.size = (width, height)
        self.state = "up"
        self.door = door
        
class ButtonCollisionSystem(ecs.Component):
    def update(self, dt, entity_manager):
        buttons_list = entity_manager.pairs_for_type(Button)        
        colliders_list = entity_manager.pairs_for_type(common.RectCollider) 
       
        if not buttons_list or not colliders_list:
            return
        
        for e_id, button in buttons_list:
            collided = False
            pos = entity_manager.component_for_entity(e_id, common.Position)
            hit_rect = cocos.rect.Rect(pos.x, pos.y, *button.size)
            for other_id, collider in colliders_list:
                if hit_rect.intersects(collider.hit_rect):
                    collided = True
            if collided:
                button.state = "down"
            else:
                button.state = "up"
            
            if button.door and button.state == 'down':
                door = entity_manager.component_for_entity(button.door, Door)
                if door:
                    door.is_open = True
                
class ButtonAnimationSystem(ecs.Component):
    def update(self, dt, entity_manager):
        buttons_list = entity_manager.pairs_for_type(Button)        
        
        if not buttons_list:
            return
        
        for e_id, button in buttons_list:
            two_state = entity_manager.component_for_entity(e_id, graphics.TwoStateGraphic)
            if button.state == "up":
                two_state.state = 0
            else:
                two_state.state = 1
        
class DoorCollisionSystem(ecs.System):
    """
    Implements doors in the game.  A door is a rectangular region which conditionally
    will allow or deny passage of an entity.
    
    """
    def update(self, dt, entity_manager):
        doors_list = entity_manager.pairs_for_type(Door)        
        colliders_list = entity_manager.pairs_for_type(common.RectCollider)
        
        if not doors_list or not colliders_list:
            return
        
        self.track_doors(doors_list, entity_manager)
        
        closed_doors = []
        for pair in doors_list:
            if not pair[1].is_open: # find doors that are closed
                closed_doors.append(pair)
        doors_list = closed_doors
        
        did_collide = False
        for c_id, collider in colliders_list:
            did_collide = False
                        
            for d_id, door in doors_list:
                c_r = (collider.hit_rect.bottom, collider.hit_rect.top)
                d_r = (door.hit_rect.bottom, door.hit_rect.top)
                                
                # see if the objects overlap vertically
                if util.range_overlaps(c_r, d_r):
                    # now test and handle collision with door
                   if self.door_collision(collider, door):
                       did_collide = True
            if did_collide:
                pos = entity_manager.component_for_entity(c_id, common.Position)
                vel = entity_manager.component_for_entity(c_id, common.Velocity)
                pos.x, pos.y = collider.hit_rect.center
                vel.v_x = 0
                 
    def door_collision(self, collider, door):
        did_collide = False
        # handle collision with right side
        if (collider.last.left >= door.hit_rect.right and 
                    collider.hit_rect.left < door.hit_rect.right):
                    
            collider.hit_rect.left = door.hit_rect.right
            did_collide = True
            
        # handle collision with right side
        elif (collider.last.right <= door.hit_rect.left and
                    collider.hit_rect.right > door.hit_rect.left):
                    
            collider.hit_rect.right = door.hit_rect.left
            did_collide = True
        
        return did_collide
    
    def track_doors(self, doors_list, entity_manager):
        """
        Updates the Door's collider to have its bottom-left corner match
        its entity's position
        
        """
        for e_id, door in doors_list:
            pos = entity_manager.component_for_entity(e_id, common.Position)
            if pos:
                door.hit_rect.position = (pos.x, pos.y)
                
class DoorAnimationSystem(ecs.System):
    def update(self, dt, entity_manager):
        doors_list = entity_manager.pairs_for_type(Door)        
        for e_id, door in doors_list:
            two_state = entity_manager.component_for_entity(e_id, graphics.TwoStateGraphic)
            if two_state:
                if door.is_open:
                    two_state.state = 1
                else:
                    two_state.state = 0
            #print util.print_rect(door.hit_rect)
    