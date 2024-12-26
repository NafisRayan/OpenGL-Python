import time
import heapq
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Grid parameters
GRID_SIZE = 20
CELL_SIZE = 30
start_node = None
goal_node = None

# Global variables for distance and time
distance = 0
time_taken = 0

# A* Algorithm class
class AStar:
    def __init__(self, grid):
        self.grid = grid
        self.path = []

    def heuristic(self, node, goal):
        """Manhattan distance heuristic."""
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    def get_neighbors(self, node):
        """Get valid neighbors of the current node."""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            x, y = node[0] + dx, node[1] + dy
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and self.grid[x][y] != 1:
                neighbors.append((x, y))
        return neighbors

    def reconstruct_path(self, came_from, current):
        """Reconstruct the path from start to goal."""
        self.path = []
        while current in came_from:
            self.path.append(current)
            current = came_from[current]
        self.path.reverse()

    def a_star_search(self, start, goal):
        global distance, time_taken  # Use global variables to store results
        self.path = []
        start_time = time.time()  # Start the timer

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                self.reconstruct_path(came_from, current)
                distance = len(self.path) - 1  # Path length minus start
                time_taken = time.time() - start_time  # Calculate time
                return

            neighbors = self.get_neighbors(current)

            for neighbor in neighbors:
                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

# Grid initialization
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
astar = AStar(grid)

# Button states
add_obstacles_mode = False
set_start_end_mode = False
start_game_mode = False


def draw_grid():
    """Draw the grid."""
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if grid[x][y] == 1:
                glColor3f(0.5, 0.5, 0.5)  # Obstacle color
            elif (x, y) == start_node:
                glColor3f(0, 1, 0)  # Start node color
            elif (x, y) == goal_node:
                glColor3f(1, 0, 0)  # Goal node color
            elif (x, y) in astar.path:
                glColor3f(0, 0, 1)  # Path color
            else:
                glColor3f(1, 1, 1)  # Default cell color

            glBegin(GL_QUADS)
            glVertex2f(x * CELL_SIZE, y * CELL_SIZE)
            glVertex2f((x + 1) * CELL_SIZE, y * CELL_SIZE)
            glVertex2f((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE)
            glVertex2f(x * CELL_SIZE, (y + 1) * CELL_SIZE)
            glEnd()

def draw_menu():
    """Draw the menu displaying distance and time."""
    glColor3f(0, 0, 0)
    glRasterPos2f(10, GRID_SIZE * CELL_SIZE - 20)  # Position at the top left
    menu_text = f"Distance: {distance} | Time: {time_taken:.2f} seconds"
    for char in menu_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_buttons():
    """Draw buttons to toggle modes and start the game."""
    glColor3f(0, 0, 0)
    glRasterPos2f(10, 10)  # Bottom left for buttons
    button_text = "[1] Add Obstacles | [2] Set Start/End | [3] Start Game | [4] Restart"
    for char in button_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def clear_grid():
    """Clear the grid and reset states."""
    global start_node, goal_node, distance, time_taken, astar
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            grid[x][y] = 0
    start_node = None
    goal_node = None
    distance = 0
    time_taken = 0
    astar.path = []
    print("Grid cleared and reset.")

def display():
    """Render the scene."""
    glClear(GL_COLOR_BUFFER_BIT)
    draw_grid()
    draw_menu()  # Add the menu to the display
    draw_buttons()  # Add buttons to the display
    glutSwapBuffers()

def keyboard_callback(key, x, y):
    """Handle keyboard input for button toggles."""
    global add_obstacles_mode, set_start_end_mode, start_game_mode

    if key == b'1':
        add_obstacles_mode = True
        set_start_end_mode = False
        start_game_mode = False
        print("Add obstacles mode enabled.")

    elif key == b'2':
        add_obstacles_mode = False
        set_start_end_mode = True
        start_game_mode = False
        print("Set start/end mode enabled.")

    elif key == b'3':
        if start_node and goal_node:
            add_obstacles_mode = False
            set_start_end_mode = False
            start_game_mode = True
            astar.a_star_search(start_node, goal_node)
            print("Game started.")

    elif key == b'4':
        clear_grid()

    glutPostRedisplay()

def mouse_callback(button, state, x, y):
    """Handle mouse clicks to set start, goal, and obstacles."""
    global start_node, goal_node
    grid_x = x // CELL_SIZE
    grid_y = (GRID_SIZE * CELL_SIZE - y) // CELL_SIZE

    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            if add_obstacles_mode:
                grid[grid_x][grid_y] = 1  # Set obstacle
            elif set_start_end_mode:
                if start_node is None:
                    start_node = (grid_x, grid_y)
                elif goal_node is None:
                    goal_node = (grid_x, grid_y)
        elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            grid[grid_x][grid_y] = 0  # Remove obstacle

        glutPostRedisplay()

def main():
    """Main function to set up the OpenGL environment."""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
    glutCreateWindow(b"A* Pathfinding with Menu and Buttons")
    glClearColor(1, 1, 1, 1)
    gluOrtho2D(0, GRID_SIZE * CELL_SIZE, 0, GRID_SIZE * CELL_SIZE)
    glutDisplayFunc(display)
    glutMouseFunc(mouse_callback)
    glutKeyboardFunc(keyboard_callback)
    glutMainLoop()

if __name__ == "__main__":
    main()
