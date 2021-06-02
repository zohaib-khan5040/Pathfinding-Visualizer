import pygame
from queue import PriorityQueue
import sys

WIDTH = 800
screen = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("Pathfinding Visualizer")

blue = (0,136,204) # Start Node
default = (59,69,80) # Default state node
black = (0,0,0) # Barrier/ Wall node
turquoise = (0,173,181) # Search Region: explored
cyan = (10,189,222) # Search Region: searching
yellow = (237,175,31) # End node
white = (255,255,255) # Path nodes
grey = (142,166,180) # Filler between nodes

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = default
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
    
    def get_pos(self):
        """Returns the position of the node as (x,y)"""
        return self.row, self.col
    
    def is_closed(self):
        """Return if we are not looking at the node anymore"""
        return self.color == turquoise
    
    def is_open(self):
        """Return if node is in the open set"""
        return self.color == cyan

    def is_wall(self):
        """Returns if node cannot be considered/is a barrier to the path"""
        return self.color == black
    
    def is_end(self):
        """Returns if we have reached the final destination"""
        return self.color == yellow
    
    def reset(self):
        """Resets node state after traversal"""
        self.color = default

    def make_start(self):
        self.color = blue

    def make_closed(self):
        self.color = turquoise

    def make_open(self):
        self.color = cyan
    
    def make_wall(self):
        self.color = black
    
    def make_end(self):
        self.color = yellow
    
    def make_path(self):
        """Final path will be white"""
        self.color = white
    
    def draw(self,screen):
        """Draws pygame rects to represent the nodes"""
        pygame.draw.rect(screen, self.color, (self.x,self.y,self.width,self.width))
    
    def update_neighbors(self,grid):
        """Finds the neighbors for a given node"""
        self.neighbors = []
        # Moving down the rows
        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_wall():
            self.neighbors.append(grid[self.row+1][self.col])
        # Moving up the rows 
        if self.row > 0 and not grid[self.row-1][self.col].is_wall():
            self.neighbors.append(grid[self.row-1][self.col])
        # Moving right
        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_wall():
            self.neighbors.append(grid[self.row][self.col+1])
        # Moving left
        if self.col > 0 and not grid[self.row][self.col-1].is_wall():
            self.neighbors.append(grid[self.row][self.col-1])

    def __lt__(self):
        """For comparing two nodes"""
        return False

def heuristic(p1,p2):
    """Euclidean distance for the heuristic function for A* Pathfinding"""
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    """The actual pathfinding algorithm"""
    count = 0
    open_set = PriorityQueue()
    # Adding the start node to the P-Queue
    open_set.put((0, count, start))
    came_from = {}

    # Defining the f and g scores for A* Pathfinding:
    # G: distance from the start to the current node
    # F: perceived distance to the end, using the heuristic
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = heuristic(start.get_pos(), end.get_pos())
    
    # Keeping track of items in the P-Queue
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

    # Accessing the Node
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
        # Construct the path
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
            
        for neighbor in current.neighbors:
            # Assuming the neighbor one unit away is one unit further from the start
            tmp_g = g_score[current] + 1

            if tmp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tmp_g
                f_score[neighbor] = tmp_g + heuristic(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
            
        draw()

        if current != start:
            # Start node already considered
            current.make_closed()
        
    return False

def make_grid(rows, width):
    """A way to manage all the nodes"""
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid(screen, rows, width):
    gap = width // rows
    # Draw horizontal lines in between rows
    for i in range(rows):
        pygame.draw.line(screen, grey, (0, i*gap), (width, i*gap))
    # Draw vertical lines between columns
        for j in range(rows):
            pygame.draw.line(screen, grey, (j*gap, 0), (j*gap, width))

def draw(screen, grid, rows, width):
    screen.fill(default)

    for row in grid:
        for spot in row:
            spot.draw(screen)
    
    draw_grid(screen, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    """Returns which node we've clicked on"""
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

def main(screen, width):
    ROWS = 40
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(screen, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()
                        
            # Left mouse button pressed
            if pygame.mouse.get_pressed()[0]:
                # Get the position of the mouse
                pos = pygame.mouse.get_pos()
                # Get the node index which was clicked on
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                # User creates the start and end positions first
                if not start and node != end:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    end = node
                    end.make_end()
                
                elif node != start and node != end:
                    node.make_wall()

            # Right mouse button pressed
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos,ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    # Run the algorithm
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    
                    algorithm(lambda: draw(screen, grid, ROWS, width), grid, start, end)
                
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    sys.exit()

main(screen, WIDTH)