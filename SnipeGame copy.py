import OpenGL.GL as GL
import OpenGL.GLUT as GLUT
import math
import random
import time

class SniperGame:
    def __init__(self):
        self.width = 1024
        self.height = 768
        self.scope_x = self.width // 2
        self.scope_y = self.height // 2
        self.scope_radius = 50
        self.score = 0
        self.ammo = 15
        self.game_over = False
        self.reload_time = 1.0
        self.last_shot_time = 0
        self.can_shoot = True
        self.level = 1
        self.targets = []
        self.powerups = []
        self.hits = []
        self.misses = []
        self.combo = 0
        self.max_combo = 0
        self.last_hit_time = 0
        self.combo_timeout = 3.0  # seconds to maintain combo
        self.zoom_level = 1.0
        self.scope_stability = 1.0
        self.points_multiplier = 1.0
        self.powerup_types = ['ammo', 'stability', 'zoom', 'multiplier']
        self.target_types = ['normal', 'fast', 'small', 'bonus']
        self.target_colors = {
            'normal': (1.0, 0.0, 0.0),
            'fast': (1.0, 0.5, 0.0),
            'small': (0.0, 1.0, 1.0),
            'bonus': (1.0, 1.0, 0.0)
        }
        self.target_points = {
            'normal': 100,
            'fast': 200,
            'small': 300,
            'bonus': 500
        }
        self.shake_offset = {'x': 0, 'y': 0}
        self.shake_decay = 0.9
        self.achievements = {
            'perfect_shot': False,
            'combo_master': False,
            'sharpshooter': False
        }
        
        # Initialize game state
        self.wind_speed = 0
        self.wind_direction = 1

        self.spawn_initial_targets()

        self.start_time = time.time()
        self.base_speed = 1.0  # Initialize base_speed with a default value
        self.level = 1
        self.update_base_speed()  # Call this method to set the initial base_speed based on level
    






    def calculate_game_play_time(self):
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        return elapsed_time

    def update_base_speed(self):
        self.base_speed = 1.0 + (self.level * 0.5)

























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

    def draw_scope(self, scope_x, scope_y):
        # Outer circle
        GL.glColor3f(0.0, 0.0, 0.0)
        self.midpoint_circle(self.scope_x, self.scope_y, self.scope_radius)
        
        # Inner circle
        self.midpoint_circle(self.scope_x, self.scope_y, self.scope_radius - 2)
        
        # Crosshairs
        self.midpoint_line(self.scope_x - self.scope_radius, self.scope_y,
                          self.scope_x + self.scope_radius, self.scope_y)
        self.midpoint_line(self.scope_x, self.scope_y - self.scope_radius,
                          self.scope_x, self.scope_y + self.scope_radius)
        
        # Range markers
        for i in range(1, 4):
            offset = i * 10
            self.midpoint_line(self.scope_x - 5, self.scope_y + offset,
                             self.scope_x + 5, self.scope_y + offset)

    def spawn_initial_targets(self):
        self.level += 1  # Increment level before spawning targets
        self.update_base_speed()  # Update base_speed based on new level
        num_targets = 3 + self.level
        for _ in range(num_targets):
            self.spawn_target()
        
        if random.random() < 0.3:  # 30% chance to spawn a powerup
            self.spawn_powerup()

    def spawn_target(self):
        target_type = random.choice(self.target_types)
        base_speed = self.base_speed
        base_radius = 15
        
        if target_type == 'fast':
            speed = base_speed * 2
            radius = base_radius
        elif target_type == 'small':
            speed = base_speed
            radius = base_radius * 0.6
        elif target_type == 'bonus':
            speed = base_speed * 1.5
            radius = base_radius * 0.8
        else:  # normal
            speed = base_speed
            radius = base_radius

        target = {
            'x': random.randint(100, self.width - 100),
            'y': random.randint(100, self.height - 100),
            'radius': radius,
            'direction': random.uniform(0, 2 * math.pi),
            'speed': speed,
            'type': target_type,
            'points': self.target_points[target_type],
            'creation_time': time.time(),
            'last_direction_change': time.time()
        }
        self.targets.append(target)

    def spawn_powerup(self):
        powerup = {
            'x': random.randint(100, self.width - 100),
            'y': random.randint(100, self.height - 100),
            'radius': 10,
            'type': random.choice(self.powerup_types),
            'duration': 10.0,  # seconds
            'creation_time': time.time(),
            'last_direction_change': time.time()
        }
        self.powerups.append(powerup)

    def apply_powerup(self, powerup_type):
        if powerup_type == 'ammo':
            self.ammo += 5
        elif powerup_type == 'stability':
            self.scope_stability = 0.5
        elif powerup_type == 'zoom':
            self.zoom_level = 1.5
        elif powerup_type == 'multiplier':
            self.points_multiplier = 2.0

    def update_shake(self):
        self.shake_offset['x'] *= self.shake_decay
        self.shake_offset['y'] *= self.shake_decay
        if abs(self.shake_offset['x']) < 0.1:
            self.shake_offset['x'] = 0
        if abs(self.shake_offset['y']) < 0.1:
            self.shake_offset['y'] = 0

    def add_screen_shake(self):
        self.shake_offset = {
            'x': random.uniform(-5, 5),
            'y': random.uniform(-5, 5)
        }

    def draw_target(self, target):
        color = self.target_colors[target['type']]
        GL.glColor3f(*color)
        
        # Draw main target circle
        self.midpoint_circle(target['x'], target['y'], target['radius'])
        
        # Draw inner circles for different target types
        if target['type'] == 'bonus':
            self.midpoint_circle(target['x'], target['y'], target['radius'] * 0.7)
            self.midpoint_circle(target['x'], target['y'], target['radius'] * 0.4)
        elif target['type'] == 'fast':
            # Draw speed indicators
            angle = math.atan2(target['direction'], target['direction'])
            end_x = target['x'] + math.cos(angle) * target['radius'] * 1.5
            end_y = target['y'] + math.sin(angle) * target['radius'] * 1.5
            self.midpoint_line(target['x'], target['y'], end_x, end_y)
    def update_targets(self):
        current_time = time.time()
        
        # Apply wind effect
        self.wind_speed = random.uniform(-0.5, 0.5)  # Random wind speed between -0.5 and 0.5
        self.wind_direction = 1 if self.wind_speed > 0 else -1  # Wind direction
        
        for target in self.targets:
            # Update position with wind effect
            target['x'] += (math.cos(target['direction']) * target['speed'] + 
                           self.wind_speed * 0.5)
            target['y'] += math.sin(target['direction']) * target['speed']
            
            # Bounce off walls
            if target['x'] - target['radius'] < 0:
                target['x'] = target['radius']
                target['direction'] = math.pi - target['direction']
            elif target['x'] + target['radius'] > self.width:
                target['x'] = self.width - target['radius']
                target['direction'] = math.pi - target['direction']
                target['direction'] = math.pi - target['direction']
            if target['y'] - target['radius'] < 0:
                target['y'] = target['radius']
                target['direction'] = -target['direction']
            elif target['y'] + target['radius'] > self.height:
                target['y'] = self.height - target['radius']
                target['direction'] = -target['direction']
            
            # Random direction changes
            if current_time - target.get('last_direction_change', 0) > 2:
                if random.random() < 0.1:
                    target['direction'] += random.uniform(-math.pi/4, math.pi/4)
                    target['last_direction_change'] = current_time
                target['direction'] = -target['direction']
    def draw_powerup(self, powerup):
        if powerup['type'] == 'ammo':
            GL.glColor3f(0.0, 1.0, 0.0)  # Green
        elif powerup['type'] == 'stability':
            GL.glColor3f(0.0, 0.0, 1.0)  # Blue
        elif powerup['type'] == 'zoom':
            GL.glColor3f(1.0, 0.0, 1.0)  # Purple
        else:  # multiplier
            GL.glColor3f(1.0, 1.0, 0.0)  # Yellow

        self.midpoint_circle(powerup['x'], powerup['y'], powerup['radius'])
        self.midpoint_circle(powerup['x'], powerup['y'], powerup['radius'] * 0.6)

    def update(self):
        current_time = time.time()
        if not self.game_over:
            # Update targets
            self.update_targets()
    
            # Update powerups
            for powerup in self.powerups[:]:
                if current_time - powerup['creation_time'] > 10.0:
                    self.powerups.remove(powerup)
    
            # Update reload status
            if not self.can_shoot and current_time - self.last_shot_time >= self.reload_time:
                self.can_shoot = True
    
            # Update combo
            if current_time - self.last_hit_time > self.combo_timeout:
                self.combo = 0
    
            # Update screen shake
            self.update_shake()
    
            # Check for level completion
            if len(self.targets) == 0:
                self.level += 1
                self.spawn_initial_targets()
                self.ammo += 5
    
        elapsed_time = self.calculate_game_play_time()

    def shoot(self, x, y):
        if not self.can_shoot or self.ammo <= 0 or self.game_over:
            return

        current_time = time.time()
        self.ammo -= 1
        self.can_shoot = False
        self.last_shot_time = current_time
        self.add_screen_shake()

        # Check for hits on targets
        hit = False
        for target in self.targets[:]:
            dx = x - target['x']
            dy = y - target['y']
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < target['radius']:
                hit = True
                points = target['points'] * self.points_multiplier * (1 + self.combo * 0.1)
                self.score += int(points)
                self.targets.remove(target)
                self.hits.append({'x': x, 'y': y, 'time': current_time, 'points': int(points)})
                self.combo += 1
                self.last_hit_time = current_time
                self.max_combo = max(self.max_combo, self.combo)
                
                # Achievement checks
                if distance < target['radius'] * 0.2:
                    self.achievements['perfect_shot'] = True
                if self.combo >= 5:
                    self.achievements['combo_master'] = True
                if self.score >= 5000:
                    self.achievements['sharpshooter'] = True
                
                if len(self.targets) == 0:
                    self.spawn_initial_targets()
                break

        # Check for hits on powerups
        for powerup in self.powerups[:]:
            dx = x - powerup['x']
            dy = y - powerup['y']
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < powerup['radius']:
                self.apply_powerup(powerup['type'])
                self.powerups.remove(powerup)
                hit = True
                break

        if not hit:
            self.misses.append({'x': x, 'y': y, 'time': current_time})
            self.combo = 0

        if self.ammo <= 0:
            self.game_over = True

    def draw_hud(self):
        GL.glColor3f(1.0, 1.0, 1.0)
        
        # Draw score
        GL.glRasterPos2f(10, self.height - 20)
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18,
                              f"Score: {self.score}".encode())
        
        # Draw ammo
        GL.glRasterPos2f(10, self.height - 40)
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18,
                              f"Ammo: {self.ammo}".encode())
        
        # Draw level
        GL.glRasterPos2f(10, self.height - 60)
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18,
                              f"Level: {self.level}".encode())
        
        # Draw combo
        if self.combo > 0:
            GL.glRasterPos2f(10, self.height - 80)
            GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18,
                                  f"Combo: x{self.combo}".encode())
        
        # Draw base speed
        GL.glRasterPos2f(10, self.height - 120)
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18,
                            f"Base Speed: {self.base_speed:.2f}".encode())
    
        
        # Draw active powerups
        y_offset = 140
        if self.scope_stability != 1.0:
            GL.glRasterPos2f(10, self.height - y_offset)
            GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18,
                                  b"Stability Boost Active")
            y_offset += 20
        
        if self.points_multiplier != 1.0:
            GL.glRasterPos2f(10, self.height - y_offset)
            GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18,
                                  b"Score Multiplier Active")
            y_offset += 20
        
        # Draw achievements
        if any(self.achievements.values()):
            y_offset = 160
            GL.glColor3f(1.0, 1.0, 0.0)  # Yellow for achievements
            for achievement, unlocked in self.achievements.items():
                if unlocked:
                    GL.glRasterPos2f(self.width - 200, self.height - y_offset)
                    GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18,
                                          f"Achievement: {achievement.replace('_', ' ').title()}".encode())
                    y_offset += 20
        
        # Add game play time display
        elapsed_time = self.calculate_game_play_time()
        minutes, seconds = divmod(elapsed_time, 60)
        hours, minutes = divmod(minutes, 60)
        time_string = f"{int(hours):02d}:{int(minutes):02d}:{seconds:.1f}"
        GL.glRasterPos2f(10, self.height - 140)
        GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18,
                              f"Game Time: {time_string}".encode())

    def display(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glLoadIdentity()
        
        # Apply screen shake
        GL.glTranslatef(self.shake_offset['x'], self.shake_offset['y'], 0)

        # Draw targets
        for target in self.targets:
            self.draw_target(target)

        # Draw powerups
        for powerup in self.powerups:
            self.draw_powerup(powerup)

        # Draw scope with stability effect
        scope_x = self.scope_x + random.uniform(-2, 2) * self.scope_stability
        scope_y = self.scope_y + random.uniform(-2, 2) * self.scope_stability
        self.draw_scope(scope_x, scope_y)
        
        
        # Draw HUD
        self.draw_hud()

        if self.game_over:
            GL.glColor3f(1.0, 0.0, 0.0)
            GL.glRasterPos2f(self.width//2 - 150, self.height//2)
            GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, 
                                 f"Game Over! Final Score: {self.score}".encode())
            GL.glRasterPos2f(self.width//2 - 100, self.height//2 - 30)
            GLUT.glutBitmapString(GLUT.GLUT_BITMAP_HELVETICA_18, 
                                 b"Press R to restart")

        GLUT.glutSwapBuffers()

    # [Previous mouse, keyboard, and reshape methods remain the same]
    # ... [Keep all the previous input handling methods]
    def mouse(self, button, state, x, y):
        if button == GLUT.GLUT_LEFT_BUTTON and state == GLUT.GLUT_DOWN:
            self.shoot(x, self.height - y)

    def keyboard(self, key, x, y):
        if key == b' ':
            self.shoot(self.scope_x, self.scope_y)
        elif key == b'r' and self.game_over:
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
    game = SniperGame()
    
    GLUT.glutInit()
    GLUT.glutInitDisplayMode(GLUT.GLUT_DOUBLE | GLUT.GLUT_RGB)
    GLUT.glutInitWindowSize(game.width, game.height)
    GLUT.glutCreateWindow(b"Advanced Sniper Hunt")
    
    GL.glClearColor(0.1, 0.1, 0.1, 0.0)  # Darker background
    GL.glPointSize(2.0)
    
    GLUT.glutDisplayFunc(game.display)
    GLUT.glutKeyboardFunc(game.keyboard)
    GLUT.glutMouseFunc(game.mouse)
    GLUT.glutPassiveMotionFunc(game.mouse_motion)
    GLUT.glutReshapeFunc(game.reshape)
    
    def update(value):
        game.update()
        GLUT.glutPostRedisplay()
        GLUT.glutTimerFunc(16, update, 0)
    
    GLUT.glutTimerFunc(0, update, 0)
    GLUT.glutMainLoop()

if __name__ == "__main__":
    main()
