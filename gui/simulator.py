import pygame
import pygame.gfxdraw
import random
import time
import math

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = 255
        self.color = color
        self.size = random.uniform(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 15
        self.size *= 0.9

    def draw(self, surface, offset_x, offset_y):
        if self.life > 0:
            alpha = max(0, min(255, int(self.life)))
            color = (*self.color[:3], alpha)
            s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x + offset_x - self.size), int(self.y + offset_y - self.size)))

class TargetSimulator:
    def __init__(self, audio_manager=None, user_name="Anon", screen_w=1024, screen_h=768):
        self.width = screen_w
        self.height = screen_h
        
        # Ocultar cursor del sistema para dibujar nuestra propia mira
        pygame.mouse.set_visible(False)
        
        self.clock = pygame.time.Clock()
        self.running = False
        self.start_time = time.time()
        self.audio = audio_manager
        self.user_name = user_name
        
        # Paleta de colores Táctica / Cyberpunk
        self.BG_COLOR = (8, 12, 16)
        self.GRID_COLOR = (20, 35, 45)
        self.CYAN = (0, 255, 255)
        self.GREEN_GLOW = (50, 255, 100)
        self.RED_GLOW = (255, 50, 80)
        self.ORANGE = (255, 150, 0)
        self.DARK_PANEL = (10, 15, 20, 220)
        
        # Tipografías (HUD Táctico)
        pygame.font.init()
        try:
            self.font_title = pygame.font.SysFont('consolas', 48, bold=True)
            self.font_large = pygame.font.SysFont('consolas', 26) 
            self.font_normal = pygame.font.SysFont('consolas', 16)
            self.font_small = pygame.font.SysFont('consolas', 12)
        except:
            self.font_title = pygame.font.SysFont('couriernew', 48, bold=True)
            self.font_large = pygame.font.SysFont('couriernew', 26)
            self.font_normal = pygame.font.SysFont('couriernew', 16)
            self.font_small = pygame.font.SysFont('couriernew', 12)
            
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.target_radius = 200
        
        self.holes = [] 
        self.particles = []
        self.screen_shake = 0
        self.glitch_offset = 0
        self.floating_texts = []
        
        self.total_shots = 0
        self.hits = 0
        self.misses = 0
        
        # Nuevas métricas
        self.last_shot_time = 0.0
        self.reaction_time = 0.0
        
        self.radar_angle = 0.0
        
        # Movimiento de la diana
        self.moving_target = False
        self.target_offset_x = 0.0
        self.target_offset_y = 0.0
        self.target_vx = random.choice([-3, -2, 2, 3])
        self.target_vy = random.choice([-3, -2, 2, 3])

    def draw_tactical_background(self):
        self.screen.fill(self.BG_COLOR)
        
        offset = (time.time() * 10) % 50
        for x in range(int(offset) - 50, self.width, 50):
            pygame.draw.line(self.screen, self.GRID_COLOR, (x, 0), (x, self.height), 1)
        for y in range(int(offset) - 50, self.height, 50):
            pygame.draw.line(self.screen, self.GRID_COLOR, (0, y), (self.width, y), 1)

        t = time.time() - self.start_time
        fps = self.clock.get_fps()
        
        telemetry = [
            f"Frec. Actualización : {fps:.1f} FPS",
            f"T. Reacción (Último): {self.reaction_time:.3f} s",
            f"Tiempo Actividad    : {t:.1f} s",
            f"Memoria Asignada    : {random.randint(1024, 2048)} MB",
            f"Latencia de Red     : {random.randint(12, 45)} ms",
            "Conexión Gateway    : E/S Activa",
            "Modo Apuntado       : Sensor Manual (Placeholder)"
        ]
        for i, text in enumerate(telemetry):
            surf = self.font_small.render(text, True, (0, 150, 150))
            self.screen.blit(surf, (20, self.height - 150 + (i * 18)))

    def draw_radar_sweep(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        p1 = (self.center_x, self.center_y)
        p2 = (self.center_x + math.cos(self.radar_angle) * 1500, 
              self.center_y + math.sin(self.radar_angle) * 1500)
        p3 = (self.center_x + math.cos(self.radar_angle - 0.5) * 1500, 
              self.center_y + math.sin(self.radar_angle - 0.5) * 1500)
        
        pygame.draw.polygon(surf, (0, 255, 255, 15), [p1, p2, p3])
        pygame.draw.line(surf, (0, 255, 255, 100), p1, p2, 2)
        
        self.screen.blit(surf, (0, 0))
        self.radar_angle += 0.03

    def draw_target(self, offset_x, offset_y):
        x = self.center_x + offset_x
        y = self.center_y + offset_y
        
        rings = [
            (self.target_radius, (30, 60, 80), "10"),
            (self.target_radius * 0.75, (40, 80, 100), "25"),
            (self.target_radius * 0.5, (0, 150, 200), "50"),
            (self.target_radius * 0.25, (0, 255, 255), "100"),
            (self.target_radius * 0.05, (255, 50, 50), "X")
        ]
        
        pygame.gfxdraw.filled_circle(self.screen, x, y, int(self.target_radius), (5, 8, 12, 200))
        
        for r, color, score in rings:
            radius = int(r)
            if radius <= 0: continue
            pygame.gfxdraw.aacircle(self.screen, x, y, radius, color)
            
            for angle in range(0, 360, 45):
                rad = math.radians(angle + (time.time() * 10))
                start_pos = (x + math.cos(rad) * (radius - 5), y + math.sin(rad) * (radius - 5))
                end_pos = (x + math.cos(rad) * (radius + 5), y + math.sin(rad) * (radius + 5))
                pygame.draw.line(self.screen, color, start_pos, end_pos, 2)
                
            if radius > 20:
                score_surf = self.font_small.render(score, True, color)
                self.screen.blit(score_surf, (x - score_surf.get_width()//2, y - radius + 5))

        cross_color = (0, 255, 255, 100)
        pygame.draw.line(self.screen, cross_color, (x, y - self.target_radius - 20), (x, y + self.target_radius + 20), 1)
        pygame.draw.line(self.screen, cross_color, (x - self.target_radius - 20, y), (x + self.target_radius + 20, y), 1)
        pygame.draw.circle(self.screen, self.RED_GLOW, (x, y), max(1, int(self.target_radius * 0.05)), 1)

    def draw_bullet_holes_and_particles(self, offset_x, offset_y):
        current_time = time.time()
        
        for hole in self.holes:
            hx, hy, is_hit, timestamp, relative_radius, angle = hole
            
            # Recalcular la posicion basada en el radio actual para que se adapte al tamaño de ventana
            current_hx = self.center_x + math.cos(angle) * (relative_radius * self.target_radius) + offset_x
            current_hy = self.center_y + math.sin(angle) * (relative_radius * self.target_radius) + offset_y
            
            age = current_time - timestamp
            
            pygame.draw.circle(self.screen, (10, 10, 10), (int(current_hx), int(current_hy)), 12)
            pygame.draw.circle(self.screen, (0, 0, 0), (int(current_hx), int(current_hy)), 7)
            pygame.draw.circle(self.screen, (40, 40, 40), (int(current_hx), int(current_hy)), 14, 2)
            
            glow_radius = max(0, 15 - age * 5)
            if glow_radius > 0:
                surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                color = self.ORANGE if is_hit else self.RED_GLOW
                pygame.draw.circle(surf, (*color[:3], 150), (15, 15), int(glow_radius))
                self.screen.blit(surf, (int(current_hx)-15, int(current_hy)-15))

        alive_particles = []
        for p in self.particles:
            p.update()
            p.draw(self.screen, offset_x, offset_y)
            if p.life > 0:
                alive_particles.append(p)
        self.particles = alive_particles

    def draw_ui(self):
        panel_rect = pygame.Rect(20, 20, 500, 140)
        
        surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.DARK_PANEL, surf.get_rect(), border_radius=8)
        pygame.draw.rect(surf, (0, 255, 255, 150), surf.get_rect(), width=1, border_radius=8)
        
        pygame.draw.line(surf, self.CYAN, (0, 10), (0, 20), 3)
        pygame.draw.line(surf, self.CYAN, (10, 0), (20, 0), 3)
        
        self.screen.blit(surf, panel_rect)
        
        title = self.font_large.render(f"SISTEMA: {self.user_name.upper()}", True, self.CYAN)
        self.screen.blit(title, (35, 30))
        
        pygame.draw.line(self.screen, (0, 100, 100), (35, 65), (480, 65), 1)
        
        stats = [
            (f"Total Disparos       : {self.total_shots:03d}", (200, 200, 200)),
            (f"Aciertos Confirmados : {self.hits:03d}", self.GREEN_GLOW),
            (f"Fallos Registrados   : {self.misses:03d}", self.RED_GLOW)
        ]
        
        for i, (text, color) in enumerate(stats):
            s = self.font_normal.render(text, True, color)
            self.screen.blit(s, (35, 75 + (i * 20)))
            
        if self.total_shots > 0:
            acc = (self.hits / self.total_shots) * 100
            acc_surface = self.font_title.render(f"{acc:04.1f}%", True, self.CYAN)
            self.screen.blit(acc_surface, (330, 75))
            lbl_surface = self.font_small.render("Nivel Precisión", True, (0, 150, 150))
            self.screen.blit(lbl_surface, (330, 125))

        inst_bg = pygame.Surface((600, 60), pygame.SRCALPHA)
        pygame.draw.rect(inst_bg, self.DARK_PANEL, inst_bg.get_rect(), border_radius=5)
        pygame.draw.rect(inst_bg, (0, 100, 100, 100), inst_bg.get_rect(), width=1, border_radius=5)
        self.screen.blit(inst_bg, (self.width // 2 - 300, self.height - 100))
        
        inst_text = self.font_normal.render("[ ESPACIO : Disparar ]   [ M : Diana Móvil ]   [ C : Limpiar ]", True, self.CYAN)
        if int(time.time() * 2) % 2 == 0:
            self.screen.blit(inst_text, (self.width // 2 - inst_text.get_width() // 2, self.height - 80))

    def update_and_draw_floating_text(self):
        new_texts = []
        for text, color, x, y, alpha, life in self.floating_texts:
            if life > 0:
                surface = self.font_large.render(text, True, color)
                surface.set_alpha(int(alpha))
                glitch_x = x + random.randint(-2, 2)
                self.screen.blit(surface, (glitch_x - surface.get_width()//2, y))
                new_texts.append((text, color, x, y - 2, alpha * 0.9, life - 1))
        self.floating_texts = new_texts

    def register_shot(self, mouse_x, mouse_y):
        self.total_shots += 1
        if self.audio: self.audio.play_shoot()
        
        # Calcular tiempo de reacción (tiempo desde el último disparo)
        current_time = time.time()
        if self.last_shot_time > 0:
            self.reaction_time = current_time - self.last_shot_time
        else:
            self.reaction_time = current_time - self.start_time
        self.last_shot_time = current_time
        
        # Calcular distancia al centro (Pitágoras)
        dx = mouse_x - self.center_x
        dy = mouse_y - self.center_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Determinar acierto real
        is_hit = distance <= self.target_radius
        
        angle = math.atan2(dy, dx)
        relative_radius = distance / self.target_radius
        
        if is_hit:
            self.hits += 1
            result = "acierto"
            color = self.GREEN_GLOW
            self.floating_texts.append(("¡ IMPACTO !", color, mouse_x, mouse_y - 50, 255, 40))
            if self.audio: self.audio.play_hit()
        else:
            self.misses += 1
            result = "fallo"
            color = self.RED_GLOW
            self.floating_texts.append(("FALLO", color, mouse_x, mouse_y - 50, 255, 40))
            if self.audio: self.audio.play_miss()
            
        self.holes.append((0, 0, is_hit, time.time(), relative_radius, angle))
        
        for _ in range(15):
            self.particles.append(Particle(mouse_x, mouse_y, self.ORANGE if is_hit else (100, 100, 100)))
        
        self.screen_shake = 20
        self.glitch_offset = 10
        
        return {
            "result": "hit" if is_hit else "miss",
            "x": mouse_x,
            "y": mouse_y
        }

    def draw_glitch_overlay(self):
        if self.glitch_offset > 0:
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            surf.fill((255, 0, 0, 10))
            self.screen.blit(surf, (self.glitch_offset, 0), special_flags=pygame.BLEND_RGBA_ADD)
            surf.fill((0, 255, 255, 10))
            self.screen.blit(surf, (-self.glitch_offset, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.glitch_offset -= 2

    def draw_crosshair(self):
        mx, my = pygame.mouse.get_pos()
        cross_color = (255, 50, 50, 200)
        # Dibujar mira (retícula)
        pygame.draw.circle(self.screen, cross_color, (mx, my), 15, 1)
        pygame.draw.circle(self.screen, cross_color, (mx, my), 2)
        pygame.draw.line(self.screen, cross_color, (mx - 25, my), (mx - 5, my), 2)
        pygame.draw.line(self.screen, cross_color, (mx + 5, my), (mx + 25, my), 2)
        pygame.draw.line(self.screen, cross_color, (mx, my - 25), (mx, my - 5), 2)
        pygame.draw.line(self.screen, cross_color, (mx, my + 5), (mx, my + 25), 2)

    def render_frame(self):
        # Limitar FPS
        self.clock.tick(60)
        
        # Movimiento de la diana
        if self.moving_target:
            self.target_offset_x += self.target_vx
            self.target_offset_y += self.target_vy
            # Rebote en los bordes
            if abs(self.target_offset_x) > self.width // 3:
                self.target_vx *= -1
            if abs(self.target_offset_y) > self.height // 3:
                self.target_vy *= -1
        
        self.center_x = (self.width // 2) + int(self.target_offset_x)
        self.center_y = (self.height // 2) + int(self.target_offset_y)
        
        # Escalar diana para que NUNCA toque la UI
        # UI ocupa 170px arriba y unos 130px abajo. Dejamos un margen.
        max_radius = min(self.width // 2 - 40, self.height // 2 - 170)
        self.target_radius = max(50, max_radius)

        offset_x = random.randint(-int(self.screen_shake), int(self.screen_shake)) if self.screen_shake > 0 else 0
        offset_y = random.randint(-int(self.screen_shake), int(self.screen_shake)) if self.screen_shake > 0 else 0
        if self.screen_shake > 0:
            self.screen_shake *= 0.8
            if self.screen_shake < 1: self.screen_shake = 0

        self.draw_tactical_background()
        self.draw_radar_sweep()
        self.draw_target(offset_x, offset_y)
        self.draw_bullet_holes_and_particles(offset_x, offset_y)
        self.draw_ui()
        self.update_and_draw_floating_text()
        self.draw_glitch_overlay()
        self.draw_crosshair()
        
        pygame.display.flip()

    def handle_events(self):
        pass
