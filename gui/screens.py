import pygame
import time
import math

class ProfileScreen:
    def __init__(self, screen_w, screen_h):
        # We'll use dynamic width/height from the surface instead
        try:
            self.font_title = pygame.font.SysFont('consolas', 52, bold=True)
            self.font_large = pygame.font.SysFont('consolas', 36, bold=True)
            self.font_small = pygame.font.SysFont('consolas', 20)
        except:
            self.font_title = pygame.font.SysFont('couriernew', 52, bold=True)
            self.font_large = pygame.font.SysFont('couriernew', 36, bold=True)
            self.font_small = pygame.font.SysFont('couriernew', 20)
            
        self.input_text = ""
        self.active = True
        self.start_time = time.time()
        self.cursor_visible = True
        self.last_cursor_toggle = time.time()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if len(self.input_text.strip()) > 0:
                    self.active = False
            elif event.key == pygame.K_ESCAPE:
                self.input_text = ""
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.unicode.isalnum() or event.unicode in (' ', '_', '-'):
                if len(self.input_text) < 15:
                    self.input_text += event.unicode

    def render(self, surface):
        w, h = surface.get_width(), surface.get_height()
        surface.fill((8, 12, 16))
        
        # Draw tactical grid
        offset = (time.time() * 10) % 50
        for x in range(int(offset) - 50, w, 50):
            pygame.draw.line(surface, (20, 35, 45), (x, 0), (x, h), 1)
        for y in range(int(offset) - 50, h, 50):
            pygame.draw.line(surface, (20, 35, 45), (0, y), (w, y), 1)

        # Title
        title_text = "SISTEMA DE IDENTIFICACIÓN"
        title = self.font_title.render(title_text, True, (0, 255, 255))
        surface.blit(title, (w//2 - title.get_width()//2, h//2 - 150))
        
        # Subtitle
        prompt = self.font_small.render("> INGRESAR CREDENCIAL DE OPERADOR:", True, (0, 150, 150))
        surface.blit(prompt, (w//2 - prompt.get_width()//2, h//2 - 60))
        
        # Input Box Background
        box_w, box_h = 500, 70
        box_x, box_y = w//2 - box_w//2, h//2 - 10
        pygame.draw.rect(surface, (10, 15, 20, 220), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surface, (0, 255, 255), (box_x, box_y, box_w, box_h), 2)
        
        # Draw corner accents
        cl = 15
        pygame.draw.line(surface, (255, 255, 255), (box_x, box_y), (box_x+cl, box_y), 3)
        pygame.draw.line(surface, (255, 255, 255), (box_x, box_y), (box_x, box_y+cl), 3)
        pygame.draw.line(surface, (255, 255, 255), (box_x+box_w-cl, box_y+box_h), (box_x+box_w, box_y+box_h), 3)
        pygame.draw.line(surface, (255, 255, 255), (box_x+box_w, box_y+box_h-cl), (box_x+box_w, box_y+box_h), 3)

        # Render Input Text
        display_text = self.input_text
        if time.time() - self.last_cursor_toggle > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = time.time()
            
        if self.cursor_visible:
            display_text += "_"
            
        txt_surf = self.font_large.render(display_text, True, (255, 255, 255))
        surface.blit(txt_surf, (box_x + 20, box_y + 15))
        
        # Instructions
        inst = self.font_small.render("[ ENTER: Confirmar ]   [ ESC: Saltar e ir Anónimo ]", True, (0, 100, 100))
        surface.blit(inst, (w//2 - inst.get_width()//2, box_y + box_h + 30))


class CalibrationScreen:
    def __init__(self, screen_w, screen_h):
        try:
            self.font_large = pygame.font.SysFont("consolas", 40, bold=True)
            self.font_small = pygame.font.SysFont("consolas", 20)
        except:
            self.font_large = pygame.font.SysFont("couriernew", 40, bold=True)
            self.font_small = pygame.font.SysFont("couriernew", 20)
            
        self.step = 0 
        self.active = True
        self.points = []
        self.start_time = time.time()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.points.append(event.pos)
            self.step += 1
            if self.step >= 2:
                self.active = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # Opción de saltar calibración usando espacio
            w, h = pygame.display.get_surface().get_size()
            self.points = [(0,0), (w, h)]
            self.active = False

    def render(self, surface):
        w, h = surface.get_width(), surface.get_height()
        surface.fill((8, 12, 16))
        
        # Scanner effect
        scan_y = int(((time.time() - self.start_time) * 300) % h)
        pygame.draw.line(surface, (0, 255, 0, 50), (0, scan_y), (w, scan_y), 2)
        
        # Draw tactical grid
        offset = (time.time() * 5) % 50
        for x in range(int(offset) - 50, w, 50):
            pygame.draw.line(surface, (20, 35, 45), (x, 0), (x, h), 1)
        for y in range(int(offset) - 50, h, 50):
            pygame.draw.line(surface, (20, 35, 45), (0, y), (w, y), 1)
        
        # Draw tactical targets on corners based on step
        target_color = (255, 50, 50)
        
        if self.step == 0:
            msg = "> ALINEANDO HARDWARE: DISPARE A LA ESQUINA SUPERIOR IZQUIERDA"
            tx, ty = 40, 40
        elif self.step == 1:
            msg = "> ALINEANDO HARDWARE: DISPARE A LA ESQUINA INFERIOR DERECHA"
            tx, ty = w - 40, h - 40
        else:
            msg = "> CALIBRACIÓN COMPLETADA. INICIANDO SECUENCIA..."
            tx, ty = -100, -100
            
        if self.step < 2:
            # Draw crosshair target
            pygame.draw.circle(surface, target_color, (tx, ty), 20, 2)
            pygame.draw.circle(surface, target_color, (tx, ty), 4)
            pygame.draw.line(surface, target_color, (tx-30, ty), (tx+30, ty), 2)
            pygame.draw.line(surface, target_color, (tx, ty-30), (tx, ty+30), 2)
            # Pulsing effect
            pulse_rad = 20 + math.sin(time.time() * 10) * 5
            pulse_s = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.circle(pulse_s, (255, 50, 50, 50), (tx, ty), int(pulse_rad))
            surface.blit(pulse_s, (0,0))

        # Center HUD panel
        panel_w, panel_h = 800, 160
        panel_x, panel_y = w//2 - panel_w//2, h//2 - panel_h//2
        pygame.draw.rect(surface, (10, 15, 20, 230), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(surface, (0, 150, 150), (panel_x, panel_y, panel_w, panel_h), 2)

        title = self.font_large.render("FASE DE CALIBRACIÓN ÓPTICA", True, (0, 255, 255))
        surface.blit(title, (w//2 - title.get_width()//2, panel_y + 25))
        
        prompt = self.font_small.render(msg, True, (200, 200, 200))
        surface.blit(prompt, (w//2 - prompt.get_width()//2, panel_y + 85))
        
        skip = self.font_small.render("[ ESPACIO para omitir (Auto-Calibración) ]", True, (0, 100, 100))
        surface.blit(skip, (w//2 - skip.get_width()//2, panel_y + 120))
