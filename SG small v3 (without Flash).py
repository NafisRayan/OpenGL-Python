import OpenGL.GL as GL
import OpenGL.GLUT as GLUT
import math
import random
import time
import json
import os

class MultiTargetSniperGame:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.scope_x = self.width // 2
        self.scope_y = self.height // 2
        self.scope_radius = 30
        self.score = 0
        self.ammo = 20
        self.game_over = False
        self.level = 1  # Start at level 1
        self.speed_increment = 0  # Initialize speed increment
        self.targets = self.spawn_targets()
        self.start_time = time.time()  # Track game start time
        self.scores_file = "scores.json"  # File to save scores
        self.scores = self.load_scores()  # Load existing scores
        self.last_speed_increase = time.time()  # Track last speed increase

    def spawn_targets(self):
        targets = []
        num_targets = 5 + self.level  # Increase number of targets with level
        for _ in range(num_targets):
            shape = random.choice(['circle', 'square', 'triangle'])  # Random shape
            target = {
                'x': random.randint(100, self.width - 100),
                'y': random.randint(100, self.height - 100),
                'radius': random.randint(20, 40),  # Random radius
                'speed': 2.0 + (self.level * 0.5) + self.speed_increment,  # Base speed + level + speed increment
                'direction': random.uniform(0, 2 * math.pi),
                'color': (random.random(), random.random(), random.random()),  # Random color
                'shape': shape  # Assign random shape
            }
            targets.append(target)
        return targets

    def draw_scope(self):
        GL.glColor3f(1.0, 1.0, 1.0)
        self.midpoint_circle(self.scope_x, self.scope_y, self.scope_radius)
        self.midpoint_line(self.scope_x - self.scope_radius, self.scope_y,
                          self.scope_x + self.scope_radius, self.scope_y)
        self.midpoint_line(self.scope_x, self.scope_y - self.scope_radius,
                          self.scope_x, self.scope_y + self.scope_radius)

    def draw_targets(self):
        for target in self.targets:
            GL.glColor3f(*target['color'])
            if target['shape'] == 'circle':
                self.midpoint_circle(target['x'], target['y'], target['radius'])
            elif target['shape'] == 'square':
                self.midpoint_square(target['x'], target['y'], target['radius'])
            elif target['shape'] == 'triangle':
                self.midpoint_triangle(target['x'], target['y'], target['radius'])

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

    def midpoint_square(self, center_x, center_y, size):
        half_size = size // 2
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glVertex2f(center_x - half_size, center_y - half_size)
        GL.glVertex2f(center_x + half_size, center_y - half_size)
        GL.glVertex2f(center_x + half_size, center_y + half_size)
        GL.glVertex2f(center_x - half_size, center_y + half_size)
        GL.glEnd()

    def midpoint_triangle(self, center_x, center_y, size):
        height = size * math.sqrt(3) / 2
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glVertex2f(center_x, center_y + height / 2)
        GL.glVertex2f(center_x - size / 2, center_y - height / 2)
        GL.glVertex2f(center_x + size / 2, center_y - height / 2)
        GL.glEnd()

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

    def update_targets(self):
        for target in self.targets:
            target['x'] += math.cos(target['direction']) * target['speed']
            target['y'] += math.sin(target['direction']) * target['speed']

            # Bounce off walls
            if target['x'] - target['radius'] < 0 or target['x'] + target['radius'] > self.width:
                target['direction'] = math.pi - target['direction']
            if target['y'] - target['radius'] < 0 or target['y'] + target['radius'] > self.height:
                target['direction'] = -target['direction']

    def shoot(self, x, y):
        if self.ammo <= 0 or self.game_over:
            return

        self.ammo -= 1
        for target in self.targets[:]:
            dx = x - target['x']
            dy = y - target['y']
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < target['radius']:
                self.score += 100
                self.targets.remove(target)
                break
        else:
            if self.ammo <= 0:
                self.game_over = True
                self.save_score()  # Save score when game ends

        if not self.targets:  # If all targets are destroyed, go to next level
            self.level += 1
            self.targets = self.spawn_targets()
            self.ammo += 10  # Refill ammo for the next level

    def save_score(self):
        elapsed_time = time.time() - self.start_time
        score_entry = {
            'index': len(self.scores) + 1,  # Auto-increment index
            'score': self.score,
            'time': round(elapsed_time, 2),  # Time in seconds, rounded to 2 decimal places
            'level': self.level  # Save the level achieved
        }
        self.scores.append(score_entry)
        with open(self.scores_file, 'w') as f:
            json.dump(self.scores, f, indent=4)

    def load_scores(self):
        if os.path.exists(self.scores_file):
            with open(self.scores_file, 'r') as f:
                scores = json.load(f)
                # Ensure all score entries have the 'level' key
                for entry in scores:
                    if 'level' not in entry:
                        entry['level'] = 1  # Default level for older entries
                return scores
        return []

    def draw_hud(self):
        GL.glColor3f(1.0, 1.0, 1.0)
        GL.glRasterPos2f(10, self.height - 20)
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, f"Score: {self.score}".encode())
        GL.glRasterPos2f(10, self.height - 40)
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, f"Ammo: {self.ammo}".encode())
        GL.glRasterPos2f(10, self.height - 60)
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, f"Level: {self.level}".encode())
        GL.glRasterPos2f(10, self.height - 80)
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, f"Time Increment: +{self.speed_increment}".encode())

    def display(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glLoadIdentity()

        self.draw_targets()
        self.draw_scope()
        self.draw_hud()

        if self.game_over:
            GL.glColor3f(1.0, 0.0, 0.0)
            GL.glRasterPos2f(self.width//2 - 100, self.height//2)
            GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, f"Game Over! Final Score: {self.score}".encode())
            GL.glRasterPos2f(self.width//2 - 80, self.height//2 - 30)
            GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, b"Press R to Restart")

            # Display saved scores
            y_offset = 60
            GL.glColor3f(0.0, 1.0, 0.0)  # Green for scores
            for score_entry in self.scores[-5:]:  # Show last 5 scores
                GL.glRasterPos2f(self.width//2 - 100, self.height//2 - y_offset)
                GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, f"Score {score_entry['index']}: {score_entry['score']} (Time: {score_entry['time']}s, Level: {score_entry['level']})".encode())
                y_offset += 20

        GLUT.glutSwapBuffers()

    def update(self):
        if not self.game_over:
            self.update_targets()
            # Check if ammo is 0 and end the game
            if self.ammo <= 0:
                self.game_over = True
                self.save_score()  # Save score when game ends

            # Increase speed every 7 seconds
            current_time = time.time()
            if current_time - self.last_speed_increase >= 7:
                self.speed_increment += 1
                self.last_speed_increase = current_time
                # Update speed of existing targets
                for target in self.targets:
                    target['speed'] += 1

        GLUT.glutPostRedisplay()

    def mouse(self, button, state, x, y):
        if button == GLUT.GLUT_LEFT_BUTTON and state == GLUT.GLUT_DOWN:
            self.shoot(x, self.height - y)

    def keyboard(self, key, x, y):
        if key == b'r':  # Restart the game
            self.__init__()
        elif key == b'q':  # Quit the game
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
    game = MultiTargetSniperGame()

    GLUT.glutInit()
    GLUT.glutInitDisplayMode(GLUT.GLUT_DOUBLE | GLUT.GLUT_RGB)
    GLUT.glutInitWindowSize(game.width, game.height)
    GLUT.glutCreateWindow(b"Multi-Target Sniper Game")

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