import OpenGL.GL as GL
import OpenGL.GLUT as GLUT
import math
import random
import time

class SimpleSniperGame:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.scope_x = self.width // 2
        self.scope_y = self.height // 2
        self.scope_radius = 30
        self.score = 0
        self.ammo = 10
        self.game_over = False
        self.target = self.spawn_target()

    def spawn_target(self):
        return {
            'x': random.randint(100, self.width - 100),
            'y': random.randint(100, self.height - 100),
            'radius': 20,
            'speed': 2.0,
            'direction': random.uniform(0, 2 * math.pi)
        }

    def draw_scope(self):
        GL.glColor3f(1.0, 1.0, 1.0)
        self.midpoint_circle(self.scope_x, self.scope_y, self.scope_radius)
        self.midpoint_line(self.scope_x - self.scope_radius, self.scope_y,
                          self.scope_x + self.scope_radius, self.scope_y)
        self.midpoint_line(self.scope_x, self.scope_y - self.scope_radius,
                          self.scope_x, self.scope_y + self.scope_radius)

    def draw_target(self):
        GL.glColor3f(1.0, 0.0, 0.0)
        self.midpoint_circle(self.target['x'], self.target['y'], self.target['radius'])

    def midpoint_circle(self, center_x, center_y, radius):
        x = radius
        y = 0
        decision = 1 - radius
        
        GL.glBegin(GL.GL_POINTS)
        self.plot_circle_points(center_x, center_y, x, y)
        
        while y < x:
            y += 1
            if decision <= 0:
                decision += 2 * y + 1
            else:
                x -= 1
                decision += 2 * (y - x) + 1
            
            self.plot_circle_points(center_x, center_y, x, y)
        GL.glEnd()

    def plot_circle_points(self, center_x, center_y, x, y):
        points = [
            (center_x + x, center_y + y), (center_x - x, center_y + y),
            (center_x + x, center_y - y), (center_x - x, center_y - y),
            (center_x + y, center_y + x), (center_x - y, center_y + x),
            (center_x + y, center_y - x), (center_x - y, center_y - x)
        ]
        for px, py in points:
            GL.glVertex2f(px, py)

    def midpoint_line(self, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steep = dy > dx

        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
            dx, dy = dy, dx

        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        y_step = 1 if y1 < y2 else -1
        decision = 2 * dy - dx
        y = y1

        GL.glBegin(GL.GL_POINTS)
        for x in range(int(x1), int(x2) + 1):
            if steep:
                GL.glVertex2f(y, x)
            else:
                GL.glVertex2f(x, y)
            if decision > 0:
                y += y_step
                decision -= 2 * dx
            decision += 2 * dy
        GL.glEnd()

    def update_target(self):
        self.target['x'] += math.cos(self.target['direction']) * self.target['speed']
        self.target['y'] += math.sin(self.target['direction']) * self.target['speed']

        # Bounce off walls
        if self.target['x'] - self.target['radius'] < 0 or self.target['x'] + self.target['radius'] > self.width:
            self.target['direction'] = math.pi - self.target['direction']
        if self.target['y'] - self.target['radius'] < 0 or self.target['y'] + self.target['radius'] > self.height:
            self.target['direction'] = -self.target['direction']

    def shoot(self, x, y):
        if self.ammo <= 0 or self.game_over:
            return

        self.ammo -= 1
        dx = x - self.target['x']
        dy = y - self.target['y']
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.target['radius']:
            self.score += 100
            self.target = self.spawn_target()
        else:
            if self.ammo <= 0:
                self.game_over = True

    def draw_hud(self):
        GL.glColor3f(1.0, 1.0, 1.0)
        GL.glRasterPos2f(10, self.height - 20)
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, f"Score: {self.score}".encode())
        GL.glRasterPos2f(10, self.height - 40)
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, f"Ammo: {self.ammo}".encode())

    def display(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glLoadIdentity()

        self.draw_target()
        self.draw_scope()
        self.draw_hud()

        if self.game_over:
            GL.glColor3f(1.0, 0.0, 0.0)
            GL.glRasterPos2f(self.width//2 - 100, self.height//2)
            GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, f"Game Over! Final Score: {self.score}".encode())

        GLUT.glutSwapBuffers()

    def update(self):
        if not self.game_over:
            self.update_target()
        GLUT.glutPostRedisplay()

    def mouse(self, button, state, x, y):
        if button == GLUT.GLUT_LEFT_BUTTON and state == GLUT.GLUT_DOWN:
            self.shoot(x, self.height - y)

    def keyboard(self, key, x, y):
        if key == b'r' and self.game_over:
            self.__init__()
        elif key == b'q':
            GLUT.glutLeaveMainLoop()

    def mouse_motion(self, x, y):
        self.scope_x = x
        self.scope_y = self.height - y

    def reshape(self, width, height):
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, width, 0, height, -1.0, 1.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

def main():
    game = SimpleSniperGame()

    GLUT.glutInit()
    GLUT.glutInitDisplayMode(GLUT.GLUT_DOUBLE | GLUT.GLUT_RGB)
    GLUT.glutInitWindowSize(game.width, game.height)
    GLUT.glutCreateWindow(b"Simple Sniper Game")

    GL.glClearColor(0.0, 0.0, 0.0, 0.0)
    GL.glPointSize(2.0)

    GLUT.glutDisplayFunc(game.display)
    GLUT.glutKeyboardFunc(game.keyboard)
    GLUT.glutMouseFunc(game.mouse)
    GLUT.glutPassiveMotionFunc(game.mouse_motion)
    GLUT.glutReshapeFunc(game.reshape)

    def update(value):
        game.update()
        GLUT.glutTimerFunc(16, update, 0)

    GLUT.glutTimerFunc(0, update, 0)
    GLUT.glutMainLoop()

if __name__ == "__main__":
    main()