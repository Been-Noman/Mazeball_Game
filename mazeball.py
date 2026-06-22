"""
MAZEBALL - Ultimate Edition (2026)
==============================================
Premium Arcade Football Engine
"""

import pygame
import random
import math
import sys

# ─────────────────────────────────────────────
# CONFIGURATION & METRIC MATRIX
# ─────────────────────────────────────────────
TITLE = "MAZEBALL"
COLS = 17  
ROWS = 13  
CELL = 54  

MAZE_W = COLS * CELL
MAZE_H = ROWS * CELL

MAZE_REGEN_SECS = 60
FPS = 60
BALL_RADIUS = 12
WIN_SCORE = 5

# High-Tech Modern Color Palette
C_UI_BG = pygame.Color("#090b0e")        
C_AMB_BORDER = pygame.Color("#1e272e")   
C_PITCH = pygame.Color("#557a2b")        
C_PITCH_LINE = pygame.Color("#ffffff")   
C_BRICK_MAIN = pygame.Color("#7f8c8d")
C_BRICK_DARK = pygame.Color("#4b5354")
C_BRICK_LIGHT = pygame.Color("#bdc3c7")
C_GOALPOST = pygame.Color("#ffffff")

C_TEAM1 = pygame.Color("#ff4757")       
C_TEAM1_GLOW = pygame.Color("#ff6b81")
C_TEAM2 = pygame.Color("#0984e3")       
C_TEAM2_GLOW = pygame.Color("#70a1ff")
C_TEXT_MUTED = pygame.Color("#a4b0be")

