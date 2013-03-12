import config

def lerp(a, b, factor):
	"""
	Returns a value that is between a and b, closer
	to b if factor is closer to 1, and closer to a
	if factor is closer to 0
    
	"""
	
	return a + (b-a)*factor
    
def range_overlaps(r_1, r_2):
    """
    Determines if the number range in 2-tuple r_1 overlaps
    the range in 2-tuple r_2
    
    """
    # sort the intervals
    if r_1[0] > r_2[0]:
        temp = r_1
        r_1 = r_2
        r_2 = temp
        
    diff = (r_2[0]-r_1[0], r_2[0]-r_1[1], r_2[1]-r_1[0], r_2[1]-r_1[1])
    for num in diff:
        if num < 0:
            return True
    
    return False
    
def print_rect(r):
    return '({:2f} {:2f}), ({:2f} {:2f})'.format(r.left, r.bottom, r.right, r.top)
    
def tile(i, j):
    """
    Returns a pixel-space position that corresponds to the tile indices i, j
    
    """
    return (i*config.TILE_SIZE[0], j*config.TILE_SIZE[1])