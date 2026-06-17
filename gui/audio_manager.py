import pygame
import numpy as np

class AudioManager:
    def __init__(self):
        try:
            # Inicializar el mixer de pygame (comúnmente a 44100 Hz, 16-bit, estéreo)
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.enabled = True
        except Exception as e:
            print(f"Error inicializando audio: {e}")
            self.enabled = False
            return

        self.sample_rate = 44100
        
        # Generar Sonidos
        self.sound_shoot = self._create_shoot_sound()
        self.sound_hit = self._create_ding_sound()
        self.sound_miss = self._create_thud_sound()
        
    def _create_shoot_sound(self):
        # Ruido blanco con un decaimiento exponencial (simula disparo/explosión)
        duration = 0.2 # segundos
        samples = int(self.sample_rate * duration)
        noise = np.random.normal(0, 1, samples)
        
        # Decaimiento
        envelope = np.exp(-np.linspace(0, 10, samples))
        audio = noise * envelope
        
        # Normalizar a 16-bit
        audio = np.int16(audio * 32767)
        # Hacer estéreo copiando el canal mono
        stereo_audio = np.column_stack((audio, audio))
        
        return pygame.sndarray.make_sound(stereo_audio)

    def _create_ding_sound(self):
        # Campana metálica para acierto (Onda senoidal con alta frecuencia)
        duration = 0.4
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # Frecuencia base de la campana
        freq = 1200
        wave = np.sin(freq * t * 2 * np.pi) * 0.5 + np.sin(freq * 1.5 * t * 2 * np.pi) * 0.25
        
        # Rápido ataque y largo decaimiento
        envelope = np.exp(-np.linspace(0, 5, samples))
        audio = wave * envelope
        
        audio = np.int16(audio * 32767 * 0.5) # Volumen un poco más bajo
        stereo_audio = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo_audio)

    def _create_thud_sound(self):
        # Ruido sordo y grave para fallo
        duration = 0.15
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # Frecuencia grave descendente
        freqs = np.linspace(150, 50, samples)
        wave = np.sin(freqs * t * 2 * np.pi)
        
        envelope = np.exp(-np.linspace(0, 5, samples))
        audio = wave * envelope
        
        audio = np.int16(audio * 32767 * 0.8)
        stereo_audio = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo_audio)

    def play_shoot(self):
        if self.enabled:
            self.sound_shoot.play()

    def play_hit(self):
        if self.enabled:
            self.sound_hit.play()

    def play_miss(self):
        if self.enabled:
            self.sound_miss.play()
