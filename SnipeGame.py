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
        self.flash_start_time = 0  # Track when the flash starts
        self.is_flashing = False  # Track if the screen is flashing
        self.flash_duration = 3  # Duration of the flash in seconds
        self.flash_color = (1.0, 1.0, 1.0)  # Flash color (white)

        self.wind_speed = random.uniform(0.5, 2.0)
        self.wind_direction = random.uniform(0, 2 * math.pi)

        # Perfect shot variables
        self.perfect_shot = False  # Flag for perfect shot
        self.perfect_shot_time = 0  # Time when the perfect shot occurred
        self.perfect_shot_duration = 2  # Duration to display the message (in seconds)

        # Combo variables
        self.combo = 0  # Combo counter
        self.last_shot_time = 0  # Time of the last successful shot
        self.combo_timeout = 2  # Combo timeout in seconds

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

        self.midpoint_line(center_x - half_size, center_y + half_size,
                          center_x + half_size, center_y + half_size)

        self.midpoint_line(center_x - half_size, center_y - half_size,
                          center_x + half_size, center_y - half_size)

        self.midpoint_line(center_x - half_size, center_y - half_size,
                          center_x - half_size, center_y + half_size)

        self.midpoint_line(center_x + half_size, center_y - half_size,
                          center_x + half_size, center_y + half_size)
    
    def midpoint_triangle(self, center_x, center_y, size):
        height = size * math.sqrt(3) / 2

        self.midpoint_line(center_x - size / 2, center_y - height / 2,
                            center_x + size / 2, center_y - height / 2)

        self.midpoint_line(center_x, center_y + height / 2,
                          center_x - size / 2, center_y - height / 2)

        self.midpoint_line(center_x, center_y + height / 2,
                          center_x + size / 2, center_y - height / 2)

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
            # Apply wind effect
            target['x'] += math.cos(target['direction']) * (target['speed'] + self.wind_speed * math.cos(self.wind_direction))
            target['y'] += math.sin(target['direction']) * (target['speed'] + self.wind_speed * math.sin(self.wind_direction))
    
            # Bounce off walls
            if target['x'] - target['radius'] < 0 or target['x'] + target['radius'] > self.width:
                target['direction'] = math.pi - target['direction']
            if target['y'] - target['radius'] < 0 or target['y'] + target['radius'] > self.height:
                target['direction'] = -target['direction']

    def shoot(self, x, y):
        if self.ammo <= 0 or self.game_over:
            return

        self.ammo -= 1
        hit = False
        for target in self.targets[:]:
            dx = x - target['x']
            dy = y - target['y']
            distance = math.sqrt(dx * dx + dy * dy)

            if target['shape'] == 'circle' and distance < target['radius']:
                hit = True
            elif target['shape'] == 'square' and self.is_point_in_square(x, y, target['x'], target['y'], target['radius'] * 2):
                hit = True
            elif target['shape'] == 'triangle' and self.is_point_in_triangle(x, y, target['x'], target['y'], target['radius'] * 2):
                hit = True

            if hit:
                self.score += 100
                self.targets.remove(target)
                # Check if the shot was perfect (hit the center)
                if distance < 5:  # Adjust the threshold for "center" as needed
                    self.perfect_shot = True
                    self.perfect_shot_time = time.time()
                # Update combo
                current_time = time.time()
                if current_time - self.last_shot_time < self.combo_timeout:
                    self.combo += 1
                else:
                    self.combo = 1  # Reset combo if timeout
                self.last_shot_time = current_time
                break

        if not hit:
            if self.is_flashing:  # End game if missed during flash
                self.game_over = True
                self.save_score()
            else:
                if self.ammo <= 0:
                    self.game_over = True
                    self.save_score()
            # Reset combo on miss
            self.combo = 0

        if not self.targets:  # If all targets are destroyed, go to next level
            self.level += 1
            self.targets = self.spawn_targets()
            self.ammo += 10  # Refill ammo for the next level

    def is_point_in_square(self, px, py, center_x, center_y, size):
        half_size = size // 2
        return (center_x - half_size <= px <= center_x + half_size and
                center_y - half_size <= py <= center_y + half_size)

    def is_point_in_triangle(self, px, py, center_x, center_y, size):
        height = size * math.sqrt(3) / 2
        x1, y1 = center_x, center_y + height / 2
        x2, y2 = center_x - size / 2, center_y - height / 2
        x3, y3 = center_x + size / 2, center_y - height / 2

        def sign(a, b, c):
            return (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])

        d1 = sign((px, py), (x1, y1), (x2, y2))
        d2 = sign((px, py), (x2, y2), (x3, y3))
        d3 = sign((px, py), (x3, y3), (x1, y1))

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

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
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, f"Speed Increment: +{self.speed_increment}".encode())

        # Display "Perfect Shot" message if applicable
        if self.perfect_shot and (time.time() - self.perfect_shot_time < self.perfect_shot_duration):
            GL.glColor3f(1.0, 1.0, 0.0)  # Yellow color
            GL.glRasterPos2f(self.width // 2 - 50, self.height - 100)
            GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, b"Perfect Shot!")
        else:
            self.perfect_shot = False  # Reset the flag after the duration expires

        # Display combo count
        if self.combo > 0:
            GL.glColor3f(1.0, 1.0, 0.0)  # Yellow color
            GL.glRasterPos2f(self.width // 2 - 30, self.height - 120)
            GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, f"Combo: {self.combo}x".encode())

    def display(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glLoadIdentity()

        # Flash the screen if score > 1000
        if self.is_flashing:
            current_time = time.time()
            if current_time - self.flash_start_time < self.flash_duration:
                # Alternate between flash color and black
                if int((current_time - self.flash_start_time) * 10) % 2 == 0:
                    GL.glClearColor(*self.flash_color, 1.0)
                else:
                    GL.glClearColor(0.0, 0.0, 0.0, 1.0)
                GL.glClear(GL.GL_COLOR_BUFFER_BIT)
            else:
                self.is_flashing = False
                GL.glClearColor(0.0, 0.0, 0.0, 1.0)

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
                self.speed_increment += 1.5
                self.last_speed_increase = current_time
                # Update speed of existing targets
                for target in self.targets:
                    target['speed'] += 1.5

            # Start flash if score > 1000
            if self.score > 1000 and not self.is_flashing:
                self.is_flashing = True
                self.flash_start_time = time.time()

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