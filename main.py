import sys
import json
import time
import pygame

from gui.simulator import TargetSimulator
from gui.screens import ProfileScreen, CalibrationScreen
from gui.audio_manager import AudioManager
from db.database import init_db, get_or_create_user, log_shot

# Importar API del Middleware (Grupo 2)
from core import (
    build_shot_result_from_raw,
    serialize_message,
    validate_message,
    MessageValidationError
)

def main():
    print("Iniciando Simulador Táctico High-Fidelity")
    
    # Iniciar BD
    init_db()
    
    pygame.init()
    info = pygame.display.Info()
    # Usar ventana maximizada (forzada con ctypes en Windows)
    import ctypes
    w, h = 1024, 768
    screen = pygame.display.set_mode((w, h), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.SRCALPHA)
    pygame.display.set_caption("Simulador Táctico Avanzado")
    try:
        hwnd = pygame.display.get_wm_info()["window"]
        ctypes.windll.user32.ShowWindow(hwnd, 3) # SW_MAXIMIZE = 3
    except:
        pass
    clock = pygame.time.Clock()
    
    audio_mgr = AudioManager()

    # ESTADO 1: Perfiles
    profile_screen = ProfileScreen(w, h)
    while profile_screen.active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                w, h = event.w, event.h
                # En Pygame 2, al hacer resize se actualiza el display
                screen = pygame.display.set_mode((w, h), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.SRCALPHA)
            profile_screen.handle_event(event)
        
        profile_screen.render(screen)
        pygame.display.flip()
        clock.tick(60)
        
    user_name = profile_screen.input_text.strip()
    if not user_name:
        user_name = "Tirador_Anonimo"
        
    user_id = get_or_create_user(user_name)
    
    # ESTADO 2: Calibración
    calib_screen = CalibrationScreen(w, h)
    while calib_screen.active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                w, h = event.w, event.h
                screen = pygame.display.set_mode((w, h), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.SRCALPHA)
            calib_screen.handle_event(event)
            
        calib_screen.render(screen)
        pygame.display.flip()
        clock.tick(60)
        
    # ESTADO 3: Simulación (El simulador tomará control de la ventana)
    w, h = screen.get_size()
    simulator = TargetSimulator(audio_manager=audio_mgr, user_name=user_name, screen_w=w, screen_h=h)
    simulator.screen = screen
    simulator.width = w
    simulator.height = h
    simulator.running = True

    while simulator.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                simulator.running = False
                
            elif event.type == pygame.KEYDOWN:
                # MOCK: Presionar espacio simula señal del ESP32
                if event.key == pygame.K_SPACE:
                    mx, my = pygame.mouse.get_pos()
                    resultado_crudo_dict = simulator.register_shot(mx, my)
                    
                    try:
                        message_model = build_shot_result_from_raw(resultado_crudo_dict)
                        json_empaquetado = serialize_message(message_model)
                        validate_message(json_empaquetado)
                        
                        # Guardar en BD
                        log_shot(user_id, json_empaquetado)
                        
                        print(f"[BD] JSON Guardado y Validado: {json_empaquetado}")
                    except MessageValidationError as e:
                        print(f"ERROR DE VALIDACIÓN: {e}")
                    except Exception as e:
                        print(f"ERROR INESPERADO: {e}")
                        
                elif event.key == pygame.K_m:
                    simulator.moving_target = not simulator.moving_target
                    if not simulator.moving_target:
                        simulator.target_offset_x = 0.0
                        simulator.target_offset_y = 0.0
                    
                elif event.key == pygame.K_c:
                    simulator.holes.clear()
                    simulator.particles.clear()
                    simulator.floating_texts.clear()
                    simulator.total_shots = 0
                    simulator.hits = 0
                    simulator.misses = 0
                    
                elif event.key == pygame.K_ESCAPE:
                    simulator.running = False
                    
            elif event.type == pygame.VIDEORESIZE:
                w, h = event.w, event.h
                simulator.width = w
                simulator.height = h
                simulator.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.SRCALPHA)

        simulator.render_frame()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
