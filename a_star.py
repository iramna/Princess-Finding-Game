import pygame
import math
from queue import PriorityQueue

pygame.init()  # Initialize all Pygame modules | drawing logic (x, y) separate from pathfinding logic (row, col).

# Total window size
WIDTH = 800
GRID_WIDTH = 600  # Grid area width
HUD_WIDTH = WIDTH - GRID_WIDTH  # Space reserved for HUD

WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Informed Princess Finding Algorithm - A*")

# Color codes for the grid and path
PINK_DARK   = (224, 33, 138)
PINK_HOT    = (255, 105, 180)
PINK_BABY   = (255, 182, 193)
PURPLE_SOFT = (216, 191, 216)
LILAC       = (200, 162, 200)
PEACH       = (255, 218, 185)
MINT        = (189, 252, 201)
SKY_BLUE    = (135, 206, 250)
CREAM       = (255, 253, 208)
ROSE_GOLD   = (183, 110, 121)
GRID_COLOR  = (220, 220, 220)  # light grey for grid lines

# Grid cell class
class State:
    def __init__(self, row, col, width, total_rows): #instead of juggling (row, col, color, …) everywhere, we bundle those properties and behaviors into a single reusable object-abstraction
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.color = CREAM
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):     # state management methods 
        return self.row, self.col

    def is_closed(self):   #Each one checks if the cell’s role in the algorithm matches its color.
        return self.color == SKY_BLUE

    def is_open(self):
        return self.color == PEACH

    def is_obstacle(self):
        return self.color == MINT

    def is_start(self):
        return self.color == ROSE_GOLD

    def is_end(self):
        return self.color == PINK_HOT

    def reset(self):
        self.color = CREAM

    def make_closed(self): #These are mutators: they set the cell into a specific role.
        self.color = SKY_BLUE

    def make_open(self):
        self.color = PEACH

    def make_obstacle(self):
        self.color = MINT

    def make_start(self):
        self.color = ROSE_GOLD

    def make_end(self):
        self.color = PINK_HOT

    def make_path(self):
        self.color = LILAC

    def draw(self, win):#drawing logic:the main loop doesn’t need to know how a cell draws itself, just that it can-encaptulation
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):# which moves are possible 
        self.neighbours = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_obstacle():
            self.neighbours.append(grid[self.row + 1][self.col])
        # UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle():
            self.neighbours.append(grid[self.row - 1][self.col])
        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_obstacle():
            self.neighbours.append(grid[self.row][self.col + 1])
        # LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle():
            self.neighbours.append(grid[self.row][self.col - 1])

    def __lt__(self, other): #“less than” operator. If you ever try to compare two State objects directly[same f score], just say neither is less than the other
        return False

# Heuristic function (Manhattan distance)
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

# Reconstruct path from end to start
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

# A* Algorithm
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue() # keeps track of nodes to explore, ordered by lowest f_score
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        current.update_neighbours(grid)

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False   
#no path exists return false

# Create grid
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = State(i, j, gap, rows)
            grid[i].append(node)
    return grid

# Draw grid lines
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows + 1):
        pygame.draw.line(win, GRID_COLOR, (0, i * gap), (width, i * gap))
    for j in range(rows + 1):
        pygame.draw.line(win, GRID_COLOR, (j * gap, 0), (j * gap, width))

def draw_title(win):
    font = pygame.font.SysFont("Courier New", 24, bold=True)  # size 24, bold  
    title_surface = font.render("Informed Princess Finding Algorithm - A star", True, (0, 0, 0))
    text_rect = title_surface.get_rect()
    # Horizontally center in the **full window**
    text_rect.centerx = (GRID_WIDTH + HUD_WIDTH)  // 2
    # Place it **10 pixels above the grid area**
    text_rect.top = 620
    win.blit(title_surface, text_rect)

# Draw legend / HUD
def draw_legend(win):
    font = pygame.font.SysFont("Courier New", 16, bold=True)  # size 24, bold
    x_start = GRID_WIDTH + 20
    y_start = 100
    spacing = 60
    box_size = 30

    labels = [
        ("Start  Prince", ROSE_GOLD),
        ("End  Princess", PINK_HOT),
        ("Open Considered", PEACH),
        ("Closed Checked", SKY_BLUE),
        ("Obstacle  Wall", MINT),
        ("Path", LILAC)
    ]

    for i, (text, color) in enumerate(labels):
        box_y = y_start + i*spacing
        pygame.draw.rect(win, color, (x_start, box_y, box_size, box_size))
        # Draw text just below the box
        label = font.render(text, True, (0, 0, 0))
        win.blit(label, (x_start, box_y + box_size + 5))

# Draw grid + HUD
def draw(win, grid, rows, width):
    win.fill(CREAM)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, GRID_WIDTH)  # grid lines
    draw_legend(win)                  # HUD
    draw_title(win)                   # draw title **after grid and HUD**
    pygame.display.update()

# Convert click position to grid coordinates
def get_click_pos(pos, rows, width):
    gap = width // rows
    x, y = pos
    if x >= GRID_WIDTH:
        return None, None
    row = min(y // gap, rows - 1)
    col = min(x // gap, rows - 1)
    return row, col

# Main function
def main(win, width):
    Rows = 50
    grid = make_grid(Rows, GRID_WIDTH)
    start = None
    end = None
    run = True
    started = False

    while run:
        draw(win, grid, Rows, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, Rows, GRID_WIDTH)
                if row is None or col is None:
                    continue
                node = grid[row][col]

                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != start and node != end:
                    node.make_obstacle()

            elif pygame.mouse.get_pressed()[2]: #undoing the start or end 
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, Rows, GRID_WIDTH)
                if row is None or col is None:
                    continue
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                    algorithm(lambda: draw(win, grid, Rows, width), grid, start, end)
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(Rows, GRID_WIDTH)

    pygame.quit()

main(WIN, WIDTH)