# ─────────────────────────────────────────────
# MAZE GENERATION WITH CLEAR GOAL ZONES
# ─────────────────────────────────────────────
def generate_maze(cols, rows, p1_pos=None, p2_pos=None, mx=0, my=0):
    grid = [[True] * cols for _ in range(rows)]
    
    def carve(cx, cy):
        grid[cy][cx] = False
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 < nx < cols - 1 and 0 < ny < rows - 1 and grid[ny][nx]:
                grid[cy + dy // 2][cx + dx // 2] = False
                carve(nx, ny)
    carve(1, 1)
    
    mid_y = rows // 2
    for gy in [mid_y - 1, mid_y, mid_y + 1]:
        grid[gy][0] = False
        grid[gy][cols - 1] = False
        
    for r in range(rows):
        for c in range(cols):
            if c < 2 or c >= (cols - 2):
                grid[r][c] = False
                
    if p1_pos:
        p1c = int((p1_pos[0] - mx) // CELL)
        p1r = int((p1_pos[1] - my) // CELL)
        if 0 <= p1c < cols and 0 <= p1r < rows:
            grid[p1r][p1c] = False
    if p2_pos:
        p2c = int((p2_pos[0] - mx) // CELL)
        p2r = int((p2_pos[1] - my) // CELL)
        if 0 <= p2c < cols and 0 <= p2r < rows:
            grid[p2r][p2c] = False
            
    return grid

# ─────────────────────────────────────────────
# GRAPHICS ENGINE (HUD & SHADING DECK)
# ─────────────────────────────────────────────
def draw_brick_wall(screen, x, y, w, h):
    shrink_size = 4 
    sx, sy = x + shrink_size, y + shrink_size
    sw, sh = w - (shrink_size * 2), h - (shrink_size * 2)

    pygame.draw.rect(screen, C_BRICK_MAIN, (sx, sy, sw, sh))
    pygame.draw.line(screen, C_BRICK_LIGHT, (sx, sy), (sx + sw, sy), 2)
    pygame.draw.line(screen, C_BRICK_DARK, (sx, sy + sh - 2), (sx + sw, sy + sh - 2), 2)
    
    mid_y = sy + sh // 2
    pygame.draw.line(screen, C_BRICK_DARK, (sx, mid_y), (sx + sw, mid_y), 1)
    pygame.draw.line(screen, C_BRICK_LIGHT, (sx, mid_y + 1), (sx + sw, mid_y + 1), 1)

def draw_ambient_fullscreen_decorations(screen, ww, wh, mx, my):
    for step in range(0, ww, 80):
        pygame.draw.line(screen, pygame.Color("#0f141c"), (step, 0), (step - 300, wh), 2)
    
    pygame.draw.rect(screen, pygame.Color("#11161d"), (mx - 60, my - 20, MAZE_W + 120, MAZE_H + 145), 0, 12)
    pygame.draw.rect(screen, pygame.Color("#1b222c"), (mx - 60, my - 20, MAZE_W + 120, MAZE_H + 145), 2, 12)

    b_len = 35
    corners = [
        ((mx - 50, my - 10), (mx - 50 + b_len, my - 10), (mx - 50, my - 10 + b_len)),
        ((mx + MAZE_W + 50, my - 10), (mx + MAZE_W + 50 - b_len, my - 10), (mx + MAZE_W + 50, my - 10 + b_len)),
        ((mx - 50, my + MAZE_H + 110), (mx - 50 + b_len, my + MAZE_H + 110), (mx - 50, my + MAZE_H + 110 - b_len)),
        ((mx + MAZE_W + 50, my + MAZE_H + 110), (mx + MAZE_W + 50 - b_len, my + MAZE_H + 110), (mx + MAZE_W + 50, my + MAZE_H + 110 - b_len))
    ]
    for pt, h_line, v_line in corners:
        pygame.draw.line(screen, pygame.Color("#3a4f66"), pt, h_line, 3)
        pygame.draw.line(screen, pygame.Color("#3a4f66"), pt, v_line, 3)

def draw_pitch(screen, grid, mx, my):
    # Plain field layout with fallback uniform color
    pygame.draw.rect(screen, C_PITCH, (mx, my, MAZE_W, MAZE_H))
    
    # Render warm yellowish-green grass details using a fixed seed to prevent flickering
    random.seed(101)
    for _ in range(400):  
        gx = random.randint(mx, mx + MAZE_W)
        gy = random.randint(my, my + MAZE_H)
        blade_color = random.choice([pygame.Color("#446322"), pygame.Color("#648f34")])
        pygame.draw.line(screen, blade_color, (gx, gy), (gx + random.randint(-1, 1), gy + random.randint(2, 4)), 1)
    random.seed()

    # SYMMETRIC WHITE GOAL BOXES
    mid_r = ROWS // 2
    box_h = CELL * 5  
    box_y = my + (mid_r - 2) * CELL
    
    pygame.draw.rect(screen, C_PITCH_LINE, (mx, box_y, CELL * 2, box_h), 2)
    pygame.draw.rect(screen, C_PITCH_LINE, (mx + MAZE_W - CELL * 2, box_y, CELL * 2, box_h), 2)

    # Render walls over the grass layer
    for r in range(ROWS):
        for c in range(COLS):
            x, y = mx + c * CELL, my + r * CELL
            if grid[r][c]:
                draw_brick_wall(screen, x, y, CELL, CELL)

def draw_net(screen, side, mx, my):
    mid_r = ROWS // 2
    g_top = my + (mid_r - 1) * CELL
    g_bot = my + (mid_r + 2) * CELL
    h = g_bot - g_top
    
    x = mx - CELL if side == 'left' else mx + MAZE_W
    
    pygame.draw.rect(screen, C_PITCH, (x, g_top, CELL, h))
    
    for step in range(0, CELL+1, 6):
        pygame.draw.line(screen, pygame.Color("#7f8c8d"), (x + step, g_top), (x + step, g_bot), 1)
    for step in range(0, h+1, 6):
        pygame.draw.line(screen, pygame.Color("#7f8c8d"), (x, g_top + step), (x + CELL, g_top + step), 1)
        
    pygame.draw.rect(screen, C_GOALPOST, (x, g_top, CELL, h), 3)

def draw_deer_ball(screen, bx, by, angle):
    r = BALL_RADIUS
    shadow = pygame.Surface((r * 3, r * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, r * 3, r * 2))
    screen.blit(shadow, (bx - r * 1.5, by - r * 0.3))

    pygame.draw.circle(screen, pygame.Color("#f1f2f6"), (int(bx), int(by)), r)
    pygame.draw.circle(screen, pygame.Color("#2f3542"), (int(bx), int(by)), r, 2)
    
    center_color = pygame.Color("#2f3542")
    c_rad = math.radians(angle)
    c_x = int(bx + (r * 0.15) * math.cos(c_rad))
    c_y = int(by + (r * 0.15) * math.sin(c_rad))
    pygame.draw.circle(screen, center_color, (c_x, c_y), int(r * 0.3))
    
    for i in range(5):
        a = math.radians(angle + i * 72)
        px = int(bx + (r * 0.65) * math.cos(a))
        py = int(by + (r * 0.65) * math.sin(a))
        pygame.draw.line(screen, center_color, (c_x, c_y), (px, py), 2)
        if math.hypot(px - bx, py - by) < r - 1:
            pygame.draw.circle(screen, center_color, (px, py), int(r * 0.22))

def draw_robot(screen, px, py, team, look_dir):
    color = C_TEAM1 if team == 1 else C_TEAM2
    glow = C_TEAM1_GLOW if team == 1 else C_TEAM2_GLOW
    x, y = int(px), int(py)
    
    pygame.draw.ellipse(screen, (16, 20, 25), (x - 19, y + 9, 38, 10))
    pygame.draw.rect(screen, pygame.Color("#1e272e"), (x - 21, y - 13, 6, 26), 0, 3)
    pygame.draw.rect(screen, pygame.Color("#1e272e"), (x + 15, y - 13, 6, 26), 0, 3)
    
    pygame.draw.rect(screen, color, (x - 15, y - 17, 30, 30), 0, 5)
    pygame.draw.rect(screen, pygame.Color("#1e272e"), (x - 15, y - 17, 30, 30), 2, 5)
    
    pygame.draw.circle(screen, glow, (x, y - 2), 7)
    pygame.draw.circle(screen, pygame.Color("#ffffff"), (x, y - 2), 3)
    
    hx, hy = x + look_dir[0] * 5, y - 19 + look_dir[1] * 2
    pygame.draw.circle(screen, pygame.Color("#dcdde1"), (int(hx), int(hy)), 11)
    pygame.draw.circle(screen, pygame.Color("#1e272e"), (int(hx), int(hy)), 11, 1)
    
    vx, vy = hx + look_dir[0] * 5, hy + look_dir[1] * 2
    pygame.draw.ellipse(screen, pygame.Color("#2f3542"), (int(vx - 5), int(vy - 3), 11, 6))
    pygame.draw.circle(screen, glow, (int(vx), int(vy)), 2)

# ─────────────────────────────────────────────
# PHYSICAL ENGINE MATRIX
# ─────────────────────────────────────────────
def is_pixel_inside_wall(grid, x, y, mx, my):
    if x < mx or x >= mx + MAZE_W or y < my or y >= my + MAZE_H:
        mid_r = ROWS // 2
        if (my + (mid_r - 1) * CELL) < y < (my + (mid_r + 2) * CELL):
            if (mx - CELL <= x <= mx) or (mx + MAZE_W <= x <= mx + MAZE_W + CELL):
                return False
        return True
    c = int((x - mx) // CELL)
    r = int((y - my) // CELL)
    return grid[r][c]

def solve_ball_wall_collision(grid, bx, by, r, mx, my):
    bc = int((bx - mx) // CELL)
    br = int((by - my) // CELL)
    
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = br + dr, bc + dc
            if 0 <= nc < COLS and 0 <= nr < ROWS and grid[nr][nc]:
                w_left = mx + nc * CELL
                w_top = my + nr * CELL
                
                cx = max(w_left, min(bx, w_left + CELL))
                cy = max(w_top, min(by, w_top + CELL))
                
                dist_x = bx - cx
                dist_y = by - cy
                dist = math.hypot(dist_x, dist_y)
                
                if dist < r and dist > 0:
                    overlap = r - dist
                    bx += (dist_x / dist) * overlap
                    by += (dist_y / dist) * overlap
    return bx, by

def advance_simulation_step(state, dt, mx, my):
    s = state
    s.bvx *= 0.972  
    s.bvy *= 0.972
    
    speed = math.hypot(s.bvx, s.bvy)
    sub_steps = int(max(1, speed // 1.5)) 
    
    for _ in range(sub_steps):
        next_x = s.bx + (s.bvx * dt / sub_steps)
        next_y = s.by + (s.bvy * dt / sub_steps)
        
        if is_pixel_inside_wall(s.grid, next_x + (BALL_RADIUS if s.bvx > 0 else -BALL_RADIUS), s.by, mx, my):
            s.bvx *= -0.75  
        else:
            s.bx = next_x
            
        if is_pixel_inside_wall(s.grid, s.bx, next_y + (BALL_RADIUS if s.bvy > 0 else -BALL_RADIUS), mx, my):
            s.bvy *= -0.75
        else:
            s.by = next_y
            
        s.bx, s.by = solve_ball_wall_collision(s.grid, s.bx, s.by, BALL_RADIUS, mx, my)
        s.spin_angle += s.bvx * 0.15

# ─────────────────────────────────────────────
# CONTROL STATE CONTROLLER
# ─────────────────────────────────────────────
class GameState:
    def __init__(self, mx, my):
        self.score = [0, 0]
        self.game_over = False
        self.winner = None
        self.spin_angle = 0
        self.grid = generate_maze(COLS, ROWS, None, None, mx, my)
        self.maze_timer = MAZE_REGEN_SECS
        
        mid_r = ROWS // 2
        self.p1x = mx + 1 * CELL + CELL // 2
        self.p1y = my + mid_r * CELL + CELL // 2
        self.p1_look = (1.0, 0.0)
        
        self.p2x = mx + (COLS - 2) * CELL + CELL // 2
        self.p2y = my + mid_r * CELL + CELL // 2
        self.p2_look = (-1.0, 0.0)
        
        self.spawn_ball(mx, my)

    def morph_maze_layout(self, mx, my):
        self.grid = generate_maze(COLS, ROWS, (self.p1x, self.p1y), (self.p2x, self.p2y), mx, my)
        self.maze_timer = MAZE_REGEN_SECS

    def spawn_ball(self, mx, my):
        mid_c, mid_r = COLS // 2, ROWS // 2
        self.grid[mid_r][mid_c] = False
        self.bx, self.by = mx + mid_c * CELL + CELL // 2, my + mid_r * CELL + CELL // 2
        self.bvx, self.bvy = random.choice([-3.5, 3.5]), random.choice([-2.5, 2.5])

class MazeBallGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.ww, self.wh = self.screen.get_size()
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Segoe UI, Arial", 13, bold=True)
        self.font_hud = pygame.font.SysFont("Impact, Arial", 32, bold=False)
        self.font_msg = pygame.font.SysFont("Segoe UI, Arial", 21, bold=True)
        
        self.mx = (self.ww - MAZE_W) // 2
        self.my = (self.wh - MAZE_H) // 2 + 15
        
        self.state = GameState(self.mx, self.my)

    def process_inputs(self):
        s = self.state
        keys = pygame.key.get_pressed()
        speed = 5.8  
        
        # Player 1 (WASD)
        dx1, dy1 = 0, 0
        if keys[pygame.K_w]: dy1 -= speed
        if keys[pygame.K_s]: dy1 += speed
        if keys[pygame.K_a]: dx1 -= speed
        if keys[pygame.K_d]: dx1 += speed
        if dx1 != 0 or dy1 != 0:
            nx, ny = s.p1x + dx1, s.p1y + dy1
            if not is_pixel_inside_wall(s.grid, nx, ny, self.mx, self.my):
                s.p1x, s.p1y = nx, ny
                mag = math.hypot(dx1, dy1)
                s.p1_look = (dx1/mag, dy1/mag)

        # Player 2 (Arrows)
        dx2, dy2 = 0, 0
        if keys[pygame.K_UP]: dy2 -= speed
        if keys[pygame.K_DOWN]: dy2 += speed
        if keys[pygame.K_LEFT]: dx2 -= speed
        if keys[pygame.K_RIGHT]: dx2 += speed
        if dx2 != 0 or dy2 != 0:
            nx, ny = s.p2x + dx2, s.p2y + dy2
            if not is_pixel_inside_wall(s.grid, nx, ny, self.mx, self.my):
                s.p2x, s.p2y = nx, ny
                mag = math.hypot(dx2, dy2)
                s.p2_look = (dx2/mag, dy2/mag)

    def verify_tactile_kicks(self):
        s = self.state
        for px, py in [(s.p1x, s.p1y), (s.p2x, s.p2y)]:
            dist = math.hypot(s.bx - px, s.by - py)
            if dist < 29:
                s.bvx = (s.bx - px) * 0.36
                s.bvy = (s.by - py) * 0.36

    def run_loop(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            if dt > 0.05: dt = 0.016
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: 
                        running = False
                    if event.key == pygame.K_r and self.state.game_over:
                        self.state = GameState(self.mx, self.my)

            if not self.state.game_over:
                self.state.maze_timer -= dt
                if self.state.maze_timer <= 0: 
                    self.state.morph_maze_layout(self.mx, self.my)
                
                self.process_inputs()
                advance_simulation_step(self.state, dt * 60, self.mx, self.my)
                self.verify_tactile_kicks()
                
                if self.state.bx < self.mx - 10:
                    self.state.score[1] += 1
                    if self.state.score[1] >= WIN_SCORE:
                        self.state.game_over, self.state.winner = True, 2
                    else: self.state.spawn_ball(self.mx, self.my)
                elif self.state.bx > self.mx + MAZE_W + 10:
                    self.state.score[0] += 1
                    if self.state.score[0] >= WIN_SCORE:
                        self.state.game_over, self.state.winner = True, 1
                    else: self.state.spawn_ball(self.mx, self.my)

            self.screen.fill(C_UI_BG)
            draw_ambient_fullscreen_decorations(self.screen, self.ww, self.wh, self.mx, self.my)
            
            draw_pitch(self.screen, self.state.grid, self.mx, self.my)
            draw_net(self.screen, 'left', self.mx, self.my)
            draw_net(self.screen, 'right', self.mx, self.my)
            
            draw_deer_ball(self.screen, self.state.bx, self.state.by, self.state.spin_angle)
            draw_robot(self.screen, self.state.p1x, self.state.p1y, 1, self.state.p1_look)
            draw_robot(self.screen, self.state.p2x, self.state.p2y, 2, self.state.p2_look)
            
            self.draw_cyber_hud()
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

    def draw_keycap(self, char, x, y):
        pygame.draw.rect(self.screen, pygame.Color("#1e272e"), (x, y, 22, 22), 0, 4)
        pygame.draw.rect(self.screen, pygame.Color("#485460"), (x, y, 22, 22), 1, 4)
        txt = self.font.render(char, True, pygame.Color("#d2d2d2"))
        self.screen.blit(txt, txt.get_rect(center=(x+11, y+11)))

    def draw_cyber_hud(self):
        # ─────────────────────────────────────────────
        # TOP SCOREBOARD
        # ─────────────────────────────────────────────
        hud_w, hud_h = 680, 56
        hud_x = (self.ww - hud_w) // 2
        hud_y = 12
        
        hud_surf = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        hud_surf.fill((12, 17, 24, 240))
        self.screen.blit(hud_surf, (hud_x, hud_y))
        pygame.draw.rect(self.screen, pygame.Color("#2c3e50"), (hud_x, hud_y, hud_w, hud_h), 1, 6)
        
        pygame.draw.rect(self.screen, C_TEAM1, (hud_x + 160, hud_y + 8, 50, 40), 2, 4)
        pygame.draw.rect(self.screen, C_TEAM2, (hud_x + hud_w - 210, hud_y + 8, 50, 40), 2, 4)
        
        scr1 = self.font_hud.render(f"{self.state.score[0]}", True, pygame.Color("#ffffff"))
        scr2 = self.font_hud.render(f"{self.state.score[1]}", True, pygame.Color("#ffffff"))
        self.screen.blit(scr1, scr1.get_rect(center=(hud_x + 185, hud_y + 28)))
        self.screen.blit(scr2, scr2.get_rect(center=(hud_x + hud_w - 185, hud_y + 28)))
        
        lbl1 = self.font_msg.render("RED TEAM", True, C_TEAM1)
        lbl2 = self.font_msg.render("BLUE TEAM", True, C_TEAM2)
        self.screen.blit(lbl1, (hud_x + 25, hud_y + 14))
        self.screen.blit(lbl2, (hud_x + hud_w - 135, hud_y + 14))
        
        clk_str = f"00:{int(max(0, self.state.maze_timer)):02d}"
        clk_color = pygame.Color("#eccc68") if self.state.maze_timer > 10 else pygame.Color("#ff4757")
        clk_lbl = self.font_hud.render(clk_str, True, clk_color)
        self.screen.blit(clk_lbl, clk_lbl.get_rect(center=(hud_x + hud_w//2, hud_y + 26)))
        
        # ─────────────────────────────────────────────
        # BOTTOM CONTROLS PANEL
        # ─────────────────────────────────────────────
        panel_y = self.my + MAZE_H + 15
        pygame.draw.rect(self.screen, pygame.Color("#0f1319"), (self.mx, panel_y, MAZE_W, 105), 0, 8)
        pygame.draw.rect(self.screen, pygame.Color("#23272a"), (self.mx, panel_y, MAZE_W, 105), 1, 8)
        
        red_box_x = self.mx + 25
        lbl_red = self.font.render("RED CONTROL", True, C_TEAM1)
        self.screen.blit(lbl_red, lbl_red.get_rect(center=(red_box_x + 40, panel_y + 20)))
        
        self.draw_keycap("W", red_box_x + 28, panel_y + 40)
        self.draw_keycap("A", red_box_x + 3, panel_y + 66)
        self.draw_keycap("S", red_box_x + 28, panel_y + 66)
        self.draw_keycap("D", red_box_x + 53, panel_y + 66)
        
        lbl_dir = self.font.render("STADIUM DIRECTIVES", True, pygame.Color("#ffffff"))
        self.screen.blit(lbl_dir, lbl_dir.get_rect(center=(self.ww // 2, panel_y + 20)))
        
        m1 = self.font.render("• Shoot the ball towards the opposing goalpost to score points.", True, C_TEXT_MUTED)
        m2 = self.font.render("• The maze layout changes structural shape dynamically every 60 seconds.", True, C_TEXT_MUTED)
        self.screen.blit(m1, m1.get_rect(center=(self.ww // 2, panel_y + 48)))
        self.screen.blit(m2, m2.get_rect(center=(self.ww // 2, panel_y + 72)))
        
        blue_box_x = self.mx + MAZE_W - 130
        lbl_blue = self.font.render("BLUE CONTROL", True, C_TEAM2)
        self.screen.blit(lbl_blue, lbl_blue.get_rect(center=(blue_box_x + 40, panel_y + 20)))
        
        self.draw_keycap("^", blue_box_x + 28, panel_y + 40)
        self.draw_keycap("<", blue_box_x + 3, panel_y + 66)
        self.draw_keycap("v", blue_box_x + 28, panel_y + 66)
        self.draw_keycap(">", blue_box_x + 53, panel_y + 66)

        esc_lbl = self.font.render("ESC: Exit Stadium Matrix", True, pygame.Color("#57606f"))
        self.screen.blit(esc_lbl, (15, 15))

        if self.state.game_over:
            overlay = pygame.Surface((self.ww, self.wh), pygame.SRCALPHA)
            overlay.fill((5, 8, 12, 230))
            self.screen.blit(overlay, (0, 0))
            
            w_color = C_TEAM1 if self.state.winner == 1 else C_TEAM2
            w_name = "RED TEAM" if self.state.winner == 1 else "BLUE TEAM"
            
            win_str = f"=== {w_name} HAS CONQUERED THE MAZE! ==="
            win_lbl = self.font_hud.render(win_str, True, w_color)
            rst_lbl = self.font_msg.render("Press 'R' to Deploy Next Match Matrix Simulation", True, pygame.Color("#ffffff"))
            
            self.screen.blit(win_lbl, win_lbl.get_rect(center=(self.ww//2, self.wh//2 - 20)))
            self.screen.blit(rst_lbl, rst_lbl.get_rect(center=(self.ww//2, self.wh//2 + 30)))

if __name__ == "__main__":
    game = MazeBallGame()
    game.run_loop()