from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time
import heapq

# Grid settings
GRID_SIZE = 10
CELL_SIZE = 40

# Colors
WHITE = (1, 1, 1)
BLACK = (0, 0, 0)
RED = (1, 0, 0)
BLUE = (0, 0, 1)
GREEN = (0, 1, 0)

# Environment
obstacles = [
    # Vertical walls
    (2, 1), (2, 2), (2, 3), (2, 4),
    (4, 5), (4, 6), (4, 7), (4, 8),
    (6, 1), (6, 2), (6, 3), (6, 4),
    (8, 5), (8, 6), (8, 7), (8, 8),
    
    # Horizontal walls
    (1, 4), (2, 4), (3, 4),
    (5, 2), (6, 2), (7, 2),
    (3, 6), (4, 6), (5, 6),
    (7, 8), (8, 8), (9, 8),
    
    # Some additional obstacles for complexity
    (0, 2), (4, 0), (8, 2), (1, 8)
]  # Obstacle positions
start = None  # Starting position (to be selected by user)
goal = None  # Ending position (to be selected by user)
path = []

def draw_cell(x, y, color):
    """Draw a grid cell."""
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x * CELL_SIZE, y * CELL_SIZE)
    glVertex2f((x + 1) * CELL_SIZE, y * CELL_SIZE)
    glVertex2f((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE)
    glVertex2f(x * CELL_SIZE, (y + 1) * CELL_SIZE)
    glEnd()

def draw_grid():
    """Draw the entire grid."""
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if (x, y) in obstacles:
                draw_cell(x, y, BLACK)
            elif (x, y) == start:
                draw_cell(x, y, BLUE)
            elif (x, y) == goal:
                draw_cell(x, y, RED)
            elif (x, y) in path:
                draw_cell(x, y, GREEN)
            else:
                draw_cell(x, y, WHITE)

def heuristic(a, b):
    """Calculate Manhattan distance."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(start, goal):
    """Find the shortest path using the A* algorithm."""
    global path
    path = []
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            reconstruct_path(came_from, current)
            return

        neighbors = [
            (current[0] + dx, current[1] + dy)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
        ]
        neighbors = [
            neighbor for neighbor in neighbors
            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE
            and neighbor not in obstacles
        ]

        for neighbor in neighbors:
            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

def reconstruct_path(came_from, current):
    """Reconstruct the path from the goal to the start."""
    global path
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()

def display():
    """Render the scene."""
    glClear(GL_COLOR_BUFFER_BIT)
    draw_grid()
    glutSwapBuffers()

def mouse_click(button, state, x, y):
    """Handle mouse clicks to set start and goal."""
    global start, goal
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        grid_x = x // CELL_SIZE
        grid_y = GRID_SIZE - 1 - y // CELL_SIZE  # Convert screen to grid coordinates

        if start is None:
            start = (grid_x, grid_y)
        elif goal is None:
            goal = (grid_x, grid_y)
            a_star_search(start, goal)
        else:
            start = goal = None
            path.clear()

def update(value):
    """Update the simulation."""
    glutPostRedisplay()
    glutTimerFunc(100, update, 0)

def main():
    """Main function."""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
    glutCreateWindow(b"Car Game: Shortest Path Finder")
    glOrtho(0, GRID_SIZE * CELL_SIZE, 0, GRID_SIZE * CELL_SIZE, -1, 1)
    glutDisplayFunc(display)
    glutMouseFunc(mouse_click)
    glutTimerFunc(100, update, 0)
    glutMainLoop()











def findzone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx >= 0:
        if dy >= 0:
            return 0 if abs(dx) > abs(dy) else 1
        else:
            return 7 if abs(dx) > abs(dy) else 6
    else:
        if dy >= 0:
            return 3 if abs(dx) > abs(dy) else 2
        else:
            return 4 if abs(dx) > abs(dy) else 5

def convert_to_zone0(x, y, original_zone):
    if original_zone == 0:
        return (x, y)
    elif original_zone == 1:
        return (y, x)
    elif original_zone == 2:
        return (y, -x)
    elif original_zone == 3:
        return (-x, y)
    elif original_zone == 4:
        return (-x, -y)
    elif original_zone == 5:
        return (-y, -x)
    elif original_zone == 6:
        return (-y, x)
    elif original_zone == 7:
        return (x, -y)

def convert_to_original_zone(x, y, original_zone):
    if original_zone == 0:
        return (x, y)
    elif original_zone == 1:
        return (y, x)
    elif original_zone == 2:
        return (-y, x)
    elif original_zone == 3:
        return (-x, y)
    elif original_zone == 4:
        return (-x, -y)
    elif original_zone == 5:
        return (-y, -x)
    elif original_zone == 6:
        return (y, -x)
    elif original_zone == 7:
        return (x, -y)

def drawpixel(x, y, original_zone):
    glPointSize(1)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def MidpointLine(x1, y1, x2, y2, color):
    zone = findzone(x1, y1, x2, y2)
    x1, y1 = convert_to_zone0(x1, y1, zone)
    x2, y2 = convert_to_zone0(x2, y2, zone)
    glColor3f(*color)
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    incrE = 2 * dy
    incrNE = 2 * (dy - dx)
    x = x1
    y = y1
    
    while x < x2:
        if d <= 0:
            d += incrE
            x += 1
        else:
            d += incrNE
            x += 1
            y += 1
        original_x, original_y = convert_to_original_zone(x, y, zone)
        drawpixel(original_x, original_y, zone)


def plotPoints(x, y, xc, yc):
    glVertex2f(x + xc, y + yc)
    glVertex2f(y + xc, x + yc)
    glVertex2f(-y + xc, x + yc)
    glVertex2f(-x + xc, y + yc)
    glVertex2f(-x + xc, -y + yc)
    glVertex2f(-y + xc, -x + yc)
    glVertex2f(y + xc, -x + yc)
    glVertex2f(x + xc, -y + yc)

def MidpointCircle(radius, xc, yc, color):
    x = 0
    y = radius
    d = 1 - radius
    glColor3f(*color)

    glBegin(GL_POINTS)
    while x < y:
        if d < 0:
            d = d + 2 * x + 3
            x += 1
        else:
            d = d + 2 * (x - y) + 5
            x += 1
            y -= 1
        plotPoints(x, y, xc, yc)
    glEnd()




def draw_circle_in_cell(x, y, radius, color):
    """Draw a circle centered in a grid cell."""
    xc = x * CELL_SIZE + CELL_SIZE // 2
    yc = y * CELL_SIZE + CELL_SIZE // 2
    MidpointCircle(radius, xc, yc, color)

def draw_line_between_cells(cell1, cell2, color):
    """Draw a line connecting two grid cells."""
    x1, y1 = cell1
    x2, y2 = cell2
    x1 = x1 * CELL_SIZE + CELL_SIZE // 2
    y1 = y1 * CELL_SIZE + CELL_SIZE // 2
    x2 = x2 * CELL_SIZE + CELL_SIZE // 2
    y2 = y2 * CELL_SIZE + CELL_SIZE // 2
    MidpointLine(x1, y1, x2, y2, color)

def draw_grid():
    """Draw the entire grid with enhanced visuals."""
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if (x, y) in obstacles:
                draw_cell(x, y, BLACK)
                draw_circle_in_cell(x, y, CELL_SIZE // 4, WHITE)  # Highlight obstacles
            elif (x, y) == start:
                draw_cell(x, y, BLUE)
                draw_circle_in_cell(x, y, CELL_SIZE // 4, RED)  # Highlight start
            elif (x, y) == goal:
                draw_cell(x, y, RED)
                draw_circle_in_cell(x, y, CELL_SIZE // 4, GREEN)  # Highlight goal
            elif (x, y) in path:
                draw_cell(x, y, GREEN)
                # Draw lines connecting path cells
                path_index = path.index((x, y))
                if path_index > 0:
                    draw_line_between_cells(path[path_index - 1], (x, y), BLUE)
            else:
                draw_cell(x, y, WHITE)




if __name__ == "__main__":
    main()