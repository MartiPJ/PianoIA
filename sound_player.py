"""
Módulo para la reproducción de sonidos de piano.
Este componente maneja la carga y reproducción de notas musicales.
"""

import numpy as np
import pygame
import os

class SoundPlayer:
    def __init__(self):
        """
        Inicializa el reproductor de sonido utilizando pygame
        """
        # Inicializar pygame y el mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.init()
        
        # Diccionario para almacenar los sonidos de las notas
        self.notes = {}
        
        # Crear directorio para las notas si no existe
        os.makedirs('notes', exist_ok=True)
        
        # Generar las notas si no existen
        self._generate_notes()
        
        # Cargar las notas del piano
        self._load_notes()
    
    def _generate_notes(self):
        """Genera archivos de sonido para las notas del piano usando síntesis simple"""
        # Diccionario con las frecuencias de las notas (en Hz)
        note_freqs = {
            'do4': 261.63, 're4': 293.66, 'mi4': 329.63, 'fa4': 349.23, 'sol4': 392.00,
            'la4': 440.00, 'si4': 493.88, 'do5': 523.25, 're5': 587.33, 'mi5': 659.26,
        }
        
        # Generar un sonido simple para cada nota
        for note_name, frequency in note_freqs.items():
            file_path = os.path.join('notes', f'{note_name}.wav')
            
            # Verificar si el archivo ya existe
            if os.path.exists(file_path):
                continue
            
            # Parámetros para la generación de sonido
            sample_rate = 44100  # Hz
            duration = 1.0  # segundos
            amplitude = 0.3  # entre 0 y 1
            
            # Generar un tono simple (onda sinusoidal)
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = amplitude * np.sin(frequency * t * 2 * np.pi)
            
            # Aplicar un envolvente ADSR simple (Attack, Decay, Sustain, Release)
            attack = int(0.02 * sample_rate)
            decay = int(0.1 * sample_rate)
            sustain_level = 0.7
            release = int(0.3 * sample_rate)
            
            envelope = np.ones(len(tone))
            # Attack
            envelope[:attack] = np.linspace(0, 1, attack)
            # Decay
            envelope[attack:attack+decay] = np.linspace(1, sustain_level, decay)
            # Sustain ya está configurado
            # Release
            envelope[-release:] = np.linspace(sustain_level, 0, release)
            
            # Aplicar envolvente
            tone = tone * envelope
            
            # Convertir a 16-bit PCM
            tone = np.int16(tone * 32767)
            
            # Guardar como WAV
            from scipy.io import wavfile
            wavfile.write(file_path, sample_rate, tone)
    
    def _load_notes(self):
        """Carga los archivos de sonido de las notas"""
        note_names = ['do4', 're4', 'mi4', 'fa4', 'sol4', 'la4', 'si4', 'do5', 're5', 'mi5']
        
        for note in note_names:
            file_path = os.path.join('notes', f'{note}.wav')
            if os.path.exists(file_path):
                self.notes[note] = pygame.mixer.Sound(file_path)
            else:
                print(f"Advertencia: No se pudo encontrar el archivo {file_path}")
    
    def play_note(self, note_name):
        """
        Reproduce una nota específica
        
        Parámetros:
        - note_name: Nombre de la nota a reproducir (ej: 'do4', 're5')
        """
        if note_name in self.notes:
            self.notes[note_name].play()
        else:
            print(f"Nota no encontrada: {note_name}")
    
    def play_chord(self, note_names):
        """
        Reproduce un acorde (varias notas simultáneamente)
        
        Parámetros:
        - note_names: Lista de nombres de notas a reproducir
        """
        for note in note_names:
            if note in self.notes:
                self.notes[note].play()
            else:
                print(f"Nota no encontrada: {note}")
    
    def cleanup(self):
        """Libera recursos"""
        pygame.mixer.quit()
        pygame.quit()